## 📄 Estándar de Documentación (Docstrings) - FastAPI Project

Este documento define cómo deben documentarse las rutas para garantizar que el **Swagger UI** (`/docs`) sea útil, descriptivo y profesional.

### 1. Estructura General

Cada función de ruta debe incluir un Docstring triple (`"""`) con los siguientes bloques:

1. **Resumen (Primera línea):** Una frase corta en imperativo que describe la acción principal.
2. **Descripción detallada:** Párrafo que explica la lógica de negocio o procesos internos (validaciones, hashes, DB).
3. **Sección de Reglas/Notas:** Uso de emojis (⚠️, ✅, ℹ️) para resaltar advertencias o requisitos.
4. **Sección de Parámetros/Retorno:** Aunque FastAPI los detecta, se listan para claridad del desarrollador.

---

### 2. Plantilla Base (Snippet)

Copia este formato para tus nuevas rutas:

```python
@router.post("/ruta", tags=["Categoría"])
async def nombre_funcion(parametro: Tipo):
    """
    Resumen corto de la acción (Aparece como descripción principal).

    Explicación detallada de lo que sucede internamente. Puedes usar varias líneas
    y formato Markdown para dar énfasis.

    ### Lógica de negocio:
    - **Paso 1:** Validación de datos.
    - **Paso 2:** Interacción con MySQL/Docker.
    - **Paso 3:** Respuesta al cliente.

    ⚠️ **Nota:** Mencionar si requiere tokens de autenticación o permisos especiales.

    - **parametro**: Descripción de qué representa este dato.
    - **Returns**: Descripción de lo que el cliente recibirá al final.
    """
    pass

```

---

### 3. Ejemplo Aplicado (Módulo de Auth)

Así es como debería verse una de tus rutas actuales con este estándar:

```python
@router.post("/login", tags=["Auth"])
async def login_user(credentials: OAuth2PasswordRequestForm = Depends()):
    """
    Autenticar usuario y generar token de acceso.

    Verifica las credenciales del usuario contra la base de datos MySQL. 
    Si son correctas, genera un JWT (JSON Web Token) válido por 30 minutos.

    ### Proceso:
    1. Busca el `username` en la tabla de usuarios.
    2. Compara el hash de la `password` usando **Passlib**.
    3. Si falla, lanza una excepción `401 Unauthorized`.

    ✅ **Retorno exitoso:** Un objeto JSON con el `access_token` y el `token_type`.
    """
    return {"access_token": "...", "token_type": "bearer"}

```

---

### 4. Recomendaciones de Formato Markdown en Swagger

FastAPI renderiza CommonMark, por lo que puedes usar:

* `**negrita**` para resaltar términos importantes.
* ``código`` para nombres de variables o tablas.
* `> bloque de cita` para notas importantes.
* `---` para líneas separadoras.

---