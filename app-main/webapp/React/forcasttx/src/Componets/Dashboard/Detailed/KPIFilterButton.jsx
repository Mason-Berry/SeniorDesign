import React from 'react';
import styles from '../../../styles/Dashboard/FilterButtons.module.css'; // Reusing your existing styles
import { CloudHail, CloudLightning, Calendar, BarChart3 } from 'lucide-react';

const KPIFilterButtons = ({
  selectedPeril,
  setSelectedPeril,
  selectedYear,
  setSelectedYear,
  handleClear
}) => {
  
  const getPerilIcon = () => {
    switch (selectedPeril) {
      case 'HAIL':
        return <CloudHail className={styles.icon} />;
      case 'THUNDERSTORM':
        return <CloudLightning className={styles.icon} />;
      default:
        return <BarChart3 className={styles.icon} />;
    }
  };

  // Available years (you can adjust this range as needed)
  const availableYears = [2025, 2026, 2027, 2028, 2029, 2030];

  return (
    <div>
      <div className={styles.controls}>
        
        {/* Peril Selection */}
        <div className={styles.selectWrapper}>
          {getPerilIcon()}
          <select 
            value={selectedPeril} 
            onChange={(e) => setSelectedPeril(e.target.value)}
          >
            <option value="HAIL">Hail</option>
            <option value="THUNDERSTORM">Thunderstorm</option>
          </select>
        </div>

        {/* Year Selection */}
        <div className={styles.selectWrapper}>
          <Calendar className={styles.icon} />
          <select 
            value={selectedYear} 
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
          >
            {availableYears.map(year => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {/* Clear Button */}
        <button onClick={handleClear}>
          Reset to Defaults
        </button>
        
      </div>
    </div>
  );
};

export default KPIFilterButtons;