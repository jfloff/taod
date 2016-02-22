import uuid
import time

class Taod:
    __logical_timer = 0;

    def __init__(self, cache, database, time='real'):
        self.cache = cache
        self.database = database
        self.time = time

    # Sets time for associations
    def __set_time(self):
        if self.time == 'real':
            import time
            return int(round(time.time() * 1000))
        if self.time == 'logical':
            self.__logical_timer += 1
            return self.__logical_timer


    ###################
    # Object API
    #

    # creates new object, returns its id.
    def obj_add(self,otype,kvs):
        uid = self.cache.obj_add(otype,kvs)
        self.database.obj_add(uid,kvs)
        return uid

    # obj_update(id, (k → v)*): updates fields
    def obj_update(self,uid,kvs):
        self.cache.obj_update(uid,kvs)
        self.database.obj_update(uid,kvs)

    # obj_delete(id): removes the object permanently
    def obj_delete(self,uid):
        self.cache.obj_delete(uid)
        self.database.obj_delete(uid)

    # returns type and fields of an object
    def obj_get(self,uid):
        kvs = self.cache.obj_get(uid)
        if not kvs:
            kvs = self.database.obj_get(uid)
        return kvs

    ###################
    # Association API
    #

    def assoc_add(self, uid1, atype, uid2, kvs):
        # time in milliseconds
        atime = self.__set_time()
        self.cache.assoc_add(uid1, atype, uid2, atime, kvs)
        self.database.assoc_add(uid1, atype, uid2, atime, kvs)

    def assoc_delete(self, uid1, atype, uid2):
        self.cache.assoc_delete(uid1, atype, uid2)
        self.database.assoc_delete(uid1, atype, uid2)

    def assoc_change_type(self, uid1, atype, uid2, newtype):
        self.cache.assoc_change_type(uid1, atype, uid2, newtype)
        self.database.assoc_change_type(uid1, atype, uid2, newtype)

    ###################
    # Association Query API
    #

    def assoc_get(self, uid1, atype, uid2set, high=None, low=None):
        # fetch first from cache
        cache_get = self.cache.assoc_get(uid1, atype, uid2set, high, low)
        # gets keys that werent fetched from cache
        cache_get_keys = [d['uid2'] for d in cache_get if d['uid2'] in uid2set]
        missing_keys = list(set(uid2set) - set(cache_get_keys))
        # if there are missing keys, gets them from db
        if missing_keys:
            database_get = self.database.assoc_get(uid1, atype, missing_keys, high, low)
            # merge cache and database gets
            cache_get += database_get
        return cache_get

    def assoc_count(self, uid1, atype):
        return self.cache.assoc_count(uid1, atype)

    def assoc_range(self, uid1, atype, pos, limit):
        return self.cache.assoc_range(uid1, atype, pos, limit)

    def assoc_time_range(self, uid1, atype, high, low, limit=6000):
        return self.cache.assoc_time_range(uid1, atype, high, low, limit)
