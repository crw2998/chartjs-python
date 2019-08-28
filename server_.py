import socketio
import aiohttp.web
import webbrowser
import asyncio
import threading

import random
import string

DEFAULT_PORT = 3000
DEFAULT_HOST = "localhost"
STATIC_FILES = "build"

class Session(object):
  def __init__(self, port=DEFAULT_PORT):
    self.port = port
    self.host = DEFAULT_HOST
    self.token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(25)])
    print (self.token)

  async def _start_server(self):
    try:
      self.app = aiohttp.web.Application()
      self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
      self.sio.attach(app)

      self.app.router.add_static("/", "build/")
      self.runner = aiohttp.web.AppRunner(self.app)
      await self.runner.setup()
      site = aiohttp.web.TCPSite(self.runner, self.host, self.port)
      await site.start()
      return True
    except Exception as e:
      print (e)
      return False

  async def _stop_server(self):
    try:
      await self.runner.cleanup()
      return True
    except Exception as e:
      print (e)
      return False

  def __enter__(self):
    self.event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.event_loop)
    # run the server both asynchronously and on a separate thread
    threading.Thread(target=self.event_loop.run_forever).start()
    future = asyncio.run_coroutine_threadsafe(self._start_server(), self.event_loop)
    # wait for server to start
    if not future.result():
      raise RuntimeError("Could not start server")

    # webbrowser.open(self.host + ":" + str(self.port) + "/" + self.token)
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    future = asyncio.run_coroutine_threadsafe(self._stop_server(), self.event_loop)
    if not future.result():
      raise RuntimeError("Could not stop server")

  async def _update(self, chart_json):
    self.sio.emit("update_graph", chart_json)

  def update(self, chart_json):
    asyncio.run_coroutine_threadsafe(self._update(), self.event_loop)

  def get_plot(self):
    return Plot(self)

  def interactive(self):
    raise NotImplementedError

class Plot(object):
  static_data = {
    datasets: [
      {
        label: 'f',
        fill: false,
        lineTension: 0,
        backgroundColor: 'rgba(255, 255, 255, 1)',
        borderColor: 'rgba(0,0,0,1)',
        borderCapStyle: 'butt',
        borderDash: [],
        borderDashOffset: 0.0,
        borderJoinStyle: 'miter',
        pointBorderColor: 'rgba(0,0,0,1)',
        pointBackgroundColor: '#fff',
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: 'rgba(0,0,0,1)',
        pointHoverBorderColor: 'rgba(220,220,220,1)',
        pointHoverBorderWidth: 2,
        pointRadius: 0,
        showLine: true,
        pointHitRadius: 10,
        yAxisID: 'yax1',
        xAxisID: 'xax1',
      },
    ],
  }
  def __init__(self, sess):
    self.json = {}
    self.sess = sess

  def set_json(self, new_json):
    self.json = new_json
    self.sess.update(self.json)

def main():
  with Session() as sess:
    plot = sess.get_plot()
    input("Press Enter to continue...")


if __name__ == '__main__':
  main()
