import React, {PureComponent} from 'react';
import {json as requestJson} from 'd3-request';

const DATA_URL = './data/museum_dict.json';

export default class LegendInfo extends PureComponent {

  constructor(props) {
    super(props);
    this.state = {
      museumDict: {}
    }

    requestJson(DATA_URL, (error, response) => {
      if (!error) {
        this.setState({
          museumDict: response
        });
      }
    });
  }

  getTopFlows() {
    const {clicked, isOutFlow} = this.props;

    const {inFlows, outFlows} = clicked.properties;
    let flows = inFlows;
    if (isOutFlow) {
      flows = outFlows;
    }

    const {museumDict} = this.state;

    if (!Object.keys(museumDict).length) {
      return;
    }

    return Object.keys(flows).sort((a, b) => {
      return flows[b] - flows[a]
    })
    .slice(0, 6)
    .map(key => {
      return (
        <div className="list-item" key={`list-item-${key}`}>
          <div className="museum-name">{museumDict[key].name}</div>
          <div className="museum-number">{flows[key]}</div>
        </div>
      )
    });
  }

  render() {
    const {clicked, title, description} = this.props;

    return (
      <div className="legend-info">
        { clicked && (<div>
          <h3>{clicked.properties.fullName}</h3>
          <h4>{title}</h4>
          <p className="description">{description}</p>
          <div className="top-list">
            {this.getTopFlows()}
          </div>
        </div>) }
      </div>
    );
  }
}
