
import sqlite3 as sql


def sql_start():
	global db, cur
	db = sql.connect('db.db')
	cur = db.cursor()
	if db:
		print('DB is connected!')
	db.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, uid int PRIMARY KEY UNIQUE, status BOOL DEFAULT(0))')
	db.commit()

async def add(uid,username):
	cur.execute("INSERT INTO users VALUES (?, ?, ?)",(username,uid, 1))
	db.commit()	

def chek(uid):
	result = cur.execute("SELECT status FROM users WHERE uid = ?",(uid,)).fetchall()	
	return result

def get_ids():
	ids = cur.execute("SELECT uid FROM users").fetchall()
	return ids

def sas(uid):
	result = cur.execute("SELECT * FROM users WHERE uid = ?",(uid,)).fetchall()
	return bool(len(result))

async def del_user(uid):
	cur.execute('DELETE FROM users WHERE uid = ?',(uid,))
	db.commit()	
