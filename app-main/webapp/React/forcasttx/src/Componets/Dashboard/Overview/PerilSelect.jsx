import React from 'react';
import styles from './../../../styles/Dashboard/Overview/SelectBox.module.css';

const PerilSelect = ({ selectedPeril = "", handlePerilChange }) => {
  const perils = ['HAIL', 'THUNDERSTORM WIND'];

  return (
    <div className={styles.selectBox}>
      <h3>Select Peril</h3>
      <select value={selectedPeril} onChange={(e) => handlePerilChange(e.target.value)}>
        <option value="">Select a peril...</option>
        {perils.map((peril) => (
          <option key={peril} value={peril}>
            {peril}
          </option>
        ))}
      </select>
      <p>Selected Peril:</p>
      <p>{selectedPeril}</p>
    </div>
  );
};

export default PerilSelect;
