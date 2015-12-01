var when = require('when');
var Wsocket = require('@saio/wsocket-component');

var Test = function(container, options) {
  this.ws = container.use('ws', Wsocket, {
    url: 'ws://crossbar:8080',
    realm: 'semanticaio'
  });
};

/**
 * Test process: (print only)
 * load
 * start
 * wait (long time)
 * stop
 * save
 */

Test.prototype.start = function() {
  var that = this;
  return when.resolve()

  // load
  .then(function() {
    return that.ws.call('semanticaio.encoder.trainer.load')
    .tap(function() {
      console.log('encoder trainer loaded');
    });
  })

  // start
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.encoder.trainer.started', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.encoder.trainer.start');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.encoder.trainer.started');
    })
    .tap(function() {
      console.log('encoder trainer started');
    });
  })

  // wait 30s
  .delay(30000)

  // stop trainer
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.encoder.trainer.stopped', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.encoder.trainer.stop');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.encoder.trainer.stopped');
    })
    .tap(function() {
      console.log('encoder trainer stopped');
    });
  })

  // save
  .then(function() {
    return that.ws.call('semanticaio.encoder.trainer.save')
    .tap(function() {
      console.log('encoder trainer saved');
    });
  })

  .tap(function() {
    console.log('IT SAUL GOODMAN');
  });
};

module.exports = Test;
