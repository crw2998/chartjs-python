import functools
import math
from collections import defaultdict
from typing import Union, Optional, List, Tuple

import numpy as np
import scipy

from .utils import exception_as_string

class _Figure(object):
  def __init__(self):
    self._options = {
      "animation": False,
      "responsive": True,
      "showLines": False,
      "maintainAspectRatio": False,
      "tooltips": {
        "enabled": False,
      },
      "scales": {
        "yAxes": [],
        "xAxes": [],
      },
    }
    self._defaultXAxis = _Axis(True, "xax0")
    self._defaultYAxis = _Axis(True, "yax0")
    self._xaxes = [self._defaultXAxis]
    self._yaxes = [self._defaultYAxis]
    self._plots = []
    self._interactive_plot = None
    self.set_legend(display=False)
    self.set_title("", display=False)

  def _get_new_axis(self, is_X):
    if is_X:
      ax = _Axis(True, "xax" + str(len(self._xaxes)))
      self._xaxes.append(ax)
    if not is_X:
      ax = _Axis(True, "yax" + str(len(self._yaxes)))
      self._yaxes.append(ax)
    return ax

  def add_interactive_plot(self):
    plot = _InteractivePlot(self, self._defaultXAxis, self._defaultYAxis, "interactive")
    self._interactive_plot = plot
    return plot

  def _get_interactive_plot(self):
    return self._interactive_plot

  def get_new_plot(self):
    plot = _Plot(self, self._defaultXAxis, self._defaultYAxis, str(len(self._plots)))
    self._plots.append(plot)
    return plot

  def _get_data(self, blocking : bool = True):
    options = self._options
    if self._legend is not None:
      options["legend"] = self._legend._get_data()
    if self._title is not None:
      options["title"] = self._title._get_data()
    options["scales"]["xAxes"] = [ax._get_data() for ax in self._xaxes]
    options["scales"]["yAxes"] = [ax._get_data() for ax in self._yaxes]

    if self._interactive_plot is not None:
      all_plots = self._plots + [self._interactive_plot]
    else:
      all_plots = self._plots
    datasets = []
    for i, p in enumerate(all_plots):
      plot_data = p._get_data()
      datasets.append(plot_data)
    data = {"datasets": datasets}

    return {
      "data": data,
      "error": "",
      "options": options,
      "interactive": self._interactive_plot is not None,
      "defaultxmin": self._defaultXAxis.ax_min,
      "defaultxmax": self._defaultXAxis.ax_max,
    }

  def set_title(self, *args, **kwargs):
    self._title = _Title(*args, **kwargs)

  def set_legend(self, *args, **kwargs):
    self._legend = _Legend(*args, **kwargs)
  def get_legend(self):
    return self._legend
    

class _Plot(object):
  def __init__(self, fig, xax, yax, id_):
    self._xaxis = xax
    self._yaxis = yax
    self.fig = fig
    self.id_ = id_
    self._dataset = {
      "label": self.id_,
      "fill": False,
      "tension": 0,
      "backgroundColor": 'rgba(255, 255, 255, 0)',
      "borderCapStyle": 'butt',
      "borderDash": [],
      "borderDashOffset": 0.0,
      "borderJoinStyle": 'miter',
      "pointBorderColor": 'rgba(0,0,0,1)',
      "pointBackgroundColor": 'rgba(0,0,0,1)',
      "pointBorderWidth": 1,
      "pointHoverRadius": 5,
      "pointHoverBorderColor": 'rgba(220,220,220,1)',
      "pointRadius": 4,
      "showLine": False,
      "pointHitRadius": 3,
      "yAxisID": "",
      "xAxisID": "",
      "data": [],
      "datalabels": {
        "display": False,
        "color": "black",
        "align": "right",
      },
    }

  def _get_data(self):
    data = self._dataset
    data["xAxisID"] = self._xaxis.get_id()
    data["yAxisID"] = self._yaxis.get_id()
    return data

  def _normalize_array(self, arr):
    res = []
    for x in arr:
      if 'numpy' in str(type(x)):
        res.append(float(x))
      else:
        res.append(x)
    return res

  def scatter(self, xvals: List[float], yvals : List[float],
              labels : Optional[List[str]] = None,
              label_size : Optional[float] = None,
              label_color : Optional[str] = "#000",
              size : Optional[Union[float, List[float]]] = None,
              color : Optional[Union[str, List[str]]] = None,
              linecolor : str = "#000"):
    self._xlims = min(xvals), max(xvals)
    self._ylims = min(yvals), max(yvals)
    xvals = self._normalize_array(xvals)
    yvals = self._normalize_array(yvals)
    self._dataset["data"] = [{"x": x, "y": y} for (x, y) in zip(xvals, yvals)]
    self._dataset["borderColor"] = linecolor
    self._dataset["pointHoverBackgroundColor"] = linecolor
    if labels is not None:
      self._dataset["datalabels"]["display"] = True
      self._dataset["datalabels"]["font"] = {}
      self._dataset["datalabels"]["color"] = label_color
      self._dataset["datalabels"]["font"]["size"] = label_size
      self._dataset["data"] = [{"x": x, "y": y, "label": l} for (x, y, l) in zip(xvals, yvals, labels)]
    else:
      self._dataset["data"] = [{"x": x, "y": y} for (x, y) in zip(xvals, yvals)]
    if size is not None:
      self._dataset["pointRadius"] = size
    if color is not None:
      self._dataset["pointBackgroundColor"] = color
    self._xaxis._update_data_lims(*self._xlims, self.id_)
    self._yaxis._update_data_lims(*self._ylims, self.id_)
    self.set_auto_lims()

  # **kwargs passed to scatter() arguments
  def plot(self, xvals : List[float], yvals : List[float], **kwargs):
    self.scatter(xvals, yvals, **kwargs)
    self._dataset["pointRadius"] = 2
    self._dataset["showLine"] = True
    self._dataset["pointRadius"] = 0

  def get_xaxis(self):
    return self._xaxis

  def get_yaxis(self):
    return self._yaxis

  def set_auto_lims(self):
    self._xaxis.set_auto_lims()
    self._yaxis.set_auto_lims()

  # if xax is None, creates a new one
  def set_xaxis(self, xax : Optional["_Axis"] = None):
    if xax is None:
      xax = self.fig._get_new_axis(True)
    self._xaxis = xax
    return yax

  # if yax is None, creates a new one
  def set_yaxis(self, yax : Optional["_Axis"] = None):
    if yax is None:
      yax = self.fig._get_new_axis(False)
    self._yaxis = yax
    return yax

  def set_label(self, label : str):
    self._dataset["label"] = label



