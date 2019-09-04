import React from 'react';
import './App.css';

import { ThemeProvider } from '@material-ui/styles';

import { Scatter } from 'react-chartjs-2';
import 'chartjs-plugin-datalabels';

import Chart from 'chart.js';
import {
  subscribeToGraphUpdates,
  requestGraphUpdate,
  unsubscribeToUpdates,
  setImageDataHandler,
  unsubscribeImageDataHandler,
  sendImageData,
  fireGraphUpdated,
} from './api';
import PythonArea from './PythonArea';
import FunctionParameters from './FunctionParameters';
import ChartControls from './ChartControls';
import theme from './theme';


class ChartView extends React.Component {
  constructor(props) {
    super(props);
    subscribeToGraphUpdates(async (res) => {
      await this.setState({
        plotData: res.data,
        error: res.error,
        options: res.options,
        interactive: res.interactive,
        defaultxmin: res.defaultxmin,
        plotExtrema: {
          xmin: res.defaultxmin,
          xmax: res.defaultxmax,
        },
        defaultxmax: res.defaultxmax,
      });
      console.log (res);
      fireGraphUpdated();
    });
    setImageDataHandler(() => {
      // loop for good measure, there should only be one
      const ids = Object.keys(Chart.instances);
      for (let i = 0; i < ids.length; i += 1) {
        const imageData = Chart.instances[ids[i]].toBase64Image();
        sendImageData(imageData);
        break;
      }
    });
    this.state = {
      plotExtrema: {
        xmin: -5,
        xmax: 5,
        ymin: undefined,
        ymax: undefined,
      },
      parameterNames: [],
      params: {},
      plotData: { datasets: [] },
    };
  }

  componentDidUpdate() {
    const ids = Object.keys(Chart.instances);
    for (let i = 0; i < ids.length; i += 1) {
      Chart.instances[ids[i]].resize();
    }
  }

  componentWillUnmount() {
    unsubscribeImageDataHandler();
    unsubscribeToUpdates();
  }

  updateData() {
    const {
      params,
      plotExtrema: {
        xmin, xmax, ymin, ymax,
      },
    } = this.state;
    const paramsForPython = {
      xmin,
      xmax,
      ymin: ymin === '' ? undefined : ymin,
      ymax: ymax === '' ? undefined : ymax,
      parameters: params,
    };
    requestGraphUpdate(paramsForPython);
  }


  async update(stateUpdate) {
    if (Object.prototype.hasOwnProperty.call(stateUpdate, 'parameterNames') && stateUpdate.parameterNames === null) {
      return;
    }
    await this.setState(stateUpdate); // yeah yeah callbacks instead of await, but this is prettier
    this.updateData();
  }

  render() {
    const {
      error, parameterNames, options, plotData, interactive, defaultxmin, defaultxmax,
    } = this.state;
    const pythonError = error || '';
    let controls;
    if (interactive) {
      controls = (
        <div className="controls-container">
          <ChartControls
            xdefaults={{ xmin: defaultxmin, xmax: defaultxmax }}
            onChange={(params) => this.update({ plotExtrema: params })}
          />
          <PythonArea
            handleFunctionUpdate={(res) => this.update({ parameterNames: res })}
            errorOverrideData={pythonError}
          />
          <FunctionParameters
            sliderDefault={{ min: -5, max: 5, value: 1 }}
            parameterNames={parameterNames}
            onChange={(params) => this.update({ params })}
          />
        </div>
      );
    }
    return (
      <div className="app-container">
        {controls}
        <div className={`chart-container${interactive ? ' interactive-chart-container' : ''}`}>
          <Scatter data={plotData} options={options} />
        </div>
      </div>
    );
  }
}

function App() {
  return <ThemeProvider theme={theme}><ChartView /></ThemeProvider>;
}

export default App;
