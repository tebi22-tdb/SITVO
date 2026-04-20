"""
Genera INFORME_RES.docx — Informe Técnico de Residencia Profesional (formato formal)
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ── Colores ──────────────────────────────────────────────────────────────────
AZUL_OSCURO  = RGBColor(0x1A, 0x3A, 0x6B)   # encabezados principales
AZUL_MEDIO   = RGBColor(0x25, 0x63, 0xA8)   # subencabezados
GRIS_TEXTO   = RGBColor(0x33, 0x33, 0x33)   # texto normal
GRIS_CLARO   = RGBColor(0x70, 0x70, 0x70)   # texto secundario
NEGRO        = RGBColor(0x00, 0x00, 0x00)
BLANCO       = RGBColor(0xFF, 0xFF, 0xFF)
GRIS_TABLA_H = RGBColor(0x2C, 0x3E, 0x50)   # encabezado de tabla
GRIS_FILA_A  = RGBColor(0xF2, 0xF5, 0xF9)   # fila alternada suave

# ── Helpers XML ──────────────────────────────────────────────────────────────
def set_cell_bg(cell, rgb: RGBColor):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    hex_color = str(rgb)
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_cell_borders(cell, sides=('top','bottom','left','right'), size=4, color='AAAAAA'):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in sides:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'),   'single')
        el.set(qn('w:sz'),    str(size))
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), color)
        tcBorders.append(el)
    tcPr.append(tcBorders)

def add_bottom_border_para(para, color='1A3A6B', size=12):
    pPr  = para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    str(size))
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), color)
    pBdr.append(bot)
    pPr.append(pBdr)

def set_para_spacing(para, before=0, after=0, line=None):
    pPr    = para._p.get_or_add_pPr()
    pSpAft = OxmlElement('w:spacing')
    pSpAft.set(qn('w:before'), str(before))
    pSpAft.set(qn('w:after'),  str(after))
    if line:
        pSpAft.set(qn('w:line'),      str(line))
        pSpAft.set(qn('w:lineRule'), 'auto')
    pPr.append(pSpAft)

def set_table_borders(table, color='CCCCCC', size=4):
    tbl    = table._tbl
    tblPr  = tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ('top','left','bottom','right','insideH','insideV'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'),   'single')
        el.set(qn('w:sz'),    str(size))
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), color)
        tblBorders.append(el)
    tblPr.append(tblBorders)

def no_space_after(para):
    set_para_spacing(para, before=0, after=0)

# ── Documento ────────────────────────────────────────────────────────────────
doc = Document()

# Márgenes
for sec in doc.sections:
    sec.top_margin    = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin   = Cm(3.0)
    sec.right_margin  = Cm(2.5)

# Estilo Normal base
normal = doc.styles['Normal']
normal.font.name = 'Calibri'
normal.font.size = Pt(10.5)
normal.font.color.rgb = GRIS_TEXTO
normal.paragraph_format.space_after  = Pt(6)
normal.paragraph_format.space_before = Pt(0)


# ─────────────────────────────────────────────────────────────────────────────
#  PORTADA
# ─────────────────────────────────────────────────────────────────────────────
def add_cover(doc):
    # Institución
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(p, before=0, after=60)
    run = p.add_run('TECNOLÓGICO NACIONAL DE MÉXICO')
    run.font.name  = 'Calibri'
    run.font.size  = Pt(11)
    run.font.bold  = True
    run.font.color.rgb = AZUL_OSCURO

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(p, before=0, after=200)
    run = p.add_run('Campus Oaxaca')
    run.font.name  = 'Calibri'
    run.font.size  = Pt(10.5)
    run.font.color.rgb = GRIS_CLARO

    # Línea separadora
    sep = doc.add_paragraph()
    sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_bottom_border_para(sep, color='1A3A6B', size=16)
    set_para_spacing(sep, before=0, after=240)

    # Título principal
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(p, before=0, after=120)
    run = p.add_run('INFORME TÉCNICO DE RESIDENCIA PROFESIONAL')
    run.font.name  = 'Calibri'
    run.font.size  = Pt(16)
    run.font.bold  = True
    run.font.color.rgb = AZUL_OSCURO

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(p, before=0, after=400)
    run = p.add_run('Implementación de Sistema de Certificación Digital de Documentos\n'
                    'Módulo PKI + Verificación por Código QR para Documentos Académicos')
    run.font.name  = 'Calibri'
    run.font.size  = Pt(13)
    run.font.color.rgb = AZUL_MEDIO

    # Tabla de datos de portada
    tbl = doc.add_table(rows=5, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    set_table_borders(tbl, color='CCCCCC', size=4)
    col_w = [Cm(4.5), Cm(9.5)]
    for i, row in enumerate(tbl.rows):
        for j, cell in enumerate(row.cells):
            cell.width = col_w[j]
            set_cell_bg(cell, RGBColor(0xF7, 0xF9, 0xFC) if j == 0 else BLANCO)

    data = [
        ('Sistema',      'SIT — Sistema Integral de Titulación del Valle de Oaxaca'),
        ('Institución',  'TECNM Campus Oaxaca'),
        ('Módulo',       'Certificación PKI + Verificación por código QR'),
        ('Periodo',      'Enero – Junio 2026'),
        ('Fecha',        'Abril 2026'),
    ]
    for i, (lbl, val) in enumerate(data):
        c0 = tbl.rows[i].cells[0]
        c1 = tbl.rows[i].cells[1]
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        r0 = p0.add_run(lbl)
        r0.font.name = 'Calibri'; r0.font.size = Pt(10); r0.font.bold = True
        r0.font.color.rgb = AZUL_OSCURO
        r1 = p1.add_run(val)
        r1.font.name = 'Calibri'; r1.font.size = Pt(10)
        r1.font.color.rgb = GRIS_TEXTO

    doc.add_page_break()

add_cover(doc)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers de sección
# ─────────────────────────────────────────────────────────────────────────────
def add_section_heading(doc, num, title):
    p = doc.add_paragraph()
    set_para_spacing(p, before=240, after=80)
    add_bottom_border_para(p, color='1A3A6B', size=8)
    run_num = p.add_run(f'{num}.  ')
    run_num.font.name = 'Calibri'; run_num.font.size = Pt(13); run_num.font.bold = True
    run_num.font.color.rgb = AZUL_OSCURO
    run_ttl = p.add_run(title.upper())
    run_ttl.font.name = 'Calibri'; run_ttl.font.size = Pt(13); run_ttl.font.bold = True
    run_ttl.font.color.rgb = AZUL_OSCURO

def add_subsection_heading(doc, title):
    p = doc.add_paragraph()
    set_para_spacing(p, before=160, after=60)
    run = p.add_run(title)
    run.font.name = 'Calibri'; run.font.size = Pt(11); run.font.bold = True
    run.font.color.rgb = AZUL_MEDIO

def add_body_para(doc, text):
    p = doc.add_paragraph(style='Normal')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_para_spacing(p, before=0, after=80, line=276)
    run = p.add_run(text)
    run.font.name = 'Calibri'; run.font.size = Pt(10.5)
    run.font.color.rgb = GRIS_TEXTO
    return p

def add_code_block(doc, text):
    """Bloque de código monoespacio con fondo gris claro."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_para_spacing(p, before=60, after=60)
    # fondo gris para el párrafo (via shading en pPr)
    pPr  = p._p.get_or_add_pPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  'F0F2F5')
    pPr.append(shd)
    # borde izquierdo
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'),   'single')
    left.set(qn('w:sz'),    '18')
    left.set(qn('w:space'), '4')
    left.set(qn('w:color'), '5B7FA6')
    pBdr.append(left)
    pPr.append(pBdr)
    run = p.add_run(text)
    run.font.name = 'Courier New'; run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    return p

