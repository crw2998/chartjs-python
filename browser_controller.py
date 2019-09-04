import contextlib
from time import sleep
import webbrowser
from pyppeteer import launch

# Simple implementation that is not up to the task of wrangling a whole browser
class SimpleBrowser(object):
  def __init__(self):
    pass

  async def start_browser(self):
    pass

  async def open_page(self, url):
    webbrowser.open(url)

  async def set_figure_size(self, width, height):
    pass

  async def close(self):
    return True

class PuppeteerBrowser(object):
  def __init__(self, headless=False, use_scale_factor=True):
    self._headless = headless
    self._use_scale_factor = use_scale_factor

  async def start_browser(self):
    try:
      self.browser = await launch(headless=self._headless, args=["--start-maximized"], setDefaultViewport=False)
      self.page = await self.browser.newPage()
      height, width, dpr = await self.page.evaluate("[screen.height, screen.width, window.devicePixelRatio]")
      await self.page.setViewport({
        "width": width-150,
        "height": height-275,
        "deviceScaleFactor": 2 if self._use_scale_factor else 1
      });
    except:
      await self.try_close()
      raise

  async def open_page(self, url):
    await self.page.goto(url)

  async def set_figure_size(self, width, height):
    await self.page.setViewport({
      "width": width,
      "height": height,
      "deviceScaleFactor": 2 if self._use_scale_factor else 1
    });

  async def try_close(self):
    # with contextlib.suppress(Exception):
      await self.browser.close()

