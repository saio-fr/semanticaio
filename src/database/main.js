var _ = require('underscore');
var when = require('when');
var Db = require('@saio/db-component');
var Wsocket = require('@saio/wsocket-component');

var Database = function(container, options) {
  this.db = container.use('db', Db, {
    dialect: 'postgres',
    user: 'postgres',
    password: 'password',
    host: 'postgres',
    port: 5432,
    dbname: 'postgres',
    model: './question.js'
  });
  this.ws = container.use('ws', Wsocket, {
    url: 'ws://crossbar:8080',
    realm: 'semanticaio'
  });
  this.Question = this.db.model.Question;
};

Database.prototype.start = function() {
  var pendingRegisters = [
    this.ws.register('semanticaio.db.get', this.get.bind(this)),
    this.ws.register('semanticaio.db.all.get', this.getAll.bind(this)),
    this.ws.register('semanticaio.db.batch.get', this.getBatch.bind(this)),
    this.ws.register('semanticaio.db.set', this.set.bind(this))
  ];
  return when.all(pendingRegisters);
};

Database.prototype.stop = function() {
  return this.ws.unregister();
};

Database.prototype.get = function(args, kwargs) {
  return this.Question.findById(kwargs.id)
  .then(function(question) {
    return question.get({ plain: true });
  });
};

Database.prototype.getAll = function(args, kwargs) {
  var constraints;
  if (kwargs.matchableOnly) {
    constraints = { where: { matchable: true } };
  } else if (kwargs.correctOnly) {
    constraints = { where: { correctFormId : null } };
  }
  return this.Question.findAll(constraints)
  .then(function(questions) {
    return _.map(questions, function(question) {
      return question.get({ plain: true });
    });
  });
};

Database.prototype.getBatch = function(args, kwargs) {
  var constraints = {};
  if (kwargs.matchableOnly) {
    constraints.where = { matchable: true };
  } else if (kwargs.correctOnly) {
    constraints.where = { correctFormId : null };
  }
  constraints.order = { raw: 'random()' }; // not sure, need test
  constraints.limit = kwargs.size;
  return this.Question.findAll(constraints)
  .then(function(questions) {
    return _.map(questions, function(question) {
      return question.get({ plain: true });
    });
  });
};

Database.prototype.set = function(args, kwargs) {
  return this.Question.findById(kwargs.id)
  .then(function(question) {
    return question.update(_.omit(kwargs, 'id'));
  });
};

module.exports = Database;
