import React, { useEffect, useState } from 'react';
import TopRegions from './TopRegions';
import styles from './../../../styles/Dashboard/Detailed/TopRegionsContainer.module.css';
import { getTop3Counties } from '../../../API/Test_API';

const TopRegionsContainer = ({ selectedPeril, selectedYear }) => {
  const [topHailCount, setTopHailCount] = useState([]);
  const [topMagnitude, setTopMagnitude] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedPeril || !selectedYear) return;

    const loadTopRegions = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log(`Loading top regions data for ${selectedPeril} in ${selectedYear}`);
        const data = await getTop3Counties(selectedYear, selectedPeril);
        console.log("✅ Raw top 3 data from backend:", data);

        // Your API returns a direct array of county objects
        if (!Array.isArray(data) || data.length === 0) {
          console.warn("No county data returned or invalid format:", data);
          setTopHailCount([]);
          setTopMagnitude([]);
          return;
        }

        console.log("Processing counties data:", data);

        // Process data for events count - API already returns top 3 sorted by maximum_hail_magnitude
        const sortedByEvents = data
          .map(county => ({
            name: county.county,
            hailEvents: parseFloat(
              selectedPeril === 'HAIL'
                ? county.occurrence_count
                : county.occurrence_count
            ).toFixed(2),
          }))
          .sort((a, b) => b.hailEvents - a.hailEvents);

        // Process data for magnitude - API already returns top 3 sorted by maximum_hail_magnitude
        const sortedByMagnitude = data
          .map(county => ({
            name: county.county,
            avgMagnitude: parseFloat(
              selectedPeril === 'HAIL'
                ? county.avg_hail_magnitude
                : county.avg_tstm_magnitude
            ),
          }))
          .sort((a, b) => b.avgMagnitude - a.avgMagnitude);

        console.log("Processed events data:", sortedByEvents);
        console.log("Processed magnitude data:", sortedByMagnitude);

        // API already returns top 3, so no need to slice
        setTopHailCount(sortedByEvents);
        setTopMagnitude(sortedByMagnitude);
      } catch (err) {
        console.error("Failed to load top 3 counties:", err);
        setError("Failed to load top regions data");
      } finally {
        setLoading(false);
      }
    };

    loadTopRegions();
  }, [selectedPeril, selectedYear]);

  const handleExport = (regionData, format) => {
    console.log(`Exporting ${regionData.title} as ${format}`);
    
    if (format === 'pdf') {
      exportToPDF(regionData);
    } else if (format === 'word') {
      exportToWord(regionData);
    }
  };

  const exportToPDF = (regionData) => {
    import('jspdf').then(({ default: jsPDF }) => {
      const doc = new jsPDF();
      
      // Set up the document
      doc.setFontSize(20);
      doc.text('Top Regions Report', 20, 20);
      
      // Add a line
      doc.setLineWidth(0.5);
      doc.line(20, 30, 190, 30);
      
      // Report Details
      doc.setFontSize(16);
      doc.text(regionData.title, 20, 50);
      
      doc.setFontSize(12);
      doc.text(`Peril: ${selectedPeril}`, 20, 70);
      doc.text(`Year: ${selectedYear}`, 20, 85);
      
      // Table headers
      doc.setFontSize(14);
      doc.text('Rank', 20, 110);
      doc.text('County Name', 50, 110);
      doc.text('Statistics', 120, 110);
      
      // Add line under headers
      doc.setLineWidth(0.3);
      doc.line(20, 115, 190, 115);
      
      // Table data
      doc.setFontSize(12);
      regionData.regionsData.forEach((region, idx) => {
        const yPos = 130 + (idx * 15);
        doc.text(`${idx + 1}`, 20, yPos);
        doc.text(region.name, 50, yPos);
        
        let statsText = '';
        if (region.hailEvents !== undefined) {
          statsText += `${region.hailEvents} ${selectedPeril} events`;
        }
        if (region.avgMagnitude !== undefined) {
          if (statsText) statsText += ', ';
          statsText += `${region.avgMagnitude.toFixed(2)} avg magnitude`;
        }
        if (region.maxMonthEvents !== undefined) {
          if (statsText) statsText += ', ';
          statsText += `${region.maxMonthEvents} events in top month`;
        }
        
        doc.text(statsText, 120, yPos);
      });
      
      // Add timestamp
      doc.setFontSize(10);
      doc.text(`Generated on: ${new Date().toLocaleString()}`, 20, 280);
      
      doc.save(`${regionData.title.replace(/\s+/g, '_')}_${selectedPeril}_${selectedYear}.pdf`);
    }).catch(err => {
      console.error('Error loading jsPDF:', err);
      alert('Error exporting to PDF. Please make sure jsPDF is installed.');
    });
  };

  const exportToWord = (regionData) => {
    import('html-docx-js/dist/html-docx').then(({ default: htmlDocx }) => {
      const tableRows = regionData.regionsData.map((region, idx) => {
        let statsContent = '';
        if (region.hailEvents !== undefined) {
          statsContent += `${region.hailEvents} ${selectedPeril} events<br/>`;
        }
        if (region.avgMagnitude !== undefined) {
          statsContent += `${region.avgMagnitude.toFixed(2)} avg magnitude<br/>`;
        }
        if (region.maxMonthEvents !== undefined) {
          statsContent += `${region.maxMonthEvents} events in top month`;
        }
        
        return `
          <tr>
            <td style="text-align: center; padding: 10px; border: 1px solid #ddd;">${idx + 1}</td>
            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">${region.name}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">${statsContent}</td>
          </tr>
        `;
      }).join('');

      const htmlContent = `
        <html>
          <head>
            <style>
              body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                line-height: 1.6;
              }
              .header { 
                text-align: center; 
                border-bottom: 2px solid #3498db; 
                padding-bottom: 20px; 
                margin-bottom: 30px;
              }
              h1 { 
                color: #2c3e50; 
                margin: 0;
              }
              .report-section {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
              }
              .report-title { 
                font-size: 18px; 
                font-weight: bold; 
                color: #2c3e50; 
                margin-bottom: 15px;
              }
              table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
              }
              th {
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
              }
              td {
                padding: 10px;
                border: 1px solid #ddd;
              }
              tr:nth-child(even) {
                background-color: #f2f2f2;
              }
              .metadata {
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
              }
              .metadata p {
                margin: 5px 0;
              }
              .footer {
                margin-top: 40px;
                text-align: center;
                font-size: 12px;
                color: #888;
              }
            </style>
          </head>
          <body>
            <div class="header">
              <h1>Top Regions Report</h1>
            </div>
            
            <div class="report-section">
              <div class="report-title">${regionData.title}</div>
              
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>County Name</th>
                    <th>Statistics</th>
                  </tr>
                </thead>
                <tbody>
                  ${tableRows}
                </tbody>
              </table>
            </div>
            
            <div class="metadata">
              <p><strong>Peril Type:</strong> ${selectedPeril}</p>
              <p><strong>Year:</strong> ${selectedYear}</p>
              <p><strong>Report Generated:</strong> ${new Date().toLocaleString()}</p>
            </div>
            
            <div class="footer">
              <p>This report was automatically generated from the Top Regions dashboard.</p>
            </div>
          </body>
        </html>
      `;
      
      const converted = htmlDocx.asBlob(htmlContent);
      const link = document.createElement('a');
      link.href = URL.createObjectURL(converted);
      link.download = `${regionData.title.replace(/\s+/g, '_')}_${selectedPeril}_${selectedYear}.docx`;
      link.click();
      
      // Clean up the URL object
      setTimeout(() => URL.revokeObjectURL(link.href), 100);
    }).catch(err => {
      console.error('Error loading html-docx-js:', err);
      alert('Error exporting to Word. Please make sure html-docx-js is installed.');
    });
  };

  // Handle loading state
  if (loading) {
    return (
      <div className={styles.container}>
        <div>Loading top regions data...</div>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div className={styles.container}>
        <div>Error: {error}</div>
      </div>
    );
  }

  // Handle case where props might not be provided yet
  if (!selectedPeril || !selectedYear) {
    return (
      <div className={styles.container}>
        <div>Please select a peril and year to view top regions data.</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.regionBox}>
        <TopRegions
          title={selectedPeril === 'HAIL' ? 'Top 3 Counties by Counted Hail' : 'Top 3 Counties by Thunderstorm Events'}
          regionsData={topHailCount || []}
          selectedPeril={selectedPeril}
          onExport={handleExport}
        />
      </div>
      <div className={styles.regionBox}>
        <TopRegions
          title={selectedPeril === 'HAIL' ? 'Avg. Predicted Magnitude for the Top 3 Hail Counties' : 'Avg. Predicted Magnitude for the Top 3 Thunderstorm Counties'}
          regionsData={topMagnitude || []}
          selectedPeril={selectedPeril}
          onExport={handleExport}
        />
      </div>
    </div>
  );
};

export default TopRegionsContainer;