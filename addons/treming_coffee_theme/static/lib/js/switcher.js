/*!
 * jquery-switcher v3.2.0
 * Flexible switcher menu using jQuery, iScroll and CSS.
 * http://git.blivesta.com/switcher
 * License : MIT
 * Author : blivesta <design@blivesta.com> (http://blivesta.com/)
 */

;(function umd(factory) {
  'use strict';
  if (typeof define === 'function' && define.amd) {
    define(['jquery'], factory);
  } else if (typeof exports === 'object') {
    module.exports = factory(require('jquery'));
  } else {
    factory(jQuery);
  }
}(function Switcher($) {
  'use strict';
  var namespace = 'switcher';
  var touches = typeof document.ontouchstart != 'undefined';
  var __ = {
    init: function init(options) {
      options = $.extend({
        iscroll: {
          mouseWheel: true,
          preventDefault: false
        },
        showOverlay: true
      }, options);

      __.settings = {
        state: false,
        events: {
          opened: 'switcher.opened',
          closed: 'switcher.closed'
        },
        dropdownEvents: {
          opened: 'shown.bs.dropdown',
          closed: 'hidden.bs.dropdown'
        }
      };

      __.settings.class = $.extend({
        nav: 'switcher-nav',
        toggle: 'switcher-toggle',
        overlay: 'switcher-overlay',
        open: 'switcher-open',
        close: 'switcher-close',
        dropdown: 'switcher-dropdown'
      }, options.class);

      return this.each(function instantiateSwitcher() {
        var _this = this;
        var $this = $(this);
        var data = $this.data(namespace);

        if (!data) {
          options = $.extend({}, options);
          $this.data(namespace, { options: options });

          __.refresh.call(_this);

          if (options.showOverlay) {
            __.addOverlay.call(_this);
          }

          $('.' + __.settings.class.toggle).on('click.' + namespace, function toggle() {
            __.toggle.call(_this);
            return _this.iScroll.refresh();
          });

          $(window).resize(function close() {
            __.close.call(_this);
            return _this.iScroll.refresh();
          });

          $('.' + __.settings.class.dropdown)
            .on(__.settings.dropdownEvents.opened + ' ' + __.settings.dropdownEvents.closed, function onOpenedOrClosed() {
              return _this.iScroll.refresh();
            });
        }

      }); // end each
    },

    refresh: function refresh() {
      this.iScroll = new IScroll(
        '.' + __.settings.class.nav,
        $(this).data(namespace).options.iscroll
      );
    },

    addOverlay: function addOverlay() {
      var _this = this;
      var $this = $(this);
      var $overlay = $('<div>').addClass(__.settings.class.overlay + ' ' + __.settings.class.toggle);

      return $this.append($overlay);
    },

    toggle: function toggle() {
      var _this = this;

      if (__.settings.state) {
        return __.close.call(_this);
      } else {
        return __.open.call(_this);
      }
    },

    open: function open() {
      var $this = $(this);

      if (touches) {
        $this.on('touchmove.' + namespace, function disableTouch(event) {
          event.preventDefault();
        });
      }

      return $this
        .removeClass(__.settings.class.close)
        .addClass(__.settings.class.open)
        .css({ 'overflow': 'hidden' })
        .switcherCallback(function triggerOpenedListeners() {
          __.settings.state = true;
          $this.trigger(__.settings.events.opened);
        });
    },

    close: function close() {
      var $this = $(this);

      if (touches) $this.off('touchmove.' + namespace);

      return $this
        .removeClass(__.settings.class.open)
        .addClass(__.settings.class.close)
        .css({ 'overflow': 'auto' })
        .switcherCallback(function triggerClosedListeners() {
          __.settings.state = false;
          $this.trigger(__.settings.events.closed);
        });
    },

    destroy: function destroy() {
      return this.each(function destroyEach() {
        var $this = $(this);
        $(window).off('.' + namespace);
        $this.removeData(namespace);
      });
    }

  };

  $.fn.switcherCallback = function switcherCallback(callback) {
    var end = 'transitionend webkitTransitionEnd';
    return this.each(function setAnimationEndHandler() {
      var $this = $(this);
      $this.on(end, function invokeCallbackOnAnimationEnd() {
        $this.off(end);
        return callback.call(this);
      });
    });
  };

  $.fn.switcher = function switcher(method) {
    if (__[method]) {
      return __[method].apply(this, Array.prototype.slice.call(arguments, 1));
    } else if (typeof method === 'object' || !method) {
      return __.init.apply(this, arguments);
    } else {
      $.error('Method ' + method + ' does not exist on jQuery.' + namespace);
    }
  };

}));
