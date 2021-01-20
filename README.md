# Prueba técnica backend

Haciendo uso del framework de desarrollo para python [FastAPI](https://fastapi.tiangolo.com/) , desarrollar las siguientes funcionalidades:
  1. Obtener un listado de <entidad>
  2. Obtener la información de <entidad> por id
  3. Actualizar la información de una <entidad>
  4. Borrar la <entidad>

Donde la <entidad> con la que se va a trabajar tiene el siguiente modelo de datos:

```python
{
  id: string,
  name: string,
  picture: string,
  create_date: string,
  is_adopted: bool
}
```

La entidad que se va a manejar es **Dog**. Para cumplir las necesidades listadas en las funcionalidades se requiere tener los siguientes ENPOINTS:

  * GET -> /api/dogs : Obtener una listado.
  * GET -> /api/dogs/{name} : Obtener una entrada a partir del nombre.
  * GET -> /api/dogs/is_adopted : Obtener todas las entradas donde la bandera is_adopted sea True.
  * POST -> /api/dogs/{name}: Guardar un registro según el esquema de arriba. El campo picture se debe rellenar con una consulta al [API](https://dog.ceo/api/breeds/image/random) externa.
  * PUT -> /api/dogs/{name}: Actualizar un registro según el nombre.
  * DELETE -> /api/dogs/{name}: Borrar un registro según el nombre.

Un ejemplo de registro:

```Json
{
  "name": "Lazy",
  "picture": "https:\/\/images.dog.ceo\/breeds\/papillon\/n02086910_6483.jpg",
  "create_date": "2020-02-20 20:58:55.164954",
  "is_adopted": true,
}
```

Los datos pueden ser guardados utilizando una base de datos, o se puede optar por hacer uso de una lista en memoria RAM.

## Opcional

1. Las rutas para ingresar un nuevo camino (el POST) debería estar protegida con alguna política de seguridad, se recomienda usar **JWT**.
2. Realizar dockerfile y docker-compose de la aplicación.
3. Desarrollar un Worker con [Celery](https://grega.xyz/2019/07/fastapi-and-celery/) cuando se llame la función POST. Las tareas en segundo plano tienen sentido para actividades que se pueden realizar de forma asíncrona. Puedes simular una latencia en el registro de los perros de unos segundos para verificar que el "Worker" está funcionando.
4. Añadir una nueva entidad llamada User con sus respectivos endpoints de CRUD básico. Esta entidad tendrá una relación de uno a muchos con la entidad Dog, es decir, un User puede tener uno o muchos Dogs (para esto solo se requiere que la entidad Dog se agregue un nuevo campo llamado id_user y guarde el id de un usuario). Los campos para la entidad User pueden ser: id, nombre, apellido, email.
