/* global window,document */
import React from 'react';
import {render} from 'react-dom';
import MapGL from 'react-map-gl';
import DeckGLOverlay from './deckgl-overlay.js';
import LegendInfo from './legend-info';
import Fountain from './fountain';

import {json as requestJson} from 'd3-request';

const CDR_DATA = require('../data/cdr_daytripper_fountain.json');
const CDR_DATA_DICT = require('../data/cdr_daytripper_dict.json');

export default class CdrFountain extends Fountain {

  constructor(props) {
    super(props);

    const item = CDR_DATA.features.find(f => {
      return f.properties.id === props.defaultItemId;
    })

    this.state = {
      ...this.state,
      dataDict: CDR_DATA_DICT,
      data: CDR_DATA.features,
      selectedItem: item,
      clicked: item
    };
  }

  render() {
    const {viewport, data, selectedItem, dataDict} = this.state;
    const {mapboxToken, title, description, isOutFlow} = this.props;

    return (
      <div>
        {this._renderTooltip()}
        <MapGL
          {...viewport}
          onViewportChange={this._onViewportChange.bind(this)}
          mapboxApiAccessToken={mapboxToken}>
          <DeckGLOverlay
            viewport={viewport}
            data={data}
            selectedFeature={selectedItem}
            isOutFlow={isOutFlow}
            onHover={this._onHover.bind(this)}
            onClick={this._onClick.bind(this)}
            overlayStyle={{
              filled: true,
              opacity: 0.2,
              wireframe: true,
              lineWidthScale: 5,
              lineWidthMinPixels: 1,
              getFillColor: d => {
                const rgb = 100 - 100 * d.properties.density;
                return [rgb, rgb, rgb]
              },
              getLineColor: () => [0, 0, 0],
            }}
          />
        </MapGL>
        <LegendInfo
          ref="infoPanel"
          clicked={selectedItem}
          title={title}
          description={description}
          isOutFlow={isOutFlow}
          dataDict={dataDict}
        />
      </div>
    );
  }
}
