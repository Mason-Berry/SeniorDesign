import React from 'react'
import styles from './../../../styles/Dashboard/Overview/SelectBox.module.css'
const SeasonSelect = ({ selectedSeason, handleSeasonChange }) => {
  //console.log('Selected Season:', selectedSeason);
  return (
    <div className={styles.selectBox}>
      <h3>Select Season</h3>
      <select
        value={selectedSeason}
        onChange={(e) => handleSeasonChange(e.target.value)} // FIXED
        className={styles.seasonDropdown}
      >
        <option value="">--Select--</option>
        <option value="Winter">Winter</option>
        <option value="Spring">Spring</option>
        <option value="Summer">Summer</option>
        <option value="Fall">Fall</option>
      </select>
      <p>Selected Season: {selectedSeason}</p>
    </div>
  );
};
export default SeasonSelect
