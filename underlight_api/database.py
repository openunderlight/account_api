import mysql.connector
import datetime
from underlight_api import bcrypt
from collections import OrderedDict
from mysql.connector.cursor import MySQLCursorPrepared

class UnderlightDatabase:
    ACCEPTABLE_DBS = ['billing', 'level', 'item', 'guild', 'server', 'player']
    @classmethod
    def get(cls):
        '''Use this as your factory so it only connects once.'''
        if getattr(cls, 'inst', None) is None:
            cls.inst = UnderlightDatabase('pw.txt')
            cls.inst.connect()
        return cls.inst

    def __init__(self, dbTxtFile):
        self.database_passwords = {}
        self.connections = {}
        with open(dbTxtFile) as f:
            for line in f.readlines():
                split = line.split()
                if split[0] == 'DBHOST':
                    self.host = split[1]
                elif split[0] == 'DBPORT':
                    self.port = split[1]
                elif self._is_db(split[0]):
                    self.database_passwords[split[0]] = (split[1], split[2])

    def _is_db(self, db_name):
        if not db_name.startswith('ul_'):
            return False
        [_, suffix] = db_name.split('_')
        if suffix not in UnderlightDatabase.ACCEPTABLE_DBS:
            return False
        return True
    
    def connect(self, db = None):
        if db is not None and db in self.database_passwords:
            return self._connect_to_one_db(db)
        else:
            for dbname in self.database_passwords.keys():
                self._connect_to_one_db(dbname)
    
    def _connect_to_one_db(self, db):
        if db not in self.connections:
            u,p = self.database_passwords[db]
            self.connections[db] = mysql.connector.connect(user = u, password = p, host = self.host, 
                database = db, port = self.port, use_pure=True)
        return self.connections[db]
    
    def retrieve_billing_account_id(self, username, password):
        cxn = self.connect(db = 'ul_billing')
        stmt = 'SELECT billing_id,password FROM ul_billing.accounts WHERE username = %s'
        cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
        cursor.execute(stmt, (username,))
        all = cursor.fetchall()
        if cursor.rowcount != 1:
            cursor.close()
            return None
        else:
            (billing_id,password_hash) = all[0]
            cursor.close()
            if not bcrypt.check_password_hash(password_hash.encode('utf-8'), password.encode('utf-8')):
                return None
            return billing_id
        
    def check_account_exists(self, username, email):
        cxn = self.connect(db = 'ul_billing')
        stmt = 'SELECT count(*) FROM ul_billing.accounts WHERE username = %s OR email = %s'            
        cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
        cursor.execute(stmt, (username, email))
        all = cursor.fetchall()
        (count,) = all[0]
        return count > 0

    def add_account(self, username, email, password, full_name):
        cxn = self.connect(db = 'ul_billing')
        stmt = 'INSERT INTO ul_billing.accounts (username, password, real_name, email, start_date, last_bill_date, end_date) VALUES ' + \
            ' (%s, %s, %s, %s, %s, %s, %s)'
        cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
        cursor.execute(stmt, (username, bcrypt.generate_password_hash(password).decode('utf-8'), full_name, email, datetime.date.today(), 
            datetime.date.today(), datetime.date(9999, 12, 31)))
        id = cursor.lastrowid
        cxn.commit()
        cursor.close()
        return id

    def update_account(self, id, fullName = None, emailAddress = None, password = None):
        cxn = self.connect(db = 'ul_billing')
        jsonToCol = {
            'real_name': fullName,
            'email': emailAddress,
            'password': bcrypt.generate_password_hash(password).decode('utf-8') if password is not None else None
        }
        updates = OrderedDict({k:v for k,v in jsonToCol.items() if v is not None})        
        stmt = 'UPDATE ul_billing.accounts SET ' + ','.join(['%s = %%s' % col for col in updates.keys()])
        w = ' WHERE billing_id=%d' % id
        stmt += w
        cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
        cursor.execute(stmt, tuple(updates.values()))
        cxn.commit()
        cursor.close()
        return True
    
    def token_in_blacklist(self, jti):
        cxn = self.connect(db = 'ul_billing')
        stmt = 'SELECT count(*) FROM ul_billing.token_blacklist WHERE token_id = %s'
        cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
        cursor.execute(stmt, (jti,))
        all = cursor.fetchall()
        (count,) = all[0]
        return count > 0
    
    def blacklist_token(self, jti):
        cxn = self.connect(db = 'ul_billing')
        stmt = 'INSERT INTO ul_billing.token_blacklist (token_id) VALUES(%s)'
        cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
        cursor.execute(stmt, (jti,))
        cxn.commit()
        cursor.close()
        return True

