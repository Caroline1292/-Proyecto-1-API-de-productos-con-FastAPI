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

import random
from locust import HttpUser, task, between


class ClienteTiendita(HttpUser):
    # Dirección de la API que se va a probar
    host = "http://127.0.0.1:8000"

    # Cada cliente simulado espera entre 1 y 3 segundos entre una acción y otra,
    # como lo haría una persona real usando la tienda.
    wait_time = between(1, 3)

    def revisar_respuesta(self, respuesta):
        """
        Revisa la respuesta del servidor.
        Si es 429, significa que el middleware bloqueó la petición por pasar
        el límite de 5 peticiones por segundo. Se marca como falla, pero con un
        mensaje claro para que en el reporte de Locust se entienda el motivo.
        """
        if respuesta.status_code == 429:
            respuesta.failure("429: bloqueada por el middleware (máximo 5 peticiones por segundo)")
        elif respuesta.status_code == 400:
            respuesta.failure("400: ya no hay stock (el Lock evitó vender de más)")
        elif respuesta.status_code != 200:
            respuesta.failure(f"Error inesperado: {respuesta.status_code}")
        else:
            respuesta.success()

    # El número en @task es el "peso": ver productos pasa 3 veces más seguido
    # que agregar uno, porque en una tienda se consulta más de lo que se registra.
    @task(3)
    def verProductos(self):
        with self.client.get("/productos", catch_response=True) as respuesta:
            self.revisar_respuesta(respuesta)

    @task(1)
    def verInicio(self):
        with self.client.get("/", catch_response=True) as respuesta:
            self.revisar_respuesta(respuesta)

    @task(1)
    def agregarYEliminarProducto(self):
        # Se agrega un producto de prueba...
        nuevo = {
            "nombre": f"Producto prueba {random.randint(1, 1000)}",
            "precio": random.randint(5, 50),
            "cantidad": random.randint(1, 20),
        }
        with self.client.post("/productos", json=nuevo, catch_response=True) as respuesta:
            self.revisar_respuesta(respuesta)
            if respuesta.status_code != 200:
                return
            # El POST regresa todo el inventario; el producto nuevo es el último
            id_nuevo = respuesta.json()[-1]["id"]

        # ...y después se elimina, para no llenar el inventario de productos de prueba.
        # name= agrupa todos los DELETE en una sola fila del reporte.
        with self.client.delete(f"/productos/{id_nuevo}", name="/productos/[id]",
                                catch_response=True) as respuesta:
            self.revisar_respuesta(respuesta)

    # Como en el ejemplo del profesor: muchos clientes intentan comprar el
    # mismo producto (id 3, Café) al mismo tiempo para probar el asyncio.Lock.
    # Al acabarse el stock, el servidor responde 400 y nunca queda negativo.
    @task(2)
    def comprarProducto(self):
        with self.client.post("/productos/3", name="/productos/3 (comprar)",
                              catch_response=True) as respuesta:
            self.revisar_respuesta(respuesta)
