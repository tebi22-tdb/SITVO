El problema es que PKI+QR garantiza autenticidad, pero NO garantiza originalidad conceptual. Alguien puede:

Tomar su tesis vieja de "Estudio de luciernagas" (firmada y validada)
Cambiar fechas, autores
Crear un documento nuevo con distinto QR pero contenido idéntico

Aquí están las 4 capas que necesitas:

Capa 1: Búsqueda de metadatos exacta
Cuando alguien presenta un documento:

Extraer: título, resumen, palabras clave, nombre estudiante, asesor
Buscar en BD si existen registros con:

Mismo título exacto
Mismo autor
Mismo asesor + disciplina



Limitación: Si cambien el título a "Ecología y comportamiento de luciernagas" vs "Estudio de luciernagas", pasas esto.

Capa 2: Análisis de similitud semántica ← Aquí es donde atrapas lo que PKI no puede
Esta es la clave. No es buscar texto idéntico, es buscar conceptos idénticos:
¿Cómo funciona?

Extrae el resumen del documento nuevo
Genera un vector semántico (embedding) usando un modelo como:

OpenAI's text-embedding-3-small
Hugging Face sentence-transformers
O incluso un modelo local si tienes servidores


Compara contra todos los resúmenes históricos (también vectorizados)
Calcula similitud coseno:

>85% = Probablemente el mismo proyecto → BLOQUEAR
70-85% = MUY parecido → ALERTA MANUAL
<70% = Diferente → ACEPTAR



Ventaja: Detecta:

"Estudio de luciernagas" vs "Análisis del comportamiento nocturno de luciernagas"
Documentos reescritos pero con mismo contenido
Cambios cosmético pero mismo núcleo


Capa 3: Hash del contenido + Firma temporal
Almacena en BD:
sqlCREATE TABLE proyectos_aprobados (
  id UUID PRIMARY KEY,
  titulo VARCHAR,
  resumen TEXT,
  resumen_embedding VECTOR(1536),  -- embeddings
  sha256_content VARCHAR,          -- hash del contenido
  similarity_threshold FLOAT,
  estudiante_id UUID,
  asesor_id UUID,
  fecha_presentacion TIMESTAMP,
  firma_qr VARCHAR,                -- tu QR+PKI actual
  disciplina VARCHAR
);
Si alguien intenta reenviar el mismo documento:

El hash SHA256 será idéntico
El QR puede ser diferente, pero el contenido no


Capa 4: Reglas de negocio flexible
javascriptfunction verificarRepeticion(documentoNuevo) {
  // 1. Búsqueda exacta por metadatos
  const exactos = bd.buscar({
    titulo: documentoNuevo.titulo,
    estudiante_id: documentoNuevo.estudiante
  });
  
  if (exactos.length > 0) {
    return { estado: 'BLOQUEADO', razon: 'Mismo título y estudiante' };
  }

  // 2. Búsqueda por similitud semántica
  const embedding_nuevo = generarEmbedding(documentoNuevo.resumen);
  const similares = bd.buscarPorSimilitud(embedding_nuevo, threshold: 0.70);
  
  if (similares.length > 0 && similares[0].similitud > 0.85) {
    return { 
      estado: 'BLOQUEADO', 
      razon: `Similitud ${(similares[0].similitud*100).toFixed(1)}% con proyecto titulado previamente`
    };
  }
  
  if (similares.length > 0 && similares[0].similitud > 0.70) {
    return {
      estado: 'REVISAR',
      razon: `Alta similitud (${similares[0].similitud*100}%) con proyecto anterior. Revisar manualmente`,
      proyecto_similar: similares[0]
    };
  }

  // 3. Verificar hash
  const hash_nuevo = sha256(documentoNuevo.contenido);
  const duplicado_hash = bd.buscarPorHash(hash_nuevo);
  
  if (duplicado_hash) {
    return { estado: 'BLOQUEADO', razon: 'Documento idéntico presentado previamente' };
  }

  return { estado: 'ACEPTADO' };
}

Implementación práctica
Opción A: Con OpenAI (rápido, no mantenimiento)
javascriptconst { OpenAIEmbeddings } = require("@langchain/openai");

const embeddings = new OpenAIEmbeddings();
const vector = await embeddings.embedQuery(resumen);

// Guardar en BD con soporte vectorial:
// - Supabase + pgvector
// - Pinecone
// - Weaviate
Opción B: Local + gratuito (Hugging Face)
pythonfrom sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
embedding = model.encode("Tu resumen aquí")

# Similitud
similarity = np.dot(embedding1, embedding2) / (
  np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
)
