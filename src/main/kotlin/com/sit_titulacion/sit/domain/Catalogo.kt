package com.sit_titulacion.sit.domain

import org.bson.types.ObjectId
import org.springframework.data.annotation.Id
import org.springframework.data.mongodb.core.mapping.Document
import java.time.Instant

@Document(collection = "catalogos")
data class Catalogo(
    @Id val id: ObjectId? = null,
    val tipo: String,
    val nombre: String,
    val activo: Boolean = true,
    val orden: Int = 0,
    /** Solo para tipo = "modalidad": duración en meses calendario (null = sin plazo, ej. CENEVAL). */
    val mesesVigencia: Int? = null,
    /** Solo para tipo = "modalidad": true cuando la modalidad es Residencia Profesional (afecta flujo de certificación). */
    val esResidencia: Boolean = false,
    /** Solo para tipo = "departamento": clave interna (ej. "virtuales", "ingenierias"). Debe coincidir con segmento_academico en usuarios. */
    val slug: String? = null,
    /** Solo para tipo = "departamento": lista de carreras asignadas. */
    val carreras: List<String> = emptyList(),
    val fechaCreacion: Instant = Instant.now(),
    val fechaActualizacion: Instant = Instant.now(),
)
