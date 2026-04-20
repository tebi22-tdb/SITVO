# Informe Técnico de Residencia Profesional
## Implementación de Sistema de Certificación Digital de Documentos

**Sistema:** SIT — Sistema Integral de Titulación del Valle de Oaxaca  
**Módulo desarrollado:** Certificación PKI + Verificación por QR de documentos académicos  
**Institución:** TECNM Campus Oaxaca  
**Fecha:** Abril 2026  

---

## 1. Introducción

Durante el desarrollo de la plataforma SIT se identificó la necesidad de garantizar la autenticidad e integridad de los documentos PDF que los egresados cargan al sistema como parte de su proceso de titulación. Sin un mecanismo de certificación, cualquier persona podría modificar un documento descargado y volver a presentarlo como original, sin que existiera forma de detectar la alteración.

Para resolver este problema se diseñó e implementó un módulo de certificación digital que combina dos tecnologías complementarias: **firma digital PKI** (infraestructura de clave pública) y **código QR de verificación**, cubriendo tanto el escenario digital como el escenario de documentos impresos en papel.

---

## 2. Problema que resuelve

| Escenario | Sin certificación | Con certificación |
|---|---|---|
| Documento digital | Cualquiera puede editar el PDF | La firma PKI invalida el documento si es modificado |
| Documento impreso | No hay forma de autenticar | El QR permite verificar autenticidad desde el celular |
| Migración de servidor | — | El ID de verificación es independiente de la URL |
| Verificación offline | — | Adobe Reader detecta la firma PKI sin internet |

---

## 3. Arquitectura de la solución

La certificación ocurre automáticamente en el backend en dos momentos del flujo de titulación:

```
Modalidad: Residencia Profesional
─────────────────────────────────────────────────────────────────
Coordinador presiona "Enviar al departamento académico"
    │
    ├── 1. Se guarda fecha_enviado_departamento_academico (timestamp)
    │
    └── 2. CertificacionPdfService.certificarDocumento()
            │
            ├── Lee PDF original desde MongoDB GridFS
            ├── Calcula SHA-256 del PDF original
            ├── Genera UUID único (ej. SIT-A3B4-C5D6-E7F8)
            ├── Genera código QR con URL de verificación
            ├── Agrega página de certificación al PDF (PDFBox)
            ├── Firma digitalmente el PDF completo (PKI + Bouncy Castle)
            ├── Guarda el PDF certificado en GridFS (reemplaza el original)
            └── Actualiza MongoDB: cert_uuid, cert_hash, fecha_certificacion

Otras modalidades (Tesis, Tesina, CENEVAL, Proyecto de Investigación)
─────────────────────────────────────────────────────────────────
Revisor académico presiona "Aprobar" en revisión de documento
    │
    └── Mismo proceso de certificación antes de marcar como aprobado
```

### Diagrama de componentes

```
Frontend Angular          Backend Spring Boot          MongoDB
──────────────────        ────────────────────         ───────
SeguimientoProcesoComponent
  │ POST /enviar-departamento-academico
  │                    EgresadoController
  │                         │
  │                    EgresadoService
  │                    .marcarEnviadoDepartamentoAcademico()
  │                         │
  │                    CertificacionPdfService         GridFS
  │                    .certificarDocumento()    ←──── PDF original
  │                         │  agregarPaginaCertificacion()
  │                         │  firmarPdf() [PKI]
  │                         │                    ────▶ PDF certificado
  │                         │
  │                    EgresadoRepository        ────▶ cert_uuid
  │                                                    cert_hash
  │                                                    fecha_certificacion

Página pública /verificar/:uuid
  │ GET /api/verificar/{uuid}
  │                    VerificacionController
  │                         │
  │                    EgresadoRepository        ←──── findByCertUuid()
  │◀── { valido, nombre, modalidad, fecha }
```

---

## 4. Tecnologías utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Apache PDFBox | 2.0.x | Manipulación de PDF: agregar páginas, dibujar contenido, firma digital |
| Bouncy Castle | 1.78.1 | Generación de certificado X.509 autofirmado, firma CMS/PKCS#7 |
| ZXing | 3.5.3 | Generación del código QR en formato PNG |
| MongoDB GridFS | — | Almacenamiento del PDF certificado |
| Spring Boot Security | 4.0.x | Control de acceso: endpoint de verificación público, demás protegidos |

---

## 5. Archivos creados y modificados

### Archivos nuevos

