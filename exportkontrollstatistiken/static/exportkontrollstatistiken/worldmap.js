/*
Copyright Lukas Bürgi 2019. This file was originally based on another,
but the resemblance is so faint by now that I assume its mine.

This file is part of km-stat.

km-stat is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

km-stat is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public
License along with km-stat.  If not, see
<https://www.gnu.org/licenses/>.
 * */

'use strict';

function Worldmap(params, countriesSource, numberFormat, dataColumnType){
  // methods //////////////////////////////////////////////////////////
  this.treatParams = function(params){
    // map is not paginated
    params.perPage = 300;
    params.pageNumber = 1;
    // ... and needs sums per country
    params.granularity = 's';
    // ... and sorted by value
    params.sortBy = 'v';
    return(params);
  };
  this.update = function(params){
    const treated = this.treatParams(params);
    if(!this.params.isEqualTo(treated)){
      this.params = treated;
      this.setRemoteData();
    }
  };
  this.setRemoteData = function(){
    loading("worldmap");
    this.dataCounter++;
    d3.json(this.params.getAPIURL()).then(
      (number =>
        (data => this.setData(number, data))
      )
      (this.dataCounter)
    );
  };
  this.setData = function(number, data) {
    if(this.dataCounter>number){
      // some other data was requested in the mean time, so this
      // data set is discarded
      return;
    }
    // the following is executed once the worldmap is loaded, or
    // immediately if it already was loaded
    this.worldmap.then( () => {
      this.hidePopup(); // if this is not the first data set, a popup might be visible containing old data

      let indicesOfTypes = {}
      data['ctypes'].forEach((type, index) => {
        indicesOfTypes[type] = index;
      });
      const dColumn = indicesOfTypes[this.dataColumnType];
      const idColumn = indicesOfTypes['country code'];
      const nameColumn = indicesOfTypes['country name'];
      
      
      data['data'].forEach(d => {
        d[dColumn] = Number(d[dColumn]);
      })

      const dataByID = {};
      data['data'].forEach(d => {
          dataByID[d[idColumn]] = {"color":d[dColumn], "name":d[nameColumn]};
      });

      let domain = [];
      let colorRange = [];
      
      if(data['data'].length == 0){
        console.log("Empty dataset");
      } else if(data['data'].length == 1){
        colorRange = ['#ff0000'];
        domain = [0];
      } else {
        colorRange = [d3.rgb(255,255,255)];
        const amountOfPartitions = Math.min(30,data['data'].length);
        for(let i=0; i<amountOfPartitions-1; i++){
          const n = 255*(amountOfPartitions-i)/amountOfPartitions
          colorRange.push(d3.rgb(255, n, n));
        }
        colorRange.push(d3.rgb(255, 0, 0));
        
        let dataLog = [];
        data['data'].forEach(d => {
          if(d[dColumn]==0){
            dataLog.push(0);
          } else {
            dataLog.push(Math.log(d[dColumn]));
          }
        });

        // TODO: fix bug, why is 0 twice at the beginning?
        const domainLog = jenks(dataLog, amountOfPartitions - 1);
        
        domain = []
        domainLog.forEach(d => {
          if(d==0){
            domain.push(0);
          } else {
            domain.push(Math.exp(d));
          }
        });
        //console.log(domain);
      }
      
      const color = d3.scaleQuantile() //scaleLog()
        .domain(domain)
        .range(colorRange);
      
      
      // color map and add mouseovers
      let dataCountriesMap = this.blankCountriesMap
          .style('fill', d => this.countryColor(d, dataByID, color))
          .on('mouseover', (d, i, nodes) => this.mouseOverCountry(d, i, nodes, dataByID, this.numberFormat))
          .on('mouseout', (d, i, nodes) => this.mouseOutCountry(d, i, nodes, dataByID, color));

      notLoading("worldmap");
      /* can change map data later: */
      //map.style('fill', d => 'black');
    });
  };
  this.mouseOverCountry = function(d, i, nodes, dataByID){
    if(d.id in dataByID){
      d3.select('#worldmap_country').text(dataByID[d.id]['name']);
      d3.select('#worldmap_exports').text(this.numberFormat(dataByID[d.id]['color']));
      d3.select('div.worldmap').on( "mousemove", this.movePopup );
      d3.select('div.worldmap_popup').style('visibility', 'visible');
      d3.select(nodes[i]).style('fill', '#AAAAAA');
    }
  };
  this.movePopup = function(){
    const popupAboveMouse = 15;

    const selectionX = d3.event.clientX;
    const middleX = document.body.clientWidth / 2;
    const popWidth = document.querySelector('div.worldmap_popup').offsetWidth;
    let popX;
    if(selectionX < middleX-popWidth/2){
      popX = selectionX;
    } else if(selectionX <= middleX+popWidth/2){
      popX = selectionX - popWidth/2;
    } else {
      popX = selectionX - popWidth;
    }
    d3.select('div.worldmap_popup')
      // two elaborate ways to calculate mouse position and popup position and that's the best I could find
      .style('top', (d3.mouse(document.querySelector('div.worldmap'))[1] - document.querySelector('div.worldmap_popup').offsetHeight - popupAboveMouse) + "px")
      .style('left', popX + "px");
  };
  this.hidePopup = function(){
    d3.select('div.worldmap_popup').style('visibility', 'hidden');
  };
  this.mouseOutCountry = function(d, i, nodes, dataByID, color){
    if(d.id in dataByID){
      this.hidePopup();
      d3.select(nodes[i]).style('fill', color(dataByID[d.id]['color']));
    }
  };
  this.countryColor = function(d, dataByID, color){
    if (d.id in dataByID) {
      return color(dataByID[d.id]['color']);
    } else if(d.id == 'CH'){
      return 'red';
    } else {
      return 'white';
    }
  };
  this.drawCountries = function(){
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
  };
  // constructor //////////////////////////////////////////////////////
  // TODO: Maybe make configurable which columns contain which data
  this.params = this.treatParams(params);
  
  this.countriesSource = countriesSource;
  this.numberFormat = numberFormat;
  this.dataColumnType = dataColumnType;

  // number data we display so we can always display the latest in case it is switched in transit
  this.dataCounter = 0;
  
  const graticuleFeature = {
      "type": "Feature",
      "geometry": d3.geoGraticule10(),
      "id" : "reticules",
  };
  const outline = {type: "Sphere"};
  const mapDecoration = {"type":"FeatureCollection","features": [outline, graticuleFeature]};
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
      .style('fill', '#EEEEFF');
      //.style('fill-opacity', '1')
      //.attr('paint-order', 'stroke');

  // draw countries, then add data
  this.worldmap = d3.json(this.countriesSource)
    .then(countries => {
      this.countries = countries;
      this.drawCountries();
      d3.select('div.worldmap_loadingMessage').remove();
    });
  this.setRemoteData();
}
