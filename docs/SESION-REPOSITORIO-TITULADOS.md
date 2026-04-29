# Sesión: Repositorio de Titulados + Flujo de Finalización

Fecha: 2026-04-22

---

## Resumen de lo implementado

### Corrección de plazos por modalidad (frontend)

**Archivos modificados:**
- `frontend/src/app/pages/seguimiento-proceso/seguimiento-proceso.component.ts`
- `frontend/src/app/pages/seguimiento/seguimiento.component.ts`

**Problema:** Ambos componentes calculaban fechas límite con días fijos (183, 365, 548) en lugar de meses calendario.

**Solución:** Se reemplazaron las funciones por:
```typescript
function mesesPorModalidad(modalidad: string): number | null {
  const m = modalidad.trim().toLowerCase();
  if (m.includes('residencia'))  return 6;
  if (m.includes('tesina'))      return 18;
  if (m.includes('tesis'))       return 18;
  if (m.includes('curso'))       return 12;
  if (m.includes('investigaci')) return 12;
  if (m.includes('ceneval'))     return null; // sin plazo
  return 12;
}

function sumarMesesCalendario(base: Date, meses: number): Date {
  return new Date(base.getFullYear(), base.getMonth() + meses, base.getDate());
}
```

**Regla de negocio:** El conteo es calendario puro — si empieza el 5 de febrero, vence el 5 de agosto (6 meses), no 183 días después. CENEVAL no tiene plazo porque es un examen.

---

### Paso 12 del dashboard del estudiante

**Archivo:** `frontend/src/app/pages/seguimiento/seguimiento.component.ts`

**Cambio:** El paso 12 ("Proceso finalizado") ya NO se completa automáticamente cuando se genera el 9.3. Ahora se completa cuando `estado_general === 'titulado'`.

```typescript
const c12 = d.estado_general === 'titulado';
```

---

### Sección de entrega de documentos finales (Opción B)

**Archivo:** `frontend/src/app/pages/seguimiento/seguimiento.component.html`

Se agregó una sección al final del timeline, visible cuando `fecha_creacion_anexo_9_3` está completo:

```html
<div *ngIf="datos.fecha_creacion_anexo_9_3" class="entrega-final-cta">
  <ng-container *ngIf="datos.estado_general !== 'titulado'">
    <h4>Paso final: entrega de documentos</h4>
    <p>Sube en un solo PDF tus documentos 9.1, 9.2 y 9.3...</p>
    <!-- TODO (compañero): input de archivo y botón de subida -->
  </ng-container>
  <ng-container *ngIf="datos.estado_general === 'titulado'">
    <p>✓ Documentos entregados. ¡Tu titulación está registrada!</p>
  </ng-container>
</div>
```

El compañero debe conectar aquí el `input[type=file]` que llame a:
`POST /api/egresados/mi-seguimiento/documento-final` con `FormData { archivo: File }`.

---

### Fase 1 — Flujo de finalización (backend)

#### Dominio: `Egresado.kt`
Se agregaron 3 campos nuevos (todos nullable con default null — sin impacto en documentos MongoDB existentes):
```kotlin
@Field("gridfs_id_doc_final") val gridfsIdDocFinal: ObjectId? = null,
@Field("fecha_subida_doc_final") val fechaSubidaDocFinal: Instant? = null,
@Field("fecha_titulacion") val fechaTitulacion: Instant? = null,
```

#### DTOs: `EgresadoDtos.kt`
Se agregaron a `EgresadoDetailDto`:
```kotlin
@JsonProperty("fecha_titulacion") val fecha_titulacion: String? = null,
@JsonProperty("tiene_doc_final") val tiene_doc_final: Boolean = false,
```

#### Servicio: `EgresadoService.kt`
Se agregaron tres métodos:

**`subirDocumentoFinal(numeroControl, archivo)`**
- Valida que `fechaCreacionAnexo93 != null` (todos los pasos completados)
- Valida que `estado_general != "titulado"` (no duplicar)
- Sube el PDF a GridFS
- Setea `estado_general = "titulado"`, `fechaTitulacion = now()`
- Agrega entrada al `historial_estados`

**`mesesPorModalidad(modalidad)`** — misma lógica que frontend (consistencia).

**`verificarYMarcarVencido(e)`** — al cargar un egresado para detalle:
- Si ya es `"titulado"` o `"vencido"`: no hace nada
- Si CENEVAL (null): no hace nada
- Si la fecha de inicio + meses de plazo < hoy: persiste `estado_general = "vencido"` en MongoDB y lo devuelve

Se actualizaron `obtenerPorId`, `obtenerPorNumeroControl`, `obtenerPorEgresadoId` para pasar por `verificarYMarcarVencido` antes de devolver el DTO.

