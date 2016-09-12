##############################################################################
#
# Copyright (c) 2013 Institut Obert de Catalunya (http://ioc.xtec.cat) 
#                    All Rights Reserved.
#                    Author: Isidre Guixà <iguixa@xtec.cat>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.related
#
##############################################################################

from osv import osv, fields
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import time
from tools.translate import _
import pytz
  
# Classe Python per la definició de l'objecte que gestiona els recursos "Sales"
class cinema_screen(osv.osv):
    _name = 'cinema.screen'

    def _check_capacity(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.capacity<=0:
            return False
        return True

    def _check_time(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.cleaning_time<=0:
            return False
        return True

    _constraints = [
        (_check_capacity, 'Capacity must be greater than zero', ['capacity']),
        (_check_time, 'Cleaning time must be greater than zero', ['cleaning_time']),
    ]
    
    _columns = {
      'name': fields.char('Screen',size=30, required=True),
      'capacity': fields.integer('Capacity', required=True),
      'cleaning_time': fields.integer('Cleaning time', required=True, help='Cleaning time in minutes')
    }
    
    _order = 'name'
    
    _sql_constraints = [
        ('name_unique','unique(name)','The name must be unique!')
    ]   
cinema_screen()

# Classe Python per la definició de l'objecte que gestiona els recursos "Categories d'espectadors"
class cinema_viewer_category(osv.osv):
    _name = 'cinema.viewer.category'
    
    _columns = {
      'name': fields.char('Category',size=30, required=True, translate=True),
    }
    
    _order = 'name'
    
    _sql_constraints = [
        ('name_unique','unique(name)','The name must be unique!')
    ]
cinema_viewer_category()

# Classe Python per la definició de l'objecte que gestiona els recursos "Tipus de sessió"
class cinema_session_type(osv.osv):
    _name = 'cinema.session.type'
    
    _columns = {
      'name': fields.char('Session type',size=30, required=True, translate=True),
    }
    
    _order = 'name'
    
    _sql_constraints = [
        ('name_unique','unique(name)','The name must be unique!')
    ]
cinema_session_type()

# Classe Python per la definició de l'objecte que gestiona els recursos "Tarifes"
class cinema_rates(osv.osv):
    _name = 'cinema.rates'

#    El següent mètode no és imprescindible, ja que enlloc és necessari mostrar ni desplegar 
#    les tarifes.
    def name_get (self, cr, uid, ids, context=None):
        st_obj = self.pool.get("cinema.session.type")
        vc_obj = self.pool.get("cinema.viewer.category")
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            session = st.browse(cr, uid, rec.session_type_id)
            viewer = vc.browser(cr, uid, rec.viewer_category_id)
            result[rec.id] = session.name + " - " + viewer.name
        return result

    def _check_price(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.price<0:
            return False
        return True

    _constraints = [
        (_check_price, 'Price must be greater than or equal to zero', ['price']),
    ]

    _columns = {
      'session_type_id': fields.many2one('cinema.session.type','Session type',required=True),
      'viewer_category_id': fields.many2one('cinema.viewer.category','Viewer category',required=True),
      'price': fields.float('Price', required=True)
    }
    
    _sql_constraints = [
        ('rate_unique','unique(session_type_id, viewer_category_id)','The couple (session_type, viewer_category) must be unique!')
    ]
cinema_rates()

# Classe Python per la definició de l'objecte que gestiona els recursos "Directors"
class cinema_director(osv.osv):
    _name = 'cinema.director'

    def _check_dates(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.birthdate and obj.deathdate and obj.deathdate<=obj.birthdate:
          # La comprovació només s'ha de dur a terme si ambdós camps contenen valor
            return False
        return True

    _constraints = [
        (_check_dates, 'Death date must be later than birthdate', ['deathdate,birthdate']),
    ]
    
    _columns = {
      'name': fields.char('Director',size=30, required=True, select=1),
      'country_id': fields.many2one('res.country','Nationality', required=True),
      'birthdate': fields.date('Birthdate'),
      'deathdate': fields.date('Death date'),
#   Donat que la classe "film" incorpora el camp "active" per marcar els films que són "actius" en el cinema,
#   estem obligats a indicar en el "domini" del següent camp, que es vegin tots els films, ja que del contrari
#   només apareixerien els "actius", pel caràcter especial d'aquest camp
      'film_ids': fields.one2many('cinema.film','director_id','Films', readonly='True', domain=['|',('active','=',False),('active','=',True)]),
    }

    _sql_constraints = [
        ('director_unique','unique(name), viewer_category_id)','The director name must be unique!')
    ]
cinema_director()

# Classe Python per la definició de l'objecte que gestiona els recursos "Pel·lícules"
class cinema_film(osv.osv):
    _name = 'cinema.film'
    
    def _check_duration(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.duration<=0:
            return False
        return True

    def _check_year(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.year<1888:
            # Considero que aquest és l'any en què va començar el cinema
            return False
        return True
        
    _constraints = [
        (_check_duration, 'Duration must be greater than zero', ['duration']),
        (_check_year, 'The first film was considered Roundhay Garden Scene in 1888. Accordingly, there can be no previous films this year.', ['year']),
    ]
    
    _columns = {
      'name': fields.char('Film',size=60, translate=True, required=True, select=1),
      'year': fields.integer('Year', required=True),
      'director_id': fields.many2one('cinema.director','Director', required=True),
      'duration': fields.integer('Duration', required=True, help='Duration in minutes'),
      'synopsis': fields.text('Synopsis', translate=True),
      'active': fields.boolean('Active', required=True),
      'web': fields.char('Web',size=60),
      'cover': fields.binary('Cover'),
      'session_ids': fields.one2many('cinema.session','film_id','Sessions', readonly='True'),
    }
    
    _defaults = {
        'active':1,
    }
cinema_film()

# Classe Python per la definició de l'objecte que gestiona els recursos "Sessions"
class cinema_session(osv.osv):
    _name = 'cinema.session'
    
    def _check_init(self, cr, uid, ids, context=None):
        # Cerquem l'objecte que gestiona les sales (per no cercar-lo cada vegada que el necessitem)
        sc_obj = self.pool.get("cinema.screen")
        for obj in self.browse(cr, uid, ids, context=context):
            # Per la sessió que volem xequejar, cerquem totes les sessions que estan a la mateixa
            # sala en la mateixa data o anterior o posterior i que no sigui la mateixa sessió
            d_ini = (datetime.date(datetime.strptime(obj.init,"%Y-%m-%d %H:%M:%S"))-timedelta(1)).strftime("%Y-%m-%d")
            d_fin = (datetime.date(datetime.strptime(obj.init,"%Y-%m-%d %H:%M:%S"))+timedelta(1)).strftime("%Y-%m-%d")
            sessions_id = self.search (cr, uid,['&',('id','!=',[obj.id]),
                                                '&',('screen_id','=',[obj.screen_id.id]),
                                                '&',('init','>=',[d_ini]),('init','<=',[d_fin])])
            # La cerca anterior facilita la llista de id de les sessions.
            # La instrucció següent ens facilita els objectes sessions de la cerca anterior
            sessions = self.browse (cr, uid, sessions_id, context=context)
            # Cerquem el temps de neteja que necessita la sala:
            sala = sc_obj.read (cr, uid, obj.screen_id.id,['cleaning_time'], context=None)
            for s in sessions:
                if (obj.init<=s.init):  # La nostra sessió es compara amb una de posterior
                    # Calculem quan acaba la neteja de la nostra sessió
                    final = datetime.strptime(obj.init,"%Y-%m-%d %H:%M:%S")
                    final = final + timedelta(minutes=obj.film_id.duration)
                    final = final + timedelta(minutes=obj.screen_id.cleaning_time)
                    if (final >= datetime.strptime(s.init,"%Y-%m-%d %H:%M:%S")):
                        raise osv.except_osv(_('Error! '),_('You can not start at this time because it overlaps with the next session!'))
                else:   # La nostra sessió es compara amb una d'anterior
                    # Calculem quan acaba la neteja de la sessió anterior
                    final = datetime.strptime(s.init,"%Y-%m-%d %H:%M:%S")
                    final = final + timedelta(minutes=s.film_id.duration)
                    final = final + timedelta(minutes=s.screen_id.cleaning_time)
                    if (final >= datetime.strptime(obj.init,"%Y-%m-%d %H:%M:%S")):
                        raise osv.except_osv(_('Error! '),_('You can not start at this time because it overlaps with the previous session!'))
        return True

    def _check_n_tickets(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.n_tickets>obj.capacity:
                return False
        return True
        
    _constraints = [
        (_check_init, 'You can not start at this time because it overlaps another session', ['init']),
#   Per distingir si es tracta d'una sessió anterior o posterior, s'ha posat una excepció dins el mètode _check_init
#   En conseqüència, el missatge d'aquesta restricció no apareixerà mai quan hi hagi un error 
        (_check_n_tickets, 'There are not enough tickets!',['n_tickets','capacity']),
#   Per si intentem canviar la sala quan ja s'ha venut tiquets... Comprovació de capacitat...
    ]
   
    def _n_tickets(self, cr, uid, ids, field_name, arg, context):   
        result = {}
        t_obj = self.pool.get("cinema.ticket")
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id]=0
            tickets = t_obj.search(cr, uid,[('session_id','=',rec.id)])
            for t in tickets:
                ticket = t_obj.browse(cr, uid, t, context = context)
                for d in ticket.detail_ids:
                    result[rec.id]=result[rec.id]+d.n_tickets
        return result
        
    def _takings(self, cr, uid, ids, field_name, arg, context):   
        result = {}
        t_obj = self.pool.get("cinema.ticket")
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id]=0
            tickets = t_obj.search(cr, uid,[('session_id','=',rec.id)])
            for t in tickets:
                ticket = t_obj.browse(cr, uid, t, context = context)
                for d in ticket.detail_ids:
                    result[rec.id]=result[rec.id]+d.n_tickets*d.price
        return result

    def name_get (self, cr, uid, ids, context=None):
        screen_obj = self.pool.get("cinema.screen")
        film_obj = self.pool.get("cinema.film")
        result = []
        for rec in self.browse(cr, uid, ids, context=context):
            screen = screen_obj.browse(cr, uid, rec.screen_id.id)
            film = film_obj.browse(cr, uid, rec.film_id.id)
            # rec.init és un camp datetime que emmagatzema a la BD l'hora en la franja horària UTC (GMT-0)
            # I com que el codi Python s'executa en el servidor, resulta que el nom que estem construint,
            # si utilitzem directament rec.init, tindria l'hora en format UTC i, nosaltres que estem en GMT+1
            # o GMT+2 (estiu) no veuríem la data correcta.
            # Això es pot solucionar si l'usuari té, a les seves preferències, la seva zona horària
            # la qual es passa per la clau "tz" dins el context. En conseqüència:
            if context['tz']==False:
                to_zone = pytz.utc;
            else:
                to_zone = pytz.timezone(context['tz'])
            hora_UTC = datetime.strptime(rec.init, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)  
            # hora_UTC conté l'hora "init" com a datetime i en la franja UTC
            hora_tz = hora_UTC.astimezone(to_zone)
            # hora_tz conté l'hora "init" com a datetime i en la franja de la preferència de l'usuari
            result.append((rec.id, hora_tz.strftime("%Y-%m-%d %H:%M") + " - " + screen.name + " - " + film.name))
        return result

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context):
        res = self.name_get(cr, uid, ids, context) 
        return dict(res)
       
    def onchange_sc (self, cr, uid, ids, screen_id):
        result = {}
        if screen_id:
            obj = self.pool.get("cinema.screen")
            screen = obj.browse(cr, uid, screen_id)
            result['capacity'] = screen.capacity
        else:
            result['capacity'] = 0
        return {'value': result}         
      
    _columns = {
        'film_id': fields.many2one('cinema.film', 'Film', required=True),
        'screen_id': fields.many2one('cinema.screen', 'Screen', required=True),
        'capacity': fields.related('screen_id', 'capacity', type='integer', string='Capacity', readonly=True),
        'init': fields.datetime('Date & Time', required=True),
        'session_type_id': fields.many2one('cinema.session.type', 'Session type', required=True),
        'n_tickets': fields.function(_n_tickets,type='integer',string='Number of tickets'),
        'takings': fields.function(_takings,type='float',string='Takings'),
        'name': fields.function(_name_get_fnc, type='char', size=255, string='Session'),
    }

    _order = 'init'
    
    _sql_constraints = [
        ('session_unique','unique(init, screen_id, film_id )','The list (film, screen, date & hour) must be unique!')
    ]
cinema_session()

# Classes Python per la definició de l'objecte que gestiona els recursos "Tiquets"
class cinema_ticket(osv.osv):
    _name = 'cinema.ticket'
    
    def _total(self, cr, uid, ids, field_name, arg, context):
        obj = self.pool.get("cinema.ticket.detail")
        result={}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id]=0
            for x in obj.browse(cr, uid, rec.detail_ids, context=context):
                result[rec.id]=result[rec.id]+x.id.total
        return result

    _columns = {
        'session_id': fields.many2one('cinema.session', 'Session', required=True, select=1),
        'init': fields.related('session_id','init'),
        'date_time_sale': fields.datetime('Date and hour of sale', select=1, readonly=True),
        'detail_ids': fields.one2many('cinema.ticket.detail', 'ticket_id', 'Detail'),
        'total': fields.function(_total,type='float',string='Total'),
        'active': fields.boolean('Active', required=True),
    }

    _defaults = {
        'active':1,
    }
            
    def unlink (self, cr, uid, ids, context=None):
        val = { 'active': False, }
        return self.write(cr, uid, ids, val, context=context)
    
    def create (self, cr, uid, values, context=None):
        # Assignació de la data+hora de venda
        values['date_time_sale'] = datetime.utcnow()
        return super(cinema_ticket,self).create(cr, uid, values, context=context)

    def onchange_detail(self, cr, uid, ids, detail_ids, context=None):
        result = {}
        result['total'] = 0
        # Fent un print detail_ids es pot veure el contingut de les línies
        # S'observa que és una llista de línies on cada línia és una llista en la que el tercer component
        # (índex 2 ja que les llistes es comencen a numerar per zero) és un diccionari que conté els valors
        # de les diverses columnes de la graella (detail_ids)
        for line in detail_ids:
            l = line[2]     # Diccionari amb el contingut de la línia
            result['total']=result['total']+l['price']*l['n_tickets']
        return {'value': result}
        
cinema_ticket()

class cinema_ticket_detail(osv.osv):
    _name = 'cinema.ticket.detail'
    
    def _check_n_tickets(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
          if obj.n_tickets <=0:
            return False
        return True
   
    _constraints = [
        (_check_n_tickets, 'Number of tickets must be greater than zero', ['n_tickets']),
    ]
  
    def _total(self, cr, uid, ids, field_name, arg, context):   
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id]=rec.n_tickets * rec.price
        return result

    def onchange_vc_pr(self, cr, uid, ids, vc_id, session_id, nt, context=None):
        result = {}
        if session_id:
            if vc_id:
                s = self.pool.get('cinema.session').browse(cr, uid, session_id, context=context)
                vc = self.pool.get('cinema.viewer.category').browse(cr, uid, vc_id, context=context)
                price_id = self.pool.get('cinema.rates').search(cr, uid,['&',('session_type_id','=',s.session_type_id.id),('viewer_category_id','=',vc.id)])
                if price_id:
                    price = self.pool.get('cinema.rates').browse(cr, uid, price_id, context=context)
                    result['price']=price[0].price
                    result['total']=result['price']*nt  #Només té efecte mentre s'edita la línia
                                                        #En canviar de línia desapareix, ja que "total" és
                                                        #un camp funcional i, per tant, de només lectura
                                                        #i els camps de només lectura no poden ser modificats
                                                        #pels mètodes on_change
                else:
                    raise osv.except_osv(_('Error! '),_('The rate is not defined!!!'))
            else:
                result['price']=0
                result['total']=0   #Només té efecte mentre s'edita la línia
                                    #En canviar de línia desapareix, ja que "total" és
                                    #un camp funcional i, per tant, de només lectura
                                    #i els camps de només lectura no poden ser modificats
                                    #pels mètodes on_change
        else:
            raise osv.except_osv(_('Error! '),_('You must enter a session before to enter the detail'))
        return {'value': result}         

    def onchange_nt(self, cr, uid, ids, nt, price, context=None):
        result = {}
        result['total']=nt*price    #Només té efecte mentre s'edita la línia
                                    #En canviar de línia desapareix, ja que "total" és
                                    #un camp funcional i, per tant, de només lectura
                                    #i els camps de només lectura no poden ser modificats
                                    #pels mètodes on_change
        return {'value': result}

    _columns = {
      'ticket_id': fields.many2one('cinema.ticket', 'Session', required=True, ondelete='cascade'),
      'viewer_category_id': fields.many2one('cinema.viewer.category', 'Viewer category', required=True),
      'n_tickets': fields.integer('Number of tickets', required=True),
      'price': fields.float('Price'),
      'total': fields.function(_total, type='float', string='Total'),
    }
    
    def create (self, cr, uid, values, context=None):
        # Comprovació de si hi ha suficients entrades
        # OpenObject és "intel·ligent" i en cas de varis tipus d'entrades en el tiquet
        # "peta" (genera l'excepció) quan arriba a una línia (detail) que supera l'aforament
        # En tal situació, tota la transacció queda avortada
        # NO s'ha programat el mètode write per què no es permet modificar tickets ja enregistrats
        #       Del contrari, caldria programar-lo per què una modificació de nombre d'entrades
        #       podria no ser possible
        t_obj = self.pool.get('cinema.ticket')
        ticket = t_obj.browse(cr,uid,values['ticket_id'],context=context)
        if ticket.session_id.capacity-ticket.session_id.n_tickets < values['n_tickets']:
            raise osv.except_osv(_('Error! '),_('There are not enough tickets!'))
        return super(cinema_ticket_detail,self).create(cr, uid, values, context=context)
cinema_ticket_detail()

