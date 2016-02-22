TaoD
======

TaoD is naive implementation of [Facebook's TAO](https://www.facebook.com/notes/facebook-engineering/tao-the-power-of-the-graph/10151525983993920/) API. TAO is a distributed write-through graph store, that's optimized for Facebook's social graph. It has a minimal API and explicitly favors availability and per-machine efficiency over strong consistency.

For more information regarding TAO, read Facebook's paper: [TAO: Facebook’s Distributed Data Store for the Social Graph, Usenix Annual Technical Conference, 2013](https://cs.uwaterloo.ca/~brecht/courses/854-Emerging-2014/readings/data-store/tao-facebook-distributed-datastore-atc-2013.pdf)

### Motivation
TaoD focus on implementing just TAO's API for Facebook's social graph. It's focus is replicating the API behavior, in detriment of performance and replication techniques that are described in the paper.

We provide an abstract API similar to the one presented in TAO's paper, which relies on a **cache** and **database** modules. The *cache* module serves as the backend of the TAO cache API. Even though TAO's is itself a distributed datastore, I realized is easier to leverage on existing datastores, and just replicate TAO's operations using the datastore's own operations. The *database* module serves as TAO's storage layer.

Any mix of both these modules is possible. Feel free to open a PR to provide more *cache* and *database* interfaces. At this moment we provide the following cache implementations:
* [Redis](http://redis.io/)

and the following database implementations:
* [SQLite](https://www.sqlite.org/)

### Usage

First initialize your cache's interface. In our example, `Redis`:
```py
import redis
r = redis.StrictRedis(host='172.17.0.2', port=6379, db=0, decode_responses=True)
```

Then pass cache's interface to its respective `TaoD` adapter:
```py
from cache.redis import Redis
redis_adapter = Redis(r)
```

Similar flow happens for the database. In our example, `SQLite`:
```py
import sqlite3 as lite
lite_adapter = lite.connect('test.db')
from db.sqlite import Sqlite
sqlite_adapter = Sqlite(lite_adapter)
```

Now you can initiate your `TaoD` instance, passing your cache and database adapters. The `time` argument is the type of timestamp for associations. You can either choose `logical` (for a simple logical counter at each add), or `real` for a milliseconds timestamp.
```py
redis_sqlite_tao = Taod(redis_adapter, sqlite_adapter, time='logical')
```

After this initial setup, you can use the same operations as the TAO's API described in Facebook's paper.

* Object API:
```
Object: (id) → (otype, (k → v)*)
  Typed nodes that are identified by a 64-bit integer (id) that is unique across all objects

  obj_add(atype, (k → v)*): creates new object, returns its id.
  obj_update(id, (k → v)*): updates fields
  obj_delete(id): removes the object permanently
  obj_get(id): returns type and fields of an object
```

* Association API
```
Association: (id1, atype, id2) → (time, (key → value)*)
  Typed directed edges between objects that are identified by the source object (id1), association type (atype) and destination object (id2)

  assoc_add(id1, atype, id2, time, (k → v)*): adds or overwrites updates the the association (id1, atype,id2), and its inverse (id1, inv(atype), id2) if defined.
  assoc_delete(id1, atype, id2): deletes the given association
  assoc_change_type(id1, atype, id2, newtype): changes the association (id1, atype, id2) to (id1, newtype, id2).
```

* Association Query API
```
Association Lists: (id1, atype) → [anew ... aold].
  We define an association list to be the list of all associations with a particular id1 and atype, arranged in descending order by the time field: (id1, atype) → [anew ... aold]

  assoc_get(id1, atype, id2set): returns all of the associations (id1, atype, id2) and their time and data, where id2 ∈ id2set.
  assoc_count(id1, atype): returns the size of the association list for (id1, atype), which is the number of edges of type atype that originate at id1.
  assoc_range(id1, atype, pos, limit): returns elements of the (id1, atype) association list with index i ∈ [pos,pos+limit].
  assoc_time_range(id1, atype, high, low, limit): returns elements from the (id1, atype) association list, ordered by time.
```

##### Full example

Taken from `redis_sqlite` example in `examples` folder.

```py
from api import Taod

# init redis cache
import redis
r = redis.StrictRedis(host='172.17.0.2', port=6379, db=0, decode_responses=True)
from cache.redis import Redis
redis_adapter = Redis(r)

# init sqlite db
import sqlite3 as lite
lite_adapter = lite.connect('test.db')
from db.sqlite import Sqlite
sqlite_adapter = Sqlite(lite_adapter)

# init taod
redis_sqlite_tao = Taod(redis_adapter, sqlite_adapter, time='logical')

# example operations
key1 = redis_sqlite_tao.obj_add("comment", {'a':1})
key2 = redis_sqlite_tao.obj_add("comment", {'a':2})
key3 = redis_sqlite_tao.obj_add("comment", {'a':3})

redis_sqlite_tao.assoc_add(key1, "friends", key2, {'a': 10})
redis_sqlite_tao.assoc_add(key1, "friends", key3, {'a': 11})

redis_sqlite_tao.assoc_get(key1, "friends", [key2,key3])
redis_sqlite_tao.assoc_delete(key1, "friends", key3)
```

### Docker
This repository includes `Dockerfile` for development and for running `TaoD`.

Run `redis_sqlite` example ([Dockerfile](examples/Dockerfile.redis_sqlite))
```shell
# to build image
docker build --rm=true -t jfloff/taod .
# start redis server
docker run --name=redis --rm -ti redis
# start python container linked with redis to run example
docker run --rm -v "$(pwd)":/home/taod -w /home/taod -ti --link redis jfloff/tao
```

If you intend to build another *cache* of *database*, creating a similar Dockerfile might be useful.


### Future work
* At this moment no inverse associations are spawned, since the library is generic enough to be adapted to any objects. In the future I might add an argument specifying the inverse relation.


### License

MIT (see LICENSE.txt file)
