
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
          line: {color: '#9B59B6', width: 2}
         },
      ];
        
        const layout ={
          margin: {t: 10, r: 10, b: 30, l: 30},
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          hovermode: "x unified",
          xaxis: {title: "Date"},
          yaxis: {title: "Value"},
        };
        Plotly.react("trendGraph", traces, layout, { //used ai here to help the problem of having to destroy the graph every time
          responsive: true,
          displaylogo: false,
        });
  }
    
//loadLiveData() sends 4 api calls to get timeseries data for each sensor, then obtain the last item(most recent)
//displays the readings on metric cards and calls renderGraph() so that it updates with new data
  async function loadLiveData() {
    try {
      const siteId="all";
    //ai was used for promise.all so that all metrics appear at the same time
      const [phData, turbidityData, levelData, temperatureData] = await Promise.all([ 
        getJSON(`/timeseries?site_code=${siteId}&metric=ph&freq=D`),
        getJSON(`/timeseries?site_code=${siteId}&metric=turbidity_ntu&freq=D`),
        getJSON(`/timeseries?site_code=${siteId}&metric=water_level_cm&freq=D`),
        getJSON(`/timeseries?site_code=${siteId}&metric=water_temperature_c&freq=D`),
      ]);
      if (!phData.length || !turbidityData.length || !levelData.length || !temperatureData.length) {
        console.error('One or more sensors returned no data');
      return;
}

      const latestPh = phData[phData.length - 1];
      const latestLevel = levelData[levelData.length - 1];
      const latestTurbidity = turbidityData[turbidityData.length - 1];
      const latestTemperature = temperatureData[temperatureData.length - 1];

      document.getElementById('lastSample').textContent = latestPh.recorded_at;
      document.getElementById('val-ph').textContent = latestPh?.ph;
      document.getElementById('val-waterlevel').textContent = latestLevel.water_level_cm;
      document.getElementById('val-turbidity').textContent = latestTurbidity.turbidity_ntu;
      document.getElementById('val-temperature').textContent = latestTemperature.water_temperature_c;

      renderGraph(
        phData.map(p => p.recorded_at),
        phData.map(p => p.ph),
        turbidityData.map(p => p.turbidity_ntu),
        temperatureData.map(p => p.water_temperature_c),
        levelData.map(p => p.water_level_cm)
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