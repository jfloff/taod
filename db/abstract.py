from abc import ABCMeta, abstractmethod

class Database:
    __metaclass__ = ABCMeta

    @abstractmethod
    def obj_add(self,uid,kvs):
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
