

import { getJSON } from "./api.js";

  document.getElementById("pageSelect").addEventListener("change", function(){
    const selectedPage=this.value;
    window.location.href=selectedPage;
  });

  //renderGraph() takes in arrays of data and draws a graph using plotly

  function renderGraph(labels, ph, turbidity_ntu, water_temperature_c, water_level_cm) {
    document.getElementById('trendPlaceholder').style.display = 'none';
    document.getElementById('trendWrap').style.display = 'block';

      const traces=[
        {
          name: 'pH',
          x: labels,
          y: ph,
          type: 'scatter',
          mode: 'lines',
          line: {color: '#185FA5', width: 2}
        },
        {
          name: 'Turbidity',
          x: labels,
          y: turbidity_ntu,
          type: 'scatter',
          mode: 'lines',
          line: {color: '#EF9F27', width: 2}
        },
        {
          name: 'Water temperature',
          x: labels,
          y: water_temperature_c,
          type: 'scatter',
          mode: 'lines',
          line: {color: '#1D9E75', width: 2},
          
        },
         {
          name: 'Water Level',
          x: labels,
          y: water_level_cm,
          type: 'scatter',
          mode: 'lines',
          line: {color: '#9B59B6', width: 2},
          yaxis: 'y2',
         },
      ];
        
        const layout ={
          margin: {t: 10, r: 10, b: 30, l: 30},
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          hovermode: "x unified",
          xaxis: {title: "Date"},
          yaxis: {title: "Value"},
          yaxis2: {
            title: "Water Level (cm)",
            overlaying: "y",
            side: "right",
            showgrid: false,
          }
        };
        Plotly.purge("trendGraph");
        Plotly.newPlot("trendGraph", traces, layout, {
          responsive: true,
          displaylogo: false,
        });
  }
    
//loadLiveData() sends 4 api calls to get timeseries data for each sensor, then obtain the last item(most recent)
//displays the readings on metric cards and calls renderGraph() so that it updates with new data
  let cachedSites = [];

  async function loadLiveData() {
    try {
      if (!cachedSites.length) {
        cachedSites = await getJSON('/sites');
      }
      const siteId = document.getElementById('siteSelect')?.value || cachedSites[0];
      const freq = document.getElementById('freqSelect')?.value || 'h';
      const today = new Date().toISOString().slice(0, 10);
      
      const [phData, turbidityData, temperatureData, levelData, latestData] = await Promise.all([
        getJSON(`/timeseries?site_code=${siteId}&metric=ph&freq=${freq}`),
        getJSON(`/timeseries?site_code=${siteId}&metric=turbidity_ntu&freq=${freq}`),
        getJSON(`/timeseries?site_code=${siteId}&metric=water_temperature_c&freq=${freq}`),
        getJSON(`/timeseries?site_code=${siteId}&metric=water_level_cm&freq=${freq}`),
        getJSON(`/latest?site_code=${siteId}`)
      ]);

      if (!phData.length || !turbidityData.length || !levelData.length || !temperatureData.length) {
        console.error('One or more sensors returned no data');
      return;
}

      const latestPh = phData[phData.length - 1];
      const latestTurbidity = turbidityData[turbidityData.length - 1];
      const latestLevel = levelData[levelData.length - 1];
      const latestTemperature = temperatureData[temperatureData.length - 1];

      document.getElementById('lastSample').textContent = latestData.recorded_at.replace('T', ' ');

      document.getElementById('siteCount').textContent = cachedSites.length;
      document.getElementById('val-ph').textContent = latestData?.ph?.toFixed(2);
      document.getElementById('val-turbidity').textContent = latestData?.turbidity_ntu?.toFixed(2);
      document.getElementById('val-temperature').textContent = latestData?.water_temperature_c?.toFixed(1);
      document.getElementById('val-waterlevel').textContent = latestData?.water_level_cm?.toFixed(1);

      document.getElementById('val-waterlevel').textContent = latestData?.water_level_cm?.toFixed(1);

      // Colour code metric values based on safe ranges
      function colourMetric(id, value, warnMin, warnMax, critMin, critMax) {
        const el = document.getElementById(id);
        if (!el || value == null) return;
        if (value < critMin || value > critMax) {
          el.style.color = '#e74c3c';
        } else if (value < warnMin || value > warnMax) {
          el.style.color = '#e67e22';
        } else {
          el.style.color = '#27ae60';
        }
      }

      colourMetric('val-ph', latestData?.ph, 6.5, 8.5, 6.0, 9.0);
      colourMetric('val-turbidity', latestData?.turbidity_ntu, 0, 4.0, 0, 10.0);
      colourMetric('val-temperature', latestData?.water_temperature_c, 0, 30, 0, 38);
      colourMetric('val-waterlevel', latestData?.water_level_cm, 0, 150, 0, 500);

      renderGraph(
        phData.map(p => p.recorded_at),
        phData.map(p => p.avg),
        turbidityData.map(p => p.avg),
        temperatureData.map(p => p.avg),
        levelData.map(p => p.avg)
      );

    } catch (error) {
      console.error('Error loading live data:', error);
      document.getElementById('trendPlaceholder').textContent = 'Failed to load data, retrying...';
      document.getElementById('trendPlaceholder').style.display = 'flex';
      document.getElementById('trendWrap').style.display = 'none';
    }
  }

loadLiveData();
setInterval(loadLiveData, 5000);
window.loadLiveData = loadLiveData;