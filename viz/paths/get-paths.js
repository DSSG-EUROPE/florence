import axios from 'axios';
import polyline from 'polyline';

const pathStrings = [
  '11.26,43.77;11.254,43.771',
  '11.254,43.771;11.26,43.77',
  '11.254,43.771;11.252,43.775',
  '11.248,43.777;11.252,43.775',
  '11.252,43.775;11.248,43.777',
  '11.252,43.775;11.254,43.771'
];

const getPath = function(latLons) {
  return axios({
    method: 'get',
    url: `http://router.project-osrm.org/route/v1/foot/${latLons}`,
    responseType:'json'
  });
};

export default function pathGetter() {
  pathStrings.forEach(latLon => {
    getPath(latLon).then(({ data }) => {
      data.routes.forEach(route => {
        const decodedRoute = polyline.decode(route.geometry);
        console.log(JSON.stringify(decodedRoute));
      });
    });
  });
};