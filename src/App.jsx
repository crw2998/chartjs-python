import React from 'react';
import './App.css';

import _ from 'lodash';

import sizeMe from 'react-sizeme';

import { ThemeProvider } from '@material-ui/styles';

import { Scatter } from 'react-chartjs-2';

import { subscribeToGraphUpdates, requestGraphUpdate, unsubscribeToUpdates } from './api';
import PythonArea from './PythonArea';
import FunctionParameters from './FunctionParameters';
import ChartControls from './ChartControls';
import theme from './theme';

const staticData = {
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
};


class ChartView extends React.Component {
  constructor(props) {
    super(props);
    subscribeToGraphUpdates((res) => this.setState({
      labels: res.labels,
      data: res.data,
      error: res.error,
    }));
    this.xdefaults = { xmin: -5, xmax: 5 };
    this.state = {
      plotExtrema: {
        xmin: this.xdefaults.xmin,
        xmax: this.xdefaults.xmax,
        ymin: undefined,
        ymax: undefined,
      },
      data: [],
      labels: [],
      parameterNames: [],
      params: {},
    };
    this.updateData();
  }

  componentWillUnmount() {
    unsubscribeToUpdates();
  }

  updateData() {
    const {
      params, plotExtrema: {
        xmin, xmax, ymin, ymax,
      },
    } = this.state;
    const paramsForPython = {
      xmin,
      xmax,
      ymin,
      ymax,
      parameters: params,
    };
    requestGraphUpdate(paramsForPython);
  }

  async update(stateUpdate) {
    if (Object.prototype.hasOwnProperty.call(stateUpdate, 'parameterNames') && stateUpdate.parameterNames === null) {
      return;
    }
    await this.setState(stateUpdate);
    this.updateData();
  }

  render() {
    const { labels, data } = this.state;
    const plotData = staticData;

    plotData.datasets[0].data = [];
    for (let i = 0; i < labels.length; i += 1) {
      plotData.datasets[0].data.push({
        x: _.round(labels[i], 3),
        y: _.round(data[i], 3),
      });
    }
    const {
      plotExtrema: {
        ymin, ymax, xmin, xmax,
      },
    } = this.state;
    const options = {
      animation: false, // {
      // duration: 0
      // }
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        yAxes: [{
          id: 'yax1',
          // type: 'linear',
          display: true,
          gridLines: {
            color: 'lightgray',
            zeroLineColor: 'black',
          },
          ticks: {
            min: ymin === '' ? undefined : ymin,
            max: ymax === '' ? undefined : ymax,
          },
        }],
        xAxes: [{
          id: 'xax1',
          // type: 'linear',
          display: true,
          gridLines: {
            color: 'lightgray',
            zeroLineColor: 'black',
          },
          ticks: {
            min: xmin,
            max: xmax,
          },
        }],
      },
    };

    const { error, parameterNames } = this.state;
    const pythonError = error || '';
    return (
      <div className="app-container">
        <div className="controls-container">
          <ChartControls
            xdefaults={this.xdefaults}
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
        <div className="chart-container">
          <Scatter data={plotData} options={options} />
        </div>
      </div>
    );
  }
}

function App() {
  const SizedChartView = sizeMe({ monitorHeight: true })(ChartView);
  return (
    <div className="App">
      <ThemeProvider theme={theme}><SizedChartView /></ThemeProvider>
    </div>
  );
}

export default App;
