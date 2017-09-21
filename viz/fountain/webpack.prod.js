// NOTE: To use this example standalone (e.g. outside of deck.gl repo)
// delete the local development overrides at the bottom of this file

// avoid destructuring for older Node version support
const resolve = require('path').resolve;
const webpack = require('webpack');
const path = require('path');
//const UglifyJSPlugin = require('uglifyjs-webpack-plugin');

const CONFIG = {
  entry: {
    app: resolve('./app.js')
  },

  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },

  devtool: "source-map",

  module: {
    rules: [{
      // Compile ES2015 using buble
      test: /\.js$/,
      loader: 'buble-loader',
      include: [resolve('.')],
      exclude: [/node_modules/],
      options: {
        objectAssign: 'Object.assign'
      }
    }]
  },

  resolve: {
    alias: {
      // From mapbox-gl-js README. Required for non-browserify bundlers (e.g. webpack):
      'mapbox-gl$': resolve('./node_modules/mapbox-gl/dist/mapbox-gl.js'),
      "react": "preact-compat",
      "react-dom": "preact-compat"
    }
  },

  plugins: [
    new webpack.DefinePlugin({ //<--key to reduce React's size
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.UglifyJsPlugin({
        sourceMap: true,
        compress: {
            warnings: false,
            comparisons: false,  // don't optimize comparisons
        },
    })
  ]

  // plugins: [
  //   new UglifyJSPlugin()
  // ]
};

module.exports = CONFIG;