**Fecha de inicio para el plazo:** `fechaEnviadoDepartamentoAcademico ?: fechaCreacion` (igual que el frontend).

#### Controller: `EgresadoController.kt`
Nuevo endpoint:
```
POST /api/egresados/mi-seguimiento/documento-final
Content-Type: multipart/form-data
archivo: <PDF>
Authorization: Bearer <token egresado>
```
- Responde 200 si se marcó como titulado
- Responde 400 si el proceso no está completo o ya estaba titulado
- Responde 400 si el archivo no es PDF/DOCX (validado por `subirArchivo`)

---

### Fase 2 — Repositorio público de titulados

#### Backend

**`RepositorioDtos.kt`** — DTO público sin datos sensibles:
Incluye: nombre completo, carrera, nivel, modalidad, nombre_proyecto, asesores, año.
NO incluye: número de control, teléfono, dirección, correo, ID de MongoDB.

**`RepositorioController.kt`** — endpoint:
```
GET /api/repositorio   (sin autenticación)
```
Devuelve todos los egresados con `estado_general = "titulado"`, ordenados por año descendente.
El año se obtiene de `fechaTitulacion ?: fechaCreacionAnexo93 ?: fechaCreacion`.

**`EgresadoRepository.kt`** — query nueva:
```kotlin
@Meta(maxExecutionTimeMs = 5000)
@Query("{ 'estado_general' : ?0 }")
fun findByEstadoGeneral(estado: String): List<Egresado>
```

**`SecurityConfig.kt`** — regla agregada antes de `/api/**`:
```kotlin
.requestMatchers("/api/repositorio/**").permitAll()
```

#### Frontend

**Ruta:** `/repositorio` — sin guard de autenticación (pública).

**`repositorio.service.ts`** — llama a `GET /api/repositorio`.

**`repositorio.component`** — página pública con:
- Header institucional (sin app-header autenticado)
- Barra de búsqueda por título/autor/carrera
- Filtros por carrera y modalidad
- Grid de cards responsivo
- Muestra: título del proyecto, autor, badges de modalidad/carrera/nivel, asesores, año

---

## Estados de `estado_general` definidos

| Estado | Quién lo asigna | Cuándo |
|--------|----------------|--------|
| `registrado` | Sistema al crear | Alta del egresado |
| `vencido` | Sistema (lazy) | Al cargar el detalle y el plazo expiró |
| `titulado` | Sistema | Al subir el PDF final por el egresado |

**Regla de originalidad (pendiente Fase 3):** Un `nombre_proyecto` que exista en CUALQUIER registro (cualquier estado, incluyendo `vencido`) bloquea ese título globalmente. Nadie puede registrar el mismo título aunque el expediente anterior haya vencido.

---

## Pendiente: Fase 3 — Verificación de originalidad

**Lo que falta implementar:**

**Backend:**
- `OriginalidadService.kt` — verifica unicidad del `nombre_proyecto`:
  1. Búsqueda exacta normalizada (lowercase, sin stopwords)
  2. Solapamiento de palabras clave > 75% → advertencia
  3. No requiere embeddings ni servicios externos
- Integrar en `EgresadoService.crear()` para bloquear al registrar
- Endpoint `GET /api/egresados/verificar-originalidad?titulo=...` para validación en tiempo real

**Frontend:**
- Validación en `nuevo-egresado.component` mientras el coordinador escribe el nombre del proyecto
- Mostrar `BLOQUEADO` (error) o `ADVERTENCIA` (amarillo) o `LIBRE` (verde) en tiempo real

---

## Archivos creados en esta sesión

```
src/main/kotlin/.../web/api/RepositorioController.kt
src/main/kotlin/.../web/api/dto/RepositorioDtos.kt
frontend/src/app/services/repositorio.service.ts
frontend/src/app/pages/repositorio/repositorio.component.ts
frontend/src/app/pages/repositorio/repositorio.component.html
frontend/src/app/pages/repositorio/repositorio.component.css
```

## Archivos modificados en esta sesión

```
src/main/kotlin/.../domain/Egresado.kt
src/main/kotlin/.../service/EgresadoService.kt
src/main/kotlin/.../web/api/EgresadoController.kt
src/main/kotlin/.../web/api/dto/EgresadoDtos.kt
src/main/kotlin/.../repository/EgresadoRepository.kt
src/main/kotlin/.../config/SecurityConfig.kt
frontend/src/app/app.routes.ts
frontend/src/app/pages/seguimiento/seguimiento.component.ts
frontend/src/app/pages/seguimiento/seguimiento.component.html
frontend/src/app/pages/seguimiento-proceso/seguimiento-proceso.component.ts
```
