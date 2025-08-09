import React, { useEffect, useState } from 'react';
import KPI from './KPI';
import styles from './../../../styles/Dashboard/Detailed/KPIContainer.module.css';
import { getKpiSummary } from '../../../API/Test_API'; // Adjust path as needed

const KPIContainer = ({ selectedPeril, selectedYear }) => {
  const [totalEvents, setTotalEvents] = useState("0.00");
  const [lowestMagnitude, setLowestMagnitude] = useState("0.00");
  const [avgMagnitude, setAvgMagnitude] = useState("0.00");
  const [maxMagnitude, setMaxMagnitude] = useState("0.00");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hoveredKPI, setHoveredKPI] = useState(null);

  useEffect(() => {
    const fetchKpiData = async () => {
      if (!selectedYear || !selectedPeril) {
        return;
      }
      setLoading(true);
      setError(null);
      try {
        console.log(`Fetching KPI data for ${selectedPeril} in ${selectedYear}`);
        const response = await getKpiSummary(selectedYear, selectedPeril);
        if (response.success) {
          setTotalEvents(response.total_events);
          setLowestMagnitude(response.lowest_magnitude);
          setAvgMagnitude(response.avg_magnitude);
          setMaxMagnitude(response.max_magnitude);
        } else {
          console.error('API returned error:', response.error);
          setError(response.error || 'Failed to fetch KPI data');
          // Set default values on error
          setTotalEvents("0.00");
          setLowestMagnitude("0.00");
          setAvgMagnitude("0.00");
          setMaxMagnitude("0.00");
        }
      } catch (err) {
        console.error('Error fetching KPI data:', err);
        setError('Failed to connect to server');
        // Set default values on error
        setTotalEvents("0.00");
        setLowestMagnitude("0.00");
        setAvgMagnitude("0.00");
        setMaxMagnitude("0.00");
      } finally {
        setLoading(false);
      }
    };
    fetchKpiData();
  }, [selectedPeril, selectedYear]);

  const handleKPIHover = (kpiId) => {
    setHoveredKPI(kpiId);
  };

  const handleKPILeave = () => {
    setHoveredKPI(null);
  };

  const handleExport = (kpiData, format) => {
    // This function will handle the export logic
    console.log(`Exporting ${kpiData.title} as ${format}`);
    
    if (format === 'pdf') {
      exportToPDF(kpiData);
    } else if (format === 'word') {
      exportToWord(kpiData);
    }
  };

  const exportToPDF = (kpiData) => {
    // Import jsPDF dynamically to avoid build issues
    import('jspdf').then(({ default: jsPDF }) => {
      const doc = new jsPDF();
      doc.setFontSize(16);
      doc.text(kpiData.title, 20, 20);
      doc.setFontSize(12);
      doc.text(`Value: ${kpiData.value}`, 20, 40);
      doc.text(`Description: ${kpiData.description}`, 20, 60);
      doc.text(`Peril: ${selectedPeril}`, 20, 80);
      doc.text(`Year: ${selectedYear}`, 20, 100);
      doc.save(`${kpiData.title.replace(/\s+/g, '_')}.pdf`);
    }).catch(err => {
      console.error('Error loading jsPDF:', err);
      alert('Error exporting to PDF. Please make sure jsPDF is installed.');
    });
  };

  const exportToWord = (kpiData) => {
    // Import html-docx-js dynamically
    import('html-docx-js/dist/html-docx').then(({ default: htmlDocx }) => {
      const htmlContent = `
        <html>
          <head>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              h1 { color: #2c3e50; }
              .kpi-value { font-size: 24px; font-weight: bold; color: #3498db; }
              .description { margin-top: 10px; color: #666; }
            </style>
          </head>
          <body>
            <h1>${kpiData.title}</h1>
            <div class="kpi-value">${kpiData.value}</div>
            <div class="description">${kpiData.description}</div>
            <p><strong>Peril:</strong> ${selectedPeril}</p>
            <p><strong>Year:</strong> ${selectedYear}</p>
          </body>
        </html>
      `;
      
      const converted = htmlDocx.asBlob(htmlContent);
      const link = document.createElement('a');
      link.href = URL.createObjectURL(converted);
      link.download = `${kpiData.title.replace(/\s+/g, '_')}.docx`;
      link.click();
    }).catch(err => {
      console.error('Error loading html-docx-js:', err);
      alert('Error exporting to Word. Please make sure html-docx-js is installed.');
    });
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div>Loading KPI data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div style={{ color: 'red' }}>Error: {error}</div>
      </div>
    );
  }

  const kpiData = [
    {
      id: 'total-events',
      title: `Total Predicted ${selectedPeril} Events`,
      value: totalEvents,
      description: "Total number of predicted events"
    },
    {
      id: 'lowest-magnitude',
      title: "Lowest Predicted Magnitude",
      value: lowestMagnitude,
      description: "Minimum magnitude across all locations"
    },
    {
      id: 'avg-magnitude',
      title: "Average Predicted Magnitude",
      value: avgMagnitude,
      description: "Average magnitude across all locations"
    },
    {
      id: 'max-magnitude',
      title: "Maximum Predicted Magnitude",
      value: maxMagnitude,
      description: "Highest magnitude across all locations"
    }
  ];

  return (
    <>
      {/* Backdrop overlay */}
      {hoveredKPI && (
        <div className={styles.backdrop} onClick={handleKPILeave} />
      )}
      
      <div className={`${styles.container} ${hoveredKPI ? styles.blurred : ''}`}>
        {kpiData.map((kpi) => (
          <KPI
            key={kpi.id}
            title={kpi.title}
            value={kpi.value}
            description={kpi.description}
            onHover={() => handleKPIHover(kpi.id)}
            onLeave={handleKPILeave}
            onExport={(format) => handleExport(kpi, format)}
            isHovered={hoveredKPI === kpi.id}
            className={hoveredKPI && hoveredKPI !== kpi.id ? styles.dimmed : ''}
          />
        ))}
      </div>
    </>
  );
};

export default KPIContainer;