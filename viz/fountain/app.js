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

const strings = {
  1: {
    showFrom: false,
    title: 'Where Do People Go?',
    description: 'These are the percentages of people who leave to go to each of the following destinations using the Firenzecard',
    type: 'museum'
  },
  0: {
    showFrom: true,
    title: 'Where Do People Come From?',
    description: 'These are the percentages of people who arrived to this destination from each of the following destinations using the Firenzecard',
    type: 'museum'
  },
  3: {
    showFrom: false,
    title: 'Where Do Foreign Excursionists Go?',
    description: 'These are the percentages of one day visit foreigners leaving to go elsewhere as calculated from telecom data from the four month period of June to September, 2016',
    type: 'daytripper'
  },
  2: {
    showFrom: true,
    title: 'Where Do Foreign Excursionists Come From?',
    description: 'These are the percentages of one day visit foreigners arriving in this location as calculated from telecom data from the four month period of June to September, 2016',
    type: 'daytripper'
  }
}

class Root extends Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedTab: 0,
      selectedTo: false,
      selectedStrings: 0
    };
  }

  handleTabClick(index) {
    this.setState({ 
      selectedTab: index,
      selectedStrings: (index * 2 + this.state.selectedTo)
    });
  }

  handleToFromToggle(direction) {
    this.setState({ 
      selectedTo: direction,
      selectedStrings: (this.state.selectedTab * 2 + direction)
    });
  }

  render() {
    const { selectedTab, selectedStrings } = this.state;
    const { showFrom, title, description, type } = strings[selectedStrings];
    const isMuseum = type === 'museum';
    const isDaytripper = type === 'daytripper';

    return (
      <div>
        <Header
          siteTitle="Project Florence"
          tabs={[
            { title: 'Museums' },
            { title: 'Excursionists' }
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
          onToggleClick={this.handleToFromToggle.bind(this)}
        />}
        {isDaytripper && <CdrFountain
          defaultItemId="55"
          mapboxToken={MAPBOX_TOKEN}
          isOutFlow={!showFrom}
          title={title}
          description={description}
          onToggleClick={this.handleToFromToggle.bind(this)}
        />}
      </div>
    );
  }
}

render(<Root />, document.body.appendChild(document.createElement('div')));
