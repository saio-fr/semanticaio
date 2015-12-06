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
 * get app & trainer state
 * get semantic config
 * load app
 * analyze
 * load trainer
 * start trainer (pretrain mode)
 * wait (long time)
 * stop trainer
 * repeat without pretrain mode
 * commit
 * analyze
 */

Test.prototype.start = function() {
  var that = this;
  return when.resolve()

  // get initial app & trainer state
  .then(function() {
    return that.ws.call('semanticaio.app.state.get')
    .tap(function(appState) {
      console.log('app state:', appState);
    });
  })
  .then(function() {
    return that.ws.call('semanticaio.trainer.state.get')
    .tap(function(trainerState) {
      console.log('trainer state:', trainerState);
    });
  })

  // get config
  .then(function() {
    return that.ws.call('semanticaio.config.get')
    .tap(function(config) {
      console.log('config:', config);
    });
  })

  // load app
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.app.state.loaded', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.app.load');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.app.state.loaded');
    });
  })

  // analyze
  .then(function() {
    var question = 'J\'ai perdu mon mot de passe';
    console.log('call analyze:', question);
    return that.ws.call('semanticaio.analyze', [], { question: question })
    .tap(function(analysis) {
      console.log('analysis:', analysis);
    });
  })

  // load trainer
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.trainer.state.loaded', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.trainer.load');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.trainer.state.loaded');
    })
    .tap(function() {
      console.log('trainer loaded');
    });
  })

  // start trainer (pretrain on)
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.trainer.state.started', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.trainer.start', [], { pretrain: true });
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.trainer.state.started');
    })
    .tap(function() {
      console.log('trainer started');
    });
  })

  .delay(90000)

  // stop trainer
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.trainer.state.stopped', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.trainer.stop');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.trainer.state.stopped');
    })
    .tap(function() {
      console.log('trainer stopped');
    });
  })

  // start trainer
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.trainer.state.started', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.trainer.start');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.trainer.state.started');
    })
    .tap(function() {
      console.log('trainer started');
    });
  })

  .delay(90000)

  // stop trainer
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.trainer.state.stopped', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.trainer.stop');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.trainer.state.stopped');
    })
    .tap(function() {
      console.log('trainer stopped');
    });
  })

  // commit
  .then(function() {
    return when.promise(function(resolve) {
      return that.ws.subscribe('semanticaio.trainer.state.committed', resolve)
      .then(function() {
        return that.ws.publish('semanticaio.trainer.commit');
      });
    })
    .then(function() {
      return that.ws.unsubscribe('semanticaio.trainer.state.committed');
    })
    .tap(function() {
      console.log('committed');
    });
  })

  // analyze
  .then(function() {
    var question = 'J\'ai perdu mon mot de passe';
    console.log('call analyze:', question);
    return that.ws.call('semanticaio.analyze', [], { question: question })
    .tap(function(analysis) {
      console.log('analysis:', analysis);
    });
  })

  .tap(function() {
    console.log('IT SAUL GOODMAN');
  });
};

module.exports = Test;
