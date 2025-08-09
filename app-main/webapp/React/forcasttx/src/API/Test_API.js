const BASE_URL = "https://forecasttx.duckdns.org";

export async function getServerMessage() {
  try {
    const res = await fetch(`${BASE_URL}/` );
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error fetching server message:", error);
    throw error;
  }
}

export async function getKpiSummary(year, perilType = 'HAIL') {
  try {
    const res = await fetch(`${BASE_URL}/api/kpi-summary?year=${year}&peril_type=${perilType}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error fetching KPI summary:", error);
    throw error;
  }
}

export async function getDetailedKpi(year, perilType = 'HAIL') {
  try {
    // Note: You don't have this endpoint in main.py - you might need to add it
    const res = await fetch(`${BASE_URL}/api/detailed-kpi?year=${year}&peril_type=${perilType}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error fetching detailed KPI:", error);
    throw error;
  }
}

export async function getTop3Counties(year, perilType = 'HAIL') {
  try {
    console.log("🚀 Fetching top 3 counties for", year, perilType);
    const res = await fetch(`${BASE_URL}/api/top3-counties?year=${year}&peril_type=${perilType}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error fetching Top 3 Counties:", error);
    throw error;
  }
}

// New county occurrences API functions
export async function getCountyOccurrences(year = null, county = null, topN = null, minEvents = null) {
  try {
    console.log("🏘️ Fetching county occurrences with filters:", { year, county, topN, minEvents });
    
    const params = new URLSearchParams();
    if (year !== null) params.append('year', year);
    if (county !== null) params.append('county', county);
    if (topN !== null) params.append('top_n', topN);
    if (minEvents !== null) params.append('min_events', minEvents);
    
    const queryString = params.toString();
    const url = `${BASE_URL}/api/county-occurrences${queryString ? `?${queryString}` : ''}`;
    
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error fetching county occurrences:", error);
    throw error;
  }
}

export async function getTopCountiesAllTime(topN = 10) {
  try {
    console.log("🏆 Fetching top counties all time, limit:", topN);
    const res = await fetch(`${BASE_URL}/api/top-counties-alltime?top_n=${topN}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error fetching top counties all time:", error);
    throw error;
  }
}

export async function getYearlySummary(year = null) {
  try {
    console.log("📈 Fetching yearly summary for:", year || 'all years');
    
    const url = year !== null
      ? `${BASE_URL}/api/yearly-summary?year=${year}`
      : `${BASE_URL}/api/yearly-summary`;
    
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (error) {
    console.error("Error fetching yearly summary:", error);
    throw error;
  }
}