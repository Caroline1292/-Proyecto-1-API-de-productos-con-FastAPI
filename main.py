"""
Titulo: Proyecto tiendita
Autor: Carolina Ruiz Gudiño
Descripción: Configuración de la API para gestión de inventario.
Fecha: 14-octubre-2026
"""


from fastapi import FastAPI  #HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio


app = FastAPI()

#Prueba asyncio
@app.get("/prueba-asyncio")
async def pruebaAsyncio():
    await asyncio.sleep(5)
    print("Se acaba de terminar los 5 segundos")
    return{"Message": "Respuesta después de 5 segundos"}
    


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


inventario = [
    {"id": 1, "nombre": "Coca-Cola", "precio": 20, "cantidad": 25},
    {"id": 2, "nombre": "Papas", "precio": 15, "cantidad": 40},
    {"id": 3, "nombre": "Café", "precio": 18, "cantidad": 15}
]

#ejemplo de API - GET para obtener mensaje inicial
@app.get("/")
def home():
    #try:
        #print("hola1")
        #resultado = "1" + 1,
        #print ("hola2")
        return {"Message": "Hola bienvenido"}
    #except Exception as error:
        #return {"Error": "Hubo un error (error)"}

#GET Obtiene lista de productos de mi inventario
@app.get("/productos")
async def getProductos():
    return inventario

#POST Agrega producto a mi inventario
@app.post("/productos")
async def addProducto(producto: dict):

    # Simula guardar en una base de datos (operación de espera / E/S)
    await asyncio.sleep(1)

    nuevo_id = max([p["id"] for p in inventario], default=0) + 1
    nuevo_producto = {
        "id": nuevo_id,    
        "nombre": producto["nombre"],
        "precio": float(producto["precio"]),
        "cantidad": int(producto["cantidad"])
    }

    inventario.append(nuevo_producto)

    return inventario

#DELETE Borrar producto de mi inventario
@app.delete("/productos/{producto_id}")
async def deleteProducto(producto_id: int):

    # Simula borrar en una base de datos (operación de espera / E/S)
    await asyncio.sleep(1)

    for producto in inventario:
        if producto["id"] == producto_id:
            inventario.remove(producto)
            return {"Message": "El producto fue eliminado"}
    return {"Message": "No fue encontrado el producto"}
  
