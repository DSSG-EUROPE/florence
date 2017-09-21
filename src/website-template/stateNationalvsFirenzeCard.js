function stateNationalvsFirenzeCard() {

	trace1 = {
	  x: ['June', 'July', 'August', 'September'], 
	  y: [98034, 124568, 157686, 90403], 
	  marker: {color: 'rgb(207, 28, 11)'}, 
	  name: 'FirenzeCard', 
	  type: 'bar', 
	  uid: 'a5d522', 
	  xsrc: 'qiweihan:427:9f88c1', 
	  ysrc: 'qiweihan:427:67d4ef'
	};
	trace2 = {
	  x: ['June', 'July', 'August', 'September'], 
	  y: ['706568', '756964', '797728', '721454'], 
	  marker: {color: 'rgb(197, 159, 124)'}, 
	  name: 'State Museums', 
	  type: 'bar', 
	  uid: '1a1367', 
	  xsrc: 'qiweihan:427:9f88c1', 
	  ysrc: 'qiweihan:427:6153b0'
	};
	data = [trace1, trace2];
	layout = {
	  autosize: true, 
	  font: {size: 18}, 
	  legend: {font: {size: 12}}, 
	  title: 'Comparison of monthly entries - Firenze Card data & State Museum data', 
	  titlefont: {size: 18}, 
	  xaxis: {
	    autorange: true, 
	    fixedrange: true, 
	    range: [-0.5, 3.5], 
	    tickfont: {size: 18}, 
	    type: 'category'
	  }, 
	  yaxis: {
	    autorange: true, 
	    fixedrange: true, 
	    range: [0, 839713.684211], 
	    title: 'Number of entries', 
	    type: 'linear'
	  }
	};
	Plotly.plot('state-national-vs-fc', {
	  data: data,
	  layout: layout
	});
};

stateNationalvsFirenzeCard()