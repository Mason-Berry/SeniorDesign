import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import _ from 'lodash';
import styles from '../../../styles/Dashboard/Detailed/HeatmapChart.module.css';
import { getCountyOccurrences } from '../../../API/Test_API';

const HeatmapChart = ({ selectedPeril, selectedYear }) => {
  const svgRef = useRef();
  const tooltipRef = useRef();
  const containerRef = useRef();
  const [currentYear, setCurrentYear] = useState(selectedYear || 2025);
  const [countyData, setCountyData] = useState({});
  const [availableYears, setAvailableYears] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Update currentYear when selectedYear prop changes
  useEffect(() => {
    if (selectedYear && selectedYear !== currentYear) {
      setCurrentYear(selectedYear);
    }
  }, [selectedYear]);

  // Fetch county occurrence data from your API
  const fetchCountyData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Map peril type to event code
      const eventCode = selectedPeril === 'HAIL' ? 1 : 2; // 1 = HAIL, 2 = THUNDERSTORM

      // Fetch all county occurrences data with event code filter
      const result = await getCountyOccurrences(null, null, null, null, eventCode);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch county data');
      }

      console.log('Raw API data:', result.data); // Debug log

      // Group data by year and county
      const groupedData = _.groupBy(result.data, 'year');
      
      // Get available years and sort them
      const years = Object.keys(groupedData).map(Number).sort();
      setAvailableYears(years);
      
      // Process data for visualization
      const processedData = {};
      years.forEach(year => {
        const yearData = groupedData[year];
        
        // Calculate percentile-based risk scores for better distribution
        const occurrenceCounts = yearData.map(d => d.occurrence_count).sort((a, b) => a - b);
        const minOccurrences = Math.min(...occurrenceCounts);
        const maxOccurrences = Math.max(...occurrenceCounts);
        
        // Calculate percentiles for more balanced risk distribution
        const p25 = d3.quantile(occurrenceCounts, 0.25);
        const p50 = d3.quantile(occurrenceCounts, 0.50);
        const p75 = d3.quantile(occurrenceCounts, 0.75);
        const p90 = d3.quantile(occurrenceCounts, 0.90);
        const p95 = d3.quantile(occurrenceCounts, 0.95);
        
        console.log(`Year ${year} - Min: ${minOccurrences}, Max: ${maxOccurrences}, P25: ${p25}, P50: ${p50}, P75: ${p75}, P90: ${p90}, P95: ${p95}`);
        
        processedData[year] = yearData.map(county => {
          const count = county.occurrence_count;
          let risk;
          
          // Assign risk based on percentiles for better distribution
          if (count >= p95) risk = 95 + ((count - p95) / (maxOccurrences - p95 + 1)) * 5; // 95-100
          else if (count >= p90) risk = 85 + ((count - p90) / (p95 - p90 + 1)) * 10; // 85-95
          else if (count >= p75) risk = 65 + ((count - p75) / (p90 - p75 + 1)) * 20; // 65-85
          else if (count >= p50) risk = 40 + ((count - p50) / (p75 - p50 + 1)) * 25; // 40-65
          else if (count >= p25) risk = 20 + ((count - p25) / (p50 - p25 + 1)) * 20; // 20-40
          else risk = (count / (p25 + 1)) * 20; // 0-20
          
          return {
            county: county.county,
            state: county.state,
            fips: county.fips,
            year: county.year,
            eventCode: county.predicted_event_code,
            occurrenceCount: county.occurrence_count,
            avgHailMagnitude: county.avg_hail_magnitude,
            avgTstmMagnitude: county.avg_tstm_magnitude,
            maxHailMagnitude: county.max_hail_magnitude,
            maxTstmMagnitude: county.max_tstm_magnitude,
            risk: Math.min(100, Math.max(0, risk)) // Clamp between 0-100
          };
        });
      });

      console.log('Processed data:', processedData); // Debug log
      setCountyData(processedData);
      
      // Set current year to selectedYear if available, otherwise latest year
      if (selectedYear && years.includes(selectedYear)) {
        setCurrentYear(selectedYear);
      } else if (years.length > 0 && !years.includes(currentYear)) {
        setCurrentYear(Math.max(...years));
      }

    } catch (err) {
      console.error('Error fetching county data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch data on component mount or when selectedPeril changes
  useEffect(() => {
    fetchCountyData();
  }, [selectedPeril]);

  useEffect(() => {
    if (loading || error || Object.keys(countyData).length === 0) {
      return;
    }

    d3.select(svgRef.current).selectAll('*').remove();

    const margin = { top: 80, right: 140, bottom: 80, left: 40 };
    const width = 900 - margin.left - margin.right;
    const height = 600 - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Get current year data
    const currentYearData = countyData[currentYear] || [];
    
    if (currentYearData.length === 0) {
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .text(`No data available for ${currentYear}`);
      return;
    }

    // Sort counties by risk level (highest first) for organized layout
    const sortedData = currentYearData.sort((a, b) => {
      // Primary sort by risk level (descending)
      if (b.risk !== a.risk) return b.risk - a.risk;
      // Secondary sort by occurrence count (descending) 
      if (b.occurrenceCount !== a.occurrenceCount) return b.occurrenceCount - a.occurrenceCount;
      // Tertiary sort by county name (alphabetical) for consistency
      return a.county.localeCompare(b.county);
    });

    // Create a grid layout for counties
    const countiesPerRow = Math.ceil(Math.sqrt(sortedData.length));
    const countiesPerCol = Math.ceil(sortedData.length / countiesPerRow);
    const countySize = Math.min(width / countiesPerRow, height / countiesPerCol);

    // Position counties in an organized grid (highest risk in top-left)
    const positionedCounties = sortedData.map((county, index) => ({
      ...county,
      x: (index % countiesPerRow) * countySize,
      y: Math.floor(index / countiesPerRow) * countySize,
      width: countySize * 0.9,
      height: countySize * 0.9
    }));

    const colorScale = d3.scaleSequential()
      .domain([0, 100])
      .interpolator(d3.interpolateViridis);

    // Define comprehensive patterns for colorblind accessibility
    const defs = svg.append('defs');

    // Pattern definitions
    defs.append('pattern')
      .attr('id', 'highRisk')
      .attr('patternUnits', 'userSpaceOnUse')
      .attr('width', 8)
      .attr('height', 8)
      .append('path')
      .attr('d', 'M0,0 l8,8')
      .attr('stroke', '#000')
      .attr('stroke-width', 3)
      .attr('opacity', 0.4);

    defs.append('pattern')
      .attr('id', 'mediumHighRisk')
      .attr('patternUnits', 'userSpaceOnUse')
      .attr('width', 6)
      .attr('height', 12)
      .append('path')
      .attr('d', 'M3,0 L3,12')
      .attr('stroke', '#000')
      .attr('stroke-width', 3)
      .attr('opacity', 0.35);

    defs.append('pattern')
      .attr('id', 'mediumRisk')
      .attr('patternUnits', 'userSpaceOnUse')
      .attr('width', 12)
      .attr('height', 6)
      .append('path')
      .attr('d', 'M0,3 L12,3')
      .attr('stroke', '#000')
      .attr('stroke-width', 3)
      .attr('opacity', 0.3);

    const dotsPattern = defs.append('pattern')
      .attr('id', 'lowMediumRisk')
      .attr('patternUnits', 'userSpaceOnUse')
      .attr('width', 10)
      .attr('height', 10);
    
    dotsPattern.append('circle')
      .attr('cx', 5)
      .attr('cy', 5)
      .attr('r', 1.5)
      .attr('fill', '#000')
      .attr('opacity', 0.25);

    const crossHatch = defs.append('pattern')
      .attr('id', 'veryHighRisk')
      .attr('patternUnits', 'userSpaceOnUse')
      .attr('width', 10)
      .attr('height', 10);
    
    crossHatch.append('path')
      .attr('d', 'M0,0 l10,10 M0,10 L10,0')
      .attr('stroke', '#000')
      .attr('stroke-width', 3)
      .attr('opacity', 0.45);

    const lowRiskPattern = defs.append('pattern')
      .attr('id', 'lowRisk')
      .attr('patternUnits', 'userSpaceOnUse')
      .attr('width', 12)
      .attr('height', 12);
    
    lowRiskPattern.append('path')
      .attr('d', 'M0,6 L12,6 M6,0 L6,12')
      .attr('stroke', 'grey')
      .attr('stroke-width', 3)
      .attr('opacity', 0.3);

    // Function to determine pattern based on risk level with updated thresholds
    const getPattern = (risk) => {
      if (risk >= 95) return 'url(#veryHighRisk)';
      if (risk >= 85) return 'url(#highRisk)';
      if (risk >= 65) return 'url(#mediumHighRisk)';
      if (risk >= 40) return 'url(#mediumRisk)';
      if (risk >= 20) return 'url(#lowMediumRisk)';
      return 'url(#lowRisk)';
    };

    // Function to get risk level description with better distribution
    const getRiskDescription = (risk) => {
      if (risk >= 95) return 'Extreme';
      if (risk >= 85) return 'Very High';
      if (risk >= 65) return 'High';
      if (risk >= 40) return 'Medium-High';
      if (risk >= 20) return 'Medium';
      return 'Low';
    };

    const counties = svg.selectAll('.county')
      .data(positionedCounties)
      .enter()
      .append('rect')
      .attr('class', styles.county)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('width', d => d.width)
      .attr('height', d => d.height)
      .attr('rx', 4)
      .attr('ry', 4)
      .style('stroke', '#fff')
      .style('stroke-width', 1)
      .style('fill', d => colorScale(d.risk))
      .style('fill-opacity', 1);

    const tooltip = d3.select(tooltipRef.current);

    // Add pattern overlays
    setTimeout(() => {
      counties.each(function(d) {
        const pattern = getPattern(d.risk);
        svg.append('rect')
          .attr('class', 'pattern-overlay')
          .attr('x', d.x)
          .attr('y', d.y)
          .attr('width', d.width)
          .attr('height', d.height)
          .attr('rx', 4)
          .attr('ry', 4)
          .style('fill', pattern)
          .style('stroke', '#fff')
          .style('stroke-width', 1)
          .style('pointer-events', 'none')
          .style('opacity', 0)
          .transition()
          .duration(200)
          .style('opacity', 1);
      });
    }, 100);

    // Add mouse interactions with enhanced tooltip
    counties
      .on('mouseover', function (event, d) {
        let tooltipContent = `
          <div class="${styles.tooltipTitle}">${d.county}, ${d.state}</div>
          <div class="${styles.tooltipRow}">
            <span>FIPS:</span>
            <span class="${styles.tooltipValue}">${d.fips}</span>
          </div>
          <div class="${styles.tooltipRow}">
            <span>Year:</span>
            <span class="${styles.tooltipValue}">${d.year}</span>
          </div>
          <div class="${styles.tooltipRow}">
            <span>Event Occurrences:</span>
            <span class="${styles.tooltipValue}">${d.occurrenceCount}</span>
          </div>
          <div class="${styles.tooltipRow}">
            <span>Risk Level:</span>
            <span class="${styles.tooltipValue}">${getRiskDescription(d.risk)}</span>
          </div>
          <div class="${styles.tooltipRow}">
            <span>Risk Score:</span>
            <span class="${styles.tooltipValue}">${Math.round(d.risk)}/100</span>
          </div>
        `;

        // Add magnitude information based on selected peril
        if (selectedPeril === 'HAIL') {
          if (d.avgHailMagnitude != null) {
            tooltipContent += `
              <div class="${styles.tooltipRow}">
                <span>Avg Hail Magnitude:</span>
                <span class="${styles.tooltipValue}">${d.avgHailMagnitude.toFixed(2)}</span>
              </div>
            `;
          }
          
          if (d.maxHailMagnitude != null) {
            tooltipContent += `
              <div class="${styles.tooltipRow}">
                <span>Max Hail Magnitude:</span>
                <span class="${styles.tooltipValue}">${d.maxHailMagnitude.toFixed(2)}</span>
              </div>
            `;
          }
        } else if (selectedPeril === 'THUNDERSTORM') {
          if (d.avgTstmMagnitude != null) {
            tooltipContent += `
              <div class="${styles.tooltipRow}">
                <span>Avg Storm Magnitude:</span>
                <span class="${styles.tooltipValue}">${d.avgTstmMagnitude.toFixed(2)}</span>
              </div>
            `;
          }
          
          if (d.maxTstmMagnitude != null) {
            tooltipContent += `
              <div class="${styles.tooltipRow}">
                <span>Max Storm Magnitude:</span>
                <span class="${styles.tooltipValue}">${d.maxTstmMagnitude.toFixed(2)}</span>
              </div>
            `;
          }
        }

        tooltip
          .style('opacity', 1)
          .html(tooltipContent);

        d3.select(this)
          .style('stroke', 'black')
          .style('stroke-width', 3);
      })
      .on('mousemove', function (event) {
        const container = containerRef.current.getBoundingClientRect();
        const tooltipBox = tooltipRef.current.getBoundingClientRect();
        const offsetX = 15;
        const offsetY = -30;

        let left = event.clientX - container.left + offsetX;
        let top = event.clientY - container.top + offsetY;

        if (left + tooltipBox.width > container.width) {
          left = container.width - tooltipBox.width - 10;
        }
        if (top + tooltipBox.height > container.height) {
          top = container.height - tooltipBox.height - 10;
        }
        if (left < 0) left = 10;
        if (top < 0) top = 10;

        tooltip
          .style('left', `${left}px`)
          .style('top', `${top}px`);
      })
      .on('mouseleave', function () {
        tooltip.style('opacity', 0);
        d3.select(this)
          .style('stroke', '#fff')
          .style('stroke-width', 1);
      });

    // Add titles and labels
    svg.append('text')
      .attr('class', styles.title)
      .attr('x', width / 2)
      .attr('y', -40)
      .attr('text-anchor', 'middle')
      .text(`Texas County ${selectedPeril || 'Weather'} Event Occurrences`);

    svg.append('text')
      .attr('class', styles.subtitle)
      .attr('x', width / 2)
      .attr('y', -15)
      .attr('text-anchor', 'middle')
      .text('County-level weather event frequency visualization');

    svg.append('text')
      .attr('class', `year-label ${styles.yearIndicator}`)
      .attr('x', width / 2)
      .attr('y', height + 40)
      .attr('text-anchor', 'middle')
      .text(`Year: ${currentYear}`);

    // Add legend
    const legendHeight = 300;
    const legendWidth = 20;
    const legendMargin = 20;

    const legendSvg = svg.append('g')
      .attr('transform', `translate(${width + legendMargin}, ${height / 2 - legendHeight / 2})`);

    const legendScale = d3.scaleLinear()
      .domain(colorScale.domain())
      .range([legendHeight - 100, 0]);

    const legendAxis = d3.axisRight(legendScale)
      .ticks(5)
      .tickFormat(d => `${d}`);

    const legendGradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', 'legend-gradient')
      .attr('x1', '0%')
      .attr('y1', '100%')
      .attr('x2', '0%')
      .attr('y2', '0%');

    legendGradient.selectAll('stop')
      .data(d3.ticks(0, 1, 10))
      .enter()
      .append('stop')
      .attr('offset', d => `${d * 100}%`)
      .attr('stop-color', d => colorScale(d * 100));

    legendSvg.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight - 100)
      .style('fill', 'url(#legend-gradient)');

    legendSvg.append('g')
      .attr('transform', `translate(${legendWidth}, 0)`)
      .call(legendAxis);

    // Pattern legend with updated thresholds
    const patternLegend = [
      { pattern: 'veryHighRisk', label: 'Extreme (95+)', y: legendHeight - 95 },
      { pattern: 'highRisk', label: 'Very High (85-94)', y: legendHeight - 75 },
      { pattern: 'mediumHighRisk', label: 'High (65-84)', y: legendHeight - 55 },
      { pattern: 'mediumRisk', label: 'Med-High (40-64)', y: legendHeight - 35 },
      { pattern: 'lowMediumRisk', label: 'Medium (20-39)', y: legendHeight - 15 },
      { pattern: 'lowRisk', label: 'Low (0-19)', y: legendHeight + 5 }
    ];

    legendSvg.append('text')
      .attr('x', 0)
      .attr('y', legendHeight - 310)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .text('Event Frequency:');

    legendSvg.append('text')
      .attr('x', 0)
      .attr('y', legendHeight)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .text('Risk Patterns:');

    patternLegend.forEach(item => {
      legendSvg.append('rect')
        .attr('x', 0)
        .attr('y', item.y + 100)
        .attr('width', 12)
        .attr('height', 12)
        .style('fill', `url(#${item.pattern})`);

      legendSvg.append('text')
        .attr('x', 18)
        .attr('y', item.y + 110)
        .attr('font-size', '10px')
        .text(item.label);
    });

  }, [currentYear, countyData, loading, error, selectedPeril]);

  if (loading) {
    return (
      <div className={styles.heatmapContainer}>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          Loading county data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.heatmapContainer}>
        <div style={{ textAlign: 'center', padding: '50px', color: 'red' }}>
          Error loading data: {error}
          <br />
          <button onClick={fetchCountyData} style={{ marginTop: '10px' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.heatmapContainer} ref={containerRef}>
      <svg ref={svgRef}></svg>
      <div ref={tooltipRef} className={styles.tooltip}></div>
    </div>
  );
};

export default HeatmapChart;