odoo.define('sale_tokopedia.TokopediaButtonMenu', function(require) {
    "use strict";

var Widget = require('web.Widget');
var core = require('web.core');
var SystrayMenu = require('web.SystrayMenu');
var TokopediaButtonMenu = Widget.extend({    
    template:'TokopediaButtonMenu',
    events: {
        "click": "on_click"
    },
    on_click: function (event) {
        var self = this;
        var _t = core._t;
        self.do_action({
            type: 'ir.actions.act_window',
            name: _t('Tokopedia Sync Order'),
            res_model: 'merchant.tokopedia.wizard',
            view_type: 'form',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
        });
    }
});
SystrayMenu.Items.push(TokopediaButtonMenu);

return TokopediaButtonMenu;
});