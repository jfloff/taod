# Instalattion:
#  > pip install redis

from .abstract import Cache
import redis
import uuid

class Redis(Cache):
    def __init__(self, instance):
        self.instance = instance

    def __obj_hash_name(self, uid, otype):
        return "%s##%s" % (uid,otype)

    def __assoc_hash_name(self, uid1, atype, uid2):
        return "%s##%s##%s" % (uid1,atype,uid2)

    def __assoc_set_name(self, uid1, atype):
        return "%s##%s" % (uid1,atype)

    def obj_add(self,otype,kvs):
        # generate uuid
        uid = str(uuid.uuid4())
        # move otype into hash
        kvs['otype'] = otype
        # hash name merges otype with id
        hash_name = self.__obj_hash_name(uid,otype)
        # set hash, and sets simple kv with hash
        self.instance.hmset(hash_name,kvs)
        self.instance.set(uid, hash_name)
        return uid

    def obj_update(self,uid,kvs):
        hash_name = self.instance.get(uid)
        self.instance.hmset(hash_name,kvs)

    def obj_delete(self,uid):
        hash_name = self.instance.get(uid)
        self.instance.delete(hash_name)
        self.instance.delete(uid)

    def obj_get(self,uid):
        hash_name = self.instance.get(uid)
        return self.instance.hgetall(hash_name)

    def assoc_add(self, uid1, atype, uid2, time, kvs):
        assoc_name = self.__assoc_hash_name(uid1,atype,uid2)
        kvs['time'] = time
        kvs['uid2'] = uid2
        self.instance.hmset(assoc_name,kvs)
        # save into uid1,atype per time set
        set_name = self.__assoc_set_name(uid1,atype)
        self.instance.zadd(set_name, time, assoc_name)

    def assoc_delete(self, uid1, atype, uid2):
        assoc_name = self.__assoc_hash_name(uid1,atype,uid2)
        self.instance.delete(assoc_name)
        set_name = self.__assoc_set_name(uid1,atype)
        self.instance.zrem(set_name, assoc_name)

    def assoc_change_type(self, uid1, atype, uid2, newtype):
        assoc_name = self.__assoc_hash_name(uid1,atype,uid2)
        set_name = self.__assoc_set_name(uid1,atype)
        time = self.instance.zrem(set_name, assoc_name)
        # rename sets
        new_assoc_name = self.__assoc_hash_name(uid1,newtype,uid2)
        new_set_name = self.__assoc_set_name(uid1,newtype)
        self.instance.rename(assoc_name, new_assoc_name)
        self.instance.zadd(new_set_name, time, new_assoc_name)

    def assoc_get(self, uid1, atype, uid2set, high, low):
        set_name = self.__assoc_set_name(uid1,atype)
        # set limits
        if high is None: high = '+inf'
        if low is None: low = '-inf'
        # get range by time
        assoc_keys = self.instance.zrangebyscore(set_name, low, high)
        # filter previous list by uid set
        assoc_keys = [a for a in assoc_keys if a.split('##')[2] in uid2set]
        return [self.instance.hgetall(a) for a in assoc_keys]

    def assoc_count(self, uid1, atype):
        set_name = self.__assoc_set_name(uid1,atype)
        return self.instance.zcard(set_name)

    def assoc_range(self, uid1, atype, pos, limit):
        set_name = self.__assoc_set_name(uid1,atype)
        # get associations keys with descending order so more recent values are first
        assoc_keys = self.instance.zrange(set_name, pos, pos+limit, desc=True)
        return [self.instance.hgetall(a) for a in assoc_keys]

    def assoc_time_range(self, uid1, atype, high, low, limit):
        set_name = self.__assoc_set_name(uid1,atype)
        # get range by time
        assoc_keys = self.instance.zrangebyscore(set_name, low, high)
        return [self.instance.hgetall(a) for a in assoc_keys]
