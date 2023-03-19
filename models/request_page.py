from odoo import models, fields


class RequestPage(models.Model):
    _name = 'request.page'
    _description = 'Request Page'

    product_id = fields.Many2one('product.product')
    quantity = fields.Integer()
    request_type = fields.Selection(selection=[
        ('purchase_order', 'Purchase Order'),
        ('internal_transfer', 'Internal Transfer')
    ], string='Request Type')
    source_location_id = fields.Many2one('stock.location',
                                         string='Source Location')
    destination_location_id = fields.Many2one('stock.location',
                                              string='Destination Location')
    material_request_id = fields.Many2one('material.request')
