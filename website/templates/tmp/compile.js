// utils.js
function rand(min, max) {
   return Math.floor(Math.random() * (max - min)) + min;
}

function randf(min, max) {
   return (Math.random() * (max - min)) + min;
}

function trim(str) {
   return str.replace(/^\s+/g, '').replace(/\s+$/g, '');
} 

function addslashes(str) {
   str=str.replace(/\\/g,'\\\\');
   str=str.replace(/\'/g,'\\\'');
   str=str.replace(/\"/g,'\\"');
   str=str.replace(/\0/g,'\\0');
   return str;
}
function stripslashes(str) {
   str=str.replace(/\\'/g,'\'');
   str=str.replace(/\\"/g,'"');
   str=str.replace(/\\0/g,'\0');
   str=str.replace(/\\\\/g,'\\');
   return str;
}

function Point(x, y) {
    this.x = x;
    this.y = y;
}

function getScroll() {
   var scrOfX = 0, scrOfY = 0;
   if( typeof( window.pageYOffset ) == 'number' ) {
            scrOfY = window.pageYOffset;
      scrOfX = window.pageXOffset;
   } else if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
            scrOfY = document.body.scrollTop;
      scrOfX = document.body.scrollLeft;
   } else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
            scrOfY = document.documentElement.scrollTop;
      scrOfX = document.documentElement.scrollLeft;
   }
   return new Point(scrOfX, scrOfY);
}



// core.js
var canvas;
var c;
var objs = new Array();
var vars = {};

var state;
var stateTime;
var nbStates = 0;
var States = {};

var medias = {};

var interval;

function addVar(name, value) {
   vars[name] = value;
}

function removeVar(name) {
   delete vars[name];
}

function addState(str) {
   States[str] = nbStates += 1;
}

function switchState(str, callback) {
   console.log("State: "+str);
   animations = 0;
   finished = 0;
   animationsComplete = function() {};
   eval("if (typeof "+state+"_end == 'function') "+state+"_end();");
   state = str;
   stateTime = new Date();
   eval("if (typeof "+state+"_init == 'function') "+state+"_init();");
}

function dt() {
   return new Date() - stateTime;
}

var frameTime = Date.now();
var fw = {
   fps: 30,
   tick: function() { return (Date.now() - frameTime); },
   main: function(canvasId, fps, width, height, scale, lloader) {
      this.fps = fps;
      window.addEventListener("load", function() {
         canvas = document.getElementById(canvasId);
         canvas.width = width;
         canvas.height = height;
         c = canvas.getContext("2d");
         new lloader();
      }, false);
   },


   update: function() {
      eval("if (typeof "+state+"_update == 'function') "+state+"_update();");

      for (var i in objs)
         objs[i].update();

      frameTime = Date.now();
   },


   paint: function() {
      c.clearRect(0, 0, canvas.width, canvas.height);

      if (typeof pre_paint == 'function') pre_paint();

      eval("if (typeof "+state+"_paint == 'function') "+state+"_paint();");

      for (var i in objs)
         objs[i].paint();

      eval("if (typeof "+state+"_post_paint == 'function') "+state+"_post_paint();");

      if (typeof post_paint == 'function') post_paint();
   },


   cycle: function() {
      fw.update();
      fw.paint();
   },


   copy: function(object) {
      if (!object || typeof(object) != 'object' || object instanceof fw.Class) {
         return object;
      } else if (object instanceof Array) {
         var c = [];
         for (var i=0, l=object.length; i<l; i++) {
            c[i] = fw.copy(object[i]);
         }
         return c;
      } else {
         var c = {};
         for (var i in object) {
            c[i] = fw.copy(object[i]);
         }
         return c;
      }
   }
};

