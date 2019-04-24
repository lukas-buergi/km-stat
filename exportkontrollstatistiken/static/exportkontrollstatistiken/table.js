function table(src){
  d3.json(src).then(drawTable);
}

function drawTable(data) {
  var table = d3.select('div.table table');
  var thead = table.select("thead");
  var tbody = table.select("tbody");
  
  /*
   * This snippet was copied from the d3 doc on .data()
   * I don't understand it whatsoever.
   * */
  
  thead
    .selectAll("tr")
    .data([data['cnames']])
    .join("tr")
    .selectAll("td")
    .data(d => d)
    .join("td")
      .text(d => d);
  // TODO: Array rows are somehow mixed. The order is not random, but seems like multiple correctly sorted parts interleaved. Columns stay correct.
  // console.log(data['data'])
  tbody
    .selectAll("tr")
    .data(data['data'])
    .join("tr")
    .selectAll("td")
    .data(d => d)
    .join("td")
      .text(d => d);
}
