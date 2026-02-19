# 🌿 GitFlow — Guía Completa

> **GitFlow** es un modelo de ramificación para Git creado por **Vincent Driessen** en 2010.  
> Define una estructura estricta de ramas que facilita el trabajo en equipo, los releases y el mantenimiento paralelo de versiones.

---

## 📌 ¿Por qué usar GitFlow?

Sin un flujo definido, los repositorios en equipo tienden al caos:

| Problema sin GitFlow | Solución con GitFlow |
|---|---|
| Todos trabajan en `main` directamente | Nadie toca `main` salvo en releases |
| Features a medias llegan a producción | Cada feature vive en su propia rama |
| Es difícil hacer hotfixes urgentes | `hotfix/` permite parchear producción sin romper el desarrollo |
| Los releases son impredecibles | `release/` estabiliza el código antes de salir |
| El historial de commits es un desastre | Merge commits etiquetados clarifican qué fue cada cosa |

**Úsalo cuando:**
- Tienes un equipo de 2+ personas
- Tu proyecto tiene releases con versiones (`v1.0`, `v2.3`...)
- Necesitas mantener producción estable mientras desarrollas

**No lo uses cuando:**
- Haces deploys continuos (CI/CD puro) → prefiere **Trunk-Based Development**
- Trabajas solo en un proyecto personal pequeño

---

## 🏗️ Las 5 Ramas de GitFlow

```
main ──────────────────────────────────────────── producción estable (tags de versión)
develop ───────────────────────────────────────── integración continua de features
feature/xxx ──────────────────────────────────── desarrollo de funcionalidades
release/x.x ──────────────────────────────────── preparación para producción
hotfix/xxx ───────────────────────────────────── parches urgentes en producción
```

### Resumen de responsabilidades

| Rama | Origen | Merge hacia | Propósito |
|---|---|---|---|
| `main` | — | — | Código en producción. Siempre estable |
| `develop` | `main` | — | Base de integración. Siempre funcional |
| `feature/*` | `develop` | `develop` | Una feature, un ticket, una idea |
| `release/*` | `develop` | `main` + `develop` | Congela features, solo bugfixes |
| `hotfix/*` | `main` | `main` + `develop` | Parche urgente de producción |

---

## 📊 Diagrama General del Flujo

```mermaid
gitGraph
   commit id: "v0.1.0 — init" tag: "v0.1.0"

   branch develop
   checkout develop
   commit id: "setup del proyecto"

   branch feature/login
   checkout feature/login
   commit id: "feat: formulario de login"
   commit id: "feat: validación de campos"
   checkout develop
   merge feature/login id: "merge feature/login"

   branch feature/registro
   checkout feature/registro
   commit id: "feat: pantalla de registro"
   commit id: "feat: hash de contraseñas"
   checkout develop
   merge feature/registro id: "merge feature/registro"

   branch release/1.0
   checkout release/1.0
   commit id: "chore: bump version 1.0.0"
   commit id: "fix: typo en mensaje de error"
   checkout main
   merge release/1.0 id: "v1.0.0" tag: "v1.0.0"
   checkout develop
   merge release/1.0 id: "sync release→develop"

   branch hotfix/crash-login
   checkout hotfix/crash-login
   commit id: "fix: null pointer en auth"
   checkout main
   merge hotfix/crash-login id: "v1.0.1" tag: "v1.0.1"
   checkout develop
   merge hotfix/crash-login id: "sync hotfix→develop"

   checkout develop
   branch feature/dashboard
   checkout feature/dashboard
   commit id: "feat: dashboard de estadísticas"
   checkout develop
   merge feature/dashboard id: "merge feature/dashboard"
```

---

## 🔄 Flujos Individuales

### 1️⃣ Feature Branch — Nueva funcionalidad

