from api import Taod
import time

# init cache
import redis
r = redis.StrictRedis(host='172.17.0.2', port=6379, db=0, decode_responses=True)
from cache.redis import Redis
redis_adapter = Redis(r)

# init db
import sqlite3 as lite
lite_adapter = lite.connect('test.db')
from db.sqlite import Sqlite
sqlite_adapter = Sqlite(lite_adapter)

# init taod
redis_tao = Taod(redis_adapter, sqlite_adapter, time='logical')

# operations
key = redis_tao.obj_add("comment", {'a':1})
print(redis_tao.obj_get(key))

redis_tao.obj_update(key, {'a':3, 'b':2})
print(redis_tao.obj_get(key))

redis_tao.obj_delete(key)
print(redis_tao.obj_get(key))

# association
key1 = redis_tao.obj_add("comment", {'a':1})
key2 = redis_tao.obj_add("comment", {'a':1})
key3 = redis_tao.obj_add("comment", {'a':1})
key4 = redis_tao.obj_add("comment", {'a':1})

redis_tao.assoc_add(key1, "friends", key2, {'a': 2})
time.sleep(0.5)
redis_tao.assoc_add(key1, "friends", key3, {'a': 3})
time.sleep(0.5)
redis_tao.assoc_add(key1, "friends", key4, {'a': 4})

print(redis_tao.assoc_get(key1, "friends", [key2,key3,key4]))

redis_tao.assoc_delete(key1, "friends", key2)
print(redis_tao.assoc_get(key1, "friends", [key2,key3,key4]))

redis_tao.assoc_add(key1, "friends", key2, {'a': 2})
print(redis_tao.assoc_get(key1, "friends", [key2,key3,key4]))

redis_tao.assoc_change_type(key1, "friends", key2, "checkin")
print(redis_tao.assoc_get(key1, "friends", [key2,key3,key4]))
print(redis_tao.assoc_get(key1, "checkin", [key2]))

print(redis_tao.assoc_get(key1, "friends", [key2,key3,key4]))

# close connections
lite_adapter.close()