window.fw.Class = function() {};
window.fw.Class.extend = function(prop) {
   var parent = this.prototype;
   initializing = true;
   var prototype = new this();
   initializing = false;
   for (var name in prop) {
      if (typeof(prop[name]) == "function" && typeof(parent[name]) == "function") {
         prototype[name] = (function(name, fn) {
            return function() {
               var tmp = this.parent;
               this.parent = parent[name];
               var ret = fn.apply(this, arguments);
               this.parent = tmp;
               return ret;
            };
         })(name, prop[name])
      } else {
         prototype[name] = prop[name];
      }
   }
   function Class() {
      if (!initializing) {
         if (this.staticInstantiate) {
            var obj = this.staticInstantiate.apply(this, arguments);
            if (obj) { return obj; }
         }
         for (p in this) {
            this[p] = fw.copy(this[p]);
         }
         if (this.init) {
            this.init.apply(this, arguments);
         }
      }
      return this;
   }
   Class.prototype = prototype;
   Class.constructor = Class;
   Class.extend = arguments.callee;
   return Class;
};

window.fw.Loader = fw.Class.extend({
   init: function() {
      this.load();
   },
   draw: function() {
   },
   load: function() {
      var t = this;
      loaded = 0;
      total = 0;
      if (this.files.length == 0) { this.endd(); return; }
      for (var i in this.files) {
         if (typeof(this.files[i]) != "string") continue;
         var name = this.files[i].substring(0, this.files[i].indexOf("."));
         var extension = this.files[i].substring(this.files[i].indexOf(".")+1, this.files[i].length);
         total++;
         var fn = this.files[i];
         switch (extension) {
            case "jpg":
            case "png":
               medias[i] = new Image();
               medias[i].src = fn;
               medias[i].onload = function() {
                  loaded++;
                  if (loaded == total)
                     t.endd();
               };
               break;
            case "ogg":
            case "wav":
               medias[i] = new Audio();
               medias[i].src = fn;
               medias[i].load();
               loaded++;
               if (loaded == total)
                  t.endd();
               break;
         }
      }
   },
   endd: function() {
      interval = setInterval(fw.cycle, 1000/fw.fps);
      this.end();
   },
   end: function() {
      console.log("END");
   }
});