```mermaid
flowchart TD
    A([🟢 develop]) -->|git checkout -b feature/mi-feature| B[feature/mi-feature]
    B --> C[💻 Desarrollas y haces commits]
    C --> D{¿Está lista?}
    D -- No --> C
    D -- Sí --> E[git checkout develop]
    E --> F[git merge --no-ff feature/mi-feature]
    F --> G[git branch -d feature/mi-feature]
    G --> H([🟢 develop actualizado])

    style A fill:#2d6a4f,color:#fff
    style H fill:#2d6a4f,color:#fff
    style B fill:#40916c,color:#fff
    style C fill:#52b788,color:#fff
    style D fill:#f4a261,color:#fff
    style E fill:#457b9d,color:#fff
    style F fill:#457b9d,color:#fff
    style G fill:#e63946,color:#fff
```

**Comandos:**
```bash
# 1. Crear la rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/nombre-feature

# 2. Trabajar normalmente
git add .
git commit -m "feat: descripción del cambio"

# 3. Mergear de vuelta a develop
git checkout develop
git merge --no-ff feature/nombre-feature

# 4. Subir y limpiar
git push origin develop
git branch -d feature/nombre-feature
git push origin --delete feature/nombre-feature
```

---

### 2️⃣ Release Branch — Preparar un release

```mermaid
flowchart TD
    A([🟢 develop]) -->|git checkout -b release/1.2| B[release/1.2]
    B --> C[🔒 Solo bugfixes y ajustes\nNO nuevas features]
    C --> D[Bump de versión\nen package.json / pom.xml]
    D --> E{¿Todo OK?}
    E -- No → fix --> C
    E -- Sí --> F[Merge a main]
    F --> G[🏷️ Tag v1.2.0]
    F --> H[Merge a develop]
    G --> I([🔵 main — v1.2.0 en prod])
    H --> J([🟢 develop actualizado])

    style A fill:#2d6a4f,color:#fff
    style B fill:#e9c46a,color:#333
    style C fill:#f4a261,color:#fff
    style D fill:#f4a261,color:#fff
    style E fill:#e76f51,color:#fff
    style F fill:#457b9d,color:#fff
    style G fill:#1d3557,color:#fff
    style I fill:#1d3557,color:#fff
    style J fill:#2d6a4f,color:#fff
```

**Comandos:**
```bash
# 1. Crear release desde develop
git checkout develop
git checkout -b release/1.2.0

# 2. Ajustes de versión y bugfixes
# Editar versión en package.json, etc.
git commit -m "chore: bump version to 1.2.0"

# 3. Mergear a main y etiquetar
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"

# 4. Mergear de vuelta a develop (para no perder los fixes)
git checkout develop
git merge --no-ff release/1.2.0

# 5. Limpiar
git branch -d release/1.2.0
git push origin main develop --tags
```

---

### 3️⃣ Hotfix Branch — Parche de emergencia

```mermaid
flowchart TD
    A([🔵 main — v1.2.0]) -->|Bug crítico en producción 🚨| B{Gravedad}
    B -- Crítico --> C[git checkout -b hotfix/crash-auth]
    C --> D[🛠️ Fix mínimo y enfocado]
    D --> E[git commit -m 'fix: ...']
    E --> F[Merge a main]
    F --> G[🏷️ Tag v1.2.1]
    F --> H[Merge a develop]
    G --> I([🔵 main — v1.2.1 estable])
    H --> J([🟢 develop con el fix])

    style A fill:#1d3557,color:#fff
    style B fill:#e63946,color:#fff
    style C fill:#e63946,color:#fff
    style D fill:#e63946,color:#fff
    style E fill:#e63946,color:#fff
    style F fill:#457b9d,color:#fff
    style G fill:#1d3557,color:#fff
    style I fill:#1d3557,color:#fff
    style J fill:#2d6a4f,color:#fff
```

**Comandos:**
```bash
# 1. Crear hotfix desde main (NO desde develop)
git checkout main
git checkout -b hotfix/crash-autenticacion

# 2. Aplicar el fix
git commit -m "fix: null pointer en validación de token"

# 3. Mergear a main y tagear
git checkout main
git merge --no-ff hotfix/crash-autenticacion
git tag -a v1.2.1 -m "Hotfix: crash en autenticación"

# 4. IMPORTANTE: también mergear a develop
git checkout develop
git merge --no-ff hotfix/crash-autenticacion

# 5. Limpiar
git branch -d hotfix/crash-autenticacion
git push origin main develop --tags
```

