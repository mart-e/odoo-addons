# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ResCurrency(models.Model):
    _name = "crypto.currency.asset"


    @api.depends('currency_id', 'quantity', 'company_id')
    def _get_asset_value(self):
        for asset in self:
            if not asset.currency_id or not asset.company_currency_id:
                continue
            asset.value = asset.currency_id.compute(
                asset.quantity, asset.company_currency_id)

    currency_id = fields.Many2one('res.currency', string="Asset")
    quantity = fields.Float()

    company_id = fields.Many2one('res.company', required=True,
        default=lambda s:s.env.user.company_id)
    company_currency_id = fields.Many2one('res.currency', readonly=True,
        related='company_id.currency_id', store=True)
    value = fields.Monetary(compute='_get_asset_value',
        currency_field='company_currency_id')