def add_note(doc, text, kind='info'):
    """Nota/callout con borde izquierdo."""
    colors = {
        'info':  ('2563A8', RGBColor(0xEB, 0xF3, 0xFD)),
        'warn':  ('B45309', RGBColor(0xFE, 0xF3, 0xC7)),
        'ok':    ('166534', RGBColor(0xDC, 0xFC, 0xE7)),
    }
    border_color, bg = colors.get(kind, colors['info'])
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_para_spacing(p, before=80, after=80)
    pPr  = p._p.get_or_add_pPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  str(bg))
    pPr.append(shd)
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'),   'single')
    left.set(qn('w:sz'),    '24')
    left.set(qn('w:space'), '6')
    left.set(qn('w:color'), border_color)
    pBdr.append(left)
    pPr.append(pBdr)
    run = p.add_run(text)
    run.font.name = 'Calibri'; run.font.size = Pt(10)
    run.font.color.rgb = GRIS_TEXTO
    return p


def add_formal_table(doc, headers, rows, col_widths=None):
    n_cols = len(headers)
    tbl = doc.add_table(rows=1+len(rows), cols=n_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    set_table_borders(tbl, color='BBBBBB', size=4)

    # Encabezado
    for j, h in enumerate(headers):
        cell = tbl.rows[0].cells[j]
        set_cell_bg(cell, GRIS_TABLA_H)
        if col_widths:
            cell.width = col_widths[j]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.font.name = 'Calibri'; run.font.size = Pt(10); run.font.bold = True
        run.font.color.rgb = BLANCO

    # Filas
    for i, row_data in enumerate(rows):
        for j, val in enumerate(row_data):
            cell = tbl.rows[i+1].cells[j]
            if col_widths:
                cell.width = col_widths[j]
            if i % 2 == 1:
                set_cell_bg(cell, GRIS_FILA_A)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(val))
            run.font.name = 'Calibri'; run.font.size = Pt(10)
            run.font.color.rgb = GRIS_TEXTO

    set_para_spacing(doc.paragraphs[-1], before=0, after=120)
    return tbl


