import React from 'react';
import styles from '../../styles/Dashboard/FilterButtons.module.css';
import CitySelect from './Overview/CitySelect'; 
import { Binoculars, Layers, CloudLightning, Wind, CloudHail, SquareStack } from 'lucide-react';

const FilterButtons = ({
  mapView, setMapView,
  mapType, setMapType,
  startDate, setStartDate,
  endDate, setEndDate,
  peril, setPeril,
  selectedCity, setSelectedCity,
  cities,
  handleClear,
  currentTile, setCurrentTile,
  layerState, setLayerState,
  thunderstormView, setThunderstormView
}) => {
  const getLayerIcon = () => {
    switch (layerState) {
      case 'All':
        return <SquareStack className={styles.icon} />;
      case 'Wind':
        return <Wind className={styles.icon} />;
      case 'Hail':
        return <CloudHail className={styles.icon} />;
      case 'Thunderstorm':
      default:
        return <CloudLightning className={styles.icon} />;
    }
  };

  return (
    <div>
      <div className={styles.controls}>
        {/* City Select */}
        <div className={styles.selectWrapper}>
          <Binoculars className={styles.icon} />
          <CitySelect 
            selectedCity={selectedCity}
            setSelectedCity={setSelectedCity}
            cities={cities}
          />
        </div>

        {/* Layer Selection with Thunderstorm View */}
        <div className={styles.selectWrapper}>
          {getLayerIcon()}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <select value={layerState} onChange={(e) => setLayerState(e.target.value)}>
              <option value="Thunderstorm">Thunderstorm</option>
              <option value="Wind">Wind</option>
              <option value="Hail">Hail</option>
              <option value="All">All</option>
            </select>

            {layerState === 'Thunderstorm' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CloudLightning className={styles.icon} />
              <select value={thunderstormView} onChange={e => setThunderstormView(e.target.value)}>
                <option value="Icons">Icons</option>
                <option value="Heatmap">Heatmap</option>
              </select>
            </div>
            )}
          </div>
        </div>

        {/* Tile Selection */}
        <div className={styles.selectWrapper}>
          <Layers className={styles.icon} />
          <select value={currentTile} onChange={e => setCurrentTile(e.target.value)}>
            <option value="dark">Dark Map</option>
            <option value="light">Light Map</option>
            <option value="terrain">Terrain</option>
          </select>
        </div>

        {/* Clear Button */}
        <button onClick={handleClear}>Clear</button>
      </div>
    </div>
  );
};

export default FilterButtons;
