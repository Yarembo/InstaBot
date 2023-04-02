import sqlite3

class Database:


    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()


    def add_users(self, userpage):
        with self.connection:
            return self.cursor.execute('INSERT OR IGNORE INTO InstaBotDataBase (userpage) VALUES (?)', (userpage,))


    def get_db_userpage(self):
        with self.connection:
            result = self.cursor.execute('SELECT userpage FROM InstaBotDataBase', ()).fetchall()
            return(result)


    def add_user_info(self, FIO, status, followers_count, subscribe_count):
        with self.connection:
            return self.cursor.execute('INSERT OR IGNORE INTO InstaBotDataBase (FIO, status, followers_count, '
                                       'subscribe_count) VALUES (?,?,?,?)', (FIO, status, followers_count,
                                                                             subscribe_count,))