# ─────────────────────────────────────────────────────────────────────────────
#  1. INTRODUCCIÓN
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 1, 'Introducción')
add_body_para(doc,
    'Durante el desarrollo de la plataforma SIT se identificó la necesidad de garantizar la '
    'autenticidad e integridad de los documentos PDF que los egresados cargan al sistema como '
    'parte de su proceso de titulación. Sin un mecanismo de certificación, cualquier persona '
    'podría modificar un documento descargado y volver a presentarlo como original, sin que '
    'existiera forma de detectar la alteración.')
add_body_para(doc,
    'Para resolver este problema se diseñó e implementó un módulo de certificación digital que '
    'combina dos tecnologías complementarias: firma digital PKI (infraestructura de clave pública) '
    'y código QR de verificación, cubriendo tanto el escenario digital como el escenario de '
    'documentos impresos en papel.')


# ─────────────────────────────────────────────────────────────────────────────
#  2. PROBLEMA QUE RESUELVE
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 2, 'Problema que resuelve')
add_formal_table(doc,
    headers=['Escenario', 'Sin certificación', 'Con certificación'],
    rows=[
        ('Documento digital',
         'Cualquiera puede editar el PDF',
         'La firma PKI invalida el documento si es modificado'),
        ('Documento impreso',
         'No hay forma de autenticar la copia',
         'El QR permite verificar autenticidad desde el celular'),
        ('Migración de servidor',
         '—',
         'El ID de verificación es independiente de la URL'),
        ('Verificación sin conexión',
         '—',
         'Adobe Reader detecta la firma PKI sin acceso a internet'),
    ],
    col_widths=[Cm(4.5), Cm(6.0), Cm(6.0)]
)


# ─────────────────────────────────────────────────────────────────────────────
#  3. ARQUITECTURA
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 3, 'Arquitectura de la solución')
add_body_para(doc,
    'La certificación ocurre automáticamente en el backend en dos momentos del flujo de '
    'titulación, según la modalidad del egresado registrada en el sistema.')

add_subsection_heading(doc, '3.1  Flujo de certificación — Residencia Profesional')
add_code_block(doc,
    'Coordinador presiona "Enviar al departamento académico"\n'
    '    │\n'
    '    ├── 1. Se guarda fecha_enviado_departamento_academico (timestamp)\n'
    '    │\n'
    '    └── 2. CertificacionPdfService.certificarDocumento()\n'
    '            ├── Lee PDF original desde MongoDB GridFS\n'
    '            ├── Calcula SHA-256 del PDF original\n'
    '            ├── Genera UUID único (ej. SIT-A3B4-C5D6-E7F8)\n'
    '            ├── Genera código QR con URL de verificación\n'
    '            ├── Agrega página de certificación al PDF (PDFBox)\n'
    '            ├── Firma digitalmente el PDF completo (PKI + Bouncy Castle)\n'
    '            ├── Guarda el PDF certificado en GridFS\n'
    '            └── Actualiza MongoDB: cert_uuid, cert_hash, fecha_certificacion\n\n'
    'Otras modalidades (Tesis, Tesina, CENEVAL, Proyecto de Investigación)\n'
    '    └── Revisor académico presiona "Aprobar" → mismo proceso de certificación'
)

