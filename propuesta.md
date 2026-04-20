# Propuesta: Gestión de Catálogos Configurables

**Sistema:** SIT — Sistema Integral de Titulación del Valle de Oaxaca  
**Módulo:** Administración de catálogos por el coordinador  
**Fecha:** Abril 2026

---

## Problema actual

Los valores de modalidades, carreras, departamentos y niveles están hardcodeados en el sistema:

| Ubicación | Qué tiene hardcodeado |
|---|---|
| `frontend/src/app/datos.ts` | Lista de modalidades, carreras, departamentos, niveles |
| `service/EgresadoService.kt` | Lógica que distingue "Residencia Profesional" por nombre exacto |
| `service/RevisionService.kt` | Lógica de qué modalidades requieren revisión académica |
| `pages/seguimiento-proceso/` | Condiciones basadas en nombre de modalidad |

Si el instituto agrega una nueva carrera o modalidad, actualmente hay que modificar el código fuente y redesplegar.

---

## Solución propuesta

Crear un módulo de catálogos que permita al coordinador administrar estas listas desde la interfaz, almacenándolas en MongoDB. El resto del sistema las consulta dinámicamente.

---

## Catálogos propuestos

### 1. Modalidades

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | String | Nombre de la modalidad (ej. "Residencia Profesional") |
| `dias_plazo` | Int | Días que tiene el egresado para completar el trámite |
| `requiere_revision_academica` | Boolean | Si pasa por el departamento académico para revisión |
| `tipo_asesores` | String | Tipo de asesores requeridos (ej. "interno+externo", "solo_interno") |
| `texto_titulacion_integral` | String | Texto que aparece en el documento de titulación integral |
| `activa` | Boolean | Si está disponible para nuevos registros |

Este catálogo reemplaza la lógica hardcodeada en `EgresadoService` y `RevisionService` que actualmente usa `if (modalidad == "Residencia Profesional")`.

### 2. Departamentos

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | String | Nombre del departamento académico |
| `clave` | String | Clave corta (ej. "ISC", "CIVIL") |
| `activa` | Boolean | Si está disponible para asignación |

### 3. Carreras

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | String | Nombre de la carrera (ej. "Ingeniería en Sistemas Computacionales") |
| `departamento` | Ref → Departamento | Departamento al que pertenece |
| `activa` | Boolean | Si está disponible para nuevos registros |

### 4. Niveles

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | String | Nivel educativo (ej. "Licenciatura", "Maestría") |
| `activa` | Boolean | Si está disponible |

---

## Impacto en el sistema existente

### Backend

- Nuevas colecciones MongoDB: `modalidades`, `departamentos`, `carreras`, `niveles`
- Nuevos repositorios y servicios para cada catálogo
- `EgresadoService` y `RevisionService` dejan de comparar strings hardcodeados; en su lugar consultan el campo `requiere_revision_academica` de la modalidad
- La lógica de certificación (actualmente `if modalidad == "Residencia Profesional"`) se mueve a un campo configurable en el catálogo de modalidades
- Nuevos endpoints REST para CRUD de catálogos (solo rol coordinador)

### Frontend

- `datos.ts` se elimina o queda solo como fallback vacío
- Los dropdowns de alta de egresados (`/home/alta`) se cargan desde la API
- Nueva sección en el panel del coordinador: "Catálogos" con pestañas para cada uno
- Operaciones: agregar, editar nombre, activar/desactivar (no se borra para preservar historial)

---

## Puntos pendientes de decisión

1. **¿Quién puede editar los catálogos?** — Por ahora solo el coordinador. ¿Se necesita un rol "administrador" separado?

2. **¿Qué pasa con egresados ya registrados?** — Si se desactiva una modalidad/carrera, los egresados que ya la tienen no se ven afectados. Solo se oculta del dropdown para nuevos registros.

3. **¿Los departamentos agrupan las carreras o son independientes?** — La propuesta actual los vincula (carrera tiene FK a departamento), pero pueden mantenerse independientes si el flujo actual no los relaciona.

4. **Migración de datos existentes** — Al implementar esto, los egresados ya en MongoDB tienen modalidad/carrera como strings. Habría que decidir si se hace una migración o se convive con ambos esquemas.

---

## Orden de implementación sugerido

1. **Carreras y Departamentos** — Son los más simples, solo nombre + activa. Impacto mínimo en lógica existente.
2. **Niveles** — Similar a carreras.
3. **Modalidades** — El más complejo por los campos de comportamiento (`requiere_revision_academica`, etc.). Requiere refactorizar `EgresadoService` y `RevisionService`.
