function worldmap(src, colorVariable, geoIDVariable, numberFormat){
  // Set tooltips
  const tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(d => `<strong>Country: </strong><span class='details'>${d['name']}<br></span><strong>${colorVariable}: </strong><span class='details'>${numberFormat(d[colorVariable])}</span>`);

    // both of those stupid tables should be replaced with some simple logic making the damn box follow the mouse pointer and avoid the borders of the map
  tip.direction(function(d) {
    if (d.id === 'AQ') return 'n';
    // Americas
    if (d.id === 'GL') return 's';
    if (d.id === 'CA') return 'e';
    if (d.id === 'US') return 'e';
    if (d.id === 'MX') return 'e';
    // Europe
    if (d.id === 'IS') return 's';
    if (d.id === 'NO') return 's';
    if (d.id === 'SE') return 's';
    if (d.id === 'FI') return 's';
    if (d.id === 'RU') return 'w';
    // Asia
    if (d.id === 'CN') return 'w';
    if (d.id === 'JP') return 's';
    // Oceania
    if (d.id === 'ID') return 'w';
    if (d.id === 'PG') return 'w';
    if (d.id === 'AU') return 'w';
    if (d.id === 'NZ') return 'w';
    // otherwise if not specified
    return 'n';
  })

  // TODO: I suspect this is broken and the offset should be in map coordinates
  tip.offset(function(d) { // [top, left]
    if (d.id === 'AQ') return [0, 0];
    // Americas
    if (d.id === 'GL') return [10, -10];
    if (d.id === 'CA') return [24, -28];
    if (d.id === 'US') return [-5, 8];
    if (d.id === 'MX') return [12, 10];
    if (d.id === 'CL') return [0, -15];
    // Europe
    if (d.id === 'IS') return [15, 0];
    if (d.id === 'NO') return [10, -28];
    if (d.id === 'SE') return [10, -8];
    if (d.id === 'FI') return [10, 0];
    if (d.id === 'FR') return [-9, 66];
    if (d.id === 'IT') return [-8, -6];
    if (d.id === 'RU') return [5, 500];
    // Africa
    if (d.id === 'MG') return [-10, 10];
    // Asia
    if (d.id === 'CN') return [-16, -8];
    if (d.id === 'MN') return [-5, 0];
    if (d.id === 'PK') return [-10, 13];
    if (d.id === 'IN') return [-11, -18];
    if (d.id === 'NP') return [-8, 1];
    if (d.id === 'MM') return [-12, 0];
    if (d.id === 'LA') return [-12, -8];
    if (d.id === 'VN') return [-12, -4];
    if (d.id === 'JP') return [5, 5];
    // Oceania
    if (d.id === 'ID') return [0, -5];
    if (d.id === 'PG') return [-5, -10];
    if (d.id === 'AU') return [-15, 0];
    if (d.id === 'NZ') return [-15, 0];
    // otherwise if not specified
    return [-10, 0];
  })

  const color = d3.scaleLog()
    .domain([10e4,10e8]) /* TODO: Choose good values. If I'm crazy, use the fancy algorithm that originally came with the map */
    .range(['#ffffff', '#FF0000']);

  const svg = d3.select('div.worldmap')
    .append('svg')
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 1000 500") // magic values
    .classed("worldmap-svg", true)
    .append('g')
    .attr('class', 'map');

  const projection = d3.geoRobinson()

  const path = d3.geoPath().projection(projection);

  svg.call(tip);

  Promise.all([
    d3.json('/static/exportkontrollstatistiken/world_countries.json'), /* TODO BROKEN */
    d3.csv(src),
  ]).then(([geography, data]) => ready(geography, data, colorVariable, geoIDVariable, svg, path, color, tip));
}

function mouseOverCountry(d, i, nodes, dataByID, tip){
  if(d.id in dataByID){
    tip.show(d);
    d3.select(nodes[i]).style('fill', 'black')
  }
}

function mouseOutCountry(d, i, nodes, dataByID, color, tip){
  if(d.id in dataByID){
        tip.hide(d);
        d3.select(nodes[i]).style('fill', color(dataByID[d.id]['color']))
  }
}

function countryColor(d, dataByID, color){
  if (d.id in dataByID) {
    return color(dataByID[d.id]['color'])
  } else {
    return 'white'
  }
}

function ready(geography, data, colorVariable, geoIDVariable, svg, path, color, tip) {
  data.forEach(d => {
    d[colorVariable] = Number(d[colorVariable].replace(',', ''));
  })

  const dataByID = {};
  data.forEach(d => {
      dataByID[d[geoIDVariable]] = {"color":d[colorVariable], "name":d['name']};
  });

  geography.features.forEach(d => {
      if(d.id in dataByID){
          d[colorVariable] = dataByID[d.id]['color']
          d['name'] = dataByID[d.id]['name']
      }
  });

  svg.append('g')
    .attr('class', 'countries')
    .selectAll('path')
    .data(geography.features)
    .enter().append('path')
      .attr('d', path)
      .style('fill', d => countryColor(d, dataByID, color))
      .style('stroke-width', 0)
      .on('mouseover', (d, i, nodes) => mouseOverCountry(d, i, nodes, dataByID, tip))
      .on('mouseout', (d, i, nodes) => mouseOutCountry(d, i, nodes, dataByID, color, tip));
  
  d3.select('div.loadingMessage').remove()
}
