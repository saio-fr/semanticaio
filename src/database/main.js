var _ = require('underscore');
var when = require('when');
var Db = require('@saio/db-component');
var Wsocket = require('@saio/wsocket-component');
var netConfig = require('config/network.json');

var DataBaseService = function(container, options) {
  var dbConfig = {
    dialect: 'postgres',
    user: undefined,
    password: undefined,
    host: 'saio-sp-db',
    port: 5432,
    dbname: undefined,
    model: './question.js'
  };
  var wsConfig = {
    url: 'ws://saio-sp-crossbar',
    realm: 'saio-sp'
  };
  this.db = container.use('db', Db, dbConfig);
  this.ws = container.use('ws', Ws, wsConfig);

  this.state = 'new'; // 'new' | 'started' | 'stopped'
};

DataBaseService.prototype.start = function() {

};

DataBaseService.prototype.stop = function() {
  this.state = 'stopped';
  return this.ws.unregister();
};

DataBaseService.prototype.get = function(args, kwargs) {

};

DataBaseService.prototype.add = function(args, kwargs) {

};

DataBaseService.prototype.update = function(args, kwargs) {

};

DataBaseService.prototype.remove = function(args, kwargs) {

};

// custom select query
DataBaseService.prototype.select = function(args, kwargs) {

};



module.exports = DataBaseService;
