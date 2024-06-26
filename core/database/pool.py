import queue

from firebird.driver import Connection as BaseConnection, connect, Cursor


class PoolConnection:
    def __init__(self, connection: BaseConnection, pool: 'PoolManager'):
        self._connection: BaseConnection = connection
        self.__pool: PoolManager = pool

    @property
    def is_alive(self) -> bool:
        return not self._connection.is_closed()

    @classmethod
    def create(cls, pool: 'PoolManager', *args, **kwargs):
        con = connect(*args, **kwargs)
        return cls(con, pool)

    def cursor(self) -> Cursor:
        return self._connection.cursor()

    def close(self):
        self.__pool.release_connection(self)

    def close_connection(self):
        if not self._connection.is_closed():
            self._connection.close()
            assert self.is_alive == False


class PoolManager:
    MAX_CONNECTION: int = 5
    _all_connection: list[PoolConnection] = []
    _available_connections: queue.Queue[PoolConnection] = None

    def __init__(self, **connection_args):
        self.__connection_args = connection_args
        if self._available_connections is None:
            self._available_connections = queue.Queue()

        self.build_connections()

    def build_connections(self):
        for _ in range(self.MAX_CONNECTION):
            self.make_connection()

    def make_connection(self) -> PoolConnection:
        con = PoolConnection.create(self, **self.__connection_args)
        self._all_connection.append(con)
        self.release_connection(con)
        return con

    def connect(self) -> PoolConnection:
        for _ in range(self.MAX_CONNECTION):
            con = self._available_connections.get()
            if con.is_alive:
                return con
            self._all_connection.remove(con)
            return self.make_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("GRACEFULLY CLOSE CONNECTIONS")
        for con in self._all_connection:
            con.close_connection()

    def release_connection(self, con):
        self._available_connections.put(con)
