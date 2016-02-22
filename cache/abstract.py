from abc import ABCMeta, abstractmethod

class Cache:
    __metaclass__ = ABCMeta

    @abstractmethod
    def obj_add(self,otype,kvs):
        pass

    @abstractmethod
    def obj_update(self,uid,kvs):
        pass

    @abstractmethod
    def obj_delete(self,uid):
        pass

    @abstractmethod
    def obj_get(self,uid):
        pass

    @abstractmethod
    def assoc_add(self, uid1, atype, uid2, time, kvs):
        pass

    @abstractmethod
    def assoc_delete(self, uid1, atype, uid2):
        pass

    @abstractmethod
    def assoc_change_type(self, uid1, atype, uid2, newtype):
        pass

    @abstractmethod
    def assoc_get(self, uid1, atype, uid2set, high, low):
        pass

    @abstractmethod
    def assoc_count(self, uid1, atype):
        pass

    @abstractmethod
    def assoc_range(self, uid1, atype, pos, limit):
        pass

    @abstractmethod
    def assoc_time_range(self, uid1, atype, high, low, limit):
        pass
