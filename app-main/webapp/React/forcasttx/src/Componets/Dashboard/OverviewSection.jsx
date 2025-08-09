import React, { useState } from 'react';
import MapContainer from './Overview/MapContainer';
import styles from './../../styles/Dashboard/Overview/OverviewSection.module.css';
import TabSection from './TabSection';
import Overviewheader from './Overview/OverviewHeader'

const OverviewSection = () => {
  const [selectedCounty, setSelectedCounty] = useState(null);

  const handleCountySelect = (county) => {
    setSelectedCounty(county);
  };

  return (
    <>
    <div className={styles.Headder}>
      <Overviewheader/>
    </div>
    
    <div className={styles.mapOnlyLayout}>
      <div className={styles.mapWrapper}>
        <MapContainer onCountySelect={handleCountySelect} />
      </div>
    </div>
  </>
  );
};

export default OverviewSection;
