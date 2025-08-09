import React, { useState, useEffect } from 'react';
import Profile from './Profile'; // Import the Profile component
import statefarmLogo from '../assets/statefarm-logo.png';
import OverviewSection from './Dashboard/OverviewSection';
import DetailedSection from './Dashboard/DetailedSection';
import Export from './Dashboard/Export/Export';
import styles from '../styles/Dashboard/Dashboard.module.css';
import TabSection from './Dashboard/TabSection';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [shifted, setShifted] = useState(false);

  const [selectedSeason, setSelectedSeason] = useState('');
  const [selectedPeril, setSelectedPeril] = useState('');
  const [selectedYear, setSelectedYear] = useState('');

  useEffect(() => {
    const timeout = setTimeout(() => {
      setShifted(true);
    }, 100);

    return () => clearTimeout(timeout);
  }, []);

  return (
    <div className={`${styles.container} ${shifted ? styles.shifted : ''}`}>
      <div className={styles.titleContainer}>
        <h1 className={styles.dashboardTitle}>ForecastTx</h1>
        <Profile /> 
      </div>
      
      <div className="dashboard-tab-content">
        <div className={styles.tabWrapper}>
          <TabSection activeTab={activeTab} setActiveTab={setActiveTab} />
        </div>
        <div className={styles.pageWrapper}>
          {activeTab === 'overview' && (
            <OverviewSection
              selectedSeason={selectedSeason}
              setSelectedSeason={setSelectedSeason}
              selectedYear={selectedYear}
              setSelectedYear={setSelectedYear}
              selectedPeril={selectedPeril}
              setSelectedPeril={setSelectedPeril}
            />
          )}
          {activeTab === 'detailed' && (
            <DetailedSection
              selectedPeril={selectedPeril}
              selectedYear={selectedYear}
            />
          )}
          {activeTab === 'export' && (
            <Export
              selectedPeril={selectedPeril}
              selectedYear={selectedYear}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;