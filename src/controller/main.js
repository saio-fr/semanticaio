var _ = require('underscore');
var when = require('when');
var Wsocket = require('@saio/wsocket-component');
var events = require('events');
var semanticConfig = require('./config/semantic.json');

var Controller = function(container, options) {
  var that = this;
  this.ws = container.use('ws', Wsocket, {
    url: 'ws://crossbar:8080',
    realm: 'semanticaio'
  });

  this.appState = 'new';
  this.trainerState = 'new';
  this.eventHandler = new events.EventEmitter();

  this.eventHandler.on('encoderTrainerStarted', function() {
    that.trainerState = 'training';
    return that.ws.publish('semanticaio.trainer.state.started', [], {})
    .tap(function() {
      console.log('[emit] semanticaio.trainer.state.started');
    });
  });

  this.eventHandler.on('encoderTrainerStopped', function() {
    that.trainerState = 'ready';
    return that.ws.publish('semanticaio.trainer.state.stopped', [], {})
    .tap(function() {
      console.log('[emit] semanticaio.trainer.state.stopped');
    });
  });
};

Controller.prototype.start = function() {
  var pendingPromises = [
    this.ws.register('semanticaio.app.state.get', this.getAppState.bind(this)),
    this.ws.register('semanticaio.trainer.state.get', this.getTrainerState.bind(this)),
    this.ws.register('semanticaio.config.get', this.getSemanticConfig.bind(this)),
    this.ws.register('semanticaio.analyze', this.analyze.bind(this)),
    this.ws.subscribe('semanticaio.app.load', this.loadApp.bind(this)),
    this.ws.subscribe('semanticaio.trainer.load', this.loadTrainer.bind(this)),
    this.ws.subscribe('semanticaio.trainer.start', this.startTrainer.bind(this)),
    this.ws.subscribe('semanticaio.trainer.stop', this.stopTrainer.bind(this)),
    this.ws.subscribe('semanticaio.trainer.commit', this.commit.bind(this)),
    this.ws.subscribe('semanticaio.encoder.trainer.started', this._onEncoderTrainerStarted.bind(this)),
    this.ws.subscribe('semanticaio.encoder.trainer.stopped', this._onEncoderTrainerStopped.bind(this)),
    this.ws.subscribe('semanticaio.tagger.trainer.trained', this._onTaggerTrained.bind(this)),
    this.ws.subscribe('semanticaio.classifier.trainer.trained', this._onClassifierTrained.bind(this))
  ];
  return when.all(pendingPromises)
  .tap(function() {
    console.log('[controller started]');
  });
};

Controller.prototype.stop = function() {
  return when.all([this.ws.unregister(), this.ws.unsubscribe()])
  .tap(function() {
    console.log('[controller stopped]');
  });
};

Controller.prototype.getSemanticConfig = function() {
  console.log('[call] semanticaio.config.get');
  return {
    tags: semanticConfig.tags,
    classes: semanticConfig.classes
  };
};

Controller.prototype.getAppState = function() {
  console.log('[call] semanticaio.app.state.get');
  return this.appState;
};

Controller.prototype.getTrainerState = function() {
  console.log('[call] semanticaio.trainer.state.get');
  return this.trainerState;
};

Controller.prototype.analyze = function(args, kwargs) {
  console.log('[call] semanticaio.analyze: ' + kwargs.question);
  var that = this;
  if (this.appState !== 'ready') {
    console.log('[error] semanticaio.analyze: app not ready');
    return;
  }

  var result = {};
  return this.ws.call('semanticaio.encoder.encode', [], {
    question: kwargs.question,
    decode: true
  })
  .then(function(encodeResult) {
    var encoded = encodeResult.encoded;
    var decoded = encodeResult.decoded;
    console.log('    - auto-encoder output: ' + decoded);

    var pendingPromises = [
      that.ws.call('semanticaio.tagger.tag', [], { question: encoded })
      .tap(function(tags) {
        console.log('    - tags: ' + tags);
        result.tags = tags;
      }),
      that.ws.call('semanticaio.classifier.classify', [], { question: encoded })
      .tap(function(classes) {
        console.log('    - classes: ' + classes);
        result.classes = classes;
      }),
      that.ws.call('semanticaio.matcher.match', [], { question: encoded })
      .then(function(match) {
        console.log('    - match distance: ' + match.distance);
        result.match = { distance: match.distance };
        return that.ws.call('semanticaio.db.get', [], { id: match.id });
      })
      .tap(function(question) {
        console.log('    - match question: ' + question.sentence);
        result.match.question = question.sentence;
      })
    ];
    return when.all(pendingPromises);
  })
  .then(function() {
    return result;
  });
};

Controller.prototype.loadApp = function() {
  var that = this;
  console.log('[event received] semanticaio.app.load');
  if (this.appState === 'loading') {
    console.log('[error] semanticaio.app.load: already loading');
    return;
  }
  if (this.trainerState === 'committing') {
    console.log('[error] semanticaio.app.load: still committing');
    return;
  }

  this.appState = 'loading';
  return this.ws.publish('semanticaio.app.state.loading', [], {})
  .then(function() {
    console.log('[emit] semanticaio.app.state.loading');
    return that.ws.call('semanticaio.encoder.load');
  })
  .then(function() {
    var pendingPromises = [
      that.ws.call('semanticaio.tagger.load', [], {}),
      that.ws.call('semanticaio.classifier.load', [], {}),
      that.ws.call('semanticaio.matcher.load', [], {})
    ];
    return when.all(pendingPromises);
  })
  .then(function() {
    that.appState = 'ready';
    return that.ws.publish('semanticaio.app.state.loaded', [], {});
  })
  .tap(function() {
    console.log('[emit] semanticaio.app.state.loaded');
  });
};

Controller.prototype.loadTrainer = function() {
  var that = this;
  console.log('[event received] semanticaio.trainer.load');
  if (this.trainerState !== 'new' && this.trainerState !== 'ready') {
    console.log('[error] semanticaio.trainer.load: invalid state: ' + this.trainerState);
    return;
  }

  this.trainerState = 'loading';
  return this.ws.publish('semanticaio.trainer.state.loading', [], {})
  .then(function() {
    console.log('[emit] semanticaio.trainer.state.loading');
    return that.ws.call('semanticaio.encoder.trainer.load');
  })
  .then(function() {
    var pendingPromises = [
      that.ws.call('semanticaio.tagger.trainer.load', [], {}),
      that.ws.call('semanticaio.classifier.trainer.load', [], {})
    ];
    return when.all(pendingPromises);
  })
  .then(function() {
    that.trainerState = 'ready';
    return that.ws.publish('semanticaio.trainer.state.loaded', [], {});
  })
  .tap(function() {
    console.log('[emit] semanticaio.trainer.state.loaded');
  });
};

Controller.prototype.startTrainer = function() {
  var that = this;
  console.log('[event received] semanticaio.trainer.start');
  if (this.trainerState !== 'ready') {
    console.log('[error] semanticaio.trainer.start: invalid state: ' + this.trainerState);
    return;
  }

  this.trainerState = 'starting';
  return this.ws.publish('semanticaio.trainer.state.starting', [], {})
  .then(function() {
    console.log('[emit] semanticaio.trainer.state.starting');
    return that.ws.publish('semanticaio.encoder.trainer.start', [], {});
  });
};

Controller.prototype.stopTrainer = function() {
  var that = this;
  console.log('[event received] semanticaio.trainer.stop');
  if (this.trainerState !== 'training') {
    console.log('[error] semanticaio.trainer.stop: invalid state: ' + this.trainerState);
    return;
  }

  this.trainerState = 'stopping';
  return this.ws.publish('semanticaio.trainer.state.stopping', [], {})
  .then(function() {
    console.log('[emit] semanticaio.trainer.state.stopping');
    return that.ws.publish('semanticaio.encoder.trainer.stop', [], {});
  });
};

