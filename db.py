# db.py

import psycopg2
from datetime import datetime

def insertar_reporte(data):
    try:
        # Ajusta estos valores según tu configuración local
        conn = psycopg2.connect(
            dbname="cierres_tienda",
            user="postgres",
            password="Dani-2032",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Insertar en reportes
        cursor.execute("""
            INSERT INTO reportes (fecha, tienda, clave, efectivo, datafono)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (datetime.now(), data['tienda'], data['clave'], data['efectivo'], data['datafono']))
        reporte_id = cursor.fetchone()[0]

        # Insertar gastos
        for gasto in data['gastos']:
            cursor.execute("""
                INSERT INTO gastos (reporte_id, valor, clase, descripcion)
                VALUES (%s, %s, %s, %s)
            """, (reporte_id, gasto['valor'], gasto['clase'], gasto['descripcion']))

        # Insertar otros medios de pago
        for pago in data['otros_pagos']:
            cursor.execute("""
                INSERT INTO otros_medios_pago (reporte_id, valor, medio, descripcion)
                VALUES (%s, %s, %s, %s)
            """, (reporte_id, pago['valor'], pago['medio'], pago['descripcion']))

        # Insertar cajas
        for caja in data['cajas']:
            cursor.execute("""
                INSERT INTO cajas (reporte_id, caja_id, valor)
                VALUES (%s, %s, %s)
            """, (reporte_id, caja['id'], caja['valor']))

        conn.commit()
        print("✅ Reporte guardado exitosamente")

    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
