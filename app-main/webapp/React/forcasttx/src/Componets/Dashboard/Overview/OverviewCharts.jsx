import React from 'react'
import MLRegression from './MLRegression'
import PastVsAi from './PastVsAi'
import styles from './../../../styles/Dashboard/Overview/OverviewCharts.module.css'
import HeatmapChart from '../Detailed/HeatmapChart'
const OverviewCharts = ({selectedCounty,selectedSeason, selectedYear, selectedPeril}) => {
  //console.log("Selected County in OverviewCharts:", selectedCounty);
  //console.log("selected year from OverviewCharts:",selectedYear);
  //console.log('Selected Season from OverviewCharts:', selectedSeason);
  return (
    <div className={styles.charts}> 
        {/* <div className="MLRegression-box">
            <MLRegression
             selectedCounty ={selectedCounty}
             selectedSeason={selectedSeason}
             selectedYear={selectedYear}
             selectedPeril={selectedPeril}
            />
        </div> */}
        
        {/* <div className="PastVsAi-box"> 
            <PastVsAi/>
        </div> */}

        <div className='Heatmap-box'>
          <HeatmapChart/>
        </div>
    </div>
  )
}

export default OverviewCharts
