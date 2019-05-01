// TODO: Complete this into a page controller?
filter = {
  initialize : function(p, countriesURL){
    // TODO: learn to code javascript
    p.getURL = function(){
      this.assembleTypes();
      url = '';
      for (var index = 0; index < this.paramNames.length; ++index){
        url += '/' + this[this.paramNames[index]];
      }
      return(url);
    };
    p.getAPIURL = function(){
      return('/api/g' + this.getURL());
    };
    p.assembleTypes = function(){
      types = ""
      if(this.k == true) types+='k';
      if(this.b == true) types+='b';
      if(this.d == true) types+='d';
      if( (!this.k) && (!this.b) && (!this.d) ){
        types = 'none';
      }
      this.types=types;
    }
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
      types=['k', 'b', 'd'];
      for(var t=0; t<=2; t++){
        curEqual = this[types[t]] == p[types[t]];
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

    worldmap.initialize(this.p.getCopy(), countriesURL, this.format);
    table.initialize(this.p.getCopy(), this.format);

    d3.select('#filter_perPage').on('change', (d, i, nodes) => {
      this.p.perPage = d3.select(nodes[i]).property("value");
      this.updateWidgets();
    });
    d3.select('#table_granularity').on('change', (d, i, nodes) => {
      this.p.granularity = d3.select(nodes[i]).property("value");
      this.updateWidgets();
    });

    d3.select('#table_beginn').on('change', (d, i, nodes) => {
      // TODO: change min/max
      this.p.year1 = d3.select(nodes[i]).property("value");
      this.updateWidgets();
    });

    d3.select('#table_ende').on('change', (d, i, nodes) => {
      // TODO: change min/max
      this.p.year2 = d3.select(nodes[i]).property("value");
      this.updateWidgets();
    });

    // TODO: Register country selection listener
    d3.select('#filter_laender').on('change', (d, i, nodes) => {
      this.p.countries = d3.select(nodes[i]).property("value");
      this.updateWidgets();
    });
  
    types=['k', 'b', 'd'];
    for(var t=0; t<=2; t++){
      d3.select('#table_' + types[t]).on('change', (d, i, nodes) => {
        type = d3.select(nodes[i]).attr('id').slice(-1);
        this.p[type] = d3.select(nodes[i]).property("checked");
        this.updateWidgets();
      });
    }
  },
  updateWidgets : function(){
    table.update(this.p.getCopy());
    worldmap.update(this.p.getCopy());
  },
}
