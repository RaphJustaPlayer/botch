import sqlite3
import os
from DataBaseAccess import DataBaseAccess
import json

connexion = sqlite3.connect(f"{os.getcwd()}\\data\\SDLM.db")
DBA = DataBaseAccess(connexion=connexion)
cursor = connexion.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INT,
                    data INT
                    )""")
cursor.execute("""CREATE TABLE IF NOT EXISTS starbotch(
                    id INT
                    jumpurl VARCHAR,
                    stars INT
                    )""")
print(DBA.showsb(782212312575508490))
