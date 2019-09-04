import React from 'react';
import './App.css';

import _ from 'lodash';
import PropTypes from 'prop-types';

import Typography from '@material-ui/core/Typography';
import Checkbox from '@material-ui/core/Checkbox';

import Latex from 'react-latex';

import NumberValidatedTextField from './NumberValidatedTextField';

class ChartControls extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      xmin: props.xdefaults.xmin,
      xmax: props.xdefaults.xmax,
      ymin: '',
      ymax: '',
      yaxAuto: true,
    };
  }

  getParams() {
    const {
      xmin, xmax, ymin, ymax, yaxAuto,
    } = this.state;

    return {
      xmin,
      xmax,
      ymin: yaxAuto ? undefined : ymin,
      ymax: yaxAuto ? undefined : ymax,
    };
  }

  errorState() {
    const {
      xmin, ymin, xmax, ymax, yaxAuto,
    } = this.state;
    return (
      (xmin === undefined)
      || (xmax === undefined)
      || (!yaxAuto && ymin === undefined)
      || (!yaxAuto && ymax === undefined)
    );
  }

  async update(valueChange) {
    let updated = false;
    Object.keys(valueChange).forEach((key) => {
      // eslint-disable-next-line react/destructuring-assignment
      if (this.state[key] !== valueChange[key]) {
        updated = true;
      }
    });
    if (updated) {
      const oldParams = this.getParams();
      await this.setState(valueChange);
      const params = this.getParams();
      if (!this.errorState() && !_.isEqual(oldParams, params)) {
        const { onChange } = this.props;
        onChange(params);
      }
    }
  }

  render() {
    const {
      xmin, xmax, ymin, ymax, yaxAuto,
    } = this.state;
    const { xdefaults } = this.props;
    return (
      <div>
        <div className="controls-row">
          <NumberValidatedTextField
            label="min"
            needsValue
            defaultValue={xdefaults.xmin}
            lowerThan={xmax}
            onChange={(value) => this.update({ xmin: value })}
          />
          <span className="leq-text"><Latex>$\leq x \leq$</Latex></span>
          <NumberValidatedTextField
            label="max"
            needsValue
            defaultValue={xdefaults.xmax}
            higherThan={xmin}
            onChange={(value) => this.update({ xmax: value })}
          />
        </div>
        <div className="controls-row">
          <NumberValidatedTextField
            label="min"
            onChange={(value) => this.update({ ymin: value })}
            lowerThan={ymax === '' ? undefined : ymax}
            defaultValue=""
            needsValue={!yaxAuto}
          />
          <span className="leq-text"><Latex>$\leq y \leq$</Latex></span>
          <NumberValidatedTextField
            label="max"
            onChange={(value) => this.update({ ymax: value })}
            higherThan={ymin === '' ? undefined : ymin}
            defaultValue=""
            needsValue={!yaxAuto}
          />
          <label className="checkbox-label" htmlFor="auto-yax">
            <Typography id="checkbox-label-text">
              Auto
            </Typography>
          </label>
          <Checkbox
            style={{ backgroundColor: 'transparent' }}
            disableRipple
            color="primary"
            checked={yaxAuto}
            id="auto-yax"
            label="Auto"
            onChange={(event, checked) => this.update({ yaxAuto: checked })}
          />
        </div>
      </div>
    );
  }
}

ChartControls.propTypes = {
  xdefaults: PropTypes.objectOf(PropTypes.number).isRequired,
  onChange: PropTypes.func.isRequired,
};

export default ChartControls;
