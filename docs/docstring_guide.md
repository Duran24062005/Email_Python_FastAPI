# Docstrings

Centrémonos exclusivamente en los **Docstrings**. FastAPI es sumamente inteligente: si no quieres llenar tus decoradores `@app.get(...)` con mucho texto, puedes usar los comentarios multilínea de Python (`"""Docstring"""`) y FastAPI los extraerá automáticamente para la documentación.

Aquí tienes cómo usarlos para que tus rutas se vean profesionales en Swagger:

---

### 1. Estructura de un Docstring para FastAPI

FastAPI utiliza la primera línea del Docstring como **Resumen** y el resto como **Descripción** detallada. Incluso puedes usar **Markdown** (negritas, listas, código) dentro de ellos.

```python
@router.post("/register", status_code=201)
async def register_user(user: UserCreate):
    """
    Registra un nuevo usuario en el sistema.

    Este endpoint realiza las siguientes acciones:
    1. **Valida** que el correo no esté registrado.
    2. **Hashea** la contraseña usando bcrypt.
    3. **Crea** el registro en la base de datos MySQL.
    4. **Envía** un correo de bienvenida.

    - **user**: Objeto JSON con username, email y password.
    - **Retorno**: El objeto del usuario creado con su ID único.
    """
    return {"message": "Usuario registrado"}

```

---

### 2. Documentando Argumentos y Retornos (Estilo Google/NumPy)

Aunque FastAPI no parsea automáticamente cada argumento listado en el docstring para ponerlo en campos separados de la tabla de Swagger (eso lo hacen `Path` y `Query`), ponerlos en el docstring ayuda mucho a la lectura del código fuente y se renderiza elegantemente en la descripción general.

```python
@router.get("/search")
async def search_items(q: str, limit: int = 10):
    """
    Busca elementos por palabra clave.

    Args:
        q (str): El término de búsqueda o palabra clave.
        limit (int, optional): Máximo de resultados a devolver. Por defecto es 10.

    Returns:
        List[Item]: Una lista de objetos que coinciden con el criterio.
    """
    return []

```

---

### 3. Diferencia entre Decorador y Docstring

Es importante saber qué gana en cada caso si usas ambos:

| Elemento | Origen | Dónde aparece en Swagger |
| --- | --- | --- |
| **Título/Resumen** | Parámetro `summary` del decorador | En la barra principal de la ruta. |
| **Título (Fallback)** | Nombre de la función `def buscar_items` | Si no hay `summary`, usa el nombre (limpiando guiones bajos). |
| **Descripción** | Parámetro `description` del decorador | Dentro de la ruta expandida. |
| **Descripción (Fallback)** | **Docstring** `""" ... """` | Si no hay `description`, toma todo el contenido del docstring. |

> **Tip Pro:** Si usas el docstring, mantén el decorador limpio:
> `@router.get("/perfil", tags=["User"])`
> Y deja toda la explicación dentro de la función. Esto hace que tu código sea mucho más fácil de leer en editores como VS Code.

---

### 4. Ejemplo con Markdown avanzado

Puedes incluir bloques de código de ejemplo directamente en el docstring para guiar al usuario que consume tu API:

```python
@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """
    Elimina un usuario de forma lógica.

    ⚠️ **Advertencia**: Esta acción no se puede deshacer desde la API.

    Ejemplo de respuesta exitosa:
    ```json
    {
        "status": "deleted",
        "user_id": 123
    }
    ```
    """
    return {"status": "deleted", "user_id": user_id}

```

¿Te gustaría que te ayude a crear una **plantilla de Docstring estándar** para que todas tus rutas en tu proyecto de `Email_Python_FastAPI` tengan la misma estructura profesional?