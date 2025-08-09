import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import styles from '../../../styles/Dashboard/Detailed/PastVsAi.module.css'

const PastVsAi = () => {
  const svgRef = useRef();
  
  useEffect(() => {
    // Clear any existing SVG content
    d3.select(svgRef.current).selectAll("*").remove();
    
    // Data
    const data = [
      { month: 'April', past: 35, ai: 40 },
      { month: 'May', past: 70, ai: 60 },
      { month: 'June', past: 50, ai: 55 },
      { month: 'July', past: 90, ai: 80 },
      { month: 'August', past: 65, ai: 70 }
    ];

    // Dimensions
    const margin = { top: 40, right: 30, bottom: 50, left: 50 };
    const width = 600 - margin.left - margin.right;
    const height = 600 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', -margin.top / 2)
      .attr('text-anchor', 'middle')
      .attr('class', 'font-bold text-lg')
      .text('Past Data vs AI Predictions')
      .attr('fill', 'black');

    // X scale
    const x = d3.scaleBand()
      .domain(data.map(d => d.month))
      .range([0, width])
      .padding(0.1);

    // Y scale
    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => Math.max(d.past, d.ai)) * 1.1])
      .range([height, 0]);

    // X axis
    const xAxis = svg.append('g')
  .attr('transform', `translate(0,${height})`)
  .call(d3.axisBottom(x));

xAxis.selectAll('.tick text')
  .style('fill', 'black');

const yAxis = svg.append('g')
  .call(d3.axisLeft(y));

yAxis.selectAll('.tick text')
  .style('fill', 'black');

    // X axis label
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', height + margin.bottom - 10)
      .attr('text-anchor', 'middle')
      .attr('class', 'text-sm font-medium')
      .text('Date');

    // Y axis label
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -margin.left + 15)
      .attr('x', -height / 2)
      .attr('text-anchor', 'middle')
      .attr('class', 'text-sm font-medium')
      .text('Values');

    // Past data area
    const pastArea = d3.area()
      .x(d => x(d.month) + x.bandwidth() / 2)
      .y0(height)
      .y1(d => y(d.past))
      .curve(d3.curveMonotoneX);

    // AI prediction area
    const aiArea = d3.area()
      .x(d => x(d.month) + x.bandwidth() / 2)
      .y0(height)
      .y1(d => y(d.ai))
      .curve(d3.curveMonotoneX);

    // Past data line
    const pastLine = d3.line()
      .x(d => x(d.month) + x.bandwidth() / 2)
      .y(d => y(d.past))
      .curve(d3.curveMonotoneX);

    // AI prediction line
    const aiLine = d3.line()
      .x(d => x(d.month) + x.bandwidth() / 2)
      .y(d => y(d.ai))
      .curve(d3.curveMonotoneX);

    // Add past area
    svg.append('path')
      .datum(data)
      .attr('fill', 'rgba(255,99,132,0.2)')
      .attr('d', pastArea);

    // Add AI area
    svg.append('path')
      .datum(data)
      .attr('fill', 'rgba(54,162,235,0.2)')
      .attr('d', aiArea);

    // Add past line
    svg.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', 'rgba(255,99,132,1)')
      .attr('stroke-width', 2)
      .attr('d', pastLine);

    // Add AI line
    svg.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', 'rgba(54,162,235,1)')
      .attr('stroke-width', 2)
      .attr('d', aiLine);

    // Add data points for past
    svg.selectAll('.past-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'past-dot')
      .attr('cx', d => x(d.month) + x.bandwidth() / 2)
      .attr('cy', d => y(d.past))
      .attr('r', 5)
      .attr('fill', 'rgba(255,99,132,1)')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 7);
        
        // Tooltip
        svg.append('text')
          .attr('class', 'tooltip')
          .attr('x', x(d.month) + x.bandwidth() / 2)
          .attr('y', y(d.past) - 15)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .text(`Past: ${d.past}`);
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 5);
        svg.selectAll('.tooltip').remove();
      });

    // Add data points for AI
    svg.selectAll('.ai-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'ai-dot')
      .attr('cx', d => x(d.month) + x.bandwidth() / 2)
      .attr('cy', d => y(d.ai))
      .attr('r', 5)
      .attr('fill', 'rgba(54,162,235,1)')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 7);
        
        // Tooltip
        svg.append('text')
          .attr('class', 'tooltip')
          .attr('x', x(d.month) + x.bandwidth() / 2)
          .attr('y', y(d.ai) - 15)
          .attr('text-anchor', 'middle')
          .attr('font-size', '12px')
          .text(`AI: ${d.ai}`);
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 5);
        svg.selectAll('.tooltip').remove();
      });

    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 100}, 0)`);

    // Past data legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', 'rgba(255,99,132,0.2)')
      .attr('stroke', 'rgba(255,99,132,1)')
      .attr('stroke-width', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .attr('class', 'text-xs')
      .text('Past Data');

    // AI prediction legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 25)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', 'rgba(54,162,235,0.2)')
      .attr('stroke', 'rgba(54,162,235,1)')
      .attr('stroke-width', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 37)
      .attr('class', 'text-xs')
      .text('AI Predictions');
  }, []);

  return (
    <div className={styles.PastVsAiContainer}>
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default PastVsAi;