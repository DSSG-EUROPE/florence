import React, {Component} from 'react';
import {scaleQuantize} from 'd3-scale';
import {setParameters} from 'luma.gl';

import DeckGL, {GeoJsonLayer} from 'deck.gl';
import ArcVariableLayer from './arc-variable-layer';

const inFlowColors = [
  [160, 176, 207],
  [136, 156, 195],
  [112, 136, 183],
  [89, 117, 171],
  [65, 97, 159],
  [41, 77, 147],
  [18, 58, 135]
];
//const inLocationColor = [0, 102, 204];
const inLocationColor = [70,70,70];

const outFlowColors = [
  [203, 160, 158],
  [190, 136, 134],
  [177, 112, 109],
  [164, 89, 85],
  [151, 65, 61],
  [138, 41, 37],
  [125, 18, 13]
];
// const outLocationColor = [205, 0, 14];
const outLocationColor = [70,70,70];

export default class DeckGLOverlay extends Component {

  static get defaultViewport() {
    return {
      longitude: 11.263,
      latitude: 43.768,
      zoom: 14,
      maxZoom: 16,
      pitch: 30,
      bearing: 30
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      arcs: this._getArcs(props)
    };
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.data !== this.props.data ||
        nextProps.selectedFeature !== this.props.selectedFeature ||
        nextProps.isOutFlow !== this.props.isOutFlow) {
      this.setState({
        arcs: this._getArcs(nextProps)
      });
    }
  }

  _getArcs({data, selectedFeature, isOutFlow}) {
    if (!data || !selectedFeature) {
      return null;
    }

    const {inFlows, outFlows, centroid} = selectedFeature.properties;
    let flows = inFlows;
    if (isOutFlow) {
      flows = outFlows;
    }

    const arcs = Object.keys(flows).map(toId => {
      const f = data.find((elem) => elem.properties.id.toString() === toId.toString());

      if (!f) {
        return null;
      }

      return {
        source: centroid,
        target: f.properties.centroid,
        value: flows[toId]
      };
    }).filter((arc) => !!arc);

    let max = 0
    let min = Infinity

    arcs.forEach(arc => {
      if (arc.value > max) {
        max = arc.value
      } else if (arc.value < min) {
        min = arc.value
      }
    })

    const scale = scaleQuantize()
      .domain([min, max])
      .range([0, 1, 2, 3, 4, 5, 6]);

    arcs.forEach(a => {
      a.gain = Math.sign(a.value);
      a.quantile = scale(Math.abs(a.value));
    });

    return arcs;
  }

  _initialize(gl) {
    setParameters(gl, {
      depthTest: true,
      depthFunc: gl.LEQUAL
    });
  }

  render() {
    const {viewport, data, isOutFlow} = this.props;
    const {arcs} = this.state;

    if (!arcs) {
      return null;
    }

    const layers = [
      new GeoJsonLayer({
        id: 'geojson',
        data,
        stroked: true,
        filled: true,
        opacity: 0.5,
        wireframe: true,
        fp64: true,
        getFillColor: () => {
          let locationColor = inLocationColor;
          if (isOutFlow) {
            locationColor = outLocationColor;
          }
          return locationColor;
        },
        getLineColor: () => [96, 96, 96],
        onHover: this.props.onHover,
        onClick: this.props.onClick,
        pickable: Boolean(this.props.onHover || this.props.onClick)
      }),
      new ArcVariableLayer({
        id: 'arc',
        data: arcs,
        getSourcePosition: d => d.source,
        getTargetPosition: d => d.target,
        getSourceColor: d => {
          let colors = inFlowColors;
          if (isOutFlow) {
            colors = outFlowColors;
          }
          return colors[d.quantile]
        },
        getTargetColor: d => {
          let colors = inFlowColors;
          if (isOutFlow) {
            colors = outFlowColors;
          }
          return colors[d.quantile]
        },
        getWidth: d => {
          return d.quantile + 1
        }
      })
    ];

    return (
      <DeckGL {...viewport} layers={ layers } onWebGLInitialized={this._initialize} />
    );
  }
}
