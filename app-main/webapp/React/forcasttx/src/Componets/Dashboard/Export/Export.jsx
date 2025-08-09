import React, { useState } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import htmlDocx from "html-docx-js/dist/html-docx";

import OverviewCharts from "../Overview/OverviewCharts";
import KPIContainer from "../Detailed/KPIContainer";
import TopRegionsContainer from "../Detailed/TopRegionsContainer";
import PastVsAi from "../Overview/PastVsAi";
import TexasMap from "../Overview/TexasMap";

import dashboardStyles from "../../../styles/Dashboard/Dashboard.module.css";
import styles from "../../../styles/Dashboard/Export/Export.module.css";

const CHARTS = [
  { label: "Overview Charts", key: "overview" },
  { label: "KPIs", key: "kpis" },
  { label: "Top Regions", key: "regions" },
  { label: "Past Data vs AI (Chart.js)", key: "pastvsai" },
  { label: "Texas Map (Leaflet & Heatmap)", key: "texasmap" },
];

const RenderSections = ({ sectionKeys, selectedPeril, selectedYear }) => (
  <div style={{ background: "#fff", padding: 24, width: "100%", boxSizing: "border-box" }}>
    {sectionKeys.includes("overview") && (
      <div data-section="overview">
        <OverviewCharts selectedPeril={selectedPeril} selectedYear={selectedYear} />
      </div>
    )}
    {sectionKeys.includes("kpis") && (
      <div data-section="kpis">
        <KPIContainer selectedPeril={selectedPeril} selectedYear={selectedYear} />
      </div>
    )}
    {sectionKeys.includes("regions") && (
      <div data-section="regions">
        <TopRegionsContainer selectedPeril={selectedPeril} selectedYear={selectedYear} />
      </div>
    )}
    {sectionKeys.includes("pastvsai") && (
      <div data-section="pastvsai">
        <PastVsAi />
      </div>
    )}
    {sectionKeys.includes("texasmap") && (
      <div data-section="texasmap">
        <TexasMap />
      </div>
    )}
  </div>
);

const ChartPreview = ({ chartKey, selectedPeril, selectedYear }) => {
  switch (chartKey) {
    case "overview":
      return <OverviewCharts selectedPeril={selectedPeril} selectedYear={selectedYear} preview />;
    case "kpis":
      return <KPIContainer selectedPeril={selectedPeril} selectedYear={selectedYear} preview />;
    case "regions":
      return <TopRegionsContainer selectedPeril={selectedPeril} selectedYear={selectedYear} preview />;
    case "pastvsai":
      return <PastVsAi preview />;
    case "texasmap":
      return <TexasMap preview />;
    default:
      return null;
  }
};

