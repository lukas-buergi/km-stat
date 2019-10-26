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

function Table(params, format){
  // methods ///////////////////////////////////////////////////////////
  this.update = function(params){
    if(!this.params.isEqualTo(params)){
      this.params = params;
      this.setRemoteData();
    }
  };
  this.setRemoteData = function(){
    this.dataCounter++;
    d3.json(this.params.getAPIURL()).then(
      (number =>
        (data => this.setData(number, data))
      )
      (this.dataCounter)
    );
    loading("table");
  };
  this.setData = function(number, data) {
    if(this.dataCounter>number){
      // some other data was requested in the mean time, so this
      // data set is discarded
      return;
    }
  
    this.numberOfPages = Math.ceil(data.total / this.params.perPage);

    // drop down
    let pageList = [];
    for(var page=1; page<=this.numberOfPages; page++){
      pageList.push(page);
    }
    d3.selectAll('#table_jumpToPage option').remove();
    const pageDropDown=d3.select('#table_jumpToPage');
    pageDropDown
      .selectAll('option')
      .data(pageList)
      .enter()
      .append('option')
        .text(d => "Gehe zu Seite " + d)
        .attr('value', d=>d)
        .attr('selected', d => {
          if(d==this.params.pageNumber){
            return true;
          }else{
            return null;
          }
        });
    pageDropDown.on('change', () => {
      this.params.pageNumber = Number(pageDropDown.property("value"));
      //console.log("drop down activated, returned " + this.params.pageNumber);
      this.setRemoteData();
    });

    // deactivate some buttons
    let onFirstPage = this.params.pageNumber == 1;
    if(!onFirstPage){onFirstPage=null;}
    let onLastPage = this.params.pageNumber == this.numberOfPages;
    if(!onLastPage){onLastPage=null;}
    // deactivate the two back buttons
    d3.select('#table_firstPage').attr('disabled', onFirstPage);
    d3.select('#table_previousPage').attr('disabled', onFirstPage);
    // deactivate the two forward buttons
    d3.select('#table_lastPage').attr('disabled', onLastPage);
    d3.select('#table_nextPage').attr('disabled', onLastPage);

    // if we have lots of columns, table should be full width
    // I mean, there could also be just a few wide columns, but I'm
    // ignoring that.
    if(data.ctypes.length < 5){
      this.table.style('max-width', '50rem');
      this.tableNav.style('max-width', '50rem');
    } else {
      this.table.style('max-width', '100%');
      this.tableNav.style('max-width', '100%');
    }
    
    // treat the data
    // format monetary amounts
    data.ctypes.forEach(function (type, typeIndex) {
      if(type == "money"){
        data.data.forEach(function (row, rowIndex){
          data.data[rowIndex][typeIndex] = this.format(data.data[rowIndex][typeIndex]);
        }, this);
      }
    }, this);
    
    // TODO: replace country codes with flag pictures

    notLoading("table");

    // Display data. The following snippet was copied from the d3 doc on .data()
    this.thead
      .selectAll("tr")
      .data([data['cnames']])
      .join("tr")
      .selectAll("td")
      .data(d => d)
      .join("td")
        .text(d => d);
    // TODO: Array rows are somehow mixed. The order is not random, but seems like multiple correctly sorted parts interleaved. Columns stay correct.
    // TODO: This started working correctly again. Find out why.
    this.tbody
      .selectAll("tr")
      .data(data['data'])
      .join("tr")
      .selectAll("td")
      .data(d => d)
      .join("td")
        .text(d => d);

    // Right-align monetary amounts. Remove manual right-align in css file.
    data.ctypes.forEach(function (type, typeIndex) {
      if(type == "money"){
        this.table
          .selectAll("td:nth-child(" + (typeIndex + 1) + ")")
          .style('text-align', 'right');
          //.style('background-color', '#ff0000');
      } else {
        this.table
          .selectAll("td:nth-child(" + (typeIndex + 1) + ")")
          .style('text-align', 'left');
          //.style('background-color', '#00ff00');
      }
    }, this);
  },
  this.firstPage = function(){
    this.params.pageNumber = 1;
    this.setRemoteData();
  };
  this.previousPage = function(){
    this.params.pageNumber = Math.max(1, this.params.pageNumber-1);
    this.setRemoteData();
  };
  this.nextPage = function(){
    //console.log("next page activated, previous page was " + this.params.pageNumber);
    //console.log("next page could be " + this.numberOfPages + " or " + (this.params.pageNumber+1) );
    this.params.pageNumber = Math.min(this.numberOfPages, this.params.pageNumber+1);
    this.setRemoteData();
  };
  this.lastPage = function(){
    this.params.pageNumber = this.numberOfPages;
    this.setRemoteData();
  };
  // constructor ///////////////////////////////////////////////////////
  this.dataCounter = 0;
  this.params = params;
  this.format = format;
  
  this.table = d3.select('table.table_content');
  this.tableNav = d3.select('div.table_pageNavigation');
  this.thead = this.table.select("thead");
  this.tbody = this.table.select("tbody");

  this.setRemoteData();
}
