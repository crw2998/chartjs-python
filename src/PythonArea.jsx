import React from 'react';
import './App.css';

import PropTypes from 'prop-types';

import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import { requestFunctionUpdate, subscribeToFunctionUpdates } from './api';

const DEFAULT_CODE = `def f(x, a, b, c):
  return a*x*x + b*x + c`;

const PythonTextField = withStyles({
  root: {
    'font-family': 'monospace',
    'padding-left': '4px',
  },
})(TextField);

class PythonArea extends React.Component {
  constructor(props) {
    super(props);
    this.contents = DEFAULT_CODE;
    subscribeToFunctionUpdates((res) => this.processFunctionResult(res));
    this.state = {
      errortext: '',
    };
  }

  componentDidMount() {
    requestFunctionUpdate({ code: this.contents });
  }

  // eslint-disable-next-line class-methods-use-this
  onChange(event) {
    const contents = event.target.value;
    requestFunctionUpdate({ code: contents });
  }

  processFunctionResult(res) {
    const { handleFunctionUpdate } = this.props;
    this.setState({ errortext: res.error === null ? '' : res.error }, () => {
      handleFunctionUpdate(res.params);
    });
  }

  render() {
    const { errortext } = this.state;
    const { errorOverrideData } = this.props;
    let err = errortext;
    if (!errortext && errorOverrideData !== null) {
      err = errorOverrideData;
    }
    let errortextHTML;
    if (Array.isArray(err)) {
      errortextHTML = [];
      for (let i = 0; i < err.length; i += 1) {
        errortextHTML.push(
          <Typography key={i} className="error-area">{err[i]}</Typography>,
        );
      }
    } else {
      errortextHTML = <Typography className="error-area">{err}</Typography>;
    }
    return (
      <div className="python-container">
        <PythonTextField
          multiline
          rows={8}
          variant="outlined"
          className="python"
          onChange={(event) => this.onChange(event)}
          defaultValue={this.contents}
        />
        <div className="error-container" data-testid="error-container">
          {errortextHTML}
        </div>
      </div>
    );
  }
}

PythonArea.propTypes = {
  handleFunctionUpdate: PropTypes.func.isRequired,
  errorOverrideData: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
    PropTypes.arrayOf(PropTypes.string),
  ]).isRequired,
};

export default PythonArea;
