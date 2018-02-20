odoo.define('google_calendar.google_calendar', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var framework = require('web.framework');
var pyeval = require('web.pyeval');
var CalendarView = require('web_calendar.CalendarView');

var _t = core._t;
var QWeb = core.qweb;

CalendarView.include({
    init: function(parent, dataset, fields_view, options){
        var self = this;
        this._super.apply(this, arguments);
        this.events = _.extend(this.events || {}, {
            'click .o_google_sync_button': function() {
                self.sync_calendar(self.fields_view);
            },
        });
    },
    sync_calendar: function(res, button) {
        var self = this;
        var context = pyeval.eval('context');
        this.$google_button.prop('disabled', true);

        this.rpc('/google_calendar/sync_data', {
            arch: res.arch,
            fields: res.fields,
            model: res.model,
            fromurl: window.location.href,
            local_context: context,
        }).done(function(o) {
            if (o.status === "need_auth") {
                Dialog.alert(self, _t("¡Serás redirigido a Google para autorizar el acceso a tu calendario!"), {
                    confirm_callback: function() {
                        framework.redirect(o.url);
                    },
                    title: _t('Redirección'),
                });
            } else if (o.status === "need_config_from_admin") {
                if (!_.isUndefined(o.action) && parseInt(o.action)) {
                    Dialog.confirm(self, _t("La Sincronización de Google necesita configurarse antes de poder usarla, ¿quieres hacerlo ahora?"), {
                        confirm_callback: function() {
                            self.do_action(o.action);
                        },
                        title: _t('Configuración'),
                    });
                } else {
                    Dialog.alert(self, _t("¡Se necesita configurar la Sincronización de Google antes de poder usarla!"), {
                        title: _t('Configuración'),
                    });
                }
            } else if (o.status === "need_refresh") {
                self.$calendar.fullCalendar('refetchEvents');
            } else if (o.status === "need_reset") {
                var confirm_text1 = _t("¡La cuenta que está intentando sincronizar (%s) no es la misma que la última (%s)!");
                var confirm_text2 = _t("Para hacer esto, primero necesita desconectar todos los eventos existentes de la cuenta anterior.");
                var confirm_text3 = _t("¿Quieres hacer esto ahora?");
                var text = _.str.sprintf(confirm_text1 + "\n" + confirm_text2 + "\n\n" + confirm_text3, o.info.new_name, o.info.old_name);
                Dialog.confirm(self, text, {
                    confirm_callback: function() {
                        self.rpc('/google_calendar/remove_references', {
                            model: res.model,
                            local_context: context,
                        }).done(function(o) {
                            if (o.status === "OK") {
                                Dialog.alert(self, _t("Todos los eventos han sido desconectados de su cuenta anterior. Ahora puede reiniciar la sincronización"), {
                                    title: _t('Desconexión de evento éxitoso'),
                                });
                            } else if (o.status === "KO") {
                                Dialog.alert(self, _t("Se produjo un error al desconectar eventos de su cuenta anterior. Vuelva a intentarlo ."), {
                                    title: _t('Desconexión de evento'),
                                });
                            } // else NOP
                        });
                    },
                    title: _t('Cuentas'),
                });
            }
        }).always(function(o) { self.$google_button.prop('disabled', false); });
    },
    extraSideBar: function() {
        var self = this;
        var result = this._super();
        this.$google_button = $();
        if (this.dataset.model === "calendar.event") {
            return result.then(function() {
                this.$google_button = $('<button/>', {type: 'button', html: _t("Sincronizar <b>Google</b>")})
                                    .addClass('o_google_sync_button oe_button btn btn-sm btn-default')
                                    .prepend($('<img/>', {
                                        src: "/google_calendar/static/src/img/calendar_32.png",
                                    }))
                                    .prependTo(self.$('.o_calendar_filter'));
            });
        }
        return result;
    },
});

});