add_subsection_heading(doc, '3.2  Diagrama de componentes')
add_code_block(doc,
    'Frontend Angular          Backend Spring Boot          MongoDB\n'
    '──────────────────        ────────────────────         ───────\n'
    'SeguimientoProcesoComponent\n'
    '  │ POST /enviar-departamento-academico\n'
    '  │                    EgresadoController\n'
    '  │                         │\n'
    '  │                    EgresadoService\n'
    '  │                    .marcarEnviadoDepartamentoAcademico()\n'
    '  │                         │\n'
    '  │                    CertificacionPdfService         GridFS\n'
    '  │                    .certificarDocumento()    <──── PDF original\n'
    '  │                         │  agregarPaginaCertificacion()\n'
    '  │                         │  firmarPdf() [PKI]\n'
    '  │                         │                    ────> PDF certificado\n'
    '  │                         │\n'
    '  │                    EgresadoRepository        ────> cert_uuid\n'
    '  │                                                    cert_hash\n'
    '  │                                                    fecha_certificacion\n\n'
    'Página pública /verificar/:uuid\n'
    '  │ GET /api/verificar/{uuid}\n'
    '  │                    VerificacionController\n'
    '  │                         │\n'
    '  │                    EgresadoRepository        <──── findByCertUuid()\n'
    '  │<── { valido, nombre, modalidad, fecha }'
)


# ─────────────────────────────────────────────────────────────────────────────
#  4. TECNOLOGÍAS
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 4, 'Tecnologías utilizadas')
add_formal_table(doc,
    headers=['Tecnología', 'Versión', 'Uso en el módulo'],
    rows=[
        ('Apache PDFBox',         '2.0.x',  'Manipulación de PDF: agregar páginas, dibujar contenido, firma digital'),
        ('Bouncy Castle',         '1.78.1', 'Generación de certificado X.509 autofirmado, firma CMS/PKCS#7'),
        ('ZXing',                 '3.5.3',  'Generación del código QR en formato PNG'),
        ('MongoDB GridFS',        '—',      'Almacenamiento del PDF certificado'),
        ('Spring Boot Security',  '4.0.x',  'Control de acceso: endpoint de verificación público, demás protegidos'),
    ],
    col_widths=[Cm(4.5), Cm(2.5), Cm(9.5)]
)


# ─────────────────────────────────────────────────────────────────────────────
#  5. ARCHIVOS CREADOS Y MODIFICADOS
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 5, 'Archivos creados y modificados')

add_subsection_heading(doc, '5.1  Archivos nuevos')
add_formal_table(doc,
    headers=['Archivo', 'Descripción'],
    rows=[
        ('service/CertificacionPdfService.kt',
         'Servicio principal: genera página de certificación, firma PKI, gestiona GridFS'),
        ('web/api/VerificacionController.kt',
         'Endpoint público GET /api/verificar/{uuid} sin autenticación'),
        ('pages/verificar-documento/…component.ts',
         'Componente Angular de la página de verificación pública'),
        ('pages/verificar-documento/…component.html',
         'Vista HTML de la página de verificación'),
        ('pages/verificar-documento/…component.css',
         'Estilos de la página de verificación'),
    ],
    col_widths=[Cm(7.0), Cm(9.5)]
)

