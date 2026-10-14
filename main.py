"""
Titulo: Proyecto tiendita
Autor: Carolina Ruiz Gudiño
Descripción: Configuración de la API para gestión de inventario.
Fecha:14-octubre-2026
"""


from fastapi import FastAPI, Request  
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import time


app = FastAPI()

#Prueba asyncio
@app.get("/prueba-asyncio")
async def pruebaAsyncio():
    await asyncio.sleep(5)
    print("Se acaba de terminar los 5 segundos")
    return{"Message": "Respuesta después de 5 segundos"}


# MIDDLEWARE: límite de 5 peticiones por segundo (por IP)
# Un middleware es código que se ejecuta ANTES y DESPUÉS de cada petición, sin importar a qué endpoint vaya. 
# Aquí lo usamos para revisar cuántas peticiones ha hecho cada cliente en el último segundo.

MAX_PETICIONES = 5        # Máximo de peticiones permitidas...
VENTANA_SEGUNDOS = 1.0    # ...en este intervalo de tiempo

peticiones_por_ip = {}    # Guarda: IP -> lista de horas de sus peticiones
candado = asyncio.Lock()  # Evita que dos peticiones modifiquen el diccionario al mismo tiempo


@app.middleware("http")
async def limitarPeticiones(request: Request, call_next):
    ip = request.client.host if request.client else "desconocida"

    # Solo una petición a la vez puede entrar a esta sección (asyncio.Lock)
    async with candado:
        ahora = time.monotonic()

        # Nos quedamos solo con las peticiones del último segundo
        recientes = [t for t in peticiones_por_ip.get(ip, []) if ahora - t < VENTANA_SEGUNDOS]

        # Si ya hizo 5 en el último segundo, la rechazamos con error 429
        if len(recientes) >= MAX_PETICIONES:
            peticiones_por_ip[ip] = recientes
            return JSONResponse(
                status_code=429,
                content={"Message": "Demasiadas peticiones. Máximo 5 por segundo."}
            )

        # Si no, registramos esta petición
        recientes.append(ahora)
        peticiones_por_ip[ip] = recientes

    # La petición sigue su camino hacia el endpoint (await = esperamos su respuesta)
    respuesta = await call_next(request)
    return respuesta


# CORS se agrega DESPUÉS del limitador para que quede "por fuera":
# así hasta la respuesta 429 lleva los permisos CORS y el navegador la puede leer.
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
# Endpoint async SIN await: leer una lista en memoria es inmediato, no hay nada que esperar (ni archivos, ni red, ni base de datos).
# Si el inventario estuviera en una base de datos aquí iría algo como:
#   productos = await db.obtener_productos()
@app.get("/productos")
async def getProductos():
    return inventario

#POST Agrega producto a mi inventario
# Endpoint async CON await: simulamos el tiempo que tardaría guardar en una base de datos. Mientras esta función espera, el servidor
# puede seguir atendiendo otras peticiones (no se bloquea).
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
# Endpoint async CON await: simulamos el tiempo que tardaría borrar el registro en una base de datos.
@app.delete("/productos/{producto_id}")
async def deleteProducto(producto_id: int):

    # Simula borrar en una base de datos (operación de espera / E/S)
    await asyncio.sleep(1)

    for producto in inventario:
        if producto["id"] == producto_id:
            inventario.remove(producto)
            return {"Message": "El producto fue eliminado"}
    return {"Message": "No fue encontrado el producto"}
  
