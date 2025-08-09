import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import 'leaflet-timedimension';
import 'leaflet-fullscreen';
import 'leaflet-velocity';
import 'leaflet-timedimension/dist/leaflet.timedimension.control.css';
import 'leaflet-fullscreen/dist/leaflet.fullscreen.css';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { point, polygon } from '@turf/helpers';

import statesGeoJson from '../../../united_states_of_america_States_level_1.json';
import hailGif from '../../../assets/5z4f.gif';
import thunderStormGif from '../../../assets/4jwl.gif';
import { getServerMessage } from "../../../API/Test_API";




const texasCities = [
  { name: "Houston", coordinates: [29.7604, -95.3698] },
  { name: "San Antonio", coordinates: [29.4241, -98.4936] },
  { name: "Dallas", coordinates: [32.7767, -96.7970] },
  { name: "Austin", coordinates: [30.2672, -97.7431] },
  { name: "Fort Worth", coordinates: [32.7555, -97.3308] },
  { name: "El Paso", coordinates: [31.7619, -106.4850] },
  { name: "Arlington", coordinates: [32.7357, -97.1081] },
  { name: "Corpus Christi", coordinates: [27.8006, -97.3964] },
  { name: "Plano", coordinates: [33.0198, -96.6989] },
  { name: "Laredo", coordinates: [27.5064, -99.5075] },
  { name: "Lubbock", coordinates: [33.5779, -101.8552] },
  { name: "Garland", coordinates: [32.9126, -96.6389] },
  { name: "Irving", coordinates: [32.8140, -96.9489] },
  { name: "Amarillo", coordinates: [35.2218, -101.8313] },
  { name: "Grand Prairie", coordinates: [32.7459, -96.9978] },
  { name: "Brownsville", coordinates: [25.9017, -97.4975] },
  { name: "McKinney", coordinates: [33.1972, -96.6398] },
  { name: "Frisco", coordinates: [33.1507, -96.8236] },
  { name: "Pasadena", coordinates: [29.6911, -95.2091] },
  { name: "Killeen", coordinates: [31.1171, -97.7278] }
];

function getThunderstormPoints(dayIndex) {
  return Array.from({ length: 10 }, (_, i) => {
    const cityIndex = (dayIndex + i) % texasCities.length;
    return texasCities[cityIndex].coordinates;
  });
}

const reusableWindData = Array.from({ length: 24 * 30 }, (_, i) => {
  const date = new Date(Date.UTC(2025, 0, Math.floor(i / 24) + 1, i % 24));
  const hour = date.getUTCHours();
  const day = date.getUTCDate();

  const timeStr = date.toISOString().split('T')[0] + `T${String(hour).padStart(2, '0')}:00:00Z`;

  return {
    baseIndex: i,
    data: [
      {
        header: {
          refTime: timeStr,
          parameterCategory: 2,
          parameterNumber: 2,
          nx: 50,
          ny: 50,
          lo1: -106,
          la1: 36.5,
          lo2: -93,
          la2: 25,
          dx: 0.3,
          dy: 0.3,
          // Add any other required header fields
        },
        data: Array.from({ length: 50 * 50 }, () => Math.random() * 20 - 10),
      },
      {
        header: {
          refTime: timeStr,
          parameterCategory: 2,
          parameterNumber: 3,
          nx: 50,
          ny: 50,
          lo1: -106,
          la1: 36.5,
          lo2: -93,
          la2: 25,
          dx: 0.3,
          dy: 0.3,
        },
        data: Array.from({ length: 50 * 50 }, () => Math.random() * 20 - 10),
      }
    ]
  };
});


function getWindDataForSlider(selectedTime) {
  const date = new Date(selectedTime);
  const hour = date.getUTCHours();
  const day = date.getUTCDate();
  const index = (day - 1) * 24 + hour;

  if (index < 0 || index >= reusableWindData.length) return null;

  const reused = JSON.parse(JSON.stringify(reusableWindData[index]));
  const timeStr = date.toISOString().split('T')[0] + `T${String(hour).padStart(2, '0')}:00:00Z`;

  reused.time = timeStr;
  reused.data.forEach(d => d.header.refTime = timeStr);

  return reused;
}




 


const STADIA_API_KEY = process.env.REACT_APP_STADIA_KEY;

