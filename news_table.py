from sqlite3 import connect


class DB:
    def __init__(self):
        conn = connect('SQLite/Data.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS "news" 
                            (news_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            title	VARCHAR(100) NOT NULL,
                            content	VARCHAR(1000) NOT NULL,
                            likes	INTEGER,
                            user_id	INTEGER,
                            FOREIGN KEY(user_id) REFERENCES users(id)
                            )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, content, likes, user_id) 
                          VALUES (?,?,?,?)''', (title, content, 0, user_id))
        cursor.close()
        self.connection.commit()

    def get_one(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE news_id = ?", str(news_id))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=False, last=False):
        cursor = self.connection.cursor()
        if not user_id and not last:
            cursor.execute("SELECT * FROM news")
        elif last:
            cursor.execute("SELECT * FROM news ORDER BY news_id DESC LIMIT 50")
        elif user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ?", str(user_id))
        rows = cursor.fetchall()
        return rows

    def like(self, news_id):
        data = self.get_one(news_id)
        cursor = self.connection.cursor()
        cursor.execute("UPDATE news SET likes = ? WHERE news_id = ?", (str(data[4] + 1), data[0]))
        cursor.close()
        self.connection.commit()

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE news_id = ?''', (str(news_id),))
        cursor.close()
        self.connection.commit()


class CommentsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''create table comments
                            (
                                com_id    INTEGER not null
                                    primary key autoincrement,
                                post_id   INTEGER not null
                                    references news,
                                user_id INTEGER not null,
                                content   TEXT    not null
                            )''')
        cursor.close()
        self.connection.commit()

    def insert(self, post_id, user_id, content):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO comments 
                          (post_id, user_id, content) 
                          VALUES (?,?,?)''', (post_id, user_id, content))
        cursor.close()
        self.connection.commit()

    def get(self, user_id=False, post_id=False, com_id=False):
        cursor = self.connection.cursor()
        if not user_id and not post_id and not com_id:
            cursor.execute("SELECT * FROM comments")
        elif post_id:
            cursor.execute("SELECT * FROM comments WHERE post_id = ?", str(post_id))
        elif user_id:
            cursor.execute("SELECT * FROM comments WHERE user_id = ?", str(user_id))
        elif com_id:
            cursor.execute("SELECT * FROM comments WHERE com_id = ?", [com_id])
        rows = cursor.fetchall()
        return rows

    def delete(self, com_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM comments WHERE com_id = ?''', (str(com_id),))
        cursor.close()
        self.connection.commit()
