import React from 'react'
import styles from './../../../styles/Dashboard/OverviewAndDetailedHeader.module.css'
const DetailedHeader = () => {
  return (
    <div className={styles.headerContainer}>
        <h2 className={styles.headerTitle}>Detailed</h2>
     <p className={styles.headerSubtitle}>
      This detailed section of the dashboard ranks the counties based the shown attributes.
      The highest ranking attribute is shown along with its percentage above the next ranked county's attribute.
      A tier list of the top 3 counties is shown below the top ranking attribute.
     </p>
  </div>
  )
}

export default DetailedHeader
