# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O##########S##################
from dateutil.parser import parse
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Importwoocommercepartners(models.TransientModel):
    _name = "import.woocommerce.partners"
    _inherit = 'import.partners'
    _description = "Import Woocommerce Partners"

    def import_now(self, **kwargs):
        data_list = []
        woocommerce = self._context.get('woocommerce')
        customer_id = kwargs.get('woocommerce_object_id')
        if customer_id:
            data_list = self.get_customer_by_id(woocommerce, customer_id)
        elif kwargs.get('woocommerce_import_date_from'):
            data_list = self._filter_customer_using_date(woocommerce, **kwargs)
        else:
            data_list = self.get_customer_all(woocommerce, **kwargs)
        return data_list

    def _filter_customer_using_date(self, woocommerce, **kwargs):
        if woocommerce:
            vals_list = []
            date_created = None
            partner_data = woocommerce.get(
                'customers',
                params={
                    'after': kwargs.get('woocommerce_import_date_from'),
                    'page': kwargs.get('page'),
                    'per_page': kwargs.get('page_size')
                }
            ).json()
            if "message" in partner_data:
                _logger.info("Error in Importing Customers : %r",partner_data["message"])
                if not kwargs.get("from_cron"):
                    raise UserError("Error in Importing Customers : {}".format(partner_data["message"]))
            if partner_data:
                for data in partner_data:
                    vals_list.append(self.get_contact_address(data))
                if kwargs.get("from_cron"):
                    date_created = partner_data[-1].get("date_created")
                    self.channel_id.import_customer_date = parse(date_created)
            return vals_list

    def get_customer_all(self, woocommerce, **kwargs):
        vals_list = []
        partner_data = woocommerce.get(
            'customers',
            params={
                'page': kwargs.get('page'),
                'per_page': kwargs.get('page_size'),
                'order': 'asc'
            }
        ).json()
        if "message" in partner_data:
            _logger.info("Error in Importing Customers : %r",partner_data["message"])
            raise UserError("Error in Importing Customers : {}".format(str(partner_data["message"])))
        if partner_data:
            for data in partner_data:
                vals_list.append(self.get_contact_address(data))
        return vals_list

    def get_contact_address(self, data):
        if data:
            channel_id = self.channel_id.id
            store_id = data.get('id')
            return {
                'channel_id': channel_id,
                'store_id'  : data.get('id'),
                'name'      : data.get('first_name'),
                'last_name' : data.get('last_name'),
                'email'     : data.get('email'),
                'contacts'  : [
                    {
                        'channel_id'  : channel_id,
                        'parent_id'   : store_id,
                        'store_id'    : f'billing_{store_id}',
                        'type'        : 'invoice',
                        'name'        : data['billing'].get('first_name'),
                        'last_name'   : data['billing'].get('last_name'),
                        'street'      : data['billing'].get('address_1'),
                        'street2'     : data['billing'].get('address_2'),
                        'city'        : data['billing'].get('city'),
                        'state_code'  : data['billing'].get('state'),
                        'country_code': data['billing'].get('country'),
                        'zip'         : data['billing'].get('postcode'),
                        'email'       : data['billing'].get('email'),
                        'phone'       : data['billing'].get('phone'),
                    },
                    {
                        'channel_id'  : channel_id,
                        'parent_id'   : store_id,
                        'store_id'    : f'shipping_{store_id}',
                        'type'        : 'delivery',
                        'name'        : data['shipping'].get('first_name'),
                        'last_name'   : data['shipping'].get('last_name'),
                        'street'      : data['shipping'].get('address_1'),
                        'street2'     : data['shipping'].get('address_2'),
                        'city'        : data['shipping'].get('city'),
                        'state_code'  : data['shipping'].get('state'),
                        'country_code': data['shipping'].get('country'),
                        'zip'         : data['shipping'].get('postcode'),
                        'phone'       : data['shipping'].get('phone'),
                    }
                ],
            }

    def get_customer_by_id(self, woocommerce, customer_id):
        vals_list = []
        partner_data = woocommerce.get(f'customers/{customer_id}').json()
        if "message" in partner_data:
            _logger.info("Error in Importing Customers : %r",partner_data["message"])
            raise UserError("Error in Importing Customers : {}".format(str(partner_data["message"])))
        if partner_data:
            vals_list.append(self.get_contact_address(partner_data))
        return vals_list
