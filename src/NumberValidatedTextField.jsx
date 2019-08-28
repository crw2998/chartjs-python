import React from 'react';
import './App.css';

import PropTypes from 'prop-types';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import clsx from 'clsx';

import theme from './theme';

const useStyles = makeStyles((themeParam) => ({
  textField: {
    width: '75px',
    fontSize: '3em',
  },
  margin: {
    margin: themeParam.spacing(1),
  },
}));

function ControlsTextField(props) {
  const classes = useStyles(theme);
  const {
    error, label, defaultValue, onChange,
  } = props;
  return (
    <TextField
      error={error}
      label={label}
      defaultValue={defaultValue}
      className={clsx(classes.margin, classes.textField)}
      onChange={onChange}
      variant="outlined"
      margin="dense"
    />
  );
}

ControlsTextField.propTypes = {
  error: PropTypes.bool.isRequired,
  label: PropTypes.string.isRequired,
  defaultValue: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]).isRequired,
  onChange: PropTypes.func.isRequired,
};

function isError(val, props) {
  const { needsValue, lowerThan, higherThan } = props;
  return (
    (needsValue && val === '')
    || (Number.isNaN(parseFloat(val)) && val !== '')
    || (val !== '' && lowerThan !== undefined && val >= lowerThan)
    || (val !== '' && higherThan !== undefined && val <= higherThan)
  );
}

function parse(val) {
  if (val === '') return '';
  return parseFloat(val);
}

class NumberValidatedTextField extends React.Component {
  constructor(props) {
    super(props);
    const { defaultValue } = props;
    this.state = { val: defaultValue || '' };
  }

  componentDidUpdate(prevProps) {
    // check if the min/max has changed and error state needs to updated
    if (prevProps === this.props) return;
    const { val } = this.state;
    const { onChange } = this.props;
    const curval = val;
    if (isError(curval, prevProps) && !isError(curval, this.props)) {
      onChange(curval);
    }
  }

  onChange(event) {
    const { onChange } = this.props;
    const val = parse(event.target.value);
    this.setState({ val });
    if (!isError(val, this.props)) {
      onChange(val);
    }
  }

  render() {
    const { val } = this.state;
    const { label, defaultValue } = this.props;
    const error = isError(val, this.props);
    return (
      <ControlsTextField
        label={label}
        error={error}
        defaultValue={defaultValue}
        onChange={(event) => this.onChange(event)}
      />
    );
  }
}

NumberValidatedTextField.propTypes = {
  defaultValue: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]).isRequired,
  onChange: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
  lowerThan: PropTypes.number,
  higherThan: PropTypes.number,
};

export default NumberValidatedTextField;
