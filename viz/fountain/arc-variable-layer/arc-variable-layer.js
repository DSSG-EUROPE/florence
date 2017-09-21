// Copyright (c) 2015 - 2017 Uber Technologies, Inc.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

import {ArcLayer, enable64bitSupport} from 'deck.gl';
import vs from './arc-variable-layer-vertex.glsl';
import vs64 from './arc-variable-layer-vertex-64.glsl';
import fs from './arc-variable-layer-fragment.glsl';
import {GL} from 'luma.gl';

const defaultProps = {
  ...ArcLayer.defaultProps,
  widthMinPixels: 0, //  min stroke width in pixels
  widthMaxPixels: Number.MAX_SAFE_INTEGER, // max stroke width in pixels
  getWidth: x => x.width || 1
};

// Positions are interpreted as [lng, lat, elevation]
// lng lat are degrees, elevation is meters. distances as meters.
const LNGLAT = 1.0;

function enable64bitSupport(props) {
  if (props.fp64) {
    if (props.projectionMode === LNGLAT) {
      return true;
    }
  }

  return false;
};

export default class ArcVariableLayer extends ArcLayer {
  getShaders() {
    return enable64bitSupport(this.props) ?
      {vs: vs64, fs, modules: ['project64']} :
      {vs, fs}; // 'project' module added by default.
  }

  initializeState() {
    const {gl} = this.context;
    this.setState({model: this._getModel(gl)});

    const {attributeManager} = this.state;

    /* eslint-disable max-len */
    attributeManager.addInstanced({
      instancePositions: {size: 4, accessor: ['getSourcePosition', 'getTargetPosition'], update: this.calculateInstancePositions},
      instanceSourceColors: {size: 4, type: GL.UNSIGNED_BYTE, accessor: 'getSourceColor', update: this.calculateInstanceSourceColors},
      instanceTargetColors: {size: 4, type: GL.UNSIGNED_BYTE, accessor: 'getTargetColor', update: this.calculateInstanceTargetColors},
      instanceStrokeWidths: {size: 1, accessor: 'getWidth', update: this.calculateStrokeWidths}
    });
    /* eslint-enable max-len */
  }

  draw({uniforms}) {
    const {widthMinPixels, widthMaxPixels} = this.props;

    this.state.model.render(Object.assign({}, uniforms, {
      widthMinPixels,
      widthMaxPixels
    }));
  }

  calculateStrokeWidths(attribute) {
    const {data, getWidth} = this.props;
    const {value, size} = attribute;

    let i = 0;
    Object.keys(data).forEach(key => {
      const object = data[key]
      const width = getWidth(object);
      value[i] = width;
      i += size;
    });
  }
}

ArcVariableLayer.layerName = 'ArcVariableLayer';
ArcVariableLayer.defaultProps = defaultProps;
