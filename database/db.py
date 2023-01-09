from abc import ABC

from peewee import Model
from playhouse.mysql_ext import MariaDBConnectorDatabase
from playhouse.pool import PooledDatabase

ip = 'myplan.ddns.net'
port = 3306
database = 'system_trading'
user = 'ybsong'
password = 'Thddudqo072!'


class PooledMariaDBDatabase(PooledDatabase, MariaDBConnectorDatabase, ABC):
    def _is_closed(self, conn):
        try:
            conn.ping(False)
        except (Exception,):
            return True
        else:
            return False


db = PooledMariaDBDatabase("system_trading", host=ip, port=port, user=user, password=password, autoconnect=True, stale_timeout=300)


class BaseModel(Model):
    class Meta:
        database = db


if __name__ == '__main__':
    print('test')
    print(db)