class _InteractivePlot(_Plot):
  def __init__(self, *args):
    super().__init__(*args)

    def f(x):
      return x
    self.f = f
    self.func_params = None

  STEP_COUNT_INIT = 275
  INC_TOL = 20  # must be even!

  # The big challenge here is to figure out how many points we need in each 
  # part of the graph to make it smooth.
  def get_result(self, params):
    if not self.func_params:
      return [], []
    f_wrapped = functools.lru_cache(maxsize=40000)(self.f)
    args = [params["parameters"][s] for s in self.func_params]

    step = (params["xmax"] - params["xmin"]) / self.STEP_COUNT_INIT

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
      padded = np.pad(inc, self.INC_TOL//2, "constant")
      big = np.repeat(padded[None], self.INC_TOL, axis=0)
      for ix, j in enumerate(range(-self.INC_TOL//2, self.INC_TOL//2)):
        big[ix] = np.roll(big[ix], j)
      inc = np.max(big, axis=0)[self.INC_TOL//2: -self.INC_TOL//2]
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
    return list(xi), yi

  def _get_function_info(self, params):
    try:
      # exec string throws error or sets f as global
      exec(params["code"], globals())
      func_params_temp = list(f.__code__.co_varnames)[:f.__code__.co_argcount]
      if func_params_temp[0] != "x":
        raise ValueError("x not first argument of f.")
      self.func_params = func_params_temp[1:]
      self.f = f
      return {"params": self.func_params, "error": None}
    except Exception as e:
      return {"error": exception_as_string(e), "params": []}

  def _update_plot(self, params):
    try:
      xi, yi = self.get_result(params)
      self.plot(xi, yi)
      if not xi:
        return {"error": None}
      self._xaxis.set_lims(params["xmin"], params["xmax"])
      if "ymin" in params:
        self._yaxis.set_lims(params["ymin"], params["ymax"])
      else:
        self._yaxis._update_data_lims(min(yi), max(yi), self.id_)
        self._yaxis.set_auto_lims()

      return {"error": None}
    except Exception as e:
      # print (exception_as_string(e))
      return {"error": exception_as_string(e)}

def round_to_n(x, n):
  return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))

class _Axis(object):
  def __init__(self, is_X, axis_id):
    self.is_X = is_X
    self.data = {
      "id": axis_id,
      "type": "linear",
      "display": True,
      "gridLines": {
        "color": "lightgray",
        "zeroLineColor": "black",
      },
      "ticks": {},
    }
    self.data_mins = {}
    self.data_maxes = {}
    self.step = None

  def get_id(self):
    return self.data["id"]

  def set_lims(self, new_min : float, new_max : float, stepSize : Optional[float] = None):
    assert new_min < new_max
    self.step = stepSize if stepSize else round_to_n((new_max - new_min) / 12, 2)

    self.ax_min = new_min
    self.ax_max = new_max

  def set_auto_lims(self):
    data_max = max(self.data_maxes.values())
    data_min = min(self.data_mins.values())
    spread = data_max - data_min
    self.set_lims(data_min - spread*0.1, data_max + spread*0.1)

  def _update_data_lims(self, new_min, new_max, dataset_id):
    self.data_mins[dataset_id] = new_min
    self.data_maxes[dataset_id] = new_max

  def _get_data(self):
    data = self.data
    data["ticks"]["min"] = self.ax_min
    data["ticks"]["max"] = self.ax_max
    data["ticks"]["stepSize"] = self.step
    return data


class _Legend(object):
  def __init__(self, display : bool = False, position : str = "top"):
    self._data = {
      "display": display,
      "position": position
    }
  def _get_data(self):
    return self._data
  def set_display(self, val : bool = True):
    self._data["display"] = val

class _Title(object):
  def __init__(self,
               title : str,
               display : bool = True,
               fontSize : float = 24,
               fontFamily : str = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
               fontColor : str = "#000",
               fontStyle : str = "bold",
               padding : float = 10,
               line_height : float = 1.2,
               position : str = "top",):
    self._data = {
      "display": display,
      "text": title,
      "fontSize": fontSize,
      "fontFamily": fontFamily,
      "fontColor": fontColor,
      "fontStyle": fontStyle,
      "padding": padding,
      "line_height": line_height,
      "position": position,
    }
  def _get_data(self):
    return self._data
