import React, { useState } from 'react';
import styles from './../../../styles/Dashboard/Detailed/KPI.module.css';
import {  Download } from 'lucide-react';

const KPI = ({ 
  title, 
  value, 
  description, 
  onHover, 
  onLeave, 
  onExport, 
  isHovered, 
  className = '' 
}) => {
  const [showExportMenu, setShowExportMenu] = useState(false);

  const handleMouseEnter = () => {
    if (onHover) onHover();
  };

  const handleMouseLeave = () => {
    if (onLeave) onLeave();
    setShowExportMenu(false);
  };

  const handleExportClick = (e) => {
    e.stopPropagation();
    setShowExportMenu(!showExportMenu);
  };

  const handleExportOption = (format) => {
    if (onExport) onExport(format);
    setShowExportMenu(false);
  };

  return (
    <div 
      className={`${styles.kpi} ${isHovered ? styles.hovered : ''} ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Menu Icon Container */}
      <div className={styles.menuIcon}>
        {/* Info Icon */}
        
        
        {/* Export Button */}
        <button 
          className={styles.exportButton}
          onClick={handleExportClick}
          title="Export KPI"
        >
          <Download size={20} />
        </button>
        
        {/* Export Menu */}
        {showExportMenu && (
          <div className={styles.exportMenu}>
            <button 
              className={styles.exportOption}
              onClick={() => handleExportOption('pdf')}
            >
              Export as PDF
            </button>
            <button 
              className={styles.exportOption}
              onClick={() => handleExportOption('word')}
            >
              Export as Word
            </button>
          </div>
        )}
      </div>

      <p className={styles.value}>{value}</p>
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.description}>{description}</p>
    </div>
  );
};

export default KPI;