| Archivo | Descripción |
|---|---|
| `src/.../service/CertificacionPdfService.kt` | Servicio principal: genera página de certificación, firma PKI, gestiona GridFS |
| `src/.../web/api/VerificacionController.kt` | Endpoint público `GET /api/verificar/{uuid}` sin autenticación |
| `frontend/.../pages/verificar-documento/verificar-documento.component.ts` | Componente Angular de verificación pública |
| `frontend/.../pages/verificar-documento/verificar-documento.component.html` | Vista HTML de la página de verificación |
| `frontend/.../pages/verificar-documento/verificar-documento.component.css` | Estilos de la página de verificación |

### Archivos modificados

| Archivo | Cambio realizado |
|---|---|
| `build.gradle.kts` | Agregadas dependencias: Bouncy Castle, ZXing |
| `domain/Egresado.kt` | Nuevos campos: `cert_uuid`, `cert_hash`, `fecha_certificacion` |
| `repository/EgresadoRepository.kt` | Nuevo método: `findByCertUuid()` |
| `service/EgresadoService.kt` | Llama a certificación en `marcarEnviadoDepartamentoAcademico()` para Residencia Profesional |
| `service/RevisionService.kt` | Llama a certificación al aprobar en otras modalidades |
| `config/SecurityConfig.kt` | Permite `/api/verificar/**` sin autenticación |
| `resources/application.properties` | Nuevas propiedades: keystore PKI, URL base del QR |
| `frontend/app.routes.ts` | Nueva ruta pública `/verificar/:uuid` sin guard |
| `web/api/EgresadoController.kt` | Endpoint de descarga de documento extendido a rol coordinador |

---

## 6. Descripción técnica detallada

### 6.1 Generación del certificado PKI autofirmado

Al iniciar el servidor por primera vez, `CertificacionPdfService` verifica si existe el archivo `sit-keystore.p12` en el directorio home del servidor. Si no existe, lo genera automáticamente:

- **Algoritmo de clave:** RSA 2048 bits
- **Algoritmo de firma:** SHA-256 with RSA
- **Vigencia:** 10 años
- **Formato:** PKCS#12 (.p12)
- **Emisor/Sujeto:** CN=SIT TECNM, O=TECNM Campus Oaxaca, C=MX

Este archivo persiste entre reinicios del servidor. Si el servidor se migra, el keystore debe copiarse al nuevo servidor para que las firmas anteriores sigan siendo válidas.

### 6.2 Proceso de certificación de un PDF

```
1. LECTURA
   └─ Se obtiene el gridfs_id del campo documento_adjunto en MongoDB
   └─ Se descarga el PDF desde MongoDB GridFS a memoria

2. HASH
   └─ Se calcula el SHA-256 del PDF original (antes de cualquier modificación)
   └─ Se genera un UUID con formato SIT-XXXX-XXXX-XXXX

3. PÁGINA DE CERTIFICACIÓN
   └─ PDFBox agrega una nueva página A4 al final del documento
   └─ Se dibuja: encabezado azul, datos del egresado, ID, código QR, aviso de firma
   └─ El QR contiene: http://[servidor]/#/verificar/SIT-XXXX-XXXX-XXXX

4. FIRMA PKI
   └─ El PDF completo (con la página de certificación) se firma digitalmente
   └─ Tipo de firma: CMS/PKCS#7 detached (adbe.pkcs7.detached)
   └─ Filtro: Adobe.PPKLite (estándar reconocido por Adobe Reader)
   └─ La firma se embebe en el PDF mediante guardado incremental

5. ALMACENAMIENTO
   └─ El PDF certificado se sube a GridFS con nombre certificado_[numero_control].pdf
   └─ Se elimina el PDF original de GridFS
   └─ Se actualiza el documento en MongoDB:
       cert_uuid: "SIT-XXXX-XXXX-XXXX"
       cert_hash: "[sha256 del original]"
       fecha_certificacion: [timestamp]
       documento_adjunto.gridfs_id: [nuevo ObjectId de GridFS]
```

### 6.3 Código QR y página de verificación

El código QR contiene la URL completa de verificación. Al ser escaneado por cualquier dispositivo con cámara, abre el navegador directamente en la página de verificación del sistema SIT, sin necesidad de instalar ninguna aplicación.

La página de verificación (`/verificar/:uuid`) es **completamente pública** — no requiere inicio de sesión. Consulta el endpoint `GET /api/verificar/{uuid}` que busca en MongoDB por el campo `cert_uuid` y devuelve:

```json
{
  "valido": true,
  "nombre": "Carlos Mendez López",
  "numero_control": "TINV2-PROY1-2",
  "modalidad": "Residencia Profesional",
  "carrera": "Ingeniería en Sistemas",
  "institucion": "TECNM Campus Oaxaca",
  "fecha_certificacion": "2026-04-18T01:40:47Z"
}
```

### 6.4 Integridad del flujo — tolerancia a fallos

