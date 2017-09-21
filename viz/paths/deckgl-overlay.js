import React, {Component} from 'react';
import DeckGL, {PolygonLayer} from 'deck.gl';

import TripsLayer from './trips-layer';

const LIGHT_SETTINGS = {
  lightsPosition: [-74.05, 40.7, 8000, -73.5, 41, 5000],
  ambientRatio: 0.05,
  diffuseRatio: 0.6,
  specularRatio: 0.8,
  lightsStrength: [2.0, 0.0, 0.0, 0.0],
  numberOfLights: 2
};

// const colors = {
//   0: [217, 65, 65],
//   1: [217, 130, 65],
//   2: [217, 195, 65],
//   3: [173, 217, 65],
//   4: [65, 217, 87],
//   5: [65, 217, 205],
//   6: [65, 152, 217],
//   7: [50, 100, 217],
//   8: [120, 65, 217],
//   9: [217, 80, 205],
//   10: [217, 80, 120]
// }

const colors = {
  0: [0, 0, 0]
}

export default class DeckGLOverlay extends Component {

  static get defaultViewport() {
    return {
      longitude: 11.25,
      latitude: 43.77,
      zoom: 13,
      maxZoom: 16,
      pitch: 45,
      bearing: 0
    };
  }

  _initialize(gl) {
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
  }

  render() {
    const {viewport, buildings, trips, trailLength, time} = this.props;

    if (!buildings || !trips) {
      return null;
    }

    const layers = [
      new TripsLayer({
        id: 'trips',
        data: trips,
        getPath: d => d.segments,
        getColor: d => colors[d.color % Object.keys(colors).length],
        opacity: 0.3,
        trailLength,
        currentTime: time
      }),
      new PolygonLayer({
        id: 'buildings',
        data: buildings,
        extruded: true,
        wireframe: false,
        fp64: true,
        opacity: 0.5,
        getPolygon: f => f.polygon,
        getElevation: f => f.height,
        getFillColor: f => [74, 80, 87],
        lightSettings: LIGHT_SETTINGS
      })
    ];

    return (
      <DeckGL {...viewport} layers={layers} onWebGLInitialized={this._initialize} />
    );
  }
}
