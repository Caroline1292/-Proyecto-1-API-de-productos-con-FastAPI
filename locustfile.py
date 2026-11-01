"""
Titulo: Pruebas de carga con Locust - Proyecto tiendita
Autor: Carolina Ruiz Gudiño
Descripción: Simula clientes que usan la API de la tiendita al mismo tiempo
             para medir cómo responde el servidor bajo carga.
Fecha: 16-octubre-2026

Cómo ejecutarlo:
    1. En una terminal, encender la API:   python -m uvicorn main:app --reload
    2. En otra terminal, encender Locust:  python -m locust
    3. Abrir en el navegador:              http://localhost:8089
"""

from locust import HttpUser, task, between


class UsuarioTienditaCompleto(HttpUser):
    # Dirección de la API
    host = "http://127.0.0.1:8000"

    # Cada usuario espera entre 0.2 y 0.8 segundos entre una tarea y otra
    wait_time = between(0.2, 0.8)

    # El número en @task es el peso: comprar se ejecuta el doble de veces
    # que las consultas, porque en una venta relámpago todos quieren comprar.
    @task(2)
    def comprarProducto(self):
        self.client.post("/productos/3")

    @task(1)
    def getProducto(self):
        self.client.get("/")

    # Función agregada: consulta el Café para ver cómo cambia su stock
    @task(1)
    def verCafe(self):
        self.client.get("/productos/3")

