from peewee import Model
from playhouse.mysql_ext import MariaDBConnectorDatabase

ip = 'myplan.ddns.net'
port = 3306
database = 'system_trading'
user = 'ybsong'
password = 'Thddudqo072!'

db = MariaDBConnectorDatabase(database, host=ip, port=port, user=user, password=password, autoconnect=True)


class BaseModel(Model):
    class Meta:
        database = db


if __name__ == '__main__':
    print('test')
    print(db)