const TILE_LAYERS = {
  dark: {
    name: 'Dark',
    url: `https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.jpg?api_key=${STADIA_API_KEY}`,
    attribution: '© Stadia Maps © OpenMapTiles © OpenStreetMap contributors',
  },
  light: {
    name: 'Light',
    url: `https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.jpg?api_key=${STADIA_API_KEY}`,
    attribution: '© OpenMapTiles © OpenStreetMap contributors',
  },
  terrain: {
    name: 'Terrain',
    url: `https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=${STADIA_API_KEY}`,
    minZoom: 0,
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
  
  
  
};

const texasBounds = [
  [25.8371, -106.6456],  // southwest [lat, lng]
  [36.5007, -93.5080],   // northeast [lat, lng]
];

function getTexasFeature(statesGeoJson) {
  return statesGeoJson.features.find((f) => (f.properties.shape1 || '').toLowerCase() === 'texas');
}

function getTexasMaskGeoJson(statesGeoJson) {
  const texasFeature = getTexasFeature(statesGeoJson);
  if (!texasFeature) return null;
  const geom = texasFeature.geometry;
  const holes = geom.type === 'MultiPolygon' ? geom.coordinates.map((polyarr) => polyarr[0]) : [geom.coordinates[0]];
  return {
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [[[-179.9, -89.9], [179.9, -89.9], [179.9, 89.9], [-179.9, 89.9], [-179.9, -89.9]], ...holes],
    },
  };
}

const texasGeoJson = getTexasFeature(statesGeoJson); // or getTexasMaskGeoJson(statesGeoJson)

function isPointInTexas(lat, lng) {
  const pt = point([lng, lat]); // note GeoJSON uses [lng, lat]
  return booleanPointInPolygon(pt, texasGeoJson);
}

const maskStyle = {
  fillColor: '#eaeaea',
  fillOpacity: 1,
  stroke: false,
  interactive: false,
};

const texasBorderStyle = {
  color: 'red',
  weight: 3,
  opacity: 1,
  fillOpacity: 0,
};

const TexasMap = ({ center, currentTile = 'dark', layerState, thunderstormView }) => {
  const defaultTexasCenter = [31.9686, -99.9018];

  return (
    <div>
      <MapContainer
        center={center || defaultTexasCenter}
        zoom={5}
        minZoom={6}
        style={{ height: '500px', width: '100%' }}
        maxBounds={texasBounds}
        maxBoundsViscosity={1.0}
        whenCreated={mapInstance => { window.mapInstance = mapInstance; }}
      >
        <TileLayer
          key={currentTile}
          url={TILE_LAYERS[currentTile].url}
          attribution={TILE_LAYERS[currentTile].attribution}
        />

        {getTexasMaskGeoJson(statesGeoJson) && <GeoJSON data={getTexasMaskGeoJson(statesGeoJson)} style={maskStyle} />}
        {getTexasFeature(statesGeoJson) && <GeoJSON data={getTexasFeature(statesGeoJson)} style={texasBorderStyle} />}

        <MapViewUpdater
          center={center}
          defaultCenter={defaultTexasCenter}
          layerState={layerState}
          thunderstormView={thunderstormView}
        />
      </MapContainer>
    </div>
  );
};

