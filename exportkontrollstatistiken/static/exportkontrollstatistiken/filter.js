function Params(p){
  // Takes either json as returned by Python view or another js Params object
  this.paramNames = p.paramNames;
  for (var index = 0; index < p.paramNames.length; ++index){
    name = p.paramNames[index];
    attr = p[name];
    this[name] = attr;
  }
  types=['k', 'b', 'd'];
  for(var t = 0; t < types.length; t++){
    this[types[t]] = p[types[t]];
  }

  this.getURL = function(){
      this.assembleTypes();
      url = '';
      for (var index = 0; index < this.paramNames.length; ++index){
        url += '/' + this[this.paramNames[index]];
      }
      return(url);
  };
  this.getAPIURL = function(){
      return('/api/g' + this.getURL());
  };
  this.assembleTypes = function(){
      types = ""
      if(this.k == true) types+='k';
      if(this.b == true) types+='b';
      if(this.d == true) types+='d';
      if( (!this.k) && (!this.b) && (!this.d) ){
        types = 'none';
      }
      this.types=types;
  };
  this.getCopy = function(){
      // shallow copy
      copy = {};
      for(var i in this){
        copy[i] = this[i];
      }
      return(copy);
  };
  this.isEqualTo = function(p){
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
}

function InputField(id, paramName, propertyName){
  return({
    id : id,
    paramName : paramName,
    propertyName : propertyName
  });
}

function Filter(name, p){
  // method definitions
  this.update = function(p){
    this.p = new Params(p);
    for(var i=0; i<this.InputFields.length; i++){
      id = this.InputFields[i].id;
      pa = this.InputFields[i].paramName;
      pr = this.InputFields[i].propertyName;
      this.setInputField(id, pa, pr);
      if(pa == 'year1'){
        d3.select(id).property('max', this.p['year2']);
      } else if(pa == 'year2'){
        d3.select(id).property('min', this.p['year1']);
      }
    }
    
  };
  this.updateWidgets = function(){
    controller.updateWidgets(this.p);
  };
  this.addInputListener = function(id, paramName, propertyName){
    d3.select(id).on('change', (d, i, nodes) => {
      this.p[paramName] = d3.select(nodes[i]).property(propertyName);
      this.updateWidgets();
    });
  };
  this.setInputField = function(id, paramName, propertyName){
    d3.select(id).property(propertyName, this.p[paramName]);
  };
  
  // constructor
  
  this.name = name;
  this.p = new Params(p);

  // define input fields belonging to this filter
  this.InputFields = [
    new InputField('#' + this.name + '_filter_perPage',       'perPage',        'value'),
    new InputField('#' + this.name + '_filter_granularity',   'granularity',    'value'),
    new InputField('#' + this.name + '_filter_laender',       'countries',      'value'),
    new InputField('#' + this.name + '_filter_beginn',        'year1',      'value'),
    new InputField('#' + this.name + '_filter_ende',          'year2',      'value'),
  ];
  types=['k', 'b', 'd'];
  for(var t=0; t<=2; t++){
    this.InputFields.push(
      new InputField('#' + this.name + '_filter_' + types[t],  types[t],        'checked'),
    );
  }

  // add listeners
  for(var i=0; i<this.InputFields.length; i++){
    id = this.InputFields[i].id;
    pa = this.InputFields[i].paramName;
    pr = this.InputFields[i].propertyName;
    this.addInputListener(id, pa, pr);
  }
}

function Controller(p, countriesURL){
  this.updateWidgets = function(p){
    this.p = new Params(p);
    table.update(new Params(p));
    worldmap.update(new Params(p));
    for(var i=0; i<this.widgets.length; i++){
      this.widgets[i].update(this.p);
    }
  };
  
  this.p = new Params(p);
  
  this.locale = d3.formatLocale({"decimal": ".",
    "thousands": "\'",
    "grouping": [3],
    "currency": ['Fr. ', '']});
  this.format = this.locale.format('$,');

  this.widgets = [];

  this.filter1 = new Filter("top", this.p);
  this.widgets.push(this.filter1);
  this.filter2 = new Filter("middle", this.p);
  this.widgets.push(this.filter2);
  worldmap.initialize(new Params(this.p), countriesURL, this.format);
  table.initialize(new Params(this.p), this.format);
}