---

## 📅 Ciclo de vida completo — Línea de tiempo

```mermaid
timeline
    title Ciclo de vida de una versión con GitFlow
    section Semana 1
        Inicio del sprint     : Crear feature/login desde develop
                              : Crear feature/registro desde develop
    section Semana 2
        Desarrollo            : Commits en feature/login
                              : Commits en feature/registro
                              : Code reviews y PR
    section Semana 3
        Integración           : Merge feature/login → develop
                              : Merge feature/registro → develop
                              : Tests de integración en develop
    section Semana 4
        Release               : Crear release/1.0 desde develop
                              : QA y bugfixes en release/1.0
                              : Merge release/1.0 → main (v1.0.0)
    section Post-release
        Producción            : Tag v1.0.0 desplegado
                              : Monitoreo activo
                              : Hotfix si hay bugs críticos
```

---

## 🏷️ Convención de nombres de ramas

```
feature/   → feature/nombre-descriptivo
             feature/login-con-google
             feature/dashboard-estadisticas
             feature/api-pagos

release/   → release/MAJOR.MINOR
             release/1.0
             release/2.3

hotfix/    → hotfix/descripcion-corta
             hotfix/crash-en-login
             hotfix/seguridad-jwt
             hotfix/null-pointer-auth

bugfix/    → bugfix/descripcion       (en develop, no urgente)
             bugfix/validacion-email
```

---

## 📝 Convención de commits (Conventional Commits)

GitFlow funciona mejor combinado con **Conventional Commits**:

```
<tipo>(<scope>): <descripción corta>

[cuerpo opcional]

[footer opcional]
```

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `chore` | Tareas de mantenimiento (deps, configs) |
| `docs` | Solo documentación |
| `refactor` | Refactorización sin cambio de funcionalidad |
| `test` | Agregar o corregir tests |
| `perf` | Mejora de rendimiento |
| `ci` | Cambios en CI/CD |

**Ejemplos:**
```bash
git commit -m "feat(auth): agregar login con Google OAuth"
git commit -m "fix(api): corregir null pointer en endpoint de usuarios"
git commit -m "chore: actualizar dependencias de seguridad"
git commit -m "docs: agregar guía de GitFlow"
git commit -m "refactor(db): extraer lógica de conexión a repositorio"
```

---

## 🔀 Comparación con otros modelos

```mermaid
quadrantChart
    title Modelos de branching — Complejidad vs Control
    x-axis Baja Complejidad --> Alta Complejidad
    y-axis Poco Control --> Mucho Control
    quadrant-1 Equipos grandes, releases versioned
    quadrant-2 Máximo control, máxima complejidad
    quadrant-3 Proyectos pequeños, solopreneurs
    quadrant-4 CI/CD rápido, deploys continuos
    GitFlow: [0.75, 0.80]
    GitHub Flow: [0.35, 0.55]
    Trunk-Based: [0.25, 0.40]
    GitLab Flow: [0.55, 0.65]
    No flow: [0.10, 0.10]
```

| Modelo | Ideal para | Complejidad |
|---|---|---|
| **GitFlow** | Apps con versiones, equipos medianos/grandes | Alta |
| **GitHub Flow** | Deploys continuos, equipos ágiles | Baja |
| **GitLab Flow** | Entre GitFlow y GitHub Flow | Media |
| **Trunk-Based** | CI/CD puro, feature flags | Muy baja |

---

## ⚠️ Errores comunes y cómo evitarlos

### ❌ Hacer commits directamente en `main`
```bash
# MAL
git checkout main
git commit -m "fix rápido"

# BIEN — siempre por hotfix
git checkout -b hotfix/mi-fix
git commit -m "fix: descripción"
# → merge a main y a develop
```

