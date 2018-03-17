# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class ResCurrencyAssetReport(models.Model):
    _name = "crypto.currency.asset.report"
    _auto = False
    _rec_name = 'currency_id'

    currency_id = fields.Many2one('res.currency', string="Asset", readonly=True)
    quantity = fields.Float(readonly=True)
    total_value = fields.Float(readonly=True)
    rate_date = fields.Date(readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    # company_currency_id = fields.Many2one('res.currency', readonly=True)

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(a.id) as id,
                    a.currency_id as currency_id,
                    sum(a.quantity) as quantity,
                    sum(a.quantity / COALESCE(cr.rate, 1.0)) as total_value,
                    cr.date_start as rate_date,
                    a.company_id as company_id
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
            crypto_currency_asset a
            LEFT JOIN currency_rate cr
            ON (cr.currency_id = a.currency_id
                AND cr.company_id = a.company_id
                AND cr.date_start <= now()
                AND (cr.date_end is null or cr.date_end > now()))
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY a.currency_id,
                    a.company_id,
                    cr.date_start
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
        )""" % (self._table, self._select(), self._from(), self._group_by()))
