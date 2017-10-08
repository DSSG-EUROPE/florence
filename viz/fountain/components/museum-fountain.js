/* global window,document */
import React from 'react';
import {render} from 'react-dom';
import MapGL from 'react-map-gl';
import DeckGLOverlay from './deckgl-overlay.js';
import LegendInfo from './legend-info';
import Fountain from './fountain';
import Toggle from './toggle';

import {json as requestJson} from 'd3-request';

const MUSEUM_DATA = require('../data/museum_fountain_wsource.json');
const MUSEUM_DATA_DICT = require('../data/museum_dict_wsource.json');

export default class MuseumFountain extends Fountain {

  constructor(props) {
    super(props);

    const item = MUSEUM_DATA.features.find(f => {
      return f.properties.id === props.defaultItemId;
    })

    this.state = {
      ...this.state,
      dataDict: MUSEUM_DATA_DICT,
      data: MUSEUM_DATA.features,
      selectedItem: item,
      clicked: item
    };
  }

  render() {
    const { viewport, data, selectedItem, dataDict } = this.state;
    const { mapboxToken, title, description, isOutFlow, onToggleClick } = this.props;

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
              opacity: 0.5,
              wireframe: true,
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
        <Toggle
          onToggleClick={onToggleClick}
        />
      </div>
    );
  }
}
