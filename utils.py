import asyncio 
import traceback

def exception_as_string(e):
  return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)

async def wait_with_timeout(event, timeout):
  try:
    await asyncio.wait_for(event.wait(), timeout)
    return True
  except asyncio.TimeoutError:
    return False
  finally:
    event.clear()  # executed before return statements
