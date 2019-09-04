import socketio
import aiohttp.web

import numpy as np
import scipy
import math
import functools
import traceback

app = aiohttp.web.Application()
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
sio.attach(app)

HOST = "localhost"
PORT = 15555

func_params = ()

def f(x):
  return x

def exception_as_string(e):
  return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)

STEP_COUNT_INIT = 275
INC_TOL = 20  # must be even!

# @functools.lru_cache(maxsize=1024)
def get_result(params):
  f_wrapped = functools.lru_cache(maxsize=40000)(f)
  args = [params["parameters"][s] for s in func_params]

  step = (params["xmax"] - params["xmin"]) / STEP_COUNT_INIT

  xi = np.arange(params["xmin"], params["xmax"] + step, step)  # +step for fencepost
  step_sizes = [step for _ in range(xi.shape[0])]
  it = 0
  while True:
    # get y values
    yi = [f_wrapped(x, *args) for x in xi]
    max_allowed_dy = (np.max(yi) - np.min(yi)) / 120
    dy = np.gradient(yi)
    # check gradient
    inc = dy > max_allowed_dy 
    if not (it < 3 and np.any(inc)): break
    # flag all the spots where the gradient is too big and areas nearby
    padded = np.pad(inc, INC_TOL//2, "constant")
    big = np.repeat(padded[None], INC_TOL, axis=0)
    for ix, j in enumerate(range(-INC_TOL//2, INC_TOL//2)):
      big[ix] = np.roll(big[ix], j)
    inc = np.max(big, axis=0)[INC_TOL//2: -INC_TOL//2]
    # recalculate x values and save step sizes for each
    new_xi = []
    new_step_sizes = []
    for i, v in enumerate(xi):
      ss = step_sizes[i]
      if inc[i]:
        new_xi.append(v - ss/3)
        new_step_sizes.append(ss/3)
        new_xi.append(v)
        new_step_sizes.append(ss/3)
        new_xi.append(v + ss/3)
        new_step_sizes.append(ss/3)
      else:
        new_xi.append(v) 
        new_step_sizes.append(ss)
    xi = new_xi
    step_sizes = new_step_sizes
    it += 1
  
  return {"labels": list(xi), "data": yi, "error": None}

@sio.on('get_graph_update')
async def get_data(sid, params):
  try:
    result = get_result(params)
    await sio.emit('update_graph', result)
    return "OK"
  except Exception as e:
    await sio.emit('update_graph', {"error": exception_as_string(e), "labels": [], "data": []})
    return "ERROR"

@sio.on('get_function_update')
async def get_data(sid, params):
  global func_params
  try:
    # exec string throws error or sets f as global
    exec(params["code"], globals())
    func_params_temp = list(f.__code__.co_varnames)[:f.__code__.co_argcount]
    if func_params_temp[0] != "x":
      raise ValueError("x not first argument of f.")
    func_params = func_params_temp[1:]
    await sio.emit('update_function', {"params": func_params, "error": None})
  except Exception as e:
    await sio.emit('update_function', {"error": exception_as_string(e), "params": []})

routes = aiohttp.web.RouteTableDef()

@routes.get('/')
async def hello(request):
  return aiohttp.web.Response(text="This is the Python endpoint, not the chart app!")

app.add_routes(routes)

if __name__ == '__main__':
  aiohttp.web.run_app(app, path=HOST, port=PORT)

##############################################
# goals for Python library:
# with chartpy.session() as session:
#   graph = session.scatter(x, y **kwargs)  # builds/controls data JSONs to send
#   graph.setTitle("my title")
#   graph.show(blocking=True)  # throw the graph up on the page
#   graph.block()  # manually block
#   graph.save("filename.png")  # saves to downloads
#   graph.generateHTML()  # not sure how this would work
#   session.scatter(x, y, multi_y=True, blocking=True)
#
# with chartpy.session() as session:
#   session.interactive()
# High priority:
# scatter, line, scatter w labels, bar
# multiple types on same graph
# multiple graphs in interactive mode
# entire interactive mode while graph is displayed

# Other features
# draggable bar between parameters and graph
# click and drag, scroll on graph
# turn animation on/off
