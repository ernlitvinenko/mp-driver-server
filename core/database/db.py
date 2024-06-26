import pickle
import socket
from firebird.driver import connect, driver_config
from redis import StrictRedis
from redis_cache import RedisCache
from sqlalchemy import QueuePool
from sqlalchemy import create_engine
import codecs


from core.config import Config

driver_config.server_defaults.host.value = Config.firebird_host
driver_config.server_defaults.user.value = Config.firebird_user
driver_config.server_defaults.password.value = Config.firebird_password


def get_connection():
    con = connect(Config.firebird_database, no_db_triggers=False, charset='WIN1251')

    stmt_register_connection = f"""
UPDATE SEANS 
set SEANS_STATUS    = 2,
            SEANS_ID_SOTR   = ?,--14,
            SEANS_ID_MST    = 0,  -- без привязки
            SEANS_COMP_NAME = ?,--//'PersonalArea'
            SEANS_REMOTE_VER = ?
where ID_SEANS = RDB$GET_CONTEXT('USER_SESSION', 'ID_SEANS');
    """
    cursor = con.cursor()
    cursor.execute(stmt_register_connection, (31, socket.gethostname(), '2024052901'))
    cursor.close()
    con.commit()
    return con


def __serializer(obj):
    return codecs.encode(pickle.dumps(obj), "base64").decode()


def __deserializer(obj):
    return pickle.loads(codecs.decode(obj.encode(), "base64"))


# pool = QueuePool(get_connection, pool_size=5, max_overflow=0, pre_ping=True, dialect=)
redis_client = StrictRedis(host="127.0.0.1", decode_responses=True)
redis_cache_obj = lambda : RedisCache(redis_client, serializer=__serializer, deserializer=__deserializer)
engine = create_engine(f'firebird+firebird://{Config.firebird_user}:{Config.firebird_password}@{Config.firebird_host}/{Config.firebird_database}?charset=WIN1251', echo=True)