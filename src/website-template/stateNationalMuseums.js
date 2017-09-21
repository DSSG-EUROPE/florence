function stateNationalMuseums() {
	trace1 = {
	  x: ['Uffizi', 'Accademia', 'Pitti', 'Santa Maria Novella', 'Palazzo Vecchio', 'Forte di Belvedere', 'Cappelle Medicee', 'Bargello', 'T. Arnolfo', 'M. San Marco', 'C. Brancacci', 'C. Orsanmichele', 'P. Davanzati', 'M. Archeologico', 'V. Ventaglio', 'F. Salvatore Romano', 'V. Medicea Petraia', 'V. Medicea Cerreto Guidi', 'M. Novecento', 'M. Bardini', 'C. Sant\'Apollonia', 'V. Medicea Castello', 'M. Pietre Dure', 'T. San Niccolo', 'C. Ognissanti', 'C. Scalzo', 'M. Casa Martelli', 'Sala del Perugino', 'V. Corsini'], 
	  y: ['201164', '160744', '137910', '44901', '44523', '36114', '31116', '20522', '17956', '12555', '6884', '4004', '3809', '3122', '3103', '3030', '2605', '2412', '1918', '1360', '1260', '1129', '969', '781', '640', '605', '364', '115', '54'], 
	  marker: {color: 'rgb(204, 23, 29)'}, 
	  name: 'A', 
	  type: 'bar', 
	  uid: 'a62de5', 
	  xsrc: 'qiweihan:481:fcc2be', 
	  ysrc: 'qiweihan:481:cddcdf'
	};
	data = [trace1];
	layout = {
	  autosize: true, 
	  hovermode: 'closest', 
	  margin: {
	    t: 40, 
	    b: 150
	  }, 
	  title: 'Average Total National and State Museum Entries for Summer 2016', 
	  titlefont: {size: 20}, 
	  xaxis: {
	    autorange: false, 
	    range: [-0.5, 28.5], 
	    title: '<br>', 
	    titlefont: {size: 18}, 
	    type: 'category'
	  }, 
	  yaxis: {
	    autorange: false, 
	    range: [-3123.17963049, 235487.744139], 
	    title: 'Average Number of Entries', 
	    titlefont: {size: 18}, 
	    type: 'linear'
	  }
	};

	Plotly.plot('state-national-museums', {
	  data: data,
	  layout: layout
	});
};

stateNationalMuseums()