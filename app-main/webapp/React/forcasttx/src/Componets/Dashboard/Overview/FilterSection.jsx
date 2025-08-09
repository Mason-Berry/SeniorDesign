import React from 'react'
import SeasonSelect from './SeasonSelect'
import YearSelect from './YearSelect'
import PerilSelect from './PerilSelect'
import styles from './../../../styles/Dashboard/Overview/FIlterSection.module.css'

const FilterSection = ({
  selectedSeason,
  handleSeasonChange,
  selectedYear,
  handleYearChange,
  selectedPeril,
  handlePerilChange,
  resetFilters,
}) => {
  //console.log("selected year from FilterSection:",selectedYear);
  //console.log('Selected Season from FilterSection:', selectedSeason);
  return (
    <div className={styles.filterRow}>
      <SeasonSelect
        selectedSeason={selectedSeason}
        handleSeasonChange={handleSeasonChange}
      />
      <YearSelect
        initialYear={selectedYear}
        onChange={handleYearChange}
      />
      <PerilSelect
        selectedPeril={selectedPeril}
        handlePerilChange={handlePerilChange}
      />
      <button className={styles.resetButton} onClick={resetFilters}>
        Reset Filters
      </button>
    </div>
  );
};

export default FilterSection;