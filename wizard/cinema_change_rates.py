
from osv import osv, fields

class cinema_change_rates(osv.osv_memory):
    _name = 'cinema.change.rates'

    def _check_percentage(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.percentage<=0:
            return False
        return True
        
    _columns = {
    'info_updates': fields.integer('Number of updated rates',readonly=True),
    'viewer_category_id': fields.many2one('cinema.viewer.category','Viewer category'),
    'session_type_id': fields.many2one('cinema.session.type','Session type'),
    'percentage': fields.float('Percentage to apply', required=True),
    'state':fields.selection([ ('init','Init'), ('done','Done'), ],'State',readonly=True)
    }
    
    _defaults = { 
    'state': lambda *a: 'init'
    }
    
    _constraints = [
        (_check_percentage, 'Percentage must be greater than or equal to zero', ['percentage']),
    ]

    def apply_percentage(self, cr, uid, ids, data, context=None):
        form = self.browse(cr, uid, ids[0])
        percentage = form.percentage
        vc_id = form.viewer_category_id
        st_id = form.session_type_id
        rates_obj = self.pool.get('cinema.rates')
        if vc_id.id>0:
            if st_id.id>0:
                rates_ids = rates_obj.search(cr, uid, [('viewer_category_id','=',vc_id.id),('session_type_id','=',st_id.id)])
            else:
                rates_ids = rates_obj.search(cr, uid, [('viewer_category_id','=',vc_id.id)])
        else:
            if st_id.id>0:
                rates_ids = rates_obj.search(cr, uid, [('session_type_id','=',st_id.id)])
            else:
                rates_ids = rates_obj.search(cr, uid, [])
        for x in rates_ids:
            rate = rates_obj.browse(cr, uid, x)
            values = { 'price': rate.price * percentage }
            rates_obj.write(cr, uid, [x], values)
        values = { 'state':'done', 'info_updates':len(rates_ids), }
        self.write(cr, uid, ids, values)
        return True    

cinema_change_rates()

