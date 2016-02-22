# pip install redis
from .abstract import Database
import sqlite3
import json
import itertools

class Sqlite(Database):
    def __init__(self, instance):
        self.instance_con = instance
        self.instance_cur = instance.cursor()
        # init tables
        self.instance_cur.execute('''
          CREATE TABLE IF NOT EXISTS objs
          (uid VARCHAR(250) PRIMARY KEY ASC,
           kvs VARCHAR(250) NOT NULL)
          ''')
        self.instance_cur.execute('''
          CREATE TABLE IF NOT EXISTS assocs
          (uid1 VARCHAR(250) NOT NULL,
           atype VARCHAR(250) NOT NULL,
           uid2 VARCHAR(250) NOT NULL,
           utime INTEGER NOT NULL,
           kvs VARCHAR(250) NOT NULL,
           PRIMARY KEY (uid1, atype, uid2));
          ''')
        self.instance_con.commit()

    def obj_add(self,uid,kvs):
        kvs = json.dumps(kvs)
        self.instance_cur.execute("INSERT OR REPLACE INTO objs (uid, kvs) VALUES (?, ?)", [uid, kvs])
        self.instance_con.commit()

    def obj_update(self,uid,kvs):
        kvs = json.dumps(kvs)
        self.instance_cur.execute("INSERT OR REPLACE INTO objs (uid, kvs) VALUES (?, ?)", [uid, kvs])
        self.instance_con.commit()

    def obj_delete(self,uid):
        self.instance_cur.execute("DELETE FROM objs WHERE uid = ?", [uid])
        self.instance_con.commit()

    def obj_get(self,uid):
        self.instance_cur.execute("SELECT kvs FROM objs WHERE uid = ?", [uid])
        kvs = self.instance_cur.fetchone()
        # check if None was returned
        if kvs:
            # return kvs as dict
            kvs = json.loads(kvs[1])
        return kvs

    def assoc_add(self, uid1, atype, uid2, time, kvs):
        kvs = json.dumps(kvs)
        self.instance_cur.execute("INSERT OR REPLACE INTO assocs (uid1, atype, uid2, utime, kvs) \
                                   VALUES (?, ?, ?, ?, ?)", [uid1, atype, uid2, time, kvs])
        self.instance_con.commit()

    def assoc_delete(self, uid1, atype, uid2):
        self.instance_cur.execute("DELETE FROM assocs WHERE uid1 = ? \
                                   AND atype = ? AND uid2 = ?", [uid1, atype, uid2])
        self.instance_con.commit()

    def assoc_change_type(self, uid1, atype, uid2, newtype):
        self.instance_cur.execute("UPDATE assocs SET atype = ? WHERE uid1 = ? \
                                   AND atype = ? AND uid2 = ?", [newtype, uid1, atype, uid2])
        self.instance_con.commit()

    def assoc_get(self, uid1, atype, uid2set, high, low):
        query = 'SELECT kvs FROM assocs WHERE uid1 = ? AND atype = ? \
                 AND uid2 IN (%s)' % ','.join('?' for k in uid2set)
        # flattens arguments so we can provide to execute
        args = [uid1, atype] + uid2set
        self.instance_cur.execute(query, args)
        kvs = self.instance_cur.fetchall()
        # check if None was returned
        if kvs:
            # return kvs as dict
            kvs = [json.loads(i[0]) for i in kvs]
        return kvs
