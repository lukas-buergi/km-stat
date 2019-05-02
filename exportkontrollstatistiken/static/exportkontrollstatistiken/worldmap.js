worldmap = {
  initialize : function (params, countriesSource, numberFormat){
    // TODO: Maybe make configurable which columns contain which data
    this.params = this.treatParams(params);
    
    this.countriesSource = countriesSource;
    this.numberFormat = numberFormat;

    // number data we display so we can always display the latest in case it is switched in transit
    this.dataCounter = 0;
    
    const graticuleFeature = {
        "type": "Feature",
        "geometry": d3.geoGraticule10(),
        "id" : "reticules",
    };
    const outline = {type: "Sphere"};
    const mapDecoration = {"type":"FeatureCollection","features": [graticuleFeature, outline]};
    const projection = d3.geoRobinson().fitWidth('1000', mapDecoration); // TODO: Why 1000?
    this.path = d3.geoPath().projection(projection);
    const bounds = this.path.bounds(mapDecoration);

    // draw empty svg
    this.map = d3.select('div.worldmap')
      .style("padding-bottom", bounds[1][1] / bounds[1][0] * 100 + "%")
      .append('svg')
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 " + bounds[1][0] + " " + bounds[1][1])
        .classed("worldmap_svg", true)
        .append('g')
          .attr('class', 'map');

    // draw grid onto map
    this.graticule = this.map
      .append('g')
      .attr('class', 'worldmap_reticules')
      .selectAll('path')
      .data(mapDecoration.features)
      .enter()
        .append('path')
        .attr('d', this.path)
        .style('stroke-width', '1px')
        .style('stroke', 'white')
        .style('fill-opacity', 0);

    // draw countries, then add data
    this.worldmap = d3.json(this.countriesSource)
      .then(countries => {
        this.countries = countries;
        this.drawCountries();
        d3.select('div.worldmap_loadingMessage').remove();
      });
    this.setRemoteData();
  },
  treatParams : function(params){
    // map is not paginated
    params.perPage = 300;
    params.pageNumber = 1;
    // ... and needs sums per country
    params.granularity = 's';
    return(params);
  },
  update : function(params){
    treated = this.treatParams(params);
    if(!this.params.isEqualTo(treated)){
      this.params = treated;
      this.setRemoteData();
    }
  },
  setRemoteData : function(){
    this.dataCounter++;
    d3.json(this.params.getAPIURL())
      .then(data => {
        this.setData(this.dataCounter, data);
      });
    // TODO: Display some data change/loading indicator
  },
  setData : function(number, data) {
    if(this.dataCounter>number){
      // some other data was requested in the mean time, so this
      // data set is discarded
      return;
    }
    // the following is executed once the worldmap is loaded, or
    // immediately if it already was loaded
    this.worldmap.then( () => {
      const color = d3.scaleLog()
        .domain([10e4,10e8]) /* TODO: Choose good values. If I'm crazy, use the fancy algorithm that originally came with the map */
        .range(['#ffffff', '#FF0000']);

      
      data['data'].forEach(d => {
        d[2] = Number(d[2]);
      })

      const dataByID = {};
      data['data'].forEach(d => {
          dataByID[d[0]] = {"color":d[2], "name":d[1]};
      });
      
      
      // color map and add mouseovers
      dataCountriesMap = this.blankCountriesMap
          .style('fill', d => this.countryColor(d, dataByID, color))
          .on('mouseover', (d, i, nodes) => this.mouseOverCountry(d, i, nodes, dataByID, this.numberFormat))
          .on('mouseout', (d, i, nodes) => this.mouseOutCountry(d, i, nodes, dataByID, color));
          
      /* can change map data later: */
      //map.style('fill', d => 'black');
    });
  },
  mouseOverCountry : function(d, i, nodes, dataByID){
    if(d.id in dataByID){
      d3.select('#worldmap_country').text(dataByID[d.id]['name']);
      d3.select('#worldmap_exports').text(this.numberFormat(dataByID[d.id]['color']));
      d3.select('div.worldmap').on( "mousemove", this.movePopup );
      d3.select('div.worldmap_popup').style('visibility', 'visible');
      d3.select(nodes[i]).style('fill', '#AAAAAA');
    }
  },
  movePopup : function(){
    // TODO: Don't leave the window
    const popupAboveMouse = 15;
    d3.select('div.worldmap_popup')
      // two elaborate ways to calculate mouse position and popup position and that's the best I could find
      .style('top', (d3.mouse(document.querySelector('div.worldmap'))[1] - document.querySelector('div.worldmap_popup').offsetHeight - popupAboveMouse) + "px")
      .style('left', (d3.event.clientX - document.querySelector('div.worldmap_popup').offsetWidth/2) + "px");
  },
  mouseOutCountry : function(d, i, nodes, dataByID, color){
    if(d.id in dataByID){
      d3.select('div.worldmap_popup').style('visibility', 'hidden');
      d3.select(nodes[i]).style('fill', color(dataByID[d.id]['color']));
    }
  },
  countryColor : function(d, dataByID, color){
    if (d.id in dataByID) {
      return color(dataByID[d.id]['color']);
    } else if(d.id == 'CH'){
      return 'red';
    } else {
      return 'white';
    }
  },
  drawCountries : function(){
    // draw white map
    this.blankCountriesMap = this.map
      .append('g')
      .attr('class', 'countries')
      .selectAll('path')
      .data(this.countries.features)
      .enter()
        .append('path')
        .attr('d', this.path)
        .style('stroke-width', '1px')
        .style('stroke', '#EEEEFF')
        .style('fill', 'white');
  },
};

