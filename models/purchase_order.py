from odoo import models, fields


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    material_req_id = fields.Many2one('material.request')