add_subsection_heading(doc, '5.2  Archivos modificados')
add_formal_table(doc,
    headers=['Archivo', 'Cambio realizado'],
    rows=[
        ('build.gradle.kts',           'Agregadas dependencias: Bouncy Castle, ZXing'),
        ('domain/Egresado.kt',         'Nuevos campos: cert_uuid, cert_hash, fecha_certificacion'),
        ('repository/EgresadoRepository.kt', 'Nuevo método: findByCertUuid()'),
        ('service/EgresadoService.kt', 'Llama a certificación en marcarEnviadoDepartamentoAcademico() para Residencia Profesional'),
        ('service/RevisionService.kt', 'Llama a certificación al aprobar en otras modalidades'),
        ('config/SecurityConfig.kt',   'Permite /api/verificar/** sin autenticación'),
        ('resources/application.properties', 'Nuevas propiedades: keystore PKI, URL base del QR'),
        ('frontend/app.routes.ts',     'Nueva ruta pública /verificar/:uuid sin guard'),
        ('web/api/EgresadoController.kt', 'Endpoint de descarga de documento extendido al rol coordinador'),
    ],
    col_widths=[Cm(6.5), Cm(10.0)]
)


# ─────────────────────────────────────────────────────────────────────────────
#  6. DESCRIPCIÓN TÉCNICA DETALLADA
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 6, 'Descripción técnica detallada')

# 6.1
add_subsection_heading(doc, '6.1  Generación del certificado PKI autofirmado')
add_body_para(doc,
    'Al iniciar el servidor por primera vez, CertificacionPdfService verifica si existe el '
    'archivo sit-keystore.p12 en el directorio home del servidor. Si no existe, lo genera '
    'automáticamente con las siguientes características:')
add_formal_table(doc,
    headers=['Parámetro', 'Valor'],
    rows=[
        ('Algoritmo de clave',   'RSA 2048 bits'),
        ('Algoritmo de firma',   'SHA-256 with RSA'),
        ('Vigencia',             '10 años'),
        ('Formato',              'PKCS#12 (.p12)'),
        ('Emisor / Sujeto',      'CN=SIT TECNM, O=TECNM Campus Oaxaca, C=MX'),
    ],
    col_widths=[Cm(5.0), Cm(11.5)]
)
add_note(doc,
    'Advertencia: este archivo persiste entre reinicios. Si el servidor se migra, el keystore '
    'debe copiarse al nuevo servidor para que las firmas anteriores sigan siendo válidas.',
    kind='warn')

# 6.2
add_subsection_heading(doc, '6.2  Proceso de certificación de un PDF')
add_code_block(doc,
    '1. LECTURA\n'
    '   └─ Se obtiene el gridfs_id del campo documento_adjunto en MongoDB\n'
    '   └─ Se descarga el PDF desde MongoDB GridFS a memoria\n\n'
    '2. HASH\n'
    '   └─ Se calcula el SHA-256 del PDF original (antes de cualquier modificación)\n'
    '   └─ Se genera un UUID con formato SIT-XXXX-XXXX-XXXX\n\n'
    '3. PÁGINA DE CERTIFICACIÓN\n'
    '   └─ PDFBox agrega una nueva página A4 al final del documento\n'
    '   └─ Se dibuja: encabezado, datos del egresado, ID, código QR, aviso de firma\n'
    '   └─ El QR contiene: http://[servidor]/#/verificar/SIT-XXXX-XXXX-XXXX\n\n'
    '4. FIRMA PKI\n'
    '   └─ El PDF completo (con la página de certificación) se firma digitalmente\n'
    '   └─ Tipo de firma: CMS/PKCS#7 detached (adbe.pkcs7.detached)\n'
    '   └─ Filtro: Adobe.PPKLite (estándar reconocido por Adobe Reader)\n'
    '   └─ La firma se embebe en el PDF mediante guardado incremental\n\n'
    '5. ALMACENAMIENTO\n'
    '   └─ El PDF certificado se sube a GridFS → certificado_[numero_control].pdf\n'
    '   └─ Se elimina el PDF original de GridFS\n'
    '   └─ Se actualiza el documento en MongoDB:\n'
    '       cert_uuid: "SIT-XXXX-XXXX-XXXX"\n'
    '       cert_hash: "[sha256 del original]"\n'
    '       fecha_certificacion: [timestamp]\n'
    '       documento_adjunto.gridfs_id: [nuevo ObjectId de GridFS]'
)

# 6.3
add_subsection_heading(doc, '6.3  Código QR y página de verificación')
add_body_para(doc,
    'El código QR contiene la URL completa de verificación. Al ser escaneado por cualquier '
    'dispositivo con cámara, abre el navegador directamente en la página de verificación del '
    'sistema SIT, sin necesidad de instalar ninguna aplicación adicional.')