const MapViewUpdater = ({ center, defaultCenter, layerState, thunderstormView }) => {
  const map = useMap();
  const fullscreenControlRef = useRef(null);
  const velocityLayerRef = useRef(null);
  const thunderStormLayerRef = useRef(null);
  const hailLayerRef = useRef(null);

  const [hailPoints, setHailPoints] = useState([]);
  const [thunderstormPoints, setThunderstormPoints] = useState([]);

  function fetchEventData(code, setState) {
    fetch(`https://forecasttx.duckdns.org/data/event_code_${code}.json`)
      .then((res) => res.json())
      .then(setState)
      .catch((err) => console.error(`Failed to load event ${code} data`, err));
  }
  
  useEffect(() => {
    fetchEventData(1, setHailPoints);
    fetchEventData(2, setThunderstormPoints);
  }, []);


  useEffect(() => {
    if (!fullscreenControlRef.current) {
      const fullscreenControl = L.control.fullscreen();
      fullscreenControl.addTo(map);
      fullscreenControlRef.current = fullscreenControl;
    }

    map.setView(center || defaultCenter, center ? 10 : 5);

    if (!map.timeDimension) {
      const timeDimension = new L.TimeDimension({
        timeInterval: '2025-01-01/2030-01-01',
        period: 'PT1H',  // PT1H = 1 hour interval
      });
      map.timeDimension = timeDimension;

      const timeControl = new L.Control.TimeDimension({
        position: 'bottomleft',
        autoPlay: true,
        loopButton: true,
        timeSliderDragUpdate: true,
        playerOptions: { transitionTime: 500, loop: true, startOver: true },
      });
      map.addControl(timeControl);
    }

    const handleTimeLoad = (e) => {
      const timeIdx = e.time;
      const dateObj = new Date(timeIdx); 
      const currentData = getWindDataForSlider(dateObj.toISOString());
 

      // Wind
      if ((layerState === 'Wind' || layerState === 'All') && currentData) {
        if (!velocityLayerRef.current) {
          velocityLayerRef.current = L.velocityLayer({
            displayValues: true,
            displayOptions: {
              velocityType: 'Global Wind',
              position: 'bottomright',
              emptyString: 'No wind data',
              angleConvention: 'bearingCW',
              speedUnit: 'm/s',
            },
            data: currentData.data,
          }).addTo(map);
        } else {
          velocityLayerRef.current.setData(currentData.data);
        }
      } else if (velocityLayerRef.current) {
        map.removeLayer(velocityLayerRef.current);
        velocityLayerRef.current = null;
      }

      // Thunderstorm - support both Thunderstorm and All
      if (layerState === 'Thunderstorm' || layerState === 'All') {
        if (thunderStormLayerRef.current) map.removeLayer(thunderStormLayerRef.current);
      
        const currentTimeMs = timeIdx;
      
        // Filter thunderstorm points by time and Texas bounds
        const thunderstormMatches = thunderstormPoints
          .filter(p => Math.abs(new Date(p.time).getTime() - currentTimeMs) < 5 * 60 * 1000)
          .filter(({ lat, lng }) => isPointInTexas(lat, lng));
      
        if (thunderstormMatches.length > 0) {
          if (thunderstormView === 'Icons') {
            const thunderstormIcon = L.divIcon({
              className: 'custom-thunderstorm-icon',
              html: `<img src="${thunderStormGif}" style="width:50px; height:50px;" />`,
              iconSize: [50, 50],
            });
      
            const thunderstormMarkers = thunderstormMatches.map(({ lat, lng }) =>
              L.marker([lat, lng], { icon: thunderstormIcon })
            );
      
            thunderStormLayerRef.current = L.layerGroup(thunderstormMarkers).addTo(map);
          } else if (thunderstormView === 'Heatmap') {
            const heat = L.heatLayer(
              thunderstormMatches.map(({ lat, lng }) => [lat, lng, 0.9]), // Increase intensity per point
              {
                radius: 40,         // Bigger radius for smoother coverage
                blur: 20,           // More blur for a glowing effect
                maxZoom: 10,        // Lower maxZoom spreads the intensity over more area
                gradient: {
                  0.2: 'blue',
                  0.4: 'lime',
                  0.6: 'yellow',
                  0.8: 'orange',
                  1.0: 'red'
                }                   // Optional: custom color ramp
              }
            );
            thunderStormLayerRef.current = heat.addTo(map);
          }
        }
      } else if (thunderStormLayerRef.current) {
        map.removeLayer(thunderStormLayerRef.current);
        thunderStormLayerRef.current = null;
      }
      

      // Hail
     // Hail
if (layerState === 'Hail' || layerState === 'All') {
  if (hailLayerRef.current) map.removeLayer(hailLayerRef.current);

  const hailIcon = L.divIcon({
    className: 'custom-hail-icon',
    html: `<img src="${hailGif}" style="width:50px; height:50px;" />`,
    iconSize: [50, 50],
  });

  // timeIdx is a number (ms)
  const currentTimeMs = timeIdx;

  // Filter points matching the current time within 1 second tolerance
 
  const hailMatches = hailPoints.filter(
    p => Math.abs(new Date(p.time).getTime() - currentTimeMs) < 5 * 60 * 1000
  );
 
  if (hailMatches.length > 0) {
    const hailMarkers = hailMatches
  .filter(({ lat, lng }) => isPointInTexas(lat, lng))
  .map(({ lat, lng }) => L.marker([lat, lng], { icon: hailIcon }));
    hailLayerRef.current = L.layerGroup(hailMarkers).addTo(map);
  }
} else if (hailLayerRef.current) {
  map.removeLayer(hailLayerRef.current);
  hailLayerRef.current = null;
} 
    };

    map.timeDimension.on('timeload', handleTimeLoad);

    return () => {
      map.timeDimension.off('timeload', handleTimeLoad);
      if (velocityLayerRef.current) map.removeLayer(velocityLayerRef.current);
      if (thunderStormLayerRef.current) map.removeLayer(thunderStormLayerRef.current);
      if (hailLayerRef.current) map.removeLayer(hailLayerRef.current);
    };
  }, [map, center, defaultCenter, layerState, thunderstormView]);

  return null;
};

export default TexasMap;