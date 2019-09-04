import socketio
import aiohttp.web
import webbrowser
import asyncio
import threading
import contextlib

from urllib.request import urlopen
import binascii

import random
import string

from plot import _Figure
from utils import exception_as_string, wait_with_timeout
from browser_controller import PuppeteerBrowser, SimpleBrowser

DEFAULT_PORT = 15555
DEFAULT_HOST = "localhost"
STATIC_FILES = "build"

RENDER_TIMEOUT = 5
SAVE_TIMEOUT = 7
BROWSER_LOAD_TIMEOUT = 10
DISCONNECT_TIMEOUT = 4

class ChartSession(object):
  def __init__(self, port=DEFAULT_PORT, retina_display=True):
    self.port = port
    self.host = DEFAULT_HOST
    self.token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(25)])  # TODO
    self._figure = _Figure()
    self._connections = set()
    self._save_file = None
    self._retina = retina_display

  async def _start_server(self):
    try:
      # Basically a condition variable without a lock, lets us lock out from shutting down event loop
      # and server if we have a pending request for image data or something
      self._is_saving = asyncio.Event()
      self._is_rendering = asyncio.Event()
      self._sio_connecting = asyncio.Event()

      self.app = aiohttp.web.Application()
      self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")  # TODO cors
      self.sio.attach(self.app)
      # request from the client for updated graph data, for interactive visualization
      self.sio.on("get_graph_update", self._update)
      # request from the client for updated function data, contains Python to execute on server and
      # give back info about exceptions and parameters for sliders
      self.sio.on("get_function_update", self._function_update)
      # signal from the client that a render triggered by _emit() is finished
      self.sio.on("graph_updated", self._graph_updated)
      # image data from the client from a save request
      self.sio.on("send_image_data", self._receive_image_data)
      self.sio.on("connect", self._record_connection)
      self.sio.on("disconnect", self._remove_connection)

      self.app.router.add_static("/", "build/")
      self.runner = aiohttp.web.AppRunner(self.app)
      await self.runner.setup()
      self.site = aiohttp.web.TCPSite(self.runner, self.host, self.port)
      await self.site.start()
      return True
    except Exception as e:
      # just try to execute the with body in order, and bail if we get another exception.
      # if sio.disconnect fails, we didn't even create the runner.
      with contextlib.suppress(Exception):
        await self._stop_server()
      print (''.join(exception_as_string(e)))
      return False

  async def _stop_server(self):
    try:
      await asyncio.wait_for(self.sio.disconnect(True), DISCONNECT_TIMEOUT)
      await asyncio.wait_for(self.runner.cleanup(), DISCONNECT_TIMEOUT)
      return True
    except asyncio.TimeoutError:
      print ("Server shutdown timed out. Close extraneous Chromium instances. Forcing shutdown...")
    except Exception as e: # won't catch KeyboardInterrupt
      print (''.join(exception_as_string(e)))
      return False

  # context manager syntax handles server spinup and teardown
  def __enter__(self):
    self.event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.event_loop)
    # puppeteer can only run from main thread due to multiprocessing things.
    self.main_thread_event_loop = asyncio.new_event_loop()
    # run the server both asynchronously and on a separate thread.

    # Start event loop on separate thread. We can throw coroutines at this event loop
    # from anywhere (any thread) we want, and wait on them to finish (if necessary) by
    # accessing the returned future.
    self._el_thread = threading.Thread(target=self.event_loop.run_forever)
    self._el_thread.start()

    # run start server coroutine on the event loop we just started.
    future = asyncio.run_coroutine_threadsafe(self._start_server(), self.event_loop)
    # wait for server to start, events to register, etc
    if not future.result():
      raise RuntimeError("Could not start server")
    # would like to use contextlib.ExitStack(), but I don't think we could wait on
    # the browser on the EL thread then
    # this ensures that we properly exit the server if we get an exception while starting the browser.
    try:
      future = self.main_thread_event_loop.run_until_complete(self._open_page())
      # wait for browser to start and go to page
      wait_for_browser = wait_with_timeout(self._sio_connecting, BROWSER_LOAD_TIMEOUT)
      future = asyncio.run_coroutine_threadsafe(wait_for_browser, self.event_loop)
      if not future.result():
        raise RuntimeError("Could not start browser")
    except Exception as e:
      print ("".join(exception_as_string(e)))
      self.__exit__(type(e), e, e.__traceback__) 
      raise

    return self

  def __exit__(self, exc_type, exc_value, traceback):
    # close browser window and process if possible
    res = self.main_thread_event_loop.run_until_complete(self._browser.try_close())
    # send server shutdown coroutine to the event loop
    future = asyncio.run_coroutine_threadsafe(self._stop_server(), self.event_loop)
    # wait for server to finish shutting down
    if not future.result():
      print ("Could not stop server. Going to force close async tasks anyway...")
    # shut down the event loop on the other thread
    asyncio.gather(*asyncio.Task.all_tasks()).cancel()  # unsure if this is advisable/necessary
    self.event_loop.call_soon_threadsafe(self.event_loop.stop)
    self.main_thread_event_loop.close()
    # join the event loop thread
    self._el_thread.join()

  async def _open_page(self):
    self._browser = PuppeteerBrowser(use_scale_factor=self._retina)
    await self._browser.start_browser()
    await self._browser.open_page(f"http://{self.host}:{3000}/index.html")
    return True

  async def _update(self, sid, params):
    ipl = self._figure._get_interactive_plot()
    if params and ipl:
      plot_result = ipl._update_plot(params)
    self.figure_data = self._figure._get_data()
    if plot_result["error"]:
      self.figure_data["error"] = plot_result["error"]
    return await self._emit()

  async def _emit(self):
    await self.sio.emit("update_graph", self.figure_data)
    return await wait_with_timeout(self._is_rendering, RENDER_TIMEOUT)

  async def _function_update(self, sid, params):
    ipl = self._figure._get_interactive_plot()
    if ipl:
      res = ipl._get_function_info(params)
      await self.sio.emit("update_function", res)

  async def _graph_updated(self, sid, params=None):
    self._is_rendering.set()

  async def _record_connection(self, sid, params):
    self._connections.add(sid)
    self._sio_connecting.set()

  async def _remove_connection(self, sid):
    self._connections.remove(sid)

  async def _request_image_data(self):
    await self.sio.emit("request_image_data")
    return await wait_with_timeout(self._is_saving, SAVE_TIMEOUT)
  
  async def _receive_image_data(self, sid, params):
    with urlopen(params) as image:
      data = image.read()
      with open(self._save_file, "wb") as f:
        f.write(data)
    self._is_saving.set()
    return True

  async def _set_figure_size(self, width, height):
    await self._browser.set_figure_size(width, height)

  # right now, there can only be one figure per session, but this could easily be changed.
  def get_figure(self):
    return self._figure

  # set height/width of figure viewport in px to be shown in Chromium.
  # the control panel for interactive figures takes up space, so this won't work correctly
  # in interactive mode (for now).
  def set_figure_size(self, width, height):
    future = self.main_thread_event_loop.run_until_complete(self._set_figure_size(width, height))

  def show(self, blocking : bool = True):
    self.figure_data = self._figure._get_data()
    future = asyncio.run_coroutine_threadsafe(self._emit(), self.event_loop)
    if not future.result():  # waits until coroutine is executed or raises
      raise RuntimeError("Could not update graph data")
    if blocking:
      input("Press enter to unblock.")

  # save the figure as a png
  def save(self, filename):
    self._save_file = filename
    future = asyncio.run_coroutine_threadsafe(self._request_image_data(), self.event_loop)
    if not future.result():  # waits until coroutine is executed
      raise RuntimeError("Could not contact browser to get image data")
    self._save_file = None

