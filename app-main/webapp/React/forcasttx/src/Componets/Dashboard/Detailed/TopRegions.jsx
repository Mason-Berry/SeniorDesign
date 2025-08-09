import React, { useState } from 'react';
import { Download } from 'lucide-react';
import styles from './../../../styles/Dashboard/Detailed/TopRegions.module.css';

const TopRegions = ({ title, regionsData, selectedPeril, onExport }) => {
  const [showExportMenu, setShowExportMenu] = useState(false);

  const handleExportClick = (e) => {
    e.stopPropagation();
    setShowExportMenu(!showExportMenu);
  };

  const handleExportOption = (format) => {
    if (onExport) {
      const regionData = { title, regionsData, selectedPeril };
      onExport(regionData, format);
    }
    setShowExportMenu(false);
  };

  return (
    <div className={styles.container}>
      {/* Export Button */}
      <div className={styles.exportContainer}>
        <button
          className={styles.exportButton}
          onClick={handleExportClick}
          title="Export Top Regions"
        >
          <Download size={20} />
        </button>
        
        {/* Export Menu */}
        {showExportMenu && (
          <div className={styles.exportMenu}>
            <button
              className={styles.exportOption}
              onClick={() => handleExportOption('pdf')}
            >
              Export as PDF
            </button>
            <button
              className={styles.exportOption}
              onClick={() => handleExportOption('word')}
            >
              Export as Word
            </button>
          </div>
        )}
      </div>

      <h3>{title}</h3>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>No.</th>
            <th>Name</th>
            <th>Stats</th>
          </tr>
        </thead>
        <tbody>
          {regionsData.map((region, idx) => (
            <tr key={idx}>
              <td>{idx + 1}</td>
              <td>{region.name}</td>
              <td>
                {region.hailEvents !== undefined && `${region.hailEvents} ${selectedPeril} events`}<br />
                {region.avgMagnitude !== undefined && `${region.avgMagnitude.toFixed(2)} avg magnitude`}<br />
                {region.maxMonthEvents !== undefined && `${region.maxMonthEvents} events in top month`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TopRegions;