add_body_para(doc,
    'La página /verificar/:uuid es completamente pública — no requiere inicio de sesión. '
    'Consulta el endpoint GET /api/verificar/{uuid} que busca en MongoDB por el campo '
    'cert_uuid y devuelve la siguiente respuesta JSON:')
add_code_block(doc,
    '{\n'
    '  "valido":              true,\n'
    '  "nombre":              "Carlos Mendez López",\n'
    '  "numero_control":      "TINV2-PROY1-2",\n'
    '  "modalidad":           "Residencia Profesional",\n'
    '  "carrera":             "Ingeniería en Sistemas",\n'
    '  "institucion":         "TECNM Campus Oaxaca",\n'
    '  "fecha_certificacion": "2026-04-18T01:40:47Z"\n'
    '}'
)

# 6.4
add_subsection_heading(doc, '6.4  Integridad del flujo — tolerancia a fallos')
add_body_para(doc,
    'Principio de diseño crítico: el proceso de titulación no se interrumpe si la certificación '
    'falla. El código guarda primero el timestamp de envío y luego intenta certificar dentro de '
    'un bloque try-catch. Si ocurre cualquier error (PDF corrupto, keystore no encontrado, error '
    'de red en GridFS), el egresado queda registrado como enviado y el error se registra en los '
    'logs del servidor.')
add_code_block(doc,
    '// EgresadoService.kt — fragmento\n'
    'egresadoRepository.save(enviado)          // Timestamp guardado siempre\n\n'
    'if (esResidenciaProfesional(e)) {\n'
    '    try {\n'
    '        val resultado = certService.certificarDocumento(e)\n'
    '        if (resultado != null) {\n'
    '            egresadoRepository.save(enviado.copy(\n'
    '                cert_uuid = resultado.certUuid, ...\n'
    '            ))\n'
    '        }\n'
    '    } catch (ex: Exception) {\n'
    '        log.error("Error al certificar: {}", ex.message)  // No lanza excepción\n'
    '    }\n'
    '}\n'
    'return true  // Siempre retorna true si el egresado existe'
)
add_note(doc,
    'Este comportamiento garantiza que un fallo técnico en la certificación no bloquee el avance '
    'académico del egresado. El coordinador puede reintentar la certificación manualmente si fuese necesario.',
    kind='info')


# ─────────────────────────────────────────────────────────────────────────────
#  7. CAMPOS EN BASE DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 7, 'Campos agregados en la base de datos')
add_body_para(doc,
    'Colección registro (Egresado) — campos nuevos incorporados al modelo de dominio:')
add_formal_table(doc,
    headers=['Campo MongoDB', 'Tipo', 'Descripción'],
    rows=[
        ('cert_uuid',          'String', 'Identificador único de verificación (ej. SIT-A3B4-C5D6-E7F8)'),
        ('cert_hash',          'String', 'SHA-256 hexadecimal del PDF original antes de certificar'),
        ('fecha_certificacion','Date',   'Timestamp de cuándo se realizó la certificación'),
    ],
    col_widths=[Cm(4.5), Cm(2.5), Cm(9.5)]
)
add_note(doc,
    'Estos campos tienen valor null en egresados sin certificación (modalidades aún en revisión '
    'o que no tienen documento adjunto al momento del registro).',
    kind='info')


# ─────────────────────────────────────────────────────────────────────────────
#  8. CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 8, 'Configuración del sistema')
add_body_para(doc,
    'Las siguientes propiedades fueron agregadas al archivo application.properties del backend:')
add_code_block(doc,
    '# Ruta al keystore PKCS12 autofirmado (se genera automáticamente si no existe)\n'
    'sit.cert.keystore-path=${user.home}/sit-keystore.p12\n\n'
    '# Contraseña del keystore\n'
    'sit.cert.keystore-password=sit-titulacion-2024\n\n'
    '# URL base pública del sistema (se embebe en el QR del documento certificado)\n'
    '# Al migrar de servidor, actualizar este valor\n'
    'sit.cert.base-url=http://77.37.74.122'
)
add_note(doc,
    'Al migrar el sistema a un nuevo servidor, se deben actualizar tanto el valor de '
    'sit.cert.base-url como copiar el archivo sit-keystore.p12 para mantener la validez '
    'de las firmas digitales previamente emitidas.',
    kind='warn')


