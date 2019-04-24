function worldmap(src, colorVariable, geoIDVariable, numberFormat){
  const reticuleFeature = {
      "type": "Feature",
      "geometry": d3.geoGraticule10(),
      "id" : "reticules",
  };
  const outline = {type: "Sphere"};
  const reticuleFeaturesCollection = {"type":"FeatureCollection","features": [reticuleFeature, outline]};
  const projection = d3.geoRobinson().fitWidth('1000', reticuleFeaturesCollection);
  const path = d3.geoPath().projection(projection);
  const bounds = path.bounds(reticuleFeaturesCollection);

  map = d3.select('div.worldmap')
    .style("padding-bottom", bounds[1][1] / bounds[1][0] * 100 + "%")
    .append('svg')
      .attr("preserveAspectRatio", "xMinYMin meet")
      .attr("viewBox", "0 0 " + bounds[1][0] + " " + bounds[1][1])
      .classed("worldmap_svg", true)
      .append('g')
        .attr('class', 'map');

  graticules = map
    .append('g')
    .attr('class', 'worldmap_reticules')
    .selectAll('path')
    .data(reticuleFeaturesCollection.features)
    .enter()
      .append('path')
      .attr('d', path)
      .style('stroke-width', '1px')
      .style('stroke', 'white')
      .style('fill-opacity', 0);
      
  Promise.all([
    d3.json('/static/exportkontrollstatistiken/world_countries.json'), /* TODO BROKEN (well, not really, but it will be if the path changes) */
    d3.json(src),
  ]).then(([geography, data]) => ready(geography, data, colorVariable, geoIDVariable, numberFormat, path, map));
}

function mouseOverCountry(d, i, nodes, dataByID, numberFormat){
  if(d.id in dataByID){
    d3.select('#worldmap_country').text(d['name']);
    d3.select('#worldmap_exports').text(numberFormat(d['color']));
    d3.select('div.worldmap').on( "mousemove", movePopup );
    d3.select('div.worldmap_popup').style('visibility', 'visible');
    d3.select(nodes[i]).style('fill', '#AAAAAA');
  }
}

function movePopup(){
  // TODO: Don't leave the window
  const popupAboveMouse = 15;
  d3.select('div.worldmap_popup')
    // two elaborate ways to calculate mouse position and popup position and that's the best I could find
    .style('top', (d3.mouse(document.querySelector('div.worldmap'))[1] - document.querySelector('div.worldmap_popup').offsetHeight - popupAboveMouse) + "px")
    .style('left', (d3.event.clientX - document.querySelector('div.worldmap_popup').offsetWidth/2) + "px");
}

function mouseOutCountry(d, i, nodes, dataByID, color){
  if(d.id in dataByID){
    d3.select('div.worldmap_popup').style('visibility', 'hidden');
    d3.select(nodes[i]).style('fill', color(dataByID[d.id]['color']));
  }
}

function countryColor(d, dataByID, color){
  if (d.id in dataByID) {
    return color(dataByID[d.id]['color']);
  } else {
    return 'white';
  }
}

function ready(geography, data, colorVariable, geoIDVariable, numberFormat, path, map) {
  const color = d3.scaleLog()
    .domain([10e4,10e8]) /* TODO: Choose good values. If I'm crazy, use the fancy algorithm that originally came with the map */
    .range(['#ffffff', '#FF0000']);

  
  // TODO: colorVariable, geoIDVariable ignored
  data['data'].forEach(d => {
    d[2] = Number(d[2]);
  })

  const dataByID = {};
  data['data'].forEach(d => {
      dataByID[d[0]] = {"color":d[2], "name":d[1]};
  });

  // combine map and numeric data - bad design TODO
  geography.features.forEach(d => {
      if(d.id in dataByID){
          d['color'] = dataByID[d.id]['color']
          d['name'] = dataByID[d.id]['name']
      }
  });

  
  // draw white map
  blankCountriesMap = map
    .append('g')
    .attr('class', 'countries')
    .selectAll('path')
    .data(geography.features)
    .enter()
      .append('path')
      .attr('d', path)
      .style('stroke-width', 0)
      .style('fill', 'white');
  // color map and add mouseovers
  dataCountriesMap = blankCountriesMap
      .style('fill', d => countryColor(d, dataByID, color))
      .on('mouseover', (d, i, nodes) => mouseOverCountry(d, i, nodes, dataByID, numberFormat))
      .on('mouseout', (d, i, nodes) => mouseOutCountry(d, i, nodes, dataByID, color));
      
  /* can change map data later: */
  //map.style('fill', d => 'black');

  d3.select('div.worldmap_loadingMessage').remove()
}
