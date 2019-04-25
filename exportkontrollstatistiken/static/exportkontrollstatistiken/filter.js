// TODO: Complete this into a page controller?
filter = {
  initialize : function(p){
    // TODO: learn to code javascript
    p.recalculateURL = function(){
      this.url = '/api/g';
      for (var index = 0; index < this.paramNames.length; ++index){
        this.url += '/' + this.params[this.paramNames[index]];
      }
    };
    p.getCopy = function(){
      copy = {};
      copy.params = JSON.parse(JSON.stringify(this.params));
      copy.url = JSON.parse(JSON.stringify(this.url));
      copy.paramNames = this.paramNames;
      copy.recalculateURL = this.recalculateURL;
      copy.getCopy = this.getCopy;
      return(copy);
    }
    this.locale = d3.formatLocale({"decimal": ".",
      "thousands": "\'",
      "grouping": [3],
      "currency": ['Fr. ', '']});
    this.format = this.locale.format('$,');

    worldmap.initialize(p.getCopy(), '/static/exportkontrollstatistiken/world_countries.json', this.format);
    table.initialize(p.getCopy());
  },
}
