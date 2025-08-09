import React, { useState } from 'react';
import KPIContainer from '../Detailed/KPIContainer';
import TopRegionsContainer from "../Detailed/TopRegionsContainer";
import styles from '../../../styles/Dashboard/Detailed/Analysis.module.css';
import KPIFilterButtons from './KPIFilterButton';
import HeatmapChart from './HeatmapChart';

const Analysis = () => {
  // Existing state for FilterButtons
  const [mapView, setMapView] = useState('Texas');
  const [mapType, setMapType] = useState('General Map');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [peril, setPeril] = useState('Hail');

  // New state for KPI filters
  const [selectedPeril, setSelectedPeril] = useState('HAIL');
  const [selectedYear, setSelectedYear] = useState(2025);

  const handleClear = () => {
    setMapView('Texas');
    setMapType('General Map');
    setStartDate('');
    setEndDate('');
    setPeril('Hail');
  };

  const handleKPIClear = () => {
    setSelectedPeril('HAIL');
    setSelectedYear(2025);
  };

  return (
    <div className={styles.analysis}>
      <div className={styles.headerRow}>
        <h3 className={styles.heading}>Analysis</h3>
        <KPIFilterButtons
          selectedPeril={selectedPeril}
          setSelectedPeril={setSelectedPeril}
          selectedYear={selectedYear}
          setSelectedYear={setSelectedYear}
          handleClear={handleKPIClear}
        />
      </div>
      <div className={styles.content}>
        <HeatmapChart
          selectedPeril={selectedPeril}
          selectedYear={selectedYear}
        />
        
        {/* KPI Section with its own filters */}
        
        
        <KPIContainer
          selectedPeril={selectedPeril}
          selectedYear={selectedYear}
        />
        
        <TopRegionsContainer 
          selectedPeril={selectedPeril}
          selectedYear={selectedYear}
        />
      </div>
    </div>
  );
};

export default Analysis;