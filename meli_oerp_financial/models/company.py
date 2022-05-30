# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, osv, models, api
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

import pdb

#from .meli_oerp_config import *
#from .warning import warning

import requests
#from ..melisdk.meli import Meli

class ResCompany(models.Model):

    _inherit = "res.company"


    mercadolibre_order_add_fea = fields.Selection([ ("manual", "No agregar"),
                                                ("per_item", "Agregar linea de orden de comision por pago/producto"),
                                                ("grouped", "Agregar linea de orden de comision agrupado")],
                                                string='Agregar comisiones a la orden',
                                                help='Agregar comisiones a la orden, por item o agrupado para poder hacer margen de ganancia')

    mercadolibre_product_fea = fields.Many2one("product.product", string="Product Fea")
