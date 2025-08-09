// import React, { useEffect, useState } from 'react';
// import { Line } from 'react-chartjs-2';
// import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
// import styles from './../../../styles/Dashboard/Overview/PastVsAi.module.css';
// import * as d3 from 'd3'; // Import d3 for CSV handling

// ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// const getCleanCountyName = (name) => {
//   return name.replace(/ County$/i, '').trim().toUpperCase();
// };

// const monthToSeason = {
//   1: 'Winter', 2: 'Winter', 12: 'Winter',
//   3: 'Spring', 4: 'Spring', 5: 'Spring',
//   6: 'Summer', 7: 'Summer', 8: 'Summer',
//   9: 'Fall', 10: 'Fall', 11: 'Fall'
// };

// const MLRegression = ({ selectedCounty,selectedSeason, selectedYear, selectedPeril }) => {
//   const [chartData, setChartData] = useState({ labels: [], datasets: [] });
//   //console.log('Selected Season from MLRegression:', selectedSeason);
//   useEffect(() => {
//     if (selectedCounty) {
//       const fetchData = async () => {
//         try {
//           let filePath = '';
//           if (selectedPeril === 'HAIL') {
//               filePath = '/assets/Data/hail_data.csv';
//           } else if (selectedPeril === 'THUNDERSTORM WIND') {
//               filePath = '/assets/Data/thunderstorm_wind_data.csv';
//           } else {
//           console.warn('Unsupported peril type:', selectedPeril);
//           return;
// }

//           console.log('Fetching CSV from:', filePath);

//           // Fetch the CSV using d3.csv
//           const data = await d3.csv(filePath);
//           console.log('CSV Data:', data);
//           console.log(selectedCounty);

//           // Clean data if necessary (trim spaces)
//           const cleanedData = data.map((row) => ({
//             ...row,
//             County: row.County.trim(),
//             Event_Type: row.Event_Type.trim(),
//             Year: row.Year?.trim(),
//             Month: row.Month?.trim(),
//             Predicted_Event_Count: row.Predicted_Event_Count?.trim(),
//           }));

//           const cleanedSelectedCounty = getCleanCountyName(selectedCounty);
//           console.log('Cleaned County:', cleanedSelectedCounty);
//           console.log('Selected Peril:', selectedPeril);
//           console.log('Selected Year:', selectedYear);
//           console.log('Selected Season:', selectedSeason);

//           // Debug log: check if the filtering works
//           // Filter the data for the selected county and HAIL event type
//           const filteredData = cleanedData.filter(
//             (row) =>
//               row.County.toUpperCase() === cleanedSelectedCounty &&
//               row.Event_Type === selectedPeril &&
//               row.Year === selectedYear
//           );
//           console.log('Filtered  Data:', filteredData);

//           const seasonFilteredData = filteredData.filter((row) => {
//             const month = parseInt(row.Month, 10);
//             const season = monthToSeason[month]; // Get the season from month
//             return selectedSeason === season;
//           });

//           console.log('Filtered Data for Season:', seasonFilteredData);

//           // Prepare data for the chart
//           const dataToUse = selectedSeason ? seasonFilteredData: filteredData;

// const sortedData = dataToUse.sort((a, b) => parseInt(a.Month) - parseInt(b.Month));

//           // Prepare chart data
//           const monthAbbreviations = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
//             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

//           const labels = sortedData.map((row) => {
//             const monthIndex = parseInt(row.Month, 10) - 1;
//             return monthAbbreviations[monthIndex] || row.Month;
//            });
//           const predictedEventCount = sortedData.map((row) => parseFloat(row.Predicted_Event_Count));

//           // Update chart data state
//           setChartData({
//             labels,
//             datasets: [
//               {
//                 label: `Predicted Events for ${selectedCounty} ${selectedPeril}`,
//                 data: predictedEventCount,
//                 borderColor: 'rgb(183, 72, 72)',
//                 backgroundColor: 'rgba(192, 75, 75, 0.2)',
//                 fill: true,
//               },
//             ],
//           });
//         } catch (error) {
//           console.error('Error fetching or parsing CSV data:', error);
//         }
//       };

//       fetchData();
//     }
//   }, [selectedCounty]);

//   const options = {
//     responsive: true,
//     plugins: {
//       title: {
//         display: true,
//         text: `ML Linear Regression Model for ${selectedCounty || 'County'}`,
//       },
//       tooltip: {
//         callbacks: {
//           label: function (tooltipItem) {
//             return `Value: ${tooltipItem.raw}`;
//           },
//         },
//       },
//     },
//   };

//   return (
//     <div className={styles.box}>
//       <h3 className={styles.boxTitle}>ML Linear Regression</h3>
//       {chartData.labels.length > 0 ? (
//         <Line data={chartData} options={options} />
//       ) : (
//         <p>Loading data...</p>
//       )}
//     </div>
//   );
// };

// export default MLRegression;