### ❌ Crear features desde `main`
```bash
# MAL
git checkout main
git checkout -b feature/algo

# BIEN — siempre desde develop
git checkout develop
git checkout -b feature/algo
```

### ❌ Olvidar mergear el release/hotfix a `develop`
Esto causa que el fix se pierda en el próximo ciclo de desarrollo.
```bash
# Después de mergear a main, SIEMPRE:
git checkout develop
git merge --no-ff release/x.x  # o hotfix/xxx
```

### ❌ Features gigantes que duran semanas
Divide features grandes en sub-features. Ramas que viven demasiado generan conflictos monstruosos.

### ❌ Merge sin `--no-ff`
El flag `--no-ff` (no fast-forward) preserva el contexto histórico del merge:
```bash
# MAL — aplana el historial, pierdes contexto
git merge feature/login

# BIEN — crea un merge commit con contexto
git merge --no-ff feature/login -m "merge feature/login"
```

---

## 🚀 Setup rápido con git-flow CLI

Puedes usar la extensión `git-flow` para automatizar los comandos:

```bash
# Instalación
# macOS
brew install git-flow-avh

# Ubuntu/Debian
apt-get install git-flow

# Inicializar en tu repo (acepta los defaults con Enter)
git flow init

# === FEATURES ===
git flow feature start nombre-feature     # crea feature/nombre-feature
git flow feature finish nombre-feature    # merge a develop y borra rama

# === RELEASES ===
git flow release start 1.2.0             # crea release/1.2.0
git flow release finish 1.2.0            # merge a main+develop, tag, borra rama

# === HOTFIXES ===
git flow hotfix start crash-login        # crea hotfix/crash-login
git flow hotfix finish crash-login       # merge a main+develop, tag, borra rama
```

---

## 📋 Checklist por tipo de rama

### ✅ Antes de crear una feature
- [ ] Estoy en `develop` actualizado (`git pull origin develop`)
- [ ] El nombre describe claramente qué hace (`feature/autenticacion-jwt`)
- [ ] Tengo el ticket/issue de referencia

### ✅ Antes de mergear una feature a develop
- [ ] Los tests pasan localmente
- [ ] Hice `git pull origin develop` y resolví conflictos
- [ ] El código fue revisado (PR/MR aprobado)
- [ ] Usé `--no-ff` en el merge

### ✅ Antes de crear un release
- [ ] Todas las features del sprint están mergeadas en `develop`
- [ ] Los tests de integración pasan en `develop`
- [ ] Definí el número de versión (SemVer: MAJOR.MINOR.PATCH)

### ✅ Antes de cerrar un release
- [ ] QA aprobó el release branch
- [ ] Actualicé el número de versión en el código
- [ ] Mergeé a `main` Y a `develop`
- [ ] Creé el tag de versión
- [ ] Documenté el CHANGELOG

### ✅ Al crear un hotfix
- [ ] Parto desde `main` (no desde `develop`)
- [ ] El fix es mínimo y enfocado en el bug
- [ ] Mergeé a `main` Y a `develop`
- [ ] Incrementé el PATCH en la versión (v1.2.0 → v1.2.1)

---

## 🔢 Versionado Semántico (SemVer)

GitFlow usa tags que siguen **Semantic Versioning**:

```
v  MAJOR  .  MINOR  .  PATCH
v    1    .    4    .    2

MAJOR → cambios que rompen compatibilidad (breaking changes)
MINOR → nuevas features retrocompatibles
PATCH → bugfixes retrocompatibles (hotfixes)
```

```mermaid
flowchart LR
    A["v1.4.2"] -->|Nueva feature| B["v1.5.0"]
    A -->|Hotfix| C["v1.4.3"]
    B -->|Breaking change| D["v2.0.0"]

    style A fill:#457b9d,color:#fff
    style B fill:#2d6a4f,color:#fff
    style C fill:#e63946,color:#fff
    style D fill:#1d3557,color:#fff
```

---

## 📚 Referencias

- [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/) — Vincent Driessen (artículo original, 2010)
- [git-flow cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

*Documentado para el equipo EduConnect — Febrero 2026*