import React, { useState } from 'react';
import TexasMap from './TexasMap';
import FilterButtons from '../FilterButtons';
import styles from './../../../styles/Dashboard/Overview/MapContainer.module.css';

const MapContainer = ({ onCountySelect }) => {
  const [mapView, setMapView] = useState('Texas');
  const [mapType, setMapType] = useState('General Map');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [peril, setPeril] = useState('Hail');
  const [selectedCity, setSelectedCity] = useState(null);
  const [currentTile, setCurrentTile] = useState('dark');
  const [layerState, setLayerState] = useState('Thunderstorm');
  const [thunderstormView, setThunderstormView] = useState('Icons');  

  const cities = {
    Houston: [29.7604, -95.3698],
    Dallas: [32.7767, -96.7970],
    Austin: [30.2672, -97.7431],
    SanAntonio: [29.4241, -98.4936],
    FortWorth: [32.7555, -97.3308],
  };

  const handleClear = () => {
    setMapView('Texas');
    setMapType('General Map');
    setStartDate('');
    setEndDate('');
    setPeril('Hail');
    setSelectedCity(null);
    setCurrentTile('dark');
    setLayerState('Thunderstorm');
    setThunderstormView('Icons');  
  };

  return (
    <div className={styles.mapContainer}>
      <h3>Map of Texas</h3>

      <FilterButtons 
        mapView={mapView}
        setMapView={setMapView}
        mapType={mapType}
        setMapType={setMapType}
        startDate={startDate}
        setStartDate={setStartDate}
        endDate={endDate}
        setEndDate={setEndDate}
        selectedCity={selectedCity}
        setSelectedCity={setSelectedCity}
        cities={cities}
        handleClear={handleClear}
        currentTile={currentTile} 
        setCurrentTile={setCurrentTile}
        layerState={layerState} 
        setLayerState={setLayerState}
        thunderstormView={thunderstormView}                
        setThunderstormView={setThunderstormView}          
      />

      <TexasMap 
        onCountySelect={onCountySelect} 
        center={selectedCity}
        currentTile={currentTile} 
        layerState={layerState}
        thunderstormView={thunderstormView} 
                       
      />
    </div>
  );
};

export default MapContainer;
