import mysql.connector
from mysql.connector import Error

def conectar():

    try:

        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pokedex",
            port=3306
        )

        if conexao.is_connected():
            print("Conectado ao banco de dados!")

        return conexao

    except Error as erro:

        print("Erro na conexao:", erro)

        return None