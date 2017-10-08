/* global window,document */
import React, {Component} from 'react';
import {render} from 'react-dom';
import MapGL from 'react-map-gl';
import DeckGLOverlay from './deckgl-overlay.js';
import LegendInfo from './legend-info';
import Toggle from './toggle';

import {json as requestJson} from 'd3-request';

const tooltipStyle = {
  position: 'absolute',
  padding: '4px',
  background: 'rgba(0, 0, 0, 0.8)',
  color: '#fff',
  maxWidth: '300px',
  fontSize: '10px',
  zIndex: 9,
  pointerEvents: 'none'
};

export default class Fountain extends Component {

  constructor(props) {
    super(props);
    this.state = {
      viewport: {
        ...DeckGLOverlay.defaultViewport,
        width: 500,
        height: 500
      },
      data: null,
      dataDict: {},
      selectedItem: null,
      hoveredItem: null
    };
  }

  componentDidMount() {
    window.addEventListener('resize', this._resize.bind(this));
    this._resize();
  }

  _resize() {
    this._onViewportChange({
      width: window.innerWidth,
      height: window.innerHeight
    });
  }

  _onHover({x, y, object}) {
    if (object) {
      this.setState({x, y, hoveredItem: object})
    }
  }

  _onClick(info) {
    this.setState({selectedItem: info.object});
  }

  _onViewportChange(viewport) {
    this.setState({
      viewport: {...this.state.viewport, ...viewport}
    });
  }

  _renderTooltip() {
    const {x, y, hoveredItem} = this.state;

    if (!hoveredItem) {
      return null;
    }

    return (
      <div style={{...tooltipStyle, left: x, top: y}}>
        <div>{hoveredItem.properties.name}</div>
      </div>
    );
  }

  render() {
    const {viewport, data, dataDict, selectedItem} = this.state;
    const {mapboxToken, title, description, isOutFlow, onToggleClick} = this.props;

    return (
      <div>
        {this._renderTooltip()}
        <MapGL
          {...viewport}
          onViewportChange={this._onViewportChange.bind(this)}
          mapboxApiAccessToken={mapboxToken}>
          <DeckGLOverlay viewport={viewport}
            data={data}
            selectedFeature={selectedItem}
            isOutFlow={isOutFlow}
            onHover={this._onHover.bind(this)}
            onClick={this._onClick.bind(this)}
            overlayStyle={{
              filled: false,
              opacity: 0.8,
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