export default function Export({ selectedPeril, selectedYear }) {
  const [selectedCharts, setSelectedCharts] = useState(CHARTS.map(ch => ch.key));
  const [filename, setFilename] = useState("charts_export");
  const [docType, setDocType] = useState("pdf");

  const EXPORT_WIDTH = 1100;

  const handleChartToggle = (chartKey) => {
    setSelectedCharts(current =>
      current.includes(chartKey)
        ? current.filter(k => k !== chartKey)
        : [...current, chartKey]
    );
  };

  // Replace canvas and svg with images before DOCX conversion
  const replaceCanvasesAndSvgsWithImages = (parentDiv) => {
    Array.from(parentDiv.querySelectorAll("canvas")).forEach((canvas) => {
      if (canvas.width === 0 || canvas.height === 0) return;
      const img = document.createElement("img");
      img.src = canvas.toDataURL("image/png");
      img.style.width = canvas.style.width || "100%";
      img.style.height = canvas.style.height || "auto";
      img.width = canvas.width;
      img.height = canvas.height;
      canvas.parentNode.replaceChild(img, canvas);
    });
    Array.from(parentDiv.querySelectorAll("svg")).forEach((svg) => {
      const serializer = new XMLSerializer();
      const svgStr = serializer.serializeToString(svg);
      const encoded = window.btoa(unescape(encodeURIComponent(svgStr)));
      const img = document.createElement("img");
      img.src = "data:image/svg+xml;base64," + encoded;
      img.style.width = svg.style.width || "100%";
      img.style.height = svg.style.height || "auto";
      svg.parentNode.replaceChild(img, svg);
    });
  };

  const handleExport = async () => {
    if (!selectedCharts.length) {
      alert("Select at least one chart to export.");
      return;
    }

    // For separating TexasMap into its own page:
    const KEY_TEXAS_MAP = "texasmap";
    const sectionKeysBeforeMap = [];
    let mapIncluded = false;
    for (let key of selectedCharts) {
      if (key === KEY_TEXAS_MAP) {
        mapIncluded = true;
        break;
      }
      sectionKeysBeforeMap.push(key);
    }
    const texasMapAlone = mapIncluded && selectedCharts.includes(KEY_TEXAS_MAP);

    // --- PDF EXPORT ---
    if (docType === "pdf") {
      const pdf = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });

      // 1. Export all charts except TexasMap (if any)
      if (sectionKeysBeforeMap.length > 0) {
        const exportDiv1 = document.createElement("div");
        exportDiv1.style.position = "fixed";
        exportDiv1.style.top = "-9999px";
        exportDiv1.style.left = "-9999px";
        exportDiv1.style.width = EXPORT_WIDTH + "px";
        exportDiv1.style.minWidth = EXPORT_WIDTH + "px";
        exportDiv1.style.maxWidth = EXPORT_WIDTH + "px";
        exportDiv1.style.background = "#fff";
        document.body.appendChild(exportDiv1);

        const { createRoot } = await import("react-dom/client");
        const root1 = createRoot(exportDiv1);
        root1.render(
          <RenderSections
            sectionKeys={sectionKeysBeforeMap}
            selectedPeril={selectedPeril}
            selectedYear={selectedYear}
          />
        );

        await new Promise((res) => setTimeout(res, 800));
        const canvas1 = await html2canvas(exportDiv1, {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          windowWidth: EXPORT_WIDTH,
          backgroundColor: "#fff"
        });

        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();
        const imgWidth = canvas1.width;
        const imgHeight = canvas1.height;
        const pageRatio = pdfWidth / imgWidth;
        const pageHeightInPx = pdfHeight / pageRatio;
        let renderedHeight = 0;
        let pageNum = 0;
        while (renderedHeight < imgHeight) {
          const pageCanvas = document.createElement("canvas");
          pageCanvas.width = imgWidth;
          pageCanvas.height = Math.min(pageHeightInPx, imgHeight - renderedHeight);
          const ctx = pageCanvas.getContext("2d");
          ctx.drawImage(
            canvas1,
            0,
            renderedHeight,
            imgWidth,
            pageCanvas.height,
            0,
            0,
            imgWidth,
            pageCanvas.height
          );
          const pageData = pageCanvas.toDataURL("image/png");
          if (pageNum > 0) pdf.addPage();
          pdf.addImage(
            pageData,
            "PNG",
            0,
            0,
            pdfWidth,
            pageCanvas.height * pageRatio
          );
          renderedHeight += pageHeightInPx;
          pageNum++;
        }
        root1.unmount();
        document.body.removeChild(exportDiv1);
      }

      // 2. Export TexasMap ONLY on a new page (if selected)
      if (texasMapAlone) {
        if (sectionKeysBeforeMap.length > 0) pdf.addPage();
        const exportDiv2 = document.createElement("div");
        exportDiv2.style.position = "fixed";
        exportDiv2.style.top = "-9999px";
        exportDiv2.style.left = "-9999px";
        exportDiv2.style.width = EXPORT_WIDTH + "px";
        exportDiv2.style.minWidth = EXPORT_WIDTH + "px";
        exportDiv2.style.maxWidth = EXPORT_WIDTH + "px";
        exportDiv2.style.background = "#fff";
        document.body.appendChild(exportDiv2);

        const { createRoot } = await import("react-dom/client");
        const root2 = createRoot(exportDiv2);
        root2.render(
          <RenderSections
            sectionKeys={["texasmap"]}
            selectedPeril={selectedPeril}
            selectedYear={selectedYear}
          />
        );
        await new Promise((res) => setTimeout(res, 900));
        const canvas2 = await html2canvas(exportDiv2, {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          windowWidth: EXPORT_WIDTH,
          backgroundColor: "#fff"
        });
        // --- FIX TEXAS MAP: aspect ratio, center, no stretch ---
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();
        const imgWidth = canvas2.width;
        const imgHeight = canvas2.height;
        // Scale to fit while maintaining aspect
        const widthRatio = pdfWidth / imgWidth;
        const heightRatio = pdfHeight / imgHeight;
        const scale = Math.min(widthRatio, heightRatio, 1); // Don't upscale
        const renderWidth = imgWidth * scale;
        const renderHeight = imgHeight * scale;
        const xOffset = (pdfWidth - renderWidth) / 2;
        const yOffset = (pdfHeight - renderHeight) / 2;
        pdf.addImage(
          canvas2.toDataURL("image/png"),
          "PNG",
          xOffset,
          yOffset,
          renderWidth,
          renderHeight
        );
        // --- END FIX ---
        root2.unmount();
        document.body.removeChild(exportDiv2);
      }

      pdf.save(`${filename || "export"}.pdf`);
      return;
    }

    // --- DOCX EXPORT (render all at once) ---
    const hiddenDiv = document.createElement("div");
    hiddenDiv.style.position = "fixed";
    hiddenDiv.style.top = "-9999px";
    hiddenDiv.style.left = "-9999px";
    hiddenDiv.style.width = EXPORT_WIDTH + "px";
    hiddenDiv.style.minWidth = EXPORT_WIDTH + "px";
    hiddenDiv.style.maxWidth = EXPORT_WIDTH + "px";
    hiddenDiv.style.background = "#fff";
    hiddenDiv.style.overflowX = "auto";
    hiddenDiv.style.zIndex = "999999";
    document.body.appendChild(hiddenDiv);

    const { createRoot } = await import("react-dom/client");
    const root = createRoot(hiddenDiv);
    root.render(
      <RenderSections
        sectionKeys={selectedCharts}
        selectedPeril={selectedPeril}
        selectedYear={selectedYear}
      />
    );
    setTimeout(async () => {
      replaceCanvasesAndSvgsWithImages(hiddenDiv);
      const htmlString = `
          <!DOCTYPE html>
          <html><head><meta charset="utf-8" /></head>
          <body>${hiddenDiv.innerHTML}</body></html>
        `;
      const blob = htmlDocx.asBlob(htmlString);
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${filename || "export"}.docx`;
      link.click();
      URL.revokeObjectURL(link.href);
      root.unmount();
      document.body.removeChild(hiddenDiv);
    }, 1200);
  };

  return (
    <div className={dashboardStyles.container}>
      <div className={styles.exportPageWrapper}>
        <div className={styles.exportLayout}>
          <div className={styles.selectorArea}>
            <h3>Select charts to export</h3>
            {CHARTS.map((chart) => (
              <label key={chart.key} className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={selectedCharts.includes(chart.key)}
                  onChange={() => handleChartToggle(chart.key)}
                />
                {chart.label}
                <div className={styles.chartPreviewThumb}>
                  <ChartPreview
                    chartKey={chart.key}
                    selectedPeril={selectedPeril}
                    selectedYear={selectedYear}
                  />
                </div>
              </label>
            ))}
          </div>
          <div className={styles.exportControlsCol}>
            <div className={styles.exportOptionsBox}>
              <div>
                <label className={styles.inputLabel}>
                  Filename:
                  <input
                    type="text"
                    value={filename}
                    onChange={e => setFilename(e.target.value)}
                    placeholder="Enter filename"
                    className={styles.input}
                  />
                </label>
              </div>
              <div className={styles.exportDocOptions}>
                <label
                  className={
                    styles.docOptionLabel +
                    (docType === "pdf" ? " " + styles.selected : "")
                  }
                >
                  <input
                    type="radio"
                    name="docType"
                    value="pdf"
                    checked={docType === "pdf"}
                    onChange={() => setDocType("pdf")}
                  />
                  PDF
                </label>
                <label
                  className={
                    styles.docOptionLabel +
                    (docType === "docx" ? " " + styles.selected : "")
                  }
                >
                  <input
                    type="radio"
                    name="docType"
                    value="docx"
                    checked={docType === "docx"}
                    onChange={() => setDocType("docx")}
                  />
                  Word (.docx)
                </label>
              </div>
              <button
                className={styles.exportButton}
                onClick={handleExport}
                disabled={!selectedCharts.length}
              >
                Export Document
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}