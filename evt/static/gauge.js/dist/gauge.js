// Generated by CoffeeScript 1.4.0
(function() {
  var BaseGauge, Gauge, GaugePointer, ValueUpdater, mergeObjects, updateObjectValues,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  (function() {
    var browserRequestAnimationFrame, isCancelled, lastId, vendor, vendors, _i, _len;
    vendors = ['ms', 'moz', 'webkit', 'o'];
    for (_i = 0, _len = vendors.length; _i < _len; _i++) {
      vendor = vendors[_i];
      if (window.requestAnimationFrame) {
        break;
      }
      window.requestAnimationFrame = window[vendor + 'RequestAnimationFrame'];
      window.cancelAnimationFrame = window[vendor + 'CancelAnimationFrame'] || window[vendor + 'CancelRequestAnimationFrame'];
    }
    browserRequestAnimationFrame = null;
    lastId = 0;
    isCancelled = {};
    if (!requestAnimationFrame) {
      window.requestAnimationFrame = function(callback, element) {
        var currTime, id, lastTime, timeToCall;
        currTime = new Date().getTime();
        timeToCall = Math.max(0, 16 - (currTime - lastTime));
        id = window.setTimeout(function() {
          return callback(currTime + timeToCall);
        }, timeToCall);
        lastTime = currTime + timeToCall;
        return id;
      };
      return window.cancelAnimationFrame = function(id) {
        return clearTimeout(id);
      };
    } else if (!window.cancelAnimationFrame) {
      browserRequestAnimationFrame = window.requestAnimationFrame;
      window.requestAnimationFrame = function(callback, element) {
        var myId;
        myId = ++lastId;
        browserRequestAnimationFrame(function() {
          if (!isCancelled[myId]) {
            return callback();
          }
        }, element);
        return myId;
      };
      return window.cancelAnimationFrame = function(id) {
        return isCancelled[id] = true;
      };
    }
  })();

  updateObjectValues = function(obj1, obj2) {
    var key, val;
    for (key in obj2) {
      if (!__hasProp.call(obj2, key)) continue;
      val = obj2[key];
      obj1[key] = val;
    }
    return obj1;
  };

  mergeObjects = function(obj1, obj2) {
    var key, out, val;
    out = {};
    for (key in obj1) {
      if (!__hasProp.call(obj1, key)) continue;
      val = obj1[key];
      out[key] = val;
    }
    for (key in obj2) {
      if (!__hasProp.call(obj2, key)) continue;
      val = obj2[key];
      out[key] = val;
    }
    return out;
  };

  ValueUpdater = (function() {

    ValueUpdater.prototype.animationSpeed = 32;

    function ValueUpdater(addToAnimationQueue, clear) {
      if (addToAnimationQueue == null) {
        addToAnimationQueue = true;
      }
      this.clear = clear != null ? clear : true;
      if (addToAnimationQueue) {
        AnimationUpdater.add(this);
      }
    }

    ValueUpdater.prototype.update = function(force) {
      var diff;
      if (force == null) {
        force = false;
      }
      if (force || this.displayedValue !== this.value) {
        if (this.ctx && this.clear) {
          this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
        diff = this.value - this.displayedValue;
        if (Math.abs(diff / this.animationSpeed) <= 0.001) {
          this.displayedValue = this.value;
        } else {
          this.displayedValue = this.displayedValue + diff / this.animationSpeed;
        }
        this.render();
        return true;
      }
      return false;
    };

    return ValueUpdater;

  })();

  BaseGauge = (function(_super) {

    __extends(BaseGauge, _super);

    function BaseGauge() {
      return BaseGauge.__super__.constructor.apply(this, arguments);
    }

    BaseGauge.prototype.displayScale = 1;

    BaseGauge.prototype.setOptions = function(options) {
      if (options == null) {
        options = null;
      }
      this.options = mergeObjects(this.options, options);
      if (this.options.angle > .5) {
        this.gauge.options.angle = .5;
      }
      this.configDisplayScale();
      return this;
    };

    BaseGauge.prototype.configDisplayScale = function() {
      var backingStorePixelRatio, devicePixelRatio, height, prevDisplayScale, width;
      prevDisplayScale = this.displayScale;
      if (this.options.highDpiSupport === false) {
        delete this.displayScale;
      } else {
        devicePixelRatio = window.devicePixelRatio || 1;
        backingStorePixelRatio = this.ctx.webkitBackingStorePixelRatio || this.ctx.mozBackingStorePixelRatio || this.ctx.msBackingStorePixelRatio || this.ctx.oBackingStorePixelRatio || this.ctx.backingStorePixelRatio || 1;
        this.displayScale = devicePixelRatio / backingStorePixelRatio;
      }
      if (this.displayScale !== prevDisplayScale) {
        width = this.canvas.G__width || this.canvas.width;
        height = this.canvas.G__height || this.canvas.height;
        this.canvas.width = width * this.displayScale;
        this.canvas.height = height * this.displayScale;
        this.canvas.style.width = "" + width + "px";
        this.canvas.style.height = "" + height + "px";
        this.canvas.G__width = width;
        this.canvas.G__height = height;
      }
      return this;
    };

    return BaseGauge;

  })(ValueUpdater);

  GaugePointer = (function(_super) {

    __extends(GaugePointer, _super);

    GaugePointer.prototype.displayedValue = 0;

    GaugePointer.prototype.value = 0;

    GaugePointer.prototype.options = {
      length: 0.9,
      strokeWidth: 0.06,
      color: "#000000"
    };

    function GaugePointer(gauge) {
      this.gauge = gauge;
      this.ctx = this.gauge.ctx;
      this.canvas = this.gauge.canvas;
      GaugePointer.__super__.constructor.call(this, false, false);
      this.setOptions();
    }

    GaugePointer.prototype.setOptions = function(options) {
      if (options == null) {
        options = null;
      }
      updateObjectValues(this.options, options);
      this.length = this.canvas.height * this.options.length;
      this.strokeWidth = this.canvas.height * this.options.strokeWidth;
      this.maxValue = this.gauge.maxValue;
      this.minValue = this.gauge.minValue;
      this.animationSpeed = this.gauge.animationSpeed;
      return this.options.angle = this.gauge.options.angle;
    };

    GaugePointer.prototype.render = function() {
      var angle, centerX, centerY, endX, endY, startX, startY, x, y;
      angle = this.gauge.getAngle.call(this, this.displayedValue);
      centerX = this.canvas.width / 2;
      centerY = this.canvas.height * 0.9;
      x = Math.round(centerX + this.length * Math.cos(angle));
      y = Math.round(centerY + this.length * Math.sin(angle));
      startX = Math.round(centerX + this.strokeWidth * Math.cos(angle - Math.PI / 2));
      startY = Math.round(centerY + this.strokeWidth * Math.sin(angle - Math.PI / 2));
      endX = Math.round(centerX + this.strokeWidth * Math.cos(angle + Math.PI / 2));
      endY = Math.round(centerY + this.strokeWidth * Math.sin(angle + Math.PI / 2));
      this.ctx.fillStyle = this.options.color;
      this.ctx.beginPath();
      this.ctx.arc(centerX, centerY, this.strokeWidth, 0, Math.PI * 2, true);
      this.ctx.fill();
      this.ctx.beginPath();
      this.ctx.moveTo(startX, startY);
      this.ctx.lineTo(x, y);
      this.ctx.lineTo(endX, endY);
      return this.ctx.fill();
    };

    return GaugePointer;

  })(ValueUpdater);

  Gauge = (function(_super) {

    __extends(Gauge, _super);

    Gauge.prototype.value = 20;

    Gauge.prototype.displayedValue = 0;

    Gauge.prototype.paddingBottom = 0.1;

    Gauge.prototype.options = {
      colorBelow: "red",
      colorAbove: "green",
      angle: 0,
      lineWidth: 0.45,
      threshold: 0
    };

    function Gauge(canvas, options) {
      this.canvas = canvas;
      Gauge.__super__.constructor.call(this);
      if (typeof G_vmlCanvasManager !== 'undefined') {
        this.canvas = window.G_vmlCanvasManager.initElement(this.canvas);
      }
      this.ctx = this.canvas.getContext('2d');
      this.pointer = new GaugePointer(this);
      this.setOptions();
      this.render();
    }

    Gauge.prototype.setOptions = function(options) {
      if (options == null) {
        options = null;
      }
      Gauge.__super__.setOptions.call(this, options);
      this.lineWidth = this.canvas.height * (1 - this.paddingBottom) * this.options.lineWidth;
      this.radius = this.canvas.height * (1 - this.paddingBottom) - this.lineWidth;
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.maxValue = this.options.maxValue;
      this.minValue = this.options.minValue;
      this.threshold_angle = this.getAngle(this.options.threshold);
      this.render();
      this.pointer.setOptions(this.options.pointer);
      this.pointer.render();
      return this;
    };

    Gauge.prototype.set = function(value) {
      this.pointer.value = value;
      this.value = value;
      return AnimationUpdater.run();
    };

    Gauge.prototype.getAngle = function(value) {
      return (1 + this.options.angle) * Math.PI + ((value - this.minValue) / (this.maxValue - this.minValue)) * (1 - this.options.angle * 2) * Math.PI;
    };

    Gauge.prototype.render = function() {
      this.setArc(this.displayedValue);
      return this.pointer.update(true);
    };

    Gauge.prototype.setArc = function() {
      var h, w;
      w = this.canvas.width / 2;
      h = this.canvas.height * (1 - this.paddingBottom);
      this.ctx.strokeStyle = this.options.colorBelow;
      this.ctx.beginPath();
      this.ctx.arc(w, h, this.radius, (1 + this.options.angle) * Math.PI, this.threshold_angle, false);
      this.ctx.lineWidth = this.lineWidth;
      this.ctx.stroke();
      this.ctx.strokeStyle = this.options.colorAbove;
      this.ctx.beginPath();
      this.ctx.arc(w, h, this.radius, this.threshold_angle, (2 - this.options.angle) * Math.PI, false);
      return this.ctx.stroke();
    };

    return Gauge;

  })(BaseGauge);

  window.AnimationUpdater = {
    elements: [],
    animId: null,
    add: function(object) {
      return AnimationUpdater.elements.push(object);
    },
    run: function() {
      var animationFinished, elem, _i, _len, _ref;
      animationFinished = true;
      _ref = AnimationUpdater.elements;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        elem = _ref[_i];
        if (elem.update()) {
          animationFinished = false;
        }
      }
      if (!animationFinished) {
        return AnimationUpdater.animId = requestAnimationFrame(AnimationUpdater.run);
      } else {
        return cancelAnimationFrame(AnimationUpdater.animId);
      }
    }
  };

  if (typeof window.define === 'function' && (window.define.amd != null)) {
    define(function() {
      return {
        Gauge: Gauge
      };
    });
  } else if (typeof module !== 'undefined' && (module.exports != null)) {
    module.exports = {
      Gauge: Gauge
    };
  } else {
    window.Gauge = Gauge;
  }

}).call(this);
