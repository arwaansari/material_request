from odoo import models, fields


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    material_req_id = fields.Many2one('material.request')
