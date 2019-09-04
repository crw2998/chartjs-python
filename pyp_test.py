from pyppeteer import launch
import asyncio
import threading

async def main():
  try:
    browser = await launch(headless=False, args=["--start-maximized"], setDefaultViewport=False)
    page = await browser.newPage()
    height, width, dpr = await page.evaluate("[screen.height, screen.width, window.devicePixelRatio]")
    await page.setViewport({
      "width": width-150,
      "height": height-275,
      "deviceScaleFactor": 2
    });
    await page.goto("http://localhost:3000/index.html")
    await page.setViewport({
      "width": 1000,
      "height": 600,
      "deviceScaleFactor": 2
    });
    return browser
  except:
    await close(browser)
    raise

async def close(browser):
  await browser.close()


if __name__ == "__main__":
  el = asyncio.new_event_loop()
  el2 = asyncio.new_event_loop()
  asyncio.set_event_loop(el2)
  t = threading.Thread(target=el2.run_forever)
  t.start()

  browser = el.run_until_complete(main())
  el.run_until_complete(close(browser))
  asyncio.gather(*asyncio.Task.all_tasks()).cancel()
  el2.call_soon_threadsafe(el2.stop)
  t.join()