import React from 'react';
import './App.css';

import PropTypes from 'prop-types';
import Slider from '@material-ui/core/Slider';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import NumberValidatedTextField from './NumberValidatedTextField';

const FunctionLimitSlider = withStyles({
  root: {
    width: '75px',
  },
})(Slider);

class FunctionParameter extends React.Component {
  constructor(props) {
    super(props);
    const { defaultMinValue, defaultMaxValue, defaultValue } = props;
    this.state = {
      min: defaultMinValue,
      max: defaultMaxValue,
    };
    this.sliderPosition = defaultValue;
  }

  async onChange(value, stateKey) {
    const val = parseFloat(value);
    if (val === undefined || val === '' || Number.isNaN(val)) {
      return;
    }
    await this.setState({ [stateKey]: val });
    this.checkSliderLimits();
  }

  checkSliderLimits() {
    const { min, max } = this.state;
    const { onChange } = this.props;
    if (this.sliderPosition > max) {
      this.sliderPosition = max;
      onChange(this.sliderPosition);
    }
    if (this.sliderPosition < min) {
      this.sliderPosition = min;
      onChange(this.sliderPosition);
    }
  }


  handleSliderChange(event, value) {
    const { onChange } = this.props;
    if (this.sliderPosition !== value) {
      this.sliderPosition = value;
      onChange(value);
    }
  }

  render() {
    const {
      defaultMinValue,
      defaultMaxValue,
      defaultValue,
      name,
    } = this.props;
    const { min, max } = this.state;
    return (
      <div className="function-parameter-div">
        <Typography className="parameter-label align-self-center">{name}</Typography>
        <NumberValidatedTextField
          defaultValue={defaultMinValue}
          onChange={(val) => this.onChange(val, 'min')}
          label="min"
          needsValue
          lowerThan={max}
          className="func-param-slider-limit"
        />
        <FunctionLimitSlider
          id={`slider-${name}`}
          defaultValue={defaultValue}
          valueLabelDisplay="auto"
          step={(max - min) / 25}
          min={min}
          max={max}
          onChange={(event, value) => this.handleSliderChange(event, value)}
          className="align-self-center func-param-slider"
        />
        <NumberValidatedTextField
          defaultValue={defaultMaxValue}
          onChange={(val) => this.onChange(val, 'max')}
          label="max"
          needsValue
          higherThan={min}
          className="func-param-slider-limit"
        />
      </div>
    );
  }
}

FunctionParameter.propTypes = {
  defaultMinValue: PropTypes.number.isRequired,
  defaultMaxValue: PropTypes.number.isRequired,
  defaultValue: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
};

export default FunctionParameter;
