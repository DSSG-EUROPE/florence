/* global window,document */
import React, {Component} from 'react';
import {render} from 'react-dom';
import MuseumFountain from './components/museum-fountain.js';
import CdrFountain from './components/cdr-fountain.js';
import Header from './components/header.js';

import {json as requestJson} from 'd3-request';

// Set your mapbox token here
const MAPBOX_TOKEN = 'pk.eyJ1IjoiaWZsYW1lbnQiLCJhIjoiY2o1an' +
'VidmhnMmE2MzJ3cnl3a3Z0NXUwcCJ9.sQQjL5Nb_m-CGRnm7_y65w';

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

const tabStrings = {
  0: {
    showFrom: false,
    title: 'Where Do People Go?',
    description: 'These are the percentages of people who leave to go to each of the following destinations using the Firenzecard',
    type: 'museum'
  },
  1: {
    showFrom: true,
    title: 'Where Do People Come From?',
    description: 'These are the percentages of people who arrived to this destination from each of the following destinations using the Firenzecard',
    type: 'museum'
  },
  2: {
    showFrom: false,
    title: 'Where Do Foreign Daytrippers Go?',
    description: 'These are the percentages of one day visit foreigners leaving to go elsewhere as calculated from telecom data from the four month period of June to September, 2016',
    type: 'daytripper'
  },
  3: {
    showFrom: true,
    title: 'Where Do Foreign Daytrippers Come From?',
    description: 'These are the percentages of one day visit foreigners arriving in this location as calculated from telecom data from the four month period of June to September, 2016',
    type: 'daytripper'
  }
}

class Root extends Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedTab: 1
    };
  }

  handleTabClick(index) {
    this.setState({ selectedTab: index });
  }

  render() {
    const {selectedTab} = this.state;
    const { showFrom, title, description, type } = tabStrings[selectedTab];
    const isMuseum = type === 'museum';
    const isDaytripper = type === 'daytripper';

    return (
      <div>
        <Header
          siteTitle="Project Florence"
          tabs={[
            { title: 'To Museums' },
            { title: 'From Museums' },
            { title: 'Daytrippers To' },
            { title: 'Daytrippers From' }
          ]}
          onTabClick={this.handleTabClick.bind(this)}
          selectedTab={selectedTab}
        />
        {isMuseum && <MuseumFountain
          defaultItemId="10"
          mapboxToken={MAPBOX_TOKEN}
          isOutFlow={!showFrom}
          title={title}
          description={description}
        />}
        {isDaytripper && <CdrFountain
          defaultItemId="55"
          mapboxToken={MAPBOX_TOKEN}
          isOutFlow={!showFrom}
          title={title}
          description={description}
        />}
      </div>
    );
  }
}

render(<Root />, document.body.appendChild(document.createElement('div')));
