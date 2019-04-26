// TODO: Complete this into a page controller?
filter = {
  initialize : function(p){
    // TODO: learn to code javascript
    p.getURL = function(){
      url = '';
      for (var index = 0; index < this.paramNames.length; ++index){
        url += '/' + this[this.paramNames[index]];
      }
      return(url);
    };
    p.getAPIURL = function(){
      return('/api/g' + this.getURL());
    };
    p.getCopy = function(){
      // shawllow copy
      copy = {};
      for(var i in this){
        copy[i] = this[i];
      }
      return(copy);
    };
    p.isEqualTo = function(p){
      equal = true;
      for (var index = 0; index < this.paramNames.length; ++index){
        curEqual = this[this.paramNames[index]] == p[this.paramNames[index]];
        equal = equal && curEqual;
      }
      return(equal);
    };
    this.p = p;
    
    this.locale = d3.formatLocale({"decimal": ".",
      "thousands": "\'",
      "grouping": [3],
      "currency": ['Fr. ', '']});
    this.format = this.locale.format('$,');

    worldmap.initialize(this.p.getCopy(), '/static/exportkontrollstatistiken/world_countries.json', this.format);
    table.initialize(this.p.getCopy(), this.format);

    // TODO: Register listeners
    d3.select('#filter_perPage').on('change', (d, i, nodes) => {
      this.p.perPage = d3.select(nodes[i]).property("value");
      this.updateWidgets();
    });
    d3.select('#table_granularity').on('change', (d, i, nodes) => {
      this.p.granularity = d3.select(nodes[i]).property("value");
      this.updateWidgets();
    });
  },
  updateWidgets : function(){
    table.update(this.p.getCopy());
    worldmap.update(this.p.getCopy());
  },
}
