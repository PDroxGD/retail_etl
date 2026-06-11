
# GENERAR VENTAS SQL
print("GENERAR VENTAS SQL")

import pandas as pd
import numpy as np

ventas = pd.DataFrame({
    "id_transaccion": range(1,10001),
    "id_cliente": np.random.randint(1,2001,10000),
    "monto": np.random.randint(100,5000,10000),
    "fecha": pd.date_range(
        start="2026-01-01",
        periods=10000
    ).strftime("%d/%m/%Y"),
    "region": np.random.choice(
        ["México","mex","mx"],
        10000
    ),
    "id_tienda": np.random.randint(
        1,51,10000
    )
})


# CARGAR A MYSQL
print("CARGAR A MYSQL")

ventas.to_csv(
    "data/ventas_historicas.csv",
    index=False
)

from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:admin123@localhost/retail"
)

ventas.to_sql(
    "ventas_historicas",
    engine,
    if_exists="append",
    index=False
)

# GENERAR MONGODB
print("GENERAR MONGODB")

import json

perfiles = []

for i in range(1,2001):

    perfiles.append({
        "id_cliente": i,
        "edad": np.random.randint(18,70),
        "preferencias":
        np.random.choice(
            ["Tecnología","Moda","Hogar"]
        ),
        "geolocalizacion":
        np.random.choice(
            ["CDMX","Guadalajara","Monterrey"]
        ),
        "ingresos":
        np.random.randint(10000,80000),
        "puntos_lealtad":
        np.random.randint(0,1000),
        "gastos_mensuales":
        np.random.randint(1000,30000)
    })

with open(
    "data/perfiles_usuarios.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        perfiles,
        f,
        ensure_ascii=False
    )

# GENERAR INVENTARIO
print("GENERAR INVENTARIO")

inventario = pd.DataFrame({
    "id_producto":
    range(1,1001),

    "stock":
    np.random.randint(
        1,200,
        1000
    ),

    "precio":
    np.random.randint(
        50,
        5000,
        1000
    )
})

# AGREGAR NULOS
print("AGREGAR NULOS")


for _ in range(100):

    fila = np.random.randint(0,1000)

    inventario.loc[
        fila,
        "stock"
    ] = np.nan

# AGREGAR DUPLICADOS
print("AGREGAR DUPLICADOS")

duplicados = inventario.sample(
    frac=0.05
)

inventario = pd.concat(
    [inventario,duplicados]
)

#GUARDAR
print("GUARDAR")

inventario.to_csv(
    "data/inventario.csv",
    index=False
)