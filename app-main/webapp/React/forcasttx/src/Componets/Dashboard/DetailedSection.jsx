import React from 'react'
import DetailedHeader from './Detailed/DetailedHeader'
import KPIContainer from './Detailed/KPIContainer'
import TopRegionsContainer from './Detailed/TopRegionsContainer'
import styles from './../../styles/Dashboard/Detailed/DetailedSection.module.css'
import Analysis from './Detailed/Analysis';
const DetailedSection = ({selectedYear,selectedPeril}) => {
  //console.log("This is the Selected Year in DetailedSection:",selectedYear )
  //console.log("This is the Selected perilin DetailedSection:",selectedPeril )
  return (
    <div className={styles.detailedContent}>
      <DetailedHeader/>
      <Analysis/>
    </div>
  )
}

export default DetailedSection
