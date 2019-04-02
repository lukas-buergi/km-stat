d3.csv('api/g/i/DE/kbd/1900/2100/v/5/1').then(function (data) {
  matrix=[]
  for(var value in data){
    matrix.push(d3.values(data[value]))
  }
  var table = d3.select("body").append("table")
  var thead = table.append("thead")
  var tbody = table.append("tbody")
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
