import sqlite3

DEBUG_MODE = True

class Database:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT)"
        self.conn.execute(stmt)
        self.conn.commit()
        if DEBUG_MODE: print("DEBUG: Database Created")

    def adduser(self,chat_id,user):
        stmt = "INSERT INTO users (id,username) VALUES (?,?)"
        args = (chat_id,user)
        self.conn.execute(stmt,args)
        self.conn.commit()
        if DEBUG_MODE: print("DEBUG: User added in the Database")

    def getuser(self,user):
        cur=self.conn.cursor()
        data=self.getall()
        stmt = "SELECT id FROM users WHERE username=?"
        cur.execute(stmt,(user,))
        userid = cur.fetchone()
        return userid

    def getall(self):
        cur=self.conn.cursor()
        stmt = "SELECT * FROM users"
        cur.execute(stmt)
        test = cur.fetchall()
        return test

    def checkuser(self,chat_id,user):
        flag=0
        cur=self.conn.cursor()
        stmt = "SELECT * from users where id = ?"
        cur.execute(stmt,(chat_id, ))
        check=cur.fetchone()
        if check:
            stmt="UPDATE users SET username = ? WHERE id = ? "
            cur.execute(stmt,(user,chat_id))
            self.conn.commit()
            if DEBUG_MODE: print("DEBUG: Username updated")
            flag=1
        else:
            self.adduser(chat_id,user)
        return flag