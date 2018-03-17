# -*- coding: utf-8 -*-

import logging
import time
import requests
from urllib.parse import urljoin

from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


API_END_POINT = "https://api.coinmarketcap.com/v1/"
SUPPORTED_CURRENCIES = ["AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR"]

class RateSync(models.TransientModel):
    _name = "crypto.currency.rate.sync"

    def _get_default_currency(self):
        if self.env.context.get('active_id') and \
            self.env.context.get('active_model') == 'res.currency':
            return self.env.context['active_id']

        return self.env['res.currency'].search([('name', '=', 'BTC')])

    sync_type = fields.Selection([
        ('top', 'Import Top Currencies'),
        ('one', 'A Specific Currency'),
        ('all', 'All Currency'),
        ], default='top', required=True,
        help="Syncrhonize with CoinMarketCap.com\n"
             "Import option will fetch the top 50 currencies and create the "
             "missing currencies.",
        string="Sync Type")
    currency_id = fields.Many2one('res.currency',
        default=_get_default_currency)

    def _sync_top_rates(self, base_currency, limit=50):
        ResCurrency = self.env['res.currency']
        ResCurrencyRate = self.env['res.currency.rate']

        url = urljoin(API_END_POINT, "ticker/")
        try:
            req = requests.get(url, params={
                'limit':limit, 'convert': base_currency.name,
            })
        except requests.exceptions.RequestException as e:
            _logger.error("Call to %s failed. Error: %s", url, str(e))
            return False

        for currency in req.json():
            code = currency['symbol']
            name = currency['id']
            c = ResCurrency.with_context(active_test=True).search(
                [('name', '=', code)])
            if not c:
                c = ResCurrency.create({
                    'name': code,
                    'active': True,
                    'currency_unit_label': name,
                    'rounding': 0.000001,
                    'symbol': code,
                })
            else:
                c.write({
                    'active': True,
                    'currency_unit_label': name,
                    'symbol': code,
                })
            date = time.strftime("%Y-%m-%d", time.gmtime(int(currency['last_updated'])))
            if ResCurrencyRate.search_count([('name', '=', date), ('currency_id', '=', c.id)]):
                # unicity constrain, one rate per day
                continue
            # e.g. price_eur
            rate = currency['price_'+base_currency.name.lower()]
            ResCurrencyRate.create({
                'name': date,
                'rate': 1/float(rate),
                'currency_id': c.id,
            })

        return True

    def _sync_all_currency_rate(self, base_currency):
        raise UserError(_("Disabled, too many requests"))
        ResCurrency = self.env['res.currency']

        for currency in ResCurrency.search([('rounding', '<', 0.01)]):
            try:
                self._sync_currency_rate(currency, base_currency)
            except UserError as e:
                _logger.warn(e.name)

    def _sync_currency_rate(self, currency, base_currency):
        ResCurrency = self.env['res.currency']
        ResCurrencyRate = self.env['res.currency.rate']

        url = urljoin(urljoin(API_END_POINT, "ticker/"), currency.currency_unit_label)
        try:
            req = requests.get(url, params={
                'convert': base_currency.name,
            })
        except requests.exceptions.RequestException as e:
            _logger.error("Call to %s failed. Error: %s", url, str(e))
            return False

        res = req.json()
        if isinstance(res, dict) and res.get('error'):
            raise UserError(_("Could not sync %s, error:") % currency.currency_unit_label +
                             '\n' + res['error'])

        date = time.strftime("%Y-%m-%S", time.gmtime(int(res[0]['last_updated'])))
        if ResCurrencyRate.search_count([('name', '=', date), ('currency_id', '=', currency.id)]):
            # unicity constrain, one rate per day
            return True

        # e.g. price_eur
        rate = res[0]['price_'+base_currency.name.lower()]
        ResCurrencyRate.create({
            'name': date,
            'rate': 1/float(rate),
            'currency_id': currency.id,
        })


    def action_sync_rate(self):
        ResCurrency = self.env['res.currency']
        ResCurrencyRate = self.env['res.currency.rate']

        base_currency = ResCurrency.search([], order='id asc').filtered(lambda c: c.rate == 1)
        if not base_currency:
            raise UserError(_("No reference currency found, please use one with rate 1.0"))
        base_currency = base_currency[0]
        if base_currency.name.upper() not in SUPPORTED_CURRENCIES:
            raise UserError(_("Unsupported reference currency %s, please use USD or EUR") % base_currency.name)

        if self.sync_type == 'top':
            return self._sync_top_rates(base_currency)
        elif self.sync_type == 'one' and self.currency_id:
            return self._sync_currency_rate(self.currency_id, base_currency)
        elif self.sync_type == 'all':
            return self._sync_all_currency_rate(base_currency)
        return False

