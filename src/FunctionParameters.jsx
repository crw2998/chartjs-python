import React from 'react';
import './App.css';

import PropTypes from 'prop-types';

import FunctionParameter from './FunctionParameter';

class FunctionParameters extends React.Component {
  constructor(props) {
    super(props);
    this.loadSliderValues();
  }

  componentDidUpdate(prevProps) {
    const { parameterNames, onChange } = this.props;
    if (prevProps.parameterNames !== parameterNames) {
      this.loadSliderValues();
      onChange(this.slider_values);
    }
  }

  loadSliderValues() {
    const { parameterNames, sliderDefault } = this.props;
    this.slider_values = {};
    for (let i = 0; i < parameterNames.length; i += 1) {
      const name = parameterNames[i];
      this.slider_values[name] = sliderDefault.value;
    }
  }

  handleSliderChange(value, parameterName) {
    const { onChange } = this.props;
    if (this.slider_values[parameterName] !== value) {
      this.slider_values[parameterName] = value;
      onChange(this.slider_values);
    }
  }


  render() {
    const { parameterNames, sliderDefault } = this.props;
    const sliders = [];
    for (let i = 0; i < parameterNames.length; i += 1) {
      const parameter = parameterNames[i];
      sliders.push(
        <FunctionParameter
          name={parameter}
          key={parameter}
          onChange={(val) => this.handleSliderChange(val, parameter)}
          defaultValue={sliderDefault.value}
          defaultMinValue={sliderDefault.min}
          defaultMaxValue={sliderDefault.max}
        />,
      );
    }
    return (
      <div>
        {sliders}
      </div>
    );
  }
}

FunctionParameters.propTypes = {
  parameterNames: PropTypes.arrayOf(PropTypes.string).isRequired,
  onChange: PropTypes.func.isRequired,
  sliderDefault: PropTypes.objectOf(PropTypes.number).isRequired,
};

export default FunctionParameters;
