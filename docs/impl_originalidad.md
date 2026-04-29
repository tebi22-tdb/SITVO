# Implementación: Verificación de Originalidad de Títulos

Fecha: 2026-04-22

---

## Qué hace

Verifica en tiempo real si el título de proyecto que el coordinador escribe al registrar un egresado ya existe o es muy similar a uno registrado. Bloquea el registro si hay coincidencia exacta, advierte si hay similitud alta (≥75%).

**Regla clave:** el bloqueo aplica sobre **todos** los registros sin importar `estado_general` — un título de un expediente vencido sigue bloqueado globalmente.

---

## Algoritmo de comparación

1. **Normalizar** el título:
   - Quitar acentos (NFD + eliminar diacríticos)
   - Convertir a minúsculas
   - Eliminar signos de puntuación
   - Descartar palabras ≤ 2 letras y stopwords en español
   - Resultado: un `Set<String>` de palabras significativas

2. **Comparar** contra cada `nombre_proyecto` existente usando **similitud Jaccard**:
   - `jaccard = |intersección| / |unión|`
   - Conjuntos idénticos → **BLOQUEADO**
   - Jaccard ≥ 0.75 → **ADVERTENCIA**
   - Jaccard < 0.75 → **LIBRE**

3. Acepta `excluirId` para ignorar el propio registro al editar un egresado.

---

## Archivos creados

### `src/main/kotlin/com/sit_titulacion/sit/service/OriginalidadService.kt`

```kotlin
package com.sit_titulacion.sit.service

import com.sit_titulacion.sit.repository.EgresadoRepository
import org.springframework.stereotype.Service
import java.text.Normalizer

data class OriginalidadResultado(
    val estado: String,          // "LIBRE", "ADVERTENCIA" o "BLOQUEADO"
    val tituloSimilar: String? = null,
)

@Service
class OriginalidadService(private val egresadoRepository: EgresadoRepository) {

    private val STOPWORDS = setOf(
        "de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas",
        "y", "e", "o", "u", "a", "en", "con", "por", "para", "que", "se",
        "al", "su", "sus", "es", "son", "como", "desde", "hacia", "hasta",
        "entre", "sobre", "bajo", "sin", "ante", "tras",
    )

    fun verificar(titulo: String, excluirId: String? = null): OriginalidadResultado {
        if (titulo.isBlank()) return OriginalidadResultado("LIBRE")
        val palabrasNuevas = normalizarPalabras(titulo)
        if (palabrasNuevas.isEmpty()) return OriginalidadResultado("LIBRE")

        for (e in egresadoRepository.findAll()) {
            if (excluirId != null && e.id?.toString() == excluirId) continue
            val tituloExistente = e.datos_proyecto.nombre_proyecto
            if (tituloExistente.isBlank()) continue
            val palabrasExistente = normalizarPalabras(tituloExistente)
            if (palabrasExistente.isEmpty()) continue

            if (palabrasNuevas == palabrasExistente) {
                return OriginalidadResultado("BLOQUEADO", tituloExistente)
            }

            val interseccion = palabrasNuevas.intersect(palabrasExistente).size
            val union = (palabrasNuevas + palabrasExistente).size
            if (union > 0 && interseccion.toDouble() / union >= 0.75) {
                return OriginalidadResultado("ADVERTENCIA", tituloExistente)
            }
        }
        return OriginalidadResultado("LIBRE")
    }

    private fun normalizarPalabras(titulo: String): Set<String> {
        val sinAcentos = Normalizer.normalize(titulo, Normalizer.Form.NFD)
            .replace(Regex("\\p{InCombiningDiacriticalMarks}"), "")
        return sinAcentos.lowercase()
            .replace(Regex("[^a-z0-9\\s]"), " ")
            .split(Regex("\\s+"))
            .filter { it.length > 2 && it !in STOPWORDS }
            .toSet()
    }
}
```

---

## Archivos modificados

### Backend: `EgresadoController.kt`

**Cambio 1 — Inyección del servicio** en el constructor:
```kotlin
private val originalidadService: OriginalidadService,
```

**Cambio 2 — Nuevo endpoint** (agregar antes de `crear()`):
```kotlin
/** Verifica si un título de proyecto choca con registros existentes. Requiere sesión. */
@GetMapping("/verificar-originalidad")
fun verificarOriginalidad(
    @RequestParam titulo: String,
    @RequestParam(required = false) excluirId: String? = null,
    @AuthenticationPrincipal principal: UsuarioPrincipal?,
): ResponseEntity<*> {
    if (principal == null) return ResponseEntity.status(HttpStatus.FORBIDDEN).build<Void>()
    val resultado = originalidadService.verificar(titulo, excluirId)
    return ResponseEntity.ok(
        mapOf(
            "estado" to resultado.estado,
            "titulo_similar" to (resultado.tituloSimilar ?: ""),
        ),
    )
}
```

**Cambio 3 — Guard en `crear()`** (primeras líneas del método, antes de llamar al servicio):
```kotlin
// Firma cambia de ResponseEntity<EgresadoResponseDto> a ResponseEntity<*>
fun crear(...): ResponseEntity<*> {
    val origResultado = originalidadService.verificar(datos.nombreProyecto ?: "")
    if (origResultado.estado == "BLOQUEADO") {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(
            EgresadoResponseDto(
                id = "",
                numero_control = datos.numero_control,
                credenciales_enviadas_correo = false,
                aviso_credenciales = "El título «${datos.nombreProyecto}» ya está registrado en el sistema y no puede usarse nuevamente.",
            ),
        )
    }
    // ... resto del método sin cambios
```

---

### Frontend: `egresado.service.ts`