// anim.js
/*
Copyright (c) 2010, ALAIN GILBERT.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by ALAIN GILBERT.
4. Neither the name of the ALAIN GILBERT nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY ALAIN GILBERT ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ALAIN GILBERT BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/


function Obj() {
   objs.push(this);

   this.focus = function() {
      var tmp = this;
      for (var i in objs) {
         if (objs[i] == this) {
            objs.splice(i, 1);
            break;
         }
      }
      objs.push(tmp);
   };
}

function Point(x, y) {
    this.x = x;
    this.y = y;
}

var formulas = {
    'linear': function(n) { return n; },
    '<': function(n) { return Math.pow(n, 3); },
    '>': function(n) { return Math.pow(n - 1, 3) + 1; },
    '<>': function(n) {
        n = n * 2;
        if (n < 1) {
            return Math.pow(n, 3) / 2;
        }
        n -= 2;
        return (Math.pow(n, 3) + 2) / 2;
    },
    backIn: function (n) {
        var s = 1.70158;
        return n * n * ((s + 1) * n - s);
    },
    backOut: function (n) {
        n = n - 1;
        var s = 1.70158;
        return n * n * ((s + 1) * n + s) + 1;
    },
    elastic: function (n) {
        if (n == 0 || n == 1) {
            return n;
        }
        var p = .3,
            s = p / 4;
        return Math.pow(2, -10 * n) * Math.sin((n - s) * (2 * Math.PI) / p) + 1;
    },
    bounce: function (n) {
        var s = 7.5625,
            p = 2.75,
            l;
        if (n < (1 / p)) {
            l = s * n * n;
        } else {
            if (n < (2 / p)) {
                n -= (1.5 / p);
                l = s * n * n + .75;
            } else {
                if (n < (2.5 / p)) {
                    n -= (2.25 / p);
                    l = s * n * n + .9375;
                } else {
                    n -= (2.625 / p);
                    l = s * n * n + .984375;
                }
            }
        }
        return l;
    }
};

var animations = 0;
var finished = 0;
function animationsComplete() {
}

function Label(params) {
    Obj.call(this);
    this.x = params.x != undefined ? params.x : null;
    this.y = params.y != undefined ? params.y : null;
    this.text = params.text != undefined ? params.text : null;
    this.color = params.color != undefined ? params.color : '#000';
    this.init_textSize = params.textSize != undefined ? params.textSize : 10;
    this.textSize = params.textSize != undefined ? params.textSize : 10;
    this.font = params.font != undefined ? params.font : this.textSize+'px sans-serif';
    this.align = params.align != undefined ? params.align : 'start';
    this.baseline = params.baseline != undefined ? params.baseline : 'alphabetic';
    this.maxWidth = params.maxWidth != undefined ? params.maxWidth : null;
    this.alpha = (params.opacity != undefined) ? params.opacity : 1;
    this.angle = params.angle ? params.angle : 0;
    this.color = params.color ? params.color : "rgba(0, 0, 0, 1)";
    this.scale = 100;

    this.width = c.measureText(this.text).width;
    this.height = this.textSize;
    
    this.onClick = function(e) { };
    this.onMouseOut = function(e) { };
    this.onMouseMove = function(e) { };
    this.onMouseOver = function(e) { };
    this.onMouseDown = function(e) { };
    this.onMouseUp = function(e) { };
    this.onUpdate = function() { };
    this.onPaint = function() {
        c.save();
        c.fillStyle = this.color;
        c.font = this.font;
        c.textAlign = this.align;
        c.textBaseline = this.baseline;
        c.fillStyle = "rgba(0, 0, 0, "+this.alpha+")";
        c.fillText(this.text, this.x, this.y, this.maxWidth);    
        c.restore();
    };

    this.paint = function() { this.onPaint(); };
    this.update = function() { this.onUpdate(); };
    this.isInside = function(point) { return point.x >= this.x && point.x <= this.x + this.width && point.y >= this.y && point.y <= this.y + this.height; };
    
    this.animate = function(conf, callback) {
       animations++;

        conf.start = (conf.start != undefined) ? conf.start : 0;

                var time = dt()/1000 + conf.start;

        var from = new Point(this.x, this.y);
        from.alpha = this.alpha;
        from.width = this.width;
        from.height = this.height;
        from.scale = this.scale;
        from.angle = this.angle;

        var to = conf.to;

                var end = false;

        this.update = function() {
            if (dt()/1000 >= conf.start && !end) {
                if (conf.debug) {
                    console.log(from, to, conf);
                }
                if (dt()/1000 <= time+conf.duration) {
                    if (conf.to) {
                        var effect = formulas[conf.effect] ? formulas[conf.effect]((dt()/1000-time)/conf.duration) : formulas['linear']((dt()/1000-time)/conf.duration);
                        if (to.x - from.x != 0) {
                            this.x = ((to.x - from.x) / (conf.duration)) * (effect * conf.duration) + from.x;
                            this.y = ((to.y - from.y) / (to.x - from.x)) * this.x + (to.y - (((to.y - from.y) / (to.x - from.x)) * to.x));
                        } else {
                            this.y = ((to.y - from.y) / (conf.duration)) * (effect * conf.duration) + from.y;
                        }
                    }
                    if (conf.width) { this.width = ((conf.width - from.width) / conf.duration) * (dt()/1000-time) + from.width; }
                    if (conf.height) { this.height = ((conf.height - from.height) / conf.duration) * (dt()/1000-time) + from.height; }
                    if (conf.opacity != undefined) { this.alpha = ((conf.opacity - from.alpha) / conf.duration) * (dt()/1000-time) + from.alpha; }
                    if (conf.rotate) { this.angle = ((conf.rotate - from.angle) / conf.duration) * (dt()/1000-time) + from.angle; }
                    if (conf.scale != undefined) {
                        this.textSize = ((((conf.scale - from.scale) / conf.duration) * (dt()/1000-time) + from.scale) / 100) * this.init_textSize;
                        this.font = this.textSize+'px sans-serif';
                        this.height = ((((conf.scale - from.scale) / conf.duration) * (dt()/1000-time) + from.scale) / 100) * this.initHeight;
                        if (!conf.to) {
                            this.x = (from.x + this.initWidth / 2) - (this.width / 2);
                            this.y = (from.y + this.initHeight / 2) - (this.height / 2);
                        }
                    }
                } else {
                    end = true;

                    if (conf.to) {
                        this.x = to.x;
                        this.y = to.y;
                    }
                    if (conf.width) { this.width = conf.width; }
                    if (conf.height) { this.height = conf.height; }
                    if (conf.opacity != undefined) { this.alpha = conf.opacity; }
                    if (conf.rotate) { this.angle = conf.rotate; }
                    if (conf.scale != undefined) {
                        this.textSize = (conf.scale / 100) * this.init_textSize;
                        this.font = this.textSize+'px sans-serif';
                        this.width = (conf.scale / 100) * this.initWidth;
                        this.height = (conf.scale / 100) * this.initHeight;
                        if (!conf.to) {
                            this.x = (from.x + this.initWidth / 2) - (this.width / 2);
                            this.y = (from.y + this.initHeight / 2) - (this.height / 2);
                        }
                        this.scale = conf.scale;
                    }

                    finished++;
                    if (finished == animations) {
                        animationsComplete();
                    }

                    if (callback) { callback(); }
                }
            }
        };
    };
}

function Anim(params) {
    Obj.call(this);
    this.img = params.img ? params.img : null;
    this.x = params.x != undefined ? params.x : null;
    this.y = params.y != undefined ? params.y : null;
    this.initWidth = params.width ? params.width : this.img.width;
    this.initHeight = params.height ? params.height : this.img.height;
    this.width = params.width ? params.width : this.img.width;
    this.height = params.height ? params.height : this.img.height;
    this.alpha = (params.opacity != undefined) ? params.opacity : 1;
    this.start;
    this.stop;
    this.focus;
    this.mouseOver;
    this.angle = params.angle ? params.angle : 0;
    this.appearIn = params.appearIn ? params.appearIn : null;

    this.caliss;

    if (params.scale != undefined) {
        this.scale = params.scale;
        this.width = (params.scale / 100) * this.initWidth;
        this.height = (params.scale / 100) * this.initHeight;
    } else {
        this.scale = 100;
    }

    this.onMouseOver = function(e) { };
    this.onMouseOut = function(e) { };
    this.onMouseMove = function(e) { };
    this.onMouseDown = function(e) { };
    this.onMouseUp = function(e) { };
    this.onKeyDown = function(e) { };
    this.onKeyUp = function(e) { };
    this.onPaint = function() {
        c.drawImage(this.img, this.x, this.y, this.width, this.height);
    };
    this.onUpdate = function() { };
    this.onFocus = function() { };
    this.onClick = function(e) { };
    this.onDblClick = function(e) { };
    this.onDragStart = function() { };
    this.onDragDrop = function() { };
    this.created = dt()/1000;
    
    this.paint = function() {
        if (this.appearIn == null || dt()/1000 >= this.created+this.appearIn) {
           c.save();
           c.globalAlpha = this.alpha;
           c.translate(this.x + this.width/2, this.y + this.height/2);
           c.rotate(this.angle);
           c.translate(-(this.x + this.width/2), -(this.y + this.height/2));
           this.onPaint();
           c.restore();
        }
    };
    this.update = function() { this.onUpdate(); };
    this.isInside = function(point) { return point.x >= this.x && point.x <= this.x + this.width && point.y >= this.y && point.y <= this.y + this.height; };

    this.animate = function(conf, callback) {
        animations++;

        conf.start = (conf.start != undefined) ? conf.start : 0;

                var time = dt()/1000 + conf.start;

        var from = new Point(this.x, this.y);
        from.alpha = this.alpha;
        from.width = this.width;
        from.height = this.height;
        from.scale = this.scale;
        from.angle = this.angle;

        var to = conf.to;

                var end = false;

        this.update = function() {
            if (dt()/1000 >= conf.start && !end) {
                if (conf.debug) {
                    console.log(from, to, conf);
                }
                if (dt()/1000 <= time+conf.duration) {
                    if (conf.to) {
                        var effect = formulas[conf.effect] ? formulas[conf.effect]((dt()/1000-time)/conf.duration) : formulas['linear']((dt()/1000-time)/conf.duration);
                        if (to.x - from.x != 0) {
                            this.x = ((to.x - from.x) / (conf.duration)) * (effect * conf.duration) + from.x;
                            this.y = ((to.y - from.y) / (to.x - from.x)) * this.x + (to.y - (((to.y - from.y) / (to.x - from.x)) * to.x));
                        } else {
                            this.y = ((to.y - from.y) / (conf.duration)) * (effect * conf.duration) + from.y;
                        }
                    }
                    if (conf.width) { this.width = ((conf.width - from.width) / conf.duration) * (dt()/1000-time) + from.width; }
                    if (conf.height) { this.height = ((conf.height - from.height) / conf.duration) * (dt()/1000-time) + from.height; }
                    if (conf.opacity != undefined) { this.alpha = ((conf.opacity - from.alpha) / conf.duration) * (dt()/1000-time) + from.alpha; }
                    if (conf.rotate) { this.angle = ((conf.rotate - from.angle) / conf.duration) * (dt()/1000-time) + from.angle; }
                    if (conf.scale != undefined) {
                        this.width = ((((conf.scale - from.scale) / conf.duration) * (dt()/1000-time) + from.scale) / 100) * this.initWidth;
                        this.height = ((((conf.scale - from.scale) / conf.duration) * (dt()/1000-time) + from.scale) / 100) * this.initHeight;
                        if (!conf.to) {
                            this.x = (from.x + from.width / 2) - (this.width / 2);
                            this.y = (from.y + from.height / 2) - (this.height / 2);
                        }
                        this.scale = ((conf.scale - from.scale) / conf.duration) * (dt()/1000-time) + from.scale;
                    }
                } else {
                    end = true;
                           
                    if (conf.to) {
                        this.x = to.x;
                        this.y = to.y;
                    }
                    if (conf.width) { this.width = conf.width; }
                    if (conf.height) { this.height = conf.height; }
                    if (conf.opacity != undefined) { this.alpha = conf.opacity; }
                    if (conf.rotate) { this.angle = conf.rotate; }
                    if (conf.scale != undefined) {
                        this.width = (conf.scale / 100) * this.initWidth;
                        this.height = (conf.scale / 100) * this.initHeight;
                        if (!conf.to) {
                            this.x = (from.x + from.width / 2) - (this.width / 2);
                            this.y = (from.y + from.height / 2) - (this.height / 2);
                        }
                        this.scale = conf.scale;
                    }

                    finished++;
                    if (finished == animations) {
                        animationsComplete();
                    }

                    if (callback) { callback(); }
                }
            }
        };
    };
}

function Sprite(params) {
   Anim.call(this, params);
   this.frame = params.frame != undefined ? params.frame : null;
   this.onPaint = function() {
      var frameh = 0;
      var framew = this.frame;
      if (this.frame >= this.img.width / this.width) {
         framew -= this.img.width / this.width;
         frameh++;
      }
      c.drawImage(this.img, framew*this.width, frameh*this.height, this.width, this.height, this.x, this.y, this.width, this.height);
   };
}



// handlers.js
HTMLElement.prototype.onMouseOver = function(e) { };
HTMLElement.prototype.onMouseOut = function(e) { };
HTMLElement.prototype.onMouseMove = function(e) { };
HTMLElement.prototype.onClick = function(e) { };
HTMLElement.prototype.onMouseDown = function(e) { };
HTMLElement.prototype.onMouseUp = function(e) { };
HTMLElement.prototype.onKeyDown = function(e) { };
HTMLElement.prototype.onKeyUp = function(e) { };
HTMLElement.prototype.onDblClick = function(e) { };
HTMLElement.prototype.init = function() { };

function bindKeys() {
   var overEl = false;
   canvas.onmousemove = function(e) {
      var pos = new Point(e.clientX - canvas.offsetLeft + getScroll().x, e.clientY - canvas.offsetTop + getScroll().y);
      for (i = objs.length-1; i >= 0; i--) {
         if (objs[i].isInside(pos)) {
            if (!overEl && !objs[i].mouseOver) {
               objs[i].onMouseOver(pos);
               objs[i].mouseOver = true;

               overEl = true;

            }
            objs[i].onMouseMove(pos);
         } else {
            if (objs[i].mouseOver) {
               objs[i].onMouseOut(pos);
               objs[i].mouseOver = false;
               overEl = false;
            }
         }
      }

      this.onMouseMove(pos);
   };

   canvas.onmouseout = function(e) {
      var pos = new Point(e.clientX - canvas.offsetLeft + getScroll().x, e.clientY - canvas.offsetTop + getScroll().y);
      for (i in objs) {
         if (objs[i].mouseOver) {
            objs[i].onMouseOut(pos);
            objs[i].mouseOver = false;
         }
      }

      this.onMouseOut(pos);
   };

   canvas.onclick = function(e) {
      var pos = new Point(e.clientX - canvas.offsetLeft + getScroll().x, e.clientY - canvas.offsetTop + getScroll().y);
      for (i = objs.length-1; i >= 0; i--) {
         if (objs[i].isInside(pos)) {
            objs[i].onClick(pos);
            break;
         }
      }

      this.onClick(pos);
   };

   canvas.ondblclick = function(e) {
      var pos = new Point(e.clientX - canvas.offsetLeft + getScroll().x, e.clientY - canvas.offsetTop + getScroll().y);
      for (i = objs.length-1; i >= 0; i--) {
         if (objs[i].isInside(pos)) {
            objs[i].onDblClick(pos);
            break;
         }
      }

      this.onDblClick(pos);
   };

   canvas.onmousedown = function(e) {
      var pos = new Point(e.clientX - canvas.offsetLeft + getScroll().x, e.clientY - canvas.offsetTop + getScroll().y);
      pos.button = e.button;

      for (i = objs.length-1; i >= 0; i--) {
         if (objs[i].isInside(pos)) {
            objs[i].onMouseDown(pos);
            break;
         }
      }

      this.onMouseDown(pos);
   };

   canvas.onmouseup = function(e) {
      var pos = new Point(e.clientX - canvas.offsetLeft + getScroll().x, e.clientY - canvas.offsetTop + getScroll().y);
      for (i = objs.length-1; i >= 0; i--) {
         if (objs[i].isInside(pos)) {
            objs[i].onMouseUp(pos);
            break;
         }
      }

      this.onMouseUp(pos);
   };
}




var avatar1, avatar2, background, lbl1, lbl2;

function splash_init() {
   background = new Anim({ 'img':medias[2], 'scale':500, 'opacity':0.2, 'x':-60, 'y':-50, 'width':75, 'height':75 });

   avatar1 = new Anim({ 'scale':0, 'opacity':0, 'img':medias[0], 'x':80, 'y':65, 'width':100, 'height':100 });
   avatar1.animate({ 'scale':100, 'opacity':1, 'duration':0.5 }, function() {
      lbl1 = new Label({ 'text':'@Masque', 'x': -170, 'y':140, 'font':'25px sans-serif' });
      lbl1.animate({'to':new Point(13, 140), 'duration':1, 'effect':'>'}, function() {
      
         avatar2 = new Anim({ 'scale':0, 'opacity':0, 'img':medias[1], 'x':230, 'y':65, 'width':130, 'height':90 });
         avatar2.animate({ 'scale':100, 'opacity':1, 'duration':0.5 }, function() {
            
            lbl2 = new Label({ 'text':'DJ Wooooo', 'x': 300, 'y':140, 'font':'25px sans-serif' });
            lbl2.animate({'to':new Point(160, 140), 'duration':1, 'effect':'bounce'});
         });
      });
   });


}


fw.main('canvas', 30, 300, 150, 1,
   fw.Loader.extend({
      files:["avatar1.png", "avatar2.png", "record.png"],
      end: function() {
         switchState('splash');
      }
   })
);
