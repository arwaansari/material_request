{
    'name': 'Material Request',
    'sequence': '-1',
    'version': '16.0.1.0.0',
    'installable': True,
    'application': True,

    'depends': ['base', 'hr', 'stock', 'purchase'],
    'data': ['security/ir.model.access.csv',
             'security/security_group.xml',
             'views/material_request_view.xml',
             'views/purchase_order_view.xml',
             'views/stock_picking.xml',
             'views/material_request_menu.xml'
             ]
}