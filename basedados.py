import sqlite3
import os

DB_NAME = "sistema.db"

class Database:
    def __init__(self):
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(DB_NAME)

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cliente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def registrar_cliente(self, usuario, senha):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cliente (usuario, senha) VALUES (?, ?)", (usuario, senha))
            conn.commit()
            return True, "Cadastrado com sucesso."
        except sqlite3.IntegrityError:
            return False, "Usuário já existe."
        except Exception as e:
            return False, str(e)
        finally:
            if conn: conn.close()

    def autenticar_cliente(self, usuario, senha):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cliente WHERE usuario = ? AND senha = ?", (usuario, senha))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0] # Retorna o ID
        return None