import { getJSON } from "./api.js";
    //function for the page selector
    document.getElementById("pageSelect").addEventListener("change", function(){
      const selectedPage=this.value;
      window.location.href=selectedPage;
      });
      //returns a list of values from the checked sensors
    function getSelectedSensors(){
      const checkboxes = document.querySelectorAll(".sensor-checkbox input:checked");
      return Array.from(checkboxes).map(cb => cb.value);
    }
    
      
    const sensors= {
      ph:{
        label: "pH",
        api:"ph",
        color: "#185FA5",

      },
      turbidity:{
        label:"turbidity",
        api: "turbidity_ntu",
        color: "#EF9F27",
        
      },
      
      level:{
        label:"water level",
        api: "water_level_cm",
        color:"#9B59B6",
        
      },
      conductivity:{
          label: "Conductivity",
          api: "conductivity_us_cm",
          color: "#6bff15" 
        },
        temperature:{
          label: "Water temperature",
          api: "water_temperature_c",
          color:"#1D9E75"
        },
      wxTemp: { 
          label: "Air Temp",
          api: "wx_temp_c",
          color: "#ff0000" 
        },
      wxRh: { 
        label: "Humidity",
        api: "wx_rh_pct",
        color: "#35fafa" 
      },
      wxRain: { 
        label: "Rain",
        api: "wx_rain_mm_hr",
        color: "#f31bc4" 
      },
      light: { 
        label: "Light",
        api: "light_lux",
        color: "#edf10f" 
      }
      
    };
    document.getElementById("siteSelector").addEventListener("change", e => {
      loadGraph(e.target.value);
    });

    document.getElementById("graphType").addEventListener("change", () => {
      const site = document.getElementById("siteSelector").value;
      loadGraph(site);
    });

    document.getElementById("dateFrom").addEventListener("change", () =>{
      const site = document.getElementById("siteSelector").value;
      loadGraph(site);
    });

    document.getElementById("dateTo").addEventListener("change", () =>{
      const site = document.getElementById("siteSelector").value;
      loadGraph(site);
    });

    document.querySelectorAll(".sensor-checkbox input").forEach(cb => {
      cb.addEventListener("change", () => {
        const site = document.getElementById("siteSelector").value;
        loadGraph(site);
      });
    });
    
    /*calls getSelectedSensors to get metrics for selected sensors,
    then builds graph with selected graph and date range and sends one api call per sensor.
    if no data is available/ checked it will display this
    */
    async function loadGraph(siteId) {
      try{
      const active = getSelectedSensors();
      if (active.length===0){
        document.getElementById("trendWrap").style.display = "none";
        document.getElementById("trendPlaceholder").style.display= "flex";
        return;
      }
      document.getElementById("trendWrap").style.display="block";
      document.getElementById("trendPlaceholder").style.display= "none";
      const graphType= document.getElementById("graphType").value;

      const typeMap = {
        line:{type:"scatter", mode: "lines" },
        scatter:{ type: "scatter", mode: "markers"},
        bar:{ type: "bar", mode: undefined}
      };
      const {type, mode}= typeMap[graphType];
      const dateFrom = document.getElementById("dateFrom").value;
      const dateTo = document.getElementById("dateTo").value;

      const results = await Promise.all(active.map(id=>{
        const metric= sensors[id].api;
        const parametres= new URLSearchParams({
          site_code: siteId,
          metric: metric,
          freq: "D",
          ...(dateFrom &&{start:dateFrom}),
          ...(dateTo &&{end: dateTo})
        });
        return getJSON(`/timeseries?${parametres}`)
          .then(data =>{
            if (!Array.isArray(data)) {
              console.error("BAD RESPONSE for", id, data); // used ai for help with console error detection 
              return { id, data: [] };
            }
            return{id, data};
          
          });
        }));
        const hasData = results.some(({data}) => data.length > 0);
        if (!hasData) {
          document.getElementById('trendPlaceholder').textContent = 'No data available for this selection';
          document.getElementById('trendPlaceholder').style.display = 'flex';
          document.getElementById('trendWrap').style.display = 'none';
          return;
}
    
      const traces= results.map(({id, data})=>{
        const s =sensors[id];
        return {
          name: s.label,
         x: data.map(p => p.recorded_at|| p.timestamp),
         y: data.map(p => p[s.api]),
          type,
          mode,
          line: { color: s.color, width: 2 },//used ai for these next couple of lines
          marker:{color: s.color, width: 2},
          hovertemplate: `<b>${s.label}</b>: %{y}<extra></extra>`
        };
      });
  

    const layout ={
      margin: { t: 20, r: 10, b: 40, l: 40 },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      hovermode: "x unified",
      xaxis: { title: "Date",
      ...(dateFrom && dateTo &&{range:[dateFrom, dateTo]}), //used ai for this line to fix a bug with the date filter
      },
      yaxis: { title: "Value" }
    };
    console.log("TRACES:", traces);
    Plotly.react("advancedGraph", traces, layout, {
    responsive: true,
    displaylogo: false,
    });
  }catch(error){
    console.error('Failed to load graph:', error);
    document.getElementById('trendPlaceholder').textContent = 'Failed to load data';
    document.getElementById('trendPlaceholder').style.display = 'flex';
    document.getElementById('trendWrap').style.display = 'none';
  }
}

  
  
/*fetches the available sites and puts them in the dropdown-
 maps them to readable names and calls load graph with the first site*/
async function loadSites() {
  try{
    const sites   = await getJSON(`/sites`);
    const select = document.getElementById("siteSelector");
    const siteNames={
      "site_upstream": "Site upstream",
      "site_downstream": "Site downstream",
      "site_reservoir": "Site reservoir"
    };
    if (!sites.length){
      console.error("no sites found");
      return;
    }

    sites.forEach(id => {
      const opt= document.createElement("option");
      opt.value= id;
      opt.textContent= siteNames[id];
      select.appendChild(opt);
    });
    loadGraph(sites[0]);
  }catch(error){
    console.error("failed to load sites");
    document.getElementById("trendPlaceholder").textContent="Failed to load sites";
  }
     
}
  
window.addEventListener("DOMContentLoaded",loadSites);