Agregar método al final de la clase `EgresadoService`:
```typescript
verificarOriginalidad(titulo: string, excluirId?: string): Observable<{ estado: string; titulo_similar: string }> {
  let params = new HttpParams().set('titulo', titulo);
  if (excluirId) params = params.set('excluirId', excluirId);
  return this.http.get<{ estado: string; titulo_similar: string }>(`${API}/verificar-originalidad`, { params });
}
```

---

### Frontend: `nuevo-egresado.component.ts`

**Imports nuevos:**
```typescript
import { Component, EventEmitter, Input, OnChanges, OnDestroy, OnInit, Output, SimpleChanges } from '@angular/core';
import { EgresadoDetail, EgresadoService } from '../../../services/egresado.service';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, of, takeUntil, catchError } from 'rxjs';
```

**Clase:** `implements OnChanges, OnInit, OnDestroy`

**Constructor:** inyectar `EgresadoService`:
```typescript
constructor(private fb: FormBuilder, private egresadoService: EgresadoService) {
```

**Propiedades nuevas** (en la clase):
```typescript
originalidadEstado: 'LIBRE' | 'ADVERTENCIA' | 'BLOQUEADO' | 'comprobando' | null = null;
originalidadTituloSimilar: string | null = null;
private destroy$ = new Subject<void>();
```

**Métodos nuevos:**
```typescript
ngOnInit(): void {
  this.form.get('nombre_proyecto')!.valueChanges.pipe(
    debounceTime(600),
    distinctUntilChanged(),
    switchMap(titulo => {
      const t = (titulo || '').trim();
      if (t.length < 5) {
        this.originalidadEstado = null;
        return of(null);
      }
      this.originalidadEstado = 'comprobando';
      const excluirId = this.egresadoParaEditar?.id;
      return this.egresadoService.verificarOriginalidad(t, excluirId).pipe(
        catchError(() => of(null)),
      );
    }),
    takeUntil(this.destroy$),
  ).subscribe(resultado => {
    if (resultado === null) {
      if (this.originalidadEstado === 'comprobando') this.originalidadEstado = null;
      return;
    }
    this.originalidadEstado = resultado.estado as 'LIBRE' | 'ADVERTENCIA' | 'BLOQUEADO';
    this.originalidadTituloSimilar = resultado.titulo_similar || null;
  });
}

ngOnDestroy(): void {
  this.destroy$.next();
  this.destroy$.complete();
}
```

**Guard en `onSubmit()`** (agregar después de `markAllAsTouched`):
```typescript
if (this.originalidadEstado === 'BLOQUEADO') return;
```

---

### Frontend: `nuevo-egresado.component.html`

Reemplazar el bloque del campo `nombre_proyecto`:
```html
<div class="form-campo" [class.form-campo-error]="campoInvalido('nombre_proyecto') || originalidadEstado === 'BLOQUEADO'">
  <label for="nombre_proyecto">Nombre del proyecto <span class="form-obligatorio">*</span></label>
  <input id="nombre_proyecto" type="text" formControlName="nombre_proyecto" />
  <span class="form-error-msg" *ngIf="campoInvalido('nombre_proyecto')">Campo obligatorio</span>
  <div class="originalidad-indicador" *ngIf="originalidadEstado">
    <span *ngIf="originalidadEstado === 'comprobando'" class="orig-comprobando">Verificando originalidad...</span>
    <span *ngIf="originalidadEstado === 'LIBRE'" class="orig-libre">✓ Título disponible</span>
    <span *ngIf="originalidadEstado === 'ADVERTENCIA'" class="orig-advertencia">⚠ Título similar al existente: «{{ originalidadTituloSimilar }}»</span>
    <span *ngIf="originalidadEstado === 'BLOQUEADO'" class="orig-bloqueado">✗ Título bloqueado, ya existe: «{{ originalidadTituloSimilar }}»</span>
  </div>
</div>
```

Botón submit:
```html
<button type="submit" class="btn btn-agregar"
  [disabled]="guardando || originalidadEstado === 'BLOQUEADO' || originalidadEstado === 'comprobando'">
  {{ guardando ? 'Guardando...' : (editando ? 'Guardar cambios' : 'Agregar') }}
</button>
```

---

### Frontend: `nuevo-egresado.component.css`

Agregar al final:
```css
.originalidad-indicador {
  margin-top: 0.4rem;
  font-size: 0.85rem;
  font-weight: 500;
}

.orig-comprobando { color: #64748b; }

.orig-libre { color: #16a34a; }

.orig-advertencia {
  color: #b45309;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  display: inline-block;
}

.orig-bloqueado {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  display: inline-block;
}
```

---

## Cómo probar

1. Levanta backend (`./gradlew bootRun --args='--spring.profiles.active=dev'`) y frontend (`cd frontend && npm start`).
2. Entra como coordinador en `http://localhost:4200`.
3. Abre el formulario "Agregar egresado" y escribe en el campo **Nombre del proyecto**:
   - Título inexistente → indicador **verde** tras 600 ms.
   - Título idéntico a uno registrado → indicador **rojo**, botón deshabilitado.
   - Título con ≥75% palabras en común → indicador **ámbar**, puede guardar.
4. Verifica en DevTools → Network → filtrar `verificar-originalidad`: debe dispararse solo al dejar de escribir (debounce de 600 ms).

---

## Limitaciones conocidas

- El algoritmo usa `findAll()` en cada verificación. Suficiente para cientos de registros; si la BD crece a miles, agregar una proyección en el repositorio para traer solo `datos_proyecto.nombre_proyecto`.
- No usa embeddings ni servicios externos: la similitud es puramente léxica (palabras compartidas). Títulos semánticamente equivalentes con vocabulario diferente no se detectan.
