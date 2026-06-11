from pymongo import MongoClient
import json

cliente = MongoClient(
    "mongodb://localhost:27017/"
)

db = cliente["retail"]

coleccion = db["perfiles"]

with open(
    "data/perfiles_usuarios.json",
    "r",
    encoding="utf-8"
) as f:

    datos = json.load(f)

coleccion.insert_many(datos)