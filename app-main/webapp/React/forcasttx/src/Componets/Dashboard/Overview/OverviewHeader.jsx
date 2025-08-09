import React from 'react'
import styles from './../../../styles/Dashboard/OverviewAndDetailedHeader.module.css'
const OverviewHeader = () => {
  return (
    <div className={styles.headerContainer}>
        <h2 className={styles.headerTitle}>Overview</h2>
        <p className={styles.headerSubtitle}>
          This overview displays the overall findings of the selected machine learning algorithm based on the selected season and county.
          Here, the user is able to select a season from the drop down menu and a county from the county map of Texas. 
          The charts display the findings of the weather prediction model outlining how many severe weather events it predicts will occur each month,
          and comparing the previous data's number of events per month to the prediction model's.

        </p>
    </div>
  )
}

export default OverviewHeader
