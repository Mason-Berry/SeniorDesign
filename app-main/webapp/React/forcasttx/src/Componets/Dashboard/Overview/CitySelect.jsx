import React from 'react';
import styles from './../../../styles/Dashboard/Overview/SelectBox.module.css';

const CitySelect = ({ selectedCity, setSelectedCity, cities = {} }) => {
  const handleCityChange = (event) => {
    const cityName = event.target.value;
    if (cityName && cities[cityName]) {
      setSelectedCity(cities[cityName]);
    } else {
      setSelectedCity(null);
    }
  };

  const getSelectedCityKey = () => {
    if (!selectedCity) return '';
    for (let city in cities) {
      if (cities[city][0] === selectedCity[0] && cities[city][1] === selectedCity[1]) {
        return city;
      }
    }
    return '';
  };

  // Determine what the first option should display
  const firstOption = selectedCity
    ? <option value="">Remove City</option>
    : <option value="">Select a City</option>;

  return (
    <select
      className={styles.selectBox}
      onChange={handleCityChange}
      value={getSelectedCityKey()}
    >
      {firstOption}
      {Object.keys(cities).map((city) => (
        <option key={city} value={city}>
          {city}
        </option>
      ))}
    </select>
  );
};

export default CitySelect;