var _ = require('underscore');
var when = require('when');
var Wsocket = require('@saio/wsocket-component');
var events = require('events');
var semanticConfig = require('config/semantic.json');

var Controller = function(container, options) {
  this.ws = container.use('ws', Wsocket, {
    url: 'ws://crossbar:8080',
    realm: 'semanticaio'
  });

  this.appState = 'new';
  this.trainerState = 'new';
  this.eventHandler = new events.EventEmitter();
};

Controller.prototype.start = function() {
  var pendingPromises = [
    this.ws.register('semanticaio.app.state.get', this.getAppState.bind(this)),
    this.ws.register('semanticaio.trainer.state.get', this.getTrainerState.bind(this)),
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
  var result = {
    tags: {},
    classes: {},
    match: { question: '', distance: 1 }
  };
  if (this.appState !== 'ready') {
    console.log('[error] semanticaio.analyze: app not ready');
    return result;
  }
  return this.ws.call('semanticaio.encoder.encode', [] {
    question: kwargs.question,
    decode: true
  })
  .then(function(encoderResult) {
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
      .tap(function(match) {
        console.log('    - match: ' + match);
        result.match = match;
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
    return that.ws.publish('semanticaio.app.state.loaded', [], {});
  })
  .tap(function() {
    that.appState = 'ready';
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
    return that.ws.publish('semanticaio.trainer.state.loaded', [], {});
  })
  .tap(function() {
    console.log('[emit] semanticaio.trainer.state.loaded');
  });
};

Controller.prototype.startTrainer = function() {

};

Controller.prototype.stopTrainer = function() {

};

Controller.prototype.commit = function() {
  // change state
  // save encoder
  // load encoder
  // re-encode db
  // train tagger & train classifier
  // load tagger, trainer, matcher
  // fire committed
};

Controller.prototype._onEncoderTrainerStarted = function() {
  this.eventHandler.emit('encoderTrainerStarted');
};

Controller.prototype._onEncoderTrainerStopped = function() {
  this.eventHandler.emit('encoderTrainerStopped');
};

Controller.prototype._onTaggerTrained = function() {
  this.eventHandler.emit('taggerTrained');
};

Controller.prototype._onClassifierTrained = function() {
  this.eventHandler.emit('classifierTrained');
};

module.exports = Controller;
