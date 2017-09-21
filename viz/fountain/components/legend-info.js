import React, {PureComponent} from 'react';
import {json as requestJson} from 'd3-request';
import classnames from 'classnames';

export default class LegendInfo extends PureComponent {

  getTopFlows() {
    const {clicked, isOutFlow, dataDict} = this.props;

    const {inFlows, outFlows} = clicked.properties;
    let flows = inFlows;
    if (isOutFlow) {
      flows = outFlows;
    }

    if (!dataDict || !Object.keys(dataDict).length) {
      return;
    }

    return Object.keys(flows).sort((a, b) => {
      return flows[b].weight - flows[a].weight
    })
    .slice(0, 6)
    .map(key => {
      return (
        <div className="list-item" key={`list-item-${key}`}>
          <div className="museum-name">{dataDict[key].name}</div>
          <div className="museum-number">{`${Math.round(flows[key].percentage)}%`}</div>
        </div>
      )
    });
  }

  renderVisitStats() {
    const { clicked } = this.props;
    const { totalFcVisits, totalVisits} = clicked.properties

    if (totalFcVisits) {
      return (
        <div>
          <h4>How Many People Visit?</h4>
          <p className="description">
            Firenzecard visits is the total numbers of people entering using the Firenzecard 
            from the four month period of June to September, 2016. 
          <br/><br/>
            Total visits is the number of people entering the museum by any manner for the same period.
          </p>
          <div className="list-item">
            <div className="museum-name">Firenzecard Visits:</div>
            <div className="museum-number">{parseInt(totalFcVisits).toLocaleString()}</div>
          </div>
          <div className="list-item">
            <div className="museum-name">Total Visits:</div>
            <div className="museum-number">{totalVisits ? totalVisits.toLocaleString() : 'Unknown'}</div>
          </div>
        </div>
      );
    }
  }

  render() {
    const { clicked, description, title } = this.props;
    const wrapperClass = classnames('legend-info', { 
        tall: !!(clicked && clicked.properties.totalFcVisits)
      });

    return (
      <div className={wrapperClass}>
        { clicked && (<div>
          <h3>{clicked.properties.fullName || `Region ${clicked.properties.name}`}</h3>
          {this.renderVisitStats()}
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
