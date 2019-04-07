/*
 * d3.csv is asynchronous, .then waits for the result.
 * The data is passed to the unnamed function defined there,
 * I had problems trying to define it separately.
 * */
d3.csv('api/g/i/DE/kbd/1900/2100/v/5/1').then(function (data) {
  /*
   * Didn't find a way to get the data into the html directly,
   * first need to make it a matrix
   * */
  var matrix=[]
  for(var value in data){
    if(value!="columns"){
      matrix.push(d3.values(data[value]))
    }
  }
  var table = d3.select('div.table').append("table")
  var thead = table.append("thead")
  var tbody = table.append("tbody")

  /*
   * This snippet was copied from the d3 doc on .data()
   * I don't understand it whatsoever.
   * I think if data.colums and matrix are modified, it should
   * be possible to have it update the html more easily
   * */
  thead
    .selectAll("tr")
    .data([data.columns])
    .join("tr")
    .selectAll("td")
    .data(d => d)
    .join("td")
      .text(d => d);
  tbody
    .selectAll("tr")
    .data(matrix)
    .join("tr")
    .selectAll("td")
    .data(d => d)
    .join("td")
      .text(d => d);
});
