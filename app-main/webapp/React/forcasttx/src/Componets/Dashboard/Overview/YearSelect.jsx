import React, { useState } from 'react';
import styles from './../../../styles/Dashboard/Overview/SelectBox.module.css';

const YearSelect = ({ initialYear = "", onChange }) => {
  const [selectedYear, setSelectedYear] = useState(initialYear);

  const handleChange = (e) => {
    const year = e.target.value;
    setSelectedYear(year);
    if (onChange) onChange(year);
  };

  const years = [];
  for (let y = 2025; y <= 2029; y++) {
    years.push(y);
  }

  //console.log("selected year from YearSelect:", selectedYear);

  return (
    <div className={styles.selectBox}>
      <h3>Select Year</h3>
      <select value={selectedYear} onChange={handleChange}>
        <option value="">Select a year...</option>
        {years.map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>
      <p>Selected Year: {selectedYear}</p>
    </div>
  );
};

export default YearSelect;
