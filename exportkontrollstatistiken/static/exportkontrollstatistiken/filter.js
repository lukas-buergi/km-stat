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
  this.urlParamNames = [ 'granularity', 'countries', 'types', 'year1', 'year2', 'sortBy', 'perPage', 'pageNumber' ];
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
      for (let index = 0; index < this.urlParamNames.length; ++index){
        url += '/' + this[this.urlParamNames[index]];
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
  this.getSerializableCopy = function(){
    let copy = {};
    copy.paramNames = this.paramNames;
    for (let index = 0; index < this.paramNames.length; ++index){
      copy[this.paramNames[index]] = this[this.paramNames[index]];
    }
    const types=['k', 'b', 'd'];
    for(let t=0; t<=2; t++){
      copy[types[t]] = this[types[t]];
    }
    return(copy);
  };
  this.getReadableSearchString = function(oldParam){
    return this.urlParamNames.reduce((search, urlParam) => {
      return oldParam[urlParam] !== this[urlParam]
        ? search + urlParam + '="' +this[urlParam] + '" '
        : search;
    }, '');
  };
}

function InputField(id, paramName, propertyName){
  // constructor ///////////////////////////////////////////////////////
  return({
    id : id,
    paramName : paramName,
    propertyName : propertyName
  });
}

function Filter(name, p){
  // method definitions ////////////////////////////////////////////////
  this.update = function(p){
    this.p = new Params(p);
    for(let i=0; i<this.InputFields.length; i++){
      const id = this.InputFields[i].id;
      const pa = this.InputFields[i].paramName;
      const pr = this.InputFields[i].propertyName;
      this.setInputField(id, pa, pr);
      if(pa == 'year1'){
        // TODO: Build drop down for year 1
        this.buildYearDropDown(id, pa);
      } else if(pa == 'year2'){
        // TODO: Build drop down for year 2
        this.buildYearDropDown(id, pa);
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
    _paq.push(['trackEvent', 'Filter', 'More Options']);
    d3.select('div.filter_constrainer').style('max-width', '100%');
    this.toggleExtendedFilter(true);
  };
  this.hideExtended = function(){
    _paq.push(['trackEvent', 'Filter', 'Less Options']);
    d3.select('div.filter_constrainer').style('max-width', '50rem');
    this.toggleExtendedFilter(false);
  };
  this.toggleExtendedFilter = function(extended){
    Array.prototype.forEach.call(document.getElementsByClassName("extended"), function(el) {
      el.style.display = extended ? 'flex' : 'none';
    });
    
    Array.prototype.forEach.call(document.getElementsByClassName("minimized"), function(el) {
      el.style.display = extended ? 'none' : 'flex';
    });
  }
  this.buildYearDropDown = function (id, pa){
    let years = []
    let year;
    let minYear = this.p.minYear;
    let maxYear = this.p.maxYear;
    if( pa == 'year1' ){
      maxYear = this.p.year2;
      year = this.p.year1;
    } else {
      minYear = this.p.year1;
      year = this.p.year2;
    }
    for(let j=minYear; j<=maxYear; j++){
      years.push(j);
    }
    const selector = d3.select(id);
    selector.selectAll("option").remove();
    selector.selectAll("option")
      .data(years)
      .enter()
        .append("option")
        .text(d => d)
        .attr("value", (d, i) => d)
        .attr("selected", d => {
          if(d == year){
            return(true);
          } else {
            return(undefined);
          }
        });
  };
  // constructor ///////////////////////////////////////////////////////
  
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

  for(let i=0; i<this.InputFields.length; i++){
    const id = this.InputFields[i].id;
    const pa = this.InputFields[i].paramName;
    const pr = this.InputFields[i].propertyName;
    // add listeners
    this.addInputListener(id, pa, pr);
    // Set up year drop down
    if(pa == 'year1' || pa == 'year2'){
      this.buildYearDropDown(id, pa);
    }
  }
}

function Controller(p, countriesURL){
  // methods ///////////////////////////////////////////////////////////
  this.updateWidgets = function(p, updateHistory=true){
    var oldParam = this.p;
    this.p = new Params(p);
    _paq.push(['trackSiteSearch', this.p.getReadableSearchString(oldParam), false, false]);
    
    if(updateHistory){
      //console.log("Saving previous state: " + this.p.getURL());
      history.pushState(this.p.getSerializableCopy(), "", this.p.getURL());
    }
    for(let i=0; i<this.widgetNames.length; i++){
      this.widgets[this.widgetNames[i]].update(new Params(p));
    }
  };
  this.handleBrowserHistoryMovement = (state) => {
    //console.log("Loading state: " + (new Params(state.state)).getURL());
    this.updateWidgets(state.state, false);
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
  this.widgets.map = new Worldmap(new Params(this.p), countriesURL, this.format, "money");
  this.widgetNames.push("map");
  this.widgets.table = new Table(new Params(this.p), this.format);
  this.widgetNames.push("table");

  history.replaceState(this.p.getSerializableCopy(), "", this.p.getURL());
  window.onpopstate = this.handleBrowserHistoryMovement;
}
