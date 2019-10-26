/*
Copyright Lukas Bürgi 2019.

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

function Params(p){
  // constructor ///////////////////////////////////////////////////////
  // Takes either json as returned by Python view or another js Params object
  this.paramNames = p.paramNames;
  for (let index = 0; index < p.paramNames.length; ++index){
    const name = p.paramNames[index];
    const attr = p[name];
    this[name] = attr;
  }
  const types=['k', 'b', 'd'];
  for(let t = 0; t < types.length; t++){
    this[types[t]] = p[types[t]];
  }
  // methods ///////////////////////////////////////////////////////////
  this.getURL = function(){
      this.assembleTypes();
      let url = '';
      for (let index = 0; index < this.paramNames.length; ++index){
        url += '/' + this[this.paramNames[index]];
      }
      return(url);
  };
  this.getAPIURL = function(){
      return('/api/g' + this.getURL());
  };
  this.assembleTypes = function(){
    let types = ""
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
      for(let i in this){
        copy[i] = this[i];
      }
      return(copy);
  };
  this.isEqualTo = function(p){
      let equal = true;
      for (let index = 0; index < this.paramNames.length; ++index){
        const curEqual = this[this.paramNames[index]] == p[this.paramNames[index]];
        equal = equal && curEqual;
      }
      const types=['k', 'b', 'd'];
      for(let t=0; t<=2; t++){
        const curEqual = this[types[t]] == p[types[t]];
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
    for(let i=0; i<this.InputFields.length; i++){
      const id = this.InputFields[i].id;
      const pa = this.InputFields[i].paramName;
      const pr = this.InputFields[i].propertyName;
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
  this.showExtended = function(){
    {
      const list = document.getElementsByClassName("extended");
      for (let i = 0; i < list.length; i++) {
        list[i].style.display = 'flex';
      }
    }
    {
      const list = document.getElementsByClassName("minimized");
      for (let i = 0; i < list.length; i++) {
        list[i].style.display = 'none';
      }
    }
  };
  this.hideExtended = function(){
    {
      const list = document.getElementsByClassName("extended");
      for (let i = 0; i < list.length; i++) {
        list[i].style.display = 'none';
      }
    }
    {
      const list = document.getElementsByClassName("minimized");
      for (let i = 0; i < list.length; i++) {
        list[i].style.display = 'flex';
      }
    }
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
  const types=['k', 'b', 'd'];
  for(let t=0; t<=2; t++){
    this.InputFields.push(
      new InputField('#' + this.name + '_filter_' + types[t],  types[t],        'checked'),
    );
  }

  // add listeners
  for(let i=0; i<this.InputFields.length; i++){
    const id = this.InputFields[i].id;
    const pa = this.InputFields[i].paramName;
    const pr = this.InputFields[i].propertyName;
    this.addInputListener(id, pa, pr);
  }
}

function Controller(p, countriesURL){
  // methods ///////////////////////////////////////////////////////////
  this.updateWidgets = function(p){
    this.p = new Params(p);
    for(let i=0; i<this.widgetNames.length; i++){
      this.widgets[this.widgetNames[i]].update(new Params(p));
    }
  };

  // constructor ///////////////////////////////////////////////////////
  this.p = new Params(p);
  
  this.locale = d3.formatLocale({"decimal": ".",
    "thousands": "\'",
    "grouping": [3],
    "currency": ['Fr. ', '']});
  this.format = this.locale.format('$,');

  this.widgets = {};
  this.widgetNames = [];

  // remember the names in the template needs to match
  this.widgets.filter = new Filter("filter", this.p);
  this.widgetNames.push("filter");
  this.widgets.map = new Worldmap(new Params(this.p), countriesURL, this.format);
  this.widgetNames.push("map");
  this.widgets.table = new Table(new Params(this.p), this.format);
  this.widgetNames.push("table");
}