Un principio de diseño crítico: **el proceso de titulación no se interrumpe si la certificación falla**. El código guarda primero el timestamp de envío y luego intenta certificar dentro de un bloque `try-catch`. Si ocurre cualquier error en la certificación (PDF corrupto, keystore no encontrado, error de red en GridFS), el egresado queda registrado como enviado al departamento y el error se registra en los logs del servidor. Esto evita que un problema técnico bloquee el proceso académico.

```kotlin
// EgresadoService.kt — fragmento simplificado
egresadoRepository.save(enviado)          // Timestamp guardado siempre

if (esResidenciaProfesional(e)) {
    try {
        val resultado = certService.certificarDocumento(e)
        if (resultado != null) {
            egresadoRepository.save(enviado.copy(cert_uuid = resultado.certUuid, ...))
        }
    } catch (ex: Exception) {
        log.error("Error al certificar: {}", ex.message)  // No lanza excepción
    }
}
return true  // Siempre retorna true si el egresado existe
```

---

## 7. Campos agregados en la base de datos

Colección `registro` (Egresado) — campos nuevos:

| Campo MongoDB | Tipo | Descripción |
|---|---|---|
| `cert_uuid` | String | Identificador único de verificación (ej. `SIT-A3B4-C5D6-E7F8`) |
| `cert_hash` | String | SHA-256 hexadecimal del PDF original antes de certificar |
| `fecha_certificacion` | Date | Timestamp de cuándo se realizó la certificación |

Estos campos son `null` en egresados sin certificación (modalidades aún en revisión o sin documento).

---

## 8. Configuración del sistema

Propiedades en `application.properties`:

```properties
# Ruta al keystore PKCS12 autofirmado (se genera automáticamente si no existe)
sit.cert.keystore-path=${user.home}/sit-keystore.p12

# Contraseña del keystore
sit.cert.keystore-password=sit-titulacion-2024

# URL base pública del sistema (se embebe en el QR del documento certificado)
# Al migrar de servidor, actualizar este valor
sit.cert.base-url=http://77.37.74.122
```

---

## 9. Capturas de pantalla recomendadas

Para complementar este informe con evidencia visual, se recomienda tomar las siguientes capturas:

### Capturas del backend / base de datos

1. **Documento en MongoDB Compass**
   - Colección `registro`, documento de un egresado certificado
   - Mostrar los campos `cert_uuid`, `cert_hash`, `fecha_certificacion` visibles

2. **Archivo en GridFS**
   - Colección `fs.files`, archivo con nombre `certificado_[numero_control].pdf`
   - Mostrar campos `filename`, `length`, `uploadDate`

3. **Terminal del servidor al momento de certificar**
   - La terminal donde corre `bootRun` mostrando el log:
     `INFO - Documento certificado: egresado=..., uuid=SIT-...`

4. **build.gradle.kts**
   - Captura de las dependencias de Bouncy Castle y ZXing agregadas

### Capturas del sistema en funcionamiento

5. **Botón "Enviar" en seguimiento-proceso**
   - Pantalla de seguimiento-proceso con un egresado de Residencia Profesional
   - El botón "Enviar" visible antes de ser presionado

6. **PDF certificado abierto — página de certificación**
   - La última página del PDF mostrando el sello completo:
     encabezado azul, datos del egresado, ID de verificación, código QR

7. **PDF certificado abierto — firma PKI en Adobe Reader**
   - Panel de firmas de Adobe Reader mostrando "Firmado por SIT TECNM"
   - O el badge de firma en la barra superior de Adobe Reader

8. **Página de verificación — resultado válido**
   - Navegar a `http://localhost:4200/#/verificar/[UUID]` sin estar logueado
   - Mostrar la página con el recuadro verde "Documento Válido" y los datos

9. **Escaneo del QR (opcional)**
   - Foto del documento impreso con el sello
   - Pantalla del celular mostrando la página de verificación tras escanear el QR

---

## 10. Conclusiones

Se implementó exitosamente un sistema de certificación digital de doble capa para los documentos del proceso de titulación:

- **Capa digital:** Firma PKI con certificado X.509 autofirmado, verificable en cualquier lector de PDF compatible (Adobe Reader, Evince, navegadores modernos). La firma invalida el documento si es alterado después de la certificación.

- **Capa física:** Código QR imprimible en el propio documento que, al ser escaneado, redirige a una página pública del sistema donde se puede confirmar la autenticidad del documento sin necesidad de cuenta ni contraseña.

El sistema es robusto ante fallos (no bloquea el flujo de titulación), portable entre servidores (el QR usa URL configurable), y extensible (el mismo mecanismo se aplicará a las demás modalidades de titulación cuando el módulo de revisiones quede completado).
