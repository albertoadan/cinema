{
        "name" : "cinema",
        "version" : "0.EAC3.1314S1",
        "author" : "Institut Obert de Catalunya",
        "website" : "http://ioc.xtec.cat",
        "category" : "Unknown",
        "description": """
          Module prepared by "Institut Obert de Catalunya" 
          to learn the use of the OpenObject framework 
          in order to adapt OpenERP and create new modules.
          
          It is part of the learning materials for the module
          "Sistemes de gestió empresarial" in the course
          "CFS Desenvolupament d'aplicacions multiplataforma".
        """,
        "depends" : ['base'],
        "init_xml" : [ ],
        "demo_xml" : ['demo/cinema_demo.xml'],
        "update_xml" : ['security/cinema_security.xml',
                        'security/ir.model.access.csv',
                        'cinema_view.xml',
                        'wizard/cinema_change_rates_view.xml',
                        'report/film_reports.xml',
                        'cinema_dashboard.xml'],
        "installable": True
}
