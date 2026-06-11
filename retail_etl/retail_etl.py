import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from pymongo import MongoClient
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns


# =====================================
# EXTRACCION
# =====================================

def extraer_sql():

    engine = create_engine(
        "mysql+pymysql://root:admin123@localhost/retail"
    )

    query = """
    SELECT *
    FROM ventas_historicas
    ORDER BY id_transaccion DESC
    LIMIT 500
    """

    ventas = pd.read_sql(query, engine)

    return ventas


def extraer_mongo():

    cliente = MongoClient(
        "mongodb://localhost:27017/"
    )

    db = cliente["retail"]

    coleccion = db["perfiles"]

    perfiles = pd.DataFrame(
        list(coleccion.find())
    )

    return perfiles


def extraer_csv():

    inventario = pd.read_csv(
        "data/inventario.csv"
    )

    return inventario


# =====================================
# LIMPIEZA
print("LIMPIEZA")
# =====================================

def limpiar_datos(ventas, perfiles, inventario):

    ventas_antes = len(ventas)
    inventario_antes = len(inventario)

    ventas = ventas.drop_duplicates()
    inventario = inventario.drop_duplicates()

    print(
        f"Duplicados eliminados en ventas: "
        f"{ventas_antes - len(ventas)}"
    )

    print(
        f"Duplicados eliminados en inventario: "
        f"{inventario_antes - len(inventario)}"
    )

    inventario["stock"] = inventario["stock"].fillna(
        inventario["stock"].median()
    )

    ventas["region"] = ventas["region"].replace({
        "México": "MX",
        "mex": "MX",
        "mx": "MX"
    })

    return ventas, perfiles, inventario


# =====================================
# NORMALIZACION
print("NORMALIZACION")
# =====================================

def normalizar_datos(ventas, perfiles):

    ventas["monto"] = pd.to_numeric(
        ventas["monto"],
        errors="coerce"
    )

    ventas["fecha"] = pd.to_datetime(
        ventas["fecha"],
        format="%d/%m/%Y"
    )

    scaler = MinMaxScaler()

    columnas = [
        "ingresos",
        "puntos_lealtad",
        "gastos_mensuales"
    ]

    perfiles[columnas] = scaler.fit_transform(
        perfiles[columnas]
    )

    return ventas, perfiles


# =====================================
# ENRIQUECIMIENTO
print("ENRIQUECIMIENTO")
# =====================================

def realizar_join(ventas, perfiles):

    if "_id" in perfiles.columns:
        perfiles = perfiles.drop("_id", axis=1)

    data_master = pd.merge(
        ventas,
        perfiles,
        on="id_cliente",
        how="left"
    )

    return data_master


# =====================================
# REGLAS DE NEGOCIO
print("REGLAS DE NEGOCIO")
# =====================================

def segmentar_clientes(data_master):

    data_master["segmento_cliente"] = np.where(
        (data_master["monto"] > 2000)
        & (data_master["edad"] < 30),

        "Premium Joven",

        np.where(
            (data_master["monto"] > 2000)
            & (data_master["edad"] >= 30),

            "Premium Adulto",

            np.where(
                data_master["puntos_lealtad"] > 0.7,

                "Cliente Leal",

                "Regular"
            )
        )
    )

    return data_master


# =====================================
# PCA
print("PCA")
# =====================================

def aplicar_pca(data_master):

    variables = [
        "monto",
        "edad",
        "ingresos",
        "puntos_lealtad",
        "gastos_mensuales",
        "id_tienda"
    ]

    datos = data_master[variables].fillna(0)

    pca = PCA(
        n_components=3
    )

    componentes = pca.fit_transform(
        datos
    )

    data_master["PC1"] = componentes[:, 0]
    data_master["PC2"] = componentes[:, 1]
    data_master["PC3"] = componentes[:, 2]

    print("\nVarianza explicada:")

    print(
        np.round(pca.explained_variance_ratio_, 4)
    )

    varianza_total = (
    pca.explained_variance_ratio_.sum()
    )   

    print(
        f"\nLos 3 componentes explican "
        f"{varianza_total:.2%} "
        f"de la varianza total."
    )

    print(
        "\nVarianza total explicada:"
    )

    print(
        pca.explained_variance_ratio_.sum()
    )

    return data_master


# =====================================
# VISUALIZACIONES
print("VISUALIZACIONES")
# =====================================

def generar_boxplot(data_master):

    plt.figure(figsize=(8, 5))

    sns.boxplot(
        x=data_master["monto"]
    )

    plt.title(
        "Boxplot de Montos de Venta"
    )

    plt.savefig(
        "output/boxplot_montos.png"
    )

    plt.close()


def generar_scatter(data_master):

    plt.figure(figsize=(8, 6))

    plt.scatter(
        data_master["PC1"],
        data_master["PC2"]
    )

    plt.xlabel("PC1")
    plt.ylabel("PC2")

    plt.title(
        "Scatter PCA"
    )

    plt.savefig(
        "output/scatter_pca.png"
    )

    plt.close()


def generar_segmentos(data_master):

    plt.figure(figsize=(8,5))

    sns.countplot(
        data=data_master,
        x="segmento_cliente"
    )

    plt.title(
        "Distribucion de Segmentos"
    )

    plt.savefig(
        "output/segmentos_clientes.png"
    )

    plt.close()

# =====================================
# EXPORTACION
print("EXPORTACION")
# =====================================

def exportar(data_master):

    data_master.to_csv(
        "output/data_master_clean.csv",
        index=False
    )


# =====================================
# MAIN
print("MAIN")
# =====================================

def main():

    print("Extrayendo datos...")

    ventas = extraer_sql()

    perfiles = extraer_mongo()

    inventario = extraer_csv()

    print("Limpiando datos...")

    ventas, perfiles, inventario = limpiar_datos(
        ventas,
        perfiles,
        inventario
    )

    print("Normalizando datos...")

    ventas, perfiles = normalizar_datos(
        ventas,
        perfiles
    )

    print("Realizando join...")

    data_master = realizar_join(
        ventas,
        perfiles
    )

    print("Aplicando reglas de negocio...")

    data_master = segmentar_clientes(
        data_master
    )

    print("Aplicando PCA...")

    data_master = aplicar_pca(
        data_master
    )

    print("Generando graficos...")

    generar_boxplot(
        data_master
    )

    generar_scatter(
        data_master
    )

    generar_segmentos(
    data_master
    )

    print("Exportando archivo final...")

    exportar(
        data_master
    )

    print(
        "\nProceso ETL completado correctamente."
    )


if __name__ == "__main__":
    main()