from odoo import models, fields, api, _


class MaterialRequest(models.Model):
    _name = 'material.request'
    _description = 'Material Request'
    _check_company_auto = True

    company_id = fields.Many2one('res.company')
    employee_id = fields.Many2one('res.users', check_company=True)

    name = fields.Char(default=lambda self: _('New'), readonly=True)
    request_ids = fields.One2many('request.page', 'material_request_id')
    purchase_order_id = fields.Many2one('purchase.order')
    po_count = fields.Integer(compute="_compute_po_count")
    internal_transfer_count = fields.Integer(
        compute="_compute_internal_transfer_count")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', required=True, readonly=True, copy=False,
        default='draft')

    def action_submit(self):
        self.write({'state': "to_approve"})

    def action_approve(self):
        self.write({'state': "approved"})
        for rec in self.request_ids:
            if rec.request_type == 'purchase_order':
                for line in rec.product_id.seller_ids:
                    self.env['purchase.order'].create({
                        'partner_id': line.partner_id.id,
                        'material_req_id': self.id,
                        'partner_ref': self.name,
                        'order_line': [(0, 0, {
                            'product_id': rec.product_id.id,
                            'product_qty': rec.quantity,
                            'price_unit': rec.product_id.list_price
                        })]
                    })
            else:
                self.env['stock.picking'].create({
                    'partner_id': self.employee_id.id,
                    'material_req_id': self.id,
                    'location_id': rec.source_location_id.id,
                    'location_dest_id': rec.destination_location_id.id,
                    'picking_type_id': self.env.ref(
                        "stock.picking_type_internal").id,
                    'move_ids': [(0, 0, {
                        'product_id': rec.product_id.id,
                        'product_uom_qty': rec.quantity,
                        'location_id': rec.source_location_id.id,
                        'location_dest_id': rec.destination_location_id.id,
                        'name': rec.product_id.default_code,
                    })]
                })

    def action_reject(self):
        self.write({'state': "rejected"})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New' == 'New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'material.request')
        res = super(MaterialRequest, self).create(vals)
        return res

    def get_purchase_order(self):
        for record in self.request_ids:
            if record.request_type == 'purchase_order':
                vals = {
                    'product_id': record.product_id.id,
                    'product_qty': record.quantity
                }
                purchase_order = self.env['purchase.order'].create(
                    {
                     'partner_id': self.employee_id.id,
                     'order_line': [(0, 0, vals)]
                    })
        if self.po_count == 1:
            return {
                'name': 'Purchase Order',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.order',
                'view_id': self.env.ref(
                    'purchase.purchase_order_form').id,
                'res_id': purchase_order.id
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Purchase Order',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'domain': [('material_req_id', '=', self.id)],
                'context': "{'create': False}"
            }

    def _compute_po_count(self):
        for record in self:
            record.po_count = self.env['purchase.order'].search_count(
                [('material_req_id', '=', self.id)])
            print(record.po_count, 'count')

    def get_internal_transfer(self):
        for record in self.request_ids:
            if record.request_type == 'internal_transfer':
                vals = {
                    'product_id': record.product_id.id,
                    'product_uom_qty': record.quantity,
                    'name': record.product_id.default_code,
                    'location_id': record.source_location_id.id,
                    'location_dest_id': record.destination_location_id.id,

                }
                internal_transfer = self.env['stock.picking'].create(
                    {
                     'partner_id': self.employee_id.id,
                     'location_id': record.source_location_id.id,
                     'location_dest_id': record.destination_location_id.id,
                     'picking_type_id': self.env.ref(
                            "stock.picking_type_internal").id,
                     'move_ids': [(0, 0, vals)]
                    })
        if self.internal_transfer_count == 1:
            return {
                'name': 'Internal Transfer',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'view_id': self.env.ref(
                    'stock.view_picking_form').id,
                'res_id': internal_transfer.id
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Internal Transfer',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'domain': [('material_req_id', '=', self.id)],
                'context': "{'create': False}"
            }

    def _compute_internal_transfer_count(self):
        for record in self:
            print(self)
            print('opop')
            record.internal_transfer_count = self.env['stock.picking'].\
                search_count([('material_req_id', '=', self.id)])
