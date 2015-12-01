var _ = require('underscore');
var semanticConfig = require('./config/semantic.json');

module.exports = function(sequelize, DataTypes) {
  var model = {
    sentence: {
      type: DataTypes.STRING,
      unique: true,
      allowNull: false
    },
    matchable: {
      type: DataTypes.BOOLEAN,
      allowNull: false
    },
    correctFormId: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    representation: {
      type: DataTypes.JSON,
      allowNull: true
    }
  };

  _.each(semanticConfig.tags, function(tag) {
    model[tag] = {
      type: DataTypes.BOOLEAN,
      allowNull: true
    };
  });

  _.each(semanticConfig.classes, function(labels, className) {
    model[className] = {
      type: DataTypes.ENUM.apply(null, labels),
      allowNull: true
    };
  });

  var options = {
    timestamps: false
  };

  return sequelize.define('Question', model, options);
};
