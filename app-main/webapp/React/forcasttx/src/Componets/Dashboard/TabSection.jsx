import React from 'react';
import styles from '../../styles/Dashboard/TabSection.module.css';
import { ArrowRightFromLineIcon, ClipboardList, Home } from 'lucide-react'; // use `Home` instead of `House`

const TabSection = ({ activeTab, setActiveTab }) => {
  return (
    <div className={styles['tab-section']}>
      <div className={styles.tabs}>
        <button
          className={`${styles['tab-btn']} ${activeTab === 'overview' ? styles.active : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Home className={styles['tab-icon']} />
          <span>Overview</span>
        </button>
        <button
          className={`${styles['tab-btn']} ${activeTab === 'detailed' ? styles.active : ''}`}
          onClick={() => setActiveTab('detailed')}
        >
          <ClipboardList className={styles['tab-icon']} />
          <span>Detailed</span>
        </button>
        <button
          className={`${styles['tab-btn']} ${activeTab === 'export' ? styles.active : ''}`}
          onClick={() => setActiveTab('export')}
        >
          <ArrowRightFromLineIcon className={styles['tab-icon']} />
          <span>Export</span>
        </button>
      </div>
    </div>
  );
};

export default TabSection;
