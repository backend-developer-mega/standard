/* Copyright 2016. Licensed by UNIBRAVO. */

odoo.define('app', function(require) {
    'use strict';

	var core = require('web.core');
	var Menu = require('web.Menu');

    var Class = require('web.Class');
	var Widget = require('web.Widget');

    var SearchView = require('web.SearchView');

    Menu.include({

        // to prevent app icons from going into more menu
        reflow: function() {
            this._super('all_outside');
        },

        /* Overload to collapse unwanted visible submenus */
        open_menu: function(id, allowOpen) {
            this._super(id);
            if (allowOpen) return;
            var $clicked_menu = this.$secondary_menus.find('a[data-menu=' + id + ']');
            $clicked_menu.parents('.oe_secondary_submenu').css('display', '');
        },

    });

    SearchView.include({

        // Prevent focus of search field on mobile devices
        toggle_visibility: function (is_visible) {
            $('div.o_searchview_input').last()
                .one('focus', $.proxy(this.preventMobileFocus, this));
            return this._super(is_visible);
        },

        // It prevents focusing of search el on mobile
        preventMobileFocus: function(event) {
            if (this.isMobile()) {
                event.preventDefault();
            }
        },

        // For lack of Modernizr, TouchEvent will do
        isMobile: function () {
            try{
                document.createEvent('TouchEvent');
                return true;
            } catch (ex) {
                return false;
            }
        },

    });

    var AppSwitcher = Class.extend({

        LEFT: 'left',
        RIGHT: 'right',
        UP: 'up',
        DOWN: 'down',

        isOpen: false,
        keyBuffer: '',
        keyBufferTime: 500,
        keyBufferTimeoutEvent: false,
        dropdownHeightFactor: 0.90,
        initialized: false,

        init: function() {
            this.directionCodes = {
                'left': this.LEFT,
                'right': this.RIGHT,
                'up': this.UP,
                'pageup': this.UP,
                'down': this.DOWN,
                'pagedown': this.DOWN,
                '+': this.RIGHT,
                '-': this.LEFT,
            };
            this.initSwitcher();
            var $clickZones = $('.o_main, ' +
                                'a.oe_menu_leaf, ' +
                                'a.oe_menu_toggler'
                                );
            $clickZones.click($.proxy(this.handleClickZones, this));
            core.bus.on('resize', this, this.handleWindowResize);
            core.bus.on('keydown', this, this.handleNavKeys);
        },

        // It provides initialization handlers for Switcher
        initSwitcher: function() {
            this.$el = $('.switcher');
            this.$el.switcher();
            this.$el.one('switcher.opened', $.proxy(this.onSwitcherOpen, this));
            this.$el.on('switcher.opened', function setIScrollProbes(){
                var onIScroll = function() {
                    var transform = (this.iScroll.y) ? this.iScroll.y * -1 : 0;
                    $(this).find('#appSwitcherAppPanelHead').css(
                        'transform', 'matrix(1, 0, 0, 1, 0, ' + transform + ')'
                    );
                };
                this.iScroll.options.probeType = 2;
                this.iScroll.on('scroll', $.proxy(onIScroll, this));
            });
            this.initialized = true;
        },

        // It provides handlers to hide switcher when "unfocused"
        handleClickZones: function() {
            this.$el.switcher('close');
            $('.o_sub_menu_content')
                .parent()
                .collapse('hide');
        },

        // It resizes bootstrap dropdowns for screen
        handleWindowResize: function() {
            $('.dropdown-scrollable').css(
                'max-height', $(window).height() * this.dropdownHeightFactor
            );
        },

        // It provides keyboard shortcuts for app switcher nav
        handleNavKeys: function(e) {
            if (!this.isOpen){
                return;
            }
            var directionCode = $.hotkeys.specialKeys[e.keyCode.toString()];
            if (Object.keys(this.directionCodes).indexOf(directionCode) !== -1) {
                var $link = this.findAdjacentAppLink(
                    this.$el.find('a:first, a:focus').last(),
                    this.directionCodes[directionCode]
                );
                this.selectAppLink($link);
            } else if ($.hotkeys.specialKeys[e.keyCode.toString()] == 'esc') {
                this.handleClickZones();
            } else {
                var buffer = this.handleKeyBuffer(e.keyCode);
                this.selectAppLink(this.searchAppLinks(buffer));
            }
        },

        /* It adds to keybuffer, sets expire timer, and returns buffer
         * @returns str of current buffer
         */
        handleKeyBuffer: function(keyCode) {
            this.keyBuffer += String.fromCharCode(keyCode);
            if (this.keyBufferTimeoutEvent) {
                clearTimeout(this.keyBufferTimeoutEvent);
            }
            this.keyBufferTimeoutEvent = setTimeout(
                $.proxy(this.clearKeyBuffer, this),
                this.keyBufferTime
            );
            return this.keyBuffer;
        },

        clearKeyBuffer: function() {
            this.keyBuffer = '';
        },

        /* It performs close actions  */
        onSwitcherClose: function() {
            core.bus.trigger('switcher.closed');
            this.$el.one('switcher.opened', $.proxy(this.onSwitcherOpen, this));
            this.isOpen = false;
            // Remove inline style inserted by switcher.js
            this.$el.css("overflow", "");
        },

        /* It finds app links and register event handlers  */
        onSwitcherOpen: function() {
            this.$appLinks = $('.app-switcher-icon-app').parent();
            this.selectAppLink($(this.$appLinks[0]));
            this.$el.one('switcher.closed', $.proxy(this.onSwitcherClose, this));
            core.bus.trigger('switcher.opened');
            this.isOpen = true;
        },

        // It selects an app link visibly
        selectAppLink: function($appLink) {
            if ($appLink) {
                $appLink.focus();
            }
        },

        /* It returns first App Link by its name according to query    */
        searchAppLinks: function(query) {
            return this.$appLinks.filter(function() {
                return $(this).data('menuName').toUpperCase().startsWith(query);
            }).first();
        },

        /* It returns the link adjacent to $appLink in provided direction.   */
        findAdjacentAppLink: function($appLink, direction) {

            var obj = [],
                $objs = this.$appLinks;

            switch(direction){
                case this.LEFT:
                    obj = $objs[$objs.index($appLink) - 1];
                    if (!obj) {
                        obj = $objs[$objs.length - 1];
                    }
                    break;
                case this.RIGHT:
                    obj = $objs[$objs.index($appLink) + 1];
                    if (!obj) {
                        obj = $objs[0];
                    }
                    break;
                case this.UP:
                    $objs = this.getRowObjs($appLink, this.$appLinks);
                    obj = $objs[$objs.index($appLink) - 1];
                    if (!obj) {
                        obj = $objs[$objs.length - 1];
                    }
                    break;
                case this.DOWN:
                    $objs = this.getRowObjs($appLink, this.$appLinks);
                    obj = $objs[$objs.index($appLink) + 1];
                    if (!obj) {
                        obj = $objs[0];
                    }
                    break;
            }

            if (obj.length) {
                event.preventDefault();
            }

            return $(obj);

        },

        /* It returns els in the same row     */
        getRowObjs: function($obj, $grid) {
            // Filter by object which middle lies within left/right bounds
            function filterWithin(left, right) {
                return function() {
                    var $this = $(this),
                        thisMiddle = $this.offset().left + ($this.width() / 2);
                    return thisMiddle >= left && thisMiddle <= right;
                };
            }
            var left = $obj.offset().left,
                right = left + $obj.outerWidth();
            return $grid.filter(filterWithin(left, right));
        },

    });

    // It inits a new AppSwitcher when the web client is ready
    core.bus.on('web_client_ready', null, function () {
        new AppSwitcher();
    });

    return {
        'AppSwitcher': AppSwitcher,
        'SearchView': SearchView,
        'Menu': Menu,
    };

});
