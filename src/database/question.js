var _ = require('underscore');
var tags = require('config/semantic.json').tags;

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
  _.each(tags, function(tag) {
    model[tag] = {
      type: DataTypes.BOOLEAN,
      allowNull: false
    }
  });

  var options = {
    timestamps: false
  };
  return sequelize.define('Question', model, options);
};