Controller.prototype.commit = function() {
  var that = this;
  console.log('[event received] semanticaio.trainer.commit');
  if (this.appState === 'loading') {
    console.log('[error] semanticaio.trainer.commit: invalid app state: loading');
    return;
  }
  if (this.trainerState !== 'ready') {
    console.log('[error] semanticaio.trainer.commit: invalid trainer state: ' + this.trainerState);
    return;
  }

  // state update
  this.trainerState = 'committing';
  this.appState = 'loading';
  return this.ws.publish('semanticaio.trainer.state.committing', [], {})
  .tap(function() {
    console.log('[emit] semanticaio.trainer.state.committing');
  })
  .then(function() {
    return that.ws.publish('semanticaio.app.state.loading', [], {});
  })
  .tap(function() {
    console.log('[emit] semanticaio.app.state.loading');
  })
  // save & reload encoder
  .then(function() {
    return that.ws.call('semanticaio.encoder.trainer.save', [], {});
  })
  .then(function() {
    return that.ws.call('semanticaio.encoder.load', [], {});
  })
  // re-encode db
  .then(function() {
    return that.ws.call('semanticaio.db.all.get', [], { correctOnly: true });
  })
  .then(function(questions) {
    var ids = _.map(questions, function(question) {
      return question.id;
    });
    var sentences = _.map(questions, function(question) {
      return question.sentence;
    });
    return that.ws.call('semanticaio.encoder.encode', [], {
      questions: sentences,
      decode: false
    })
    .then(function(encodeResult) {
      var pendingUpdates = _.map(ids, function(id, index) {
        return that.ws.call('semanticaio.db.set', [], {
          id: id,
          representation: encodeResult.encoded[index]
        });
      });
      return when.all(pendingUpdates);
    });
  })
  // train classifier & tagger
  .then(function() {
    return when.promise(function(resolve) {
      var taggerTrained = false;
      var classifierTrained = false;
      that.eventHandler.once('taggerTrained', function() {
        taggerTrained = true;
        if (classifierTrained) {
          resolve();
        }
      });
      that.eventHandler.once('classifierTrained', function() {
        classifierTrained = true;
        if (taggerTrained) {
          resolve();
        }
      });
      that.ws.publish('semanticaio.tagger.trainer.train', [], {});
      that.ws.publish('semanticaio.classifier.trainer.train', [], {});
    });
  })
  // save classifier & tagger
  .then(function() {
    var pendingSaves = [
      that.ws.call('semanticaio.tagger.trainer.save'),
      that.ws.call('semanticaio.classifier.trainer.save')
    ];
    return when.all(pendingSaves);
  })
  // reload classifier, tagger & matcher
  .then(function() {
    var pendingLoads = [
      that.ws.call('semanticaio.tagger.load'),
      that.ws.call('semanticaio.classifier.load'),
      that.ws.call('semanticaio.matcher.load')
    ];
    return when.all(pendingLoads);
  })
  // update state
  .then(function() {
    that.appState = 'ready';
    that.trainerState = 'ready';
    var pendingPubs = [
      that.ws.publish('semanticaio.app.state.loaded'),
      that.ws.publish('semanticaio.trainer.state.committed')
    ];
    return when.all(pendingPubs);
  })
  .tap(function() {
    console.log('[emit] semanticaio.app.state.loaded');
    console.log('[emit] semanticaio.trainer.state.committed');
  });
};

Controller.prototype._onEncoderTrainerStarted = function() {
  console.log('[internal event received] semanticaio.encoder.trainer.started');
  this.eventHandler.emit('encoderTrainerStarted');
};

Controller.prototype._onEncoderTrainerStopped = function() {
  console.log('[internal event received] semanticaio.encoder.trainer.stopped');
  this.eventHandler.emit('encoderTrainerStopped');
};

Controller.prototype._onTaggerTrained = function() {
  console.log('[internal event received] semanticaio.tagger.trainer.trained');
  this.eventHandler.emit('taggerTrained');
};

Controller.prototype._onClassifierTrained = function() {
  console.log('[internal event received] semanticaio.classifier.trainer.trained');
  this.eventHandler.emit('classifierTrained');
};

module.exports = Controller;
