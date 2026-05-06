package com.sit_titulacion.sit.web.api

import com.sit_titulacion.sit.repository.EgresadoRepository
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.time.format.DateTimeFormatter

@RestController
@RequestMapping("/api/verificar")
class VerificacionController(
    private val egresadoRepository: EgresadoRepository,
) {
    private val formatter = DateTimeFormatter.ISO_INSTANT

    @GetMapping("/{uuid}")
    fun verificar(@PathVariable uuid: String): ResponseEntity<Map<String, Any?>> {
        val trimmed = uuid.trim()
        val egresado = egresadoRepository.findByCertUuidAny(trimmed)
        return if (egresado != null) {
            val p = egresado.datos_personales
            val nombre = listOf(p.nombre, p.apellido_paterno, p.apellido_materno)
                .filter { !it.isNullOrBlank() }
                .joinToString(" ")
            val documento = when (trimmed) {
                egresado.cert_uuid -> "Documento principal"
                egresado.certUuid91 -> "Anexo 9.1"
                egresado.certUuid93 -> "Anexo 9.3"
                else -> "Documento"
            }
            ResponseEntity.ok(
                mapOf(
                    "valido" to true,
                    "documento" to documento,
                    "nombre" to nombre,
                    "numero_control" to egresado.numero_control,
                    "modalidad" to egresado.datos_proyecto.modalidad,
                    "carrera" to p.carrera,
                    "institucion" to "TECNM Campus Oaxaca",
                    "fecha_certificacion" to egresado.fechaCertificacion?.let { formatter.format(it) },
                ),
            )
        } else {
            ResponseEntity.ok(
                mapOf(
                    "valido" to false,
                    "mensaje" to "Documento no encontrado en el sistema.",
                ),
            )
        }
    }
}