# ─────────────────────────────────────────────────────────────────────────────
#  9. CAPTURAS RECOMENDADAS
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 9, 'Capturas de pantalla recomendadas')
add_body_para(doc,
    'Para complementar este informe con evidencia visual, se recomienda obtener las siguientes '
    'capturas de pantalla antes de la entrega final:')

add_subsection_heading(doc, 'Backend y base de datos')
add_formal_table(doc,
    headers=['#', 'Elemento a capturar', 'Detalle requerido'],
    rows=[
        ('1', 'Documento en MongoDB Compass',
              'Colección registro — mostrar campos cert_uuid, cert_hash y fecha_certificacion visibles en un documento certificado.'),
        ('2', 'Archivo en GridFS',
              'Colección fs.files — mostrar filename, length y uploadDate del archivo certificado_*.pdf.'),
        ('3', 'Terminal del servidor al certificar',
              'Log INFO — Documento certificado: egresado=..., uuid=SIT-... en la salida del proceso bootRun.'),
        ('4', 'build.gradle.kts',
              'Sección de dependencias mostrando Bouncy Castle y ZXing agregadas.'),
    ],
    col_widths=[Cm(0.8), Cm(5.0), Cm(10.7)]
)

add_subsection_heading(doc, 'Sistema en funcionamiento')
add_formal_table(doc,
    headers=['#', 'Elemento a capturar', 'Detalle requerido'],
    rows=[
        ('5', 'Botón "Enviar" en seguimiento-proceso',
              'Pantalla con egresado de Residencia Profesional; botón visible antes de presionarse.'),
        ('6', 'Página de certificación en PDF',
              'Última página del PDF mostrando el sello: encabezado, datos del egresado, ID de verificación y código QR.'),
        ('7', 'Firma PKI en Adobe Reader',
              'Panel de firmas mostrando "Firmado por SIT TECNM" o badge en barra superior.'),
        ('8', 'Página de verificación — resultado válido',
              'Navegar a /verificar/[UUID] sin sesión activa; mostrar mensaje de documento válido con datos del egresado.'),
        ('9', 'Escaneo del QR (opcional)',
              'Foto del documento impreso y pantalla del celular mostrando la página de verificación tras escanear.'),
    ],
    col_widths=[Cm(0.8), Cm(5.0), Cm(10.7)]
)


# ─────────────────────────────────────────────────────────────────────────────
#  10. CONCLUSIONES
# ─────────────────────────────────────────────────────────────────────────────
add_section_heading(doc, 10, 'Conclusiones')
add_body_para(doc,
    'Se implementó exitosamente un sistema de certificación digital de doble capa para los '
    'documentos del proceso de titulación, cumpliendo con los objetivos establecidos al inicio '
    'de la residencia profesional:')

add_subsection_heading(doc, 'Capa digital — Firma PKI')
add_body_para(doc,
    'Firma con certificado X.509 autofirmado, verificable en cualquier lector de PDF compatible '
    '(Adobe Reader, Evince, navegadores modernos). La firma invalida el documento si es alterado '
    'después de la certificación, garantizando la integridad del archivo en formato digital.')

add_subsection_heading(doc, 'Capa física — Código QR imprimible')
add_body_para(doc,
    'Código QR embebido en el propio documento que, al ser escaneado, redirige a una página '
    'pública del sistema donde se puede confirmar la autenticidad del documento sin necesidad '
    'de cuenta de usuario ni contraseña, facilitando la verificación en papel.')

add_note(doc,
    'El sistema es robusto ante fallos (no bloquea el flujo de titulación), portable entre '
    'servidores (el QR usa URL configurable), y extensible: el mismo mecanismo se aplicará a '
    'las demás modalidades de titulación conforme avance el desarrollo del módulo de revisiones.',
    kind='ok')


# ─────────────────────────────────────────────────────────────────────────────
#  Guardar
# ─────────────────────────────────────────────────────────────────────────────
doc.save('INFORME_RES.docx')
print('OK: INFORME_RES.docx generado correctamente.')
