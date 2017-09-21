function fcTotalEntriesPerMuseum() {

	trace1 = {
	  x: ['Primo Conti', 'M. Calcio', 'M. Preistoria', 'M. Stibbert', 'M. Marini', 'M. Horne', 'M. Mineralogia', 'M. Stefano Bardini', 'M. Geologia', 'M. Civici Fiesole', 'M. Antropologia', 'M. Opificio', 'Orto Botanico', 'La Specola', 'M. Novecento', 'M. Ebraico', 'M. Palazzo Davanzati', 'M. Ferragamo', 'Casa Buonarroti', 'V. Bardini', 'M. Innocenti', 'M. Archeologico', 'Palazzo Strozzi', 'Brancacci', 'M. Casa Dante', 'Laurenziana', 'M. San Marco', 'Palazzo Medici', 'M. Bargello', 'M. Galileo', 'Torre di Palazzo Vecchio', 'Cappelle Medicee', 'M. Santa Maria Novella', 'San Lorenzo', 'Santa Croce', 'M. Palazzo Vecchio', 'Pitti', 'Accademia', 'Uffizi', 'Opera del Duomo'], 
	  y: [2, 14, 28, 230, 282, 296, 302, 383, 730, 734, 1056, 1103, 1200, 1274, 1325, 1350, 1365, 1555, 1845, 2139, 2472, 2638, 4262, 4488, 5430, 7399, 8736, 13234, 14415, 15133, 16680, 18759, 19595, 20086, 22979, 32757, 34007, 42417, 44339, 49889], 
	  marker: {color: '#CC171D'}, 
	  type: 'bar', 
	  uid: '2761aa', 
	  xsrc: 'qiweihan:434:0a9eb8', 
	  ysrc: 'qiweihan:434:1ed517'
	};
	data = [trace1];
	layout = {
	  title: 'Number of Entries per Museum ( June - Sept. 2016 )', 
	  xaxis: {
	    autorange: true, 
	    range: [-0.5, 39.5], 
	    type: 'category'
	  }, 
	  yaxis: {
	    autorange: true, 
	    range: [0, 52514.7368421], 
	    title: 'Total number of entries', 
	    type: 'linear'
	  }
	};
	Plotly.plot('fc-total-entries-per-museum', {
	  data: data,
	  layout: layout
	});
};

fcTotalEntriesPerMuseum()
