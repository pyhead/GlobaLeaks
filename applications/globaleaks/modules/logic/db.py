from gluon import DAL, Field

class DB(DAL):
    def __init__(self):
        DAL.__init__(self, 'sqlite://storage.db')
        self.create_db()
    
    def create_db(self):
        self.define_table('target',
            Field('name'),
            Field('category'),
            Field('desc'),
            Field('url'),
            Field('type'),
            Field('info'),
            Field('status'),
            Field('last_sent_tulip'),
            Field('last_access'),
            Field('last_download'),
            Field('tulip_counter'),
            Field('download_counter'),
            format='%(name)s'
        )
            
        self.define_table('leak',
            Field('title'),
            Field('desc'),
            Field('submission_timestamp'),
            Field('leaker_id', self.target),
            Field('spooled', 'boolean', False),
            format='%(name)s'
        )
            
        self.define_table('comment',
            Field('leak_id', self.leak),
            Field('commenter_id', self.target),
            Field('comment'),
            format='%(name)s'
        )
    
        self.define_table('material',
            Field('url', unique=True),
            Field('leak_id', self.leak),
            Field('type'),
            format='%(name)s'
        )
            
        self.define_table('tulip',
            Field('url', unique=True),
            Field('leak_id', self.leak),
            Field('target_id'),
            Field('allowed_accesses'),
            Field('accesses_counter'),
            Field('allowed_downloads'),
            Field('downloads_counter'),
            Field('expiry_time'),
            format='%(name)s'
            )
            
        self.define_table('mail',
            Field('target'),
            Field('address'),
            Field('tulip', unique=True),
            format='%(name)s'
        )

db = DB()
