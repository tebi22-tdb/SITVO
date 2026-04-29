package com.sit_titulacion.sit.repository

import com.sit_titulacion.sit.domain.Catalogo
import org.bson.types.ObjectId
import org.springframework.data.mongodb.repository.MongoRepository
import org.springframework.stereotype.Repository

@Repository
interface CatalogoRepository : MongoRepository<Catalogo, ObjectId> {
    fun findByTipoAndActivoTrue(tipo: String): List<Catalogo>
    fun findByTipoAndSlug(tipo: String, slug: String): Catalogo?
    fun existsByTipoAndNombreIgnoreCase(tipo: String, nombre: String): Boolean
}
