import React, {PureComponent} from 'react';
import classnames from 'classnames';

export default class Toggle extends PureComponent {

  constructor(props) {
    super(props);
    this.state = {}
  }

  render() {
    const { onToggleClick } = this.props;

    return (
      <div className="to-from-toggle">
        <label className="label label-toggle">
          <div className="input-toggle">
            <input 
              className="input-checkbox"
              id="night-mode" 
              type="checkbox"
              onChange={({ target }) => {
                onToggleClick(target.checked);
              }}
            />
            <div className="input-toggle-handle"></div>
          </div>
        </label>
      </div>
    );
  }
}

Toggle.defaultProps = {
  onToggleClicked: () => {},
};