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
import requests
import re

from odoo.addons.meli_oerp.models import versions
from odoo.addons.meli_oerp.models.versions import *

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    meli_order_item_payment_id = fields.Char('Meli Order Item Payment Id')
    meli_order_item_sku = fields.Char('Meli Order Item SKU')

SaleOrderLine()

class SaleOrder(models.Model):

    _inherit = "sale.order"


    def _meli_margen_real( self):
        for ord in self:
            #Margen de la venta: Precio unitario - Costo - Comision - Envio (no quita el impuesto como margen)
            ord.meli_margen_real = 0
            for item in ord.order_line:
                if item.product_id.default_code == "ENVIO":
                    ord.meli_margen_real-= ord.purchase_price;
                else if item.product_id.default_code == "COMISIONML":
                    ord.meli_margen_real-= ord.purchase_price;
                else:
                    ord.meli_margen_real+= ( ord.price_unit- ord.purchase_price ) * ord.product_uom_qty;


    meli_margen_real = fields.Float(string="Margen Real (ML)", help="Forumla: (Precio_unitario sin impuesto - costo producto) x cantidad - costo comision - costo envio" compute=_meli_margen_real,store=True,index=True)

    def confirm_ml_financial( self, meli=None, config=None, force=False ):

        _logger.info("meli_oerp_financial confirm_ml_financial config:"+str(config and config.name))
        company = (config and 'company_id' in config._fields and config.company_id) or self.env.user.company_id
        config = config or company

        sorder = self
        saleorderline_obj = self.env['sale.order.line']

        #agregar ids
        if "mercadolibre_order_add_fea" in config and config.mercadolibre_order_add_fea:

            if "per_item" in config.mercadolibre_order_add_fea:

                for morder in sorder.meli_orders:
                    #_logger.info("meli_oerp_financial confirm_ml_financial morder:"+str(morder and morder.name))
                    order_item = morder.order_items and morder.order_items[0]
                    order_item_id = (order_item and order_item.order_item_id) or ""
                    order_item_variation_id = (order_item and order_item.order_item_variation_id) or ""

                    meli_order_item_id = str("FEA ")+str(order_item_id)
                    meli_order_item_variation_id = str("FEA ")+str(order_item_variation_id)
                    fea_amount = morder.fee_amount

                    product_fea = "mercadolibre_product_fea" in config and config.mercadolibre_product_fea

                    if not product_fea:
                        product_fea = self.env["product.product"].search( ['|','|',('default_code','ilike','COMISION_ML'),('default_code','ilike','COMISIONML'),('default_code','ilike','COMISION ML')], limit=1 )

                    if not product_fea:
                        continue;

                    com_name = ((product_fea and product_fea.display_name) or "COMISION ")
                    com_name+=  str(" ")+ str(meli_order_item_id)
                    if (order_item and order_item.product_id and order_item.product_id.default_code):
                        com_name+= str(" ") + str(order_item.product_id.default_code)

                    saleorderline_item_fields = {
                        'company_id': company.id,
                        'order_id': sorder.id,
                        'meli_order_item_id': meli_order_item_id,
                        'meli_order_item_variation_id': meli_order_item_variation_id,
                        'purchase_price': float(fea_amount),
                        'price_unit': float(0.0),
                        'product_id': (product_fea and product_fea.id),
                        'product_uom_qty': 1.0,
                        'product_uom': (product_fea and product_fea.uom_id.id),
                        'name': com_name,
                    }
                    #saleorderline_item_fields.update( self._set_product_unit_price( product_related_obj=product_related_obj, Item=Item, config=config ) )

                    saleorderline_item_ids = saleorderline_obj.search( [('meli_order_item_id','=',meli_order_item_id),
                                                                        ('meli_order_item_variation_id','=',meli_order_item_variation_id),
                                                                        ('order_id','=',sorder.id)] )

                    if not saleorderline_item_ids:
                        saleorderline_item_ids = saleorderline_obj.sudo().create( ( saleorderline_item_fields ))
                    else:
                        saleorderline_item_ids.sudo().write( ( saleorderline_item_fields ) )

                if sorder.meli_shipping_list_cost and sorder.carrier_id:
                    delivery_line = get_delivery_line( sorder )
                    if delivery_line:
                        delivery_line.sudo().write({'purchase_price': float(sorder.meli_shipping_list_cost) } )

            if "grouped" in config.mercadolibre_order_add_fea:

                morder = sorder.meli_orders[0]
                #_logger.info("meli_oerp_financial confirm_ml_financial morder:"+str(morder and morder.name))
                order_item = morder.order_items and morder.order_items[0]
                order_item_id = (morder.pack_id) or (order_item and order_item.order_item_id) or ""
                order_item_variation_id = ""

                meli_order_item_id = str("FEA ")+str(order_item_id)
                meli_order_item_variation_id = str("FEA ")+str(order_item_variation_id)
                fea_amount = morder.fee_amount

                product_fea = "mercadolibre_product_fea" in config and config.mercadolibre_product_fea

                if not product_fea:
                    product_fea = self.env["product.product"].search( ['|','|',('default_code','ilike','COMISION_ML'),('default_code','ilike','COMISIONML'),('default_code','ilike','COMISION ML')], limit=1 )

                if not product_fea:
                    return

                com_name = ((product_fea and product_fea.display_name) or "COMISION ")
                #com_name+=  str(" ")+ str(meli_order_item_id)
                com_name+= str(" ") + str(sorder.name)

                saleorderline_item_fields = {
                    'company_id': company.id,
                    'order_id': sorder.id,
                    'meli_order_item_id': meli_order_item_id,
                    'meli_order_item_variation_id': meli_order_item_variation_id,
                    'purchase_price': float(fea_amount),
                    'price_unit': float(0.0),
                    'product_id': (product_fea and product_fea.id),
                    'product_uom_qty': 1.0,
                    'product_uom': (product_fea and product_fea.uom_id.id),
                    'name': com_name,
                }
                #saleorderline_item_fields.update( self._set_product_unit_price( product_related_obj=product_related_obj, Item=Item, config=config ) )

                #saleorderline_item_ids = saleorderline_obj.search( [('meli_order_item_id','=',meli_order_item_id),
                #                                                    ('meli_order_item_variation_id','=',meli_order_item_variation_id),
                #                                                    ('order_id','=',sorder.id)] )
                saleorderline_item_ids = saleorderline_obj.search( [('product_id','=',(product_fea and product_fea.id)),
                                                                    ('order_id','=',sorder.id)] )

                if not saleorderline_item_ids:
                    saleorderline_item_ids = saleorderline_obj.sudo().create( ( saleorderline_item_fields ))
                else:
                    saleorderline_item_ids.sudo().write( ( saleorderline_item_fields ) )


                if sorder.meli_shipping_list_cost and sorder.carrier_id:
                    try:
                        _logger.info("carrier: "+str(sorder.carrier_id and sorder.carrier_id.name))
                        delivery_line = get_delivery_line( sorder )
                        if delivery_line:
                            delivery_line.sudo().write({'purchase_price': float(sorder.meli_shipping_list_cost) } )
                        else:
                            set_delivery_line(sorder, 0.0, "costo de envío" )
                            delivery_line = get_delivery_line( sorder )
                            if delivery_line:
                                delivery_line.sudo().write({'purchase_price': float(sorder.meli_shipping_list_cost) } )
                    except Exception as E:
                        _logger.error(E, exc_info=True)
                        pass;

        #_logger.info("meli_oerp_financial confirm_ml_financial ended")
        #costs for products
        for oline in sorder.order_line:
            _logger.info("updating purchase price: "+str(oline))
            if oline.meli_order_item_id:
                pp = oline.product_id
                _logger.info("updating purchase price product_id: "+str(oline.product_id))
                if pp and pp["variant_seller_ids"]:
                    costs = pp.variant_seller_ids and pp.variant_seller_ids[0] and pp.variant_seller_ids[0].price
                    _logger.info("updating purchase price product_id purchase_price: "+str(costs))
                    if costs:
                        oline.sudo().write({'purchase_price': float(costs) } )


    #try to update order before confirmation (quotation)
    def confirm_ml( self, meli=None, config=None ):

        _logger.info("meli_oerp_financial confirm_ml: config:"+str(config and config.name))

        company = (config and 'company_id' in config._fields and config.company_id) or self.env.user.company_id
        config = config or company

        self.confirm_ml_financial( meli=meli, config=config )

        super(SaleOrder, self).confirm_ml( meli=meli, config=config )

        #seleccionar en la confirmacion del stock.picking la informacion del carrier
        #
        #_logger.info("meli_oerp_financial confirm_ml ended.")


class MercadolibreOrder(models.Model):

    _inherit = "mercadolibre.orders"


    def prepare_sale_order_vals( self, meli=None, order_json=None, config=None, sale_order=None, shipment=None ):
        meli_order_fields = super(MercadolibreOrder, self).prepare_sale_order_vals(meli=meli, order_json=order_json, config=config, sale_order=sale_order, shipment=shipment )

        #meli_order_fields.update({'warehouse_id': wh_id.id })

        #_logger.info("prepare_sale_order_vals > meli_order_fields:"+str(meli_order_fields))

        return meli_order_fields
