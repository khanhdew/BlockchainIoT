import sqlite3

class Connector:
    def __init__(self,db_name = "database.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.initDatabase()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Connector, cls).__new__(cls)
        return cls.instance

    def initDatabase(self):
        self.execute("CREATE TABLE IF NOT EXISTS \"transaction\" (id INTEGER PRIMARY KEY, hashed_value TEXT, time interger, hash_key interger, foreign key(hash_key) references hash_key(id))")
        self.execute("CREATE TABLE IF NOT EXISTS \"hash_key\" (id INTEGER PRIMARY KEY, hash TEXT)")
        self.commit()

    def execute(self, query):
        return self.cursor.execute(query)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

