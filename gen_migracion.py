"""
Genera GUIA_MIGRACION_SERVIDOR.docx
Guía de configuraciones que deben actualizarse al cambiar el servidor del sistema SIT.
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Paleta formal ────────────────────────────────────────────────────────────
AZUL_OSC   = RGBColor(0x1A, 0x3A, 0x6B)
AZUL_MED   = RGBColor(0x25, 0x63, 0xA8)
GRIS_TXT   = RGBColor(0x22, 0x22, 0x22)
GRIS_SEC   = RGBColor(0x55, 0x55, 0x55)
BLANCO     = RGBColor(0xFF, 0xFF, 0xFF)
HDR_TBL    = RGBColor(0x2C, 0x3E, 0x50)
FILA_ALT   = RGBColor(0xF2, 0xF5, 0xF9)
BG_CODE    = 'F0F2F5'
BG_WARN    = 'FEF3C7'
BG_OK      = 'DCFCE7'
BG_DANGER  = 'FEE2E2'
BG_INFO    = 'EBF3FD'
COL_WARN   = 'B45309'
COL_OK     = '166534'
COL_DANGER = '991B1B'
COL_INFO   = '1A3A6B'
COL_CODE   = '5B7FA6'

# ── XML helpers ──────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex6: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex6)
    tcPr.append(shd)

def set_table_borders(table, color='BBBBBB', size=4):
    tblPr = table._tbl.tblPr
    tblB  = OxmlElement('w:tblBorders')
    for side in ('top','left','bottom','right','insideH','insideV'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'),   'single')
        el.set(qn('w:sz'),    str(size))
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), color)
        tblB.append(el)
    tblPr.append(tblB)

def spacing(para, before=0, after=80, line=None):
    pPr = para._p.get_or_add_pPr()
    sp  = OxmlElement('w:spacing')
    sp.set(qn('w:before'), str(before))
    sp.set(qn('w:after'),  str(after))
    if line:
        sp.set(qn('w:line'),     str(line))
        sp.set(qn('w:lineRule'), 'auto')
    pPr.append(sp)

def bottom_border(para, color='1A3A6B', size=8):
    pPr  = para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    str(size))
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), color)
    pBdr.append(bot)
    pPr.append(pBdr)

def para_bg(para, fill: str):
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  fill)
    pPr.append(shd)

def left_border(para, color: str, size='24'):
    pPr  = para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'),   'single')
    left.set(qn('w:sz'),    size)
    left.set(qn('w:space'), '6')
    left.set(qn('w:color'), color)
    pBdr.append(left)
    pPr.append(pBdr)

# ── Constructores de contenido ────────────────────────────────────────────────
def sec_head(doc, num, title):
    p = doc.add_paragraph()
    spacing(p, before=260, after=80)
    bottom_border(p, color='1A3A6B', size=8)
    r = p.add_run(f'{num}.  {title.upper()}')
    r.font.name = 'Calibri'; r.font.size = Pt(13); r.font.bold = True
    r.font.color.rgb = AZUL_OSC

def sub_head(doc, title):
    p = doc.add_paragraph()
    spacing(p, before=160, after=60)
    r = p.add_run(title)
    r.font.name = 'Calibri'; r.font.size = Pt(11); r.font.bold = True
    r.font.color.rgb = AZUL_MED

def body(doc, text):
    p = doc.add_paragraph(style='Normal')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    spacing(p, before=0, after=80, line=276)
    r = p.add_run(text)
    r.font.name = 'Calibri'; r.font.size = Pt(10.5)
    r.font.color.rgb = GRIS_TXT
    return p

def code(doc, text):
    p = doc.add_paragraph()
    spacing(p, before=60, after=60)
    para_bg(p, BG_CODE)
    left_border(p, COL_CODE, size='18')
    r = p.add_run(text)
    r.font.name = 'Courier New'; r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    return p

def note(doc, text, kind='info'):
    cfg = {
        'info':   (BG_INFO,   COL_INFO),
        'warn':   (BG_WARN,   COL_WARN),
        'ok':     (BG_OK,     COL_OK),
        'danger': (BG_DANGER, COL_DANGER),
    }
    bg, border = cfg.get(kind, cfg['info'])
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    spacing(p, before=60, after=80)
    para_bg(p, bg)
    left_border(p, border, size='24')
    r = p.add_run(text)
    r.font.name = 'Calibri'; r.font.size = Pt(10)
    r.font.color.rgb = GRIS_TXT
    return p

def table(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=1+len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    set_table_borders(tbl, color='BBBBBB', size=4)
    # encabezado
    for j, h in enumerate(headers):
        cell = tbl.rows[0].cells[j]
        set_cell_bg(cell, str(HDR_TBL))
        if col_widths: cell.width = col_widths[j]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Calibri'; r.font.size = Pt(10); r.font.bold = True
        r.font.color.rgb = BLANCO
    # filas
    for i, row_data in enumerate(rows):
        for j, val in enumerate(row_data):
            cell = tbl.rows[i+1].cells[j]
            if col_widths: cell.width = col_widths[j]
            if i % 2 == 1:
                set_cell_bg(cell, str(FILA_ALT))
            p = cell.paragraphs[0]
            r = p.add_run(str(val))
            r.font.name = 'Calibri'; r.font.size = Pt(10)
            r.font.color.rgb = GRIS_TXT
    doc.add_paragraph()
    return tbl

def bullet(doc, items: list):
    for item in items:
        p = doc.add_paragraph(style='Normal')
        spacing(p, before=0, after=40)
        p.paragraph_format.left_indent = Cm(0.8)
        r = p.add_run(f'•  {item}')
        r.font.name = 'Calibri'; r.font.size = Pt(10.5)
        r.font.color.rgb = GRIS_TXT

# ─────────────────────────────────────────────────────────────────────────────
#  DOCUMENTO
# ─────────────────────────────────────────────────────────────────────────────
doc = Document()
for sec in doc.sections:
    sec.top_margin    = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin   = Cm(3.0)
    sec.right_margin  = Cm(2.5)

normal = doc.styles['Normal']
normal.font.name = 'Calibri'
normal.font.size = Pt(10.5)
normal.font.color.rgb = GRIS_TXT
normal.paragraph_format.space_after  = Pt(6)
normal.paragraph_format.space_before = Pt(0)


# ── PORTADA ──────────────────────────────────────────────────────────────────
def cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(p, before=0, after=60)
    r = p.add_run('TECNOLÓGICO NACIONAL DE MÉXICO')
    r.font.name = 'Calibri'; r.font.size = Pt(11); r.font.bold = True
    r.font.color.rgb = AZUL_OSC

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(p, before=0, after=280)
    r = p.add_run('Campus Oaxaca')
    r.font.name = 'Calibri'; r.font.size = Pt(10.5)
    r.font.color.rgb = GRIS_SEC

    sep = doc.add_paragraph()
    bottom_border(sep, color='1A3A6B', size=16)
    spacing(sep, before=0, after=280)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(p, before=0, after=100)
    r = p.add_run('GUÍA DE MIGRACIÓN DE SERVIDOR')
    r.font.name = 'Calibri'; r.font.size = Pt(16); r.font.bold = True
    r.font.color.rgb = AZUL_OSC

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(p, before=0, after=400)
    r = p.add_run('Sistema Integral de Titulación (SIT)\n'
                  'Configuraciones que deben actualizarse al cambiar de servidor')
    r.font.name = 'Calibri'; r.font.size = Pt(12)
    r.font.color.rgb = AZUL_MED

    tbl = doc.add_table(rows=4, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    set_table_borders(tbl, color='CCCCCC', size=4)
    data = [
        ('Sistema',      'SIT — Sistema Integral de Titulación del Valle de Oaxaca'),
        ('Institución',  'TECNM Campus Oaxaca'),
        ('Servidor actual', '77.37.74.122  (referencia en este documento)'),
        ('Fecha',        'Abril 2026'),
    ]
    for i, (lbl, val) in enumerate(data):
        c0, c1 = tbl.rows[i].cells[0], tbl.rows[i].cells[1]
        c0.width = Cm(4.5); c1.width = Cm(9.5)
        set_cell_bg(c0, 'F2F5F9')
        r0 = c0.paragraphs[0].add_run(lbl)
        r0.font.name = 'Calibri'; r0.font.size = Pt(10); r0.font.bold = True
        r0.font.color.rgb = AZUL_OSC
        r1 = c1.paragraphs[0].add_run(val)
        r1.font.name = 'Calibri'; r1.font.size = Pt(10)
        r1.font.color.rgb = GRIS_TXT

    doc.add_page_break()

cover(doc)


# ── 1. INTRODUCCIÓN ──────────────────────────────────────────────────────────
sec_head(doc, 1, 'Introducción')
body(doc,
    'Este documento describe todas las configuraciones que deben revisarse y actualizarse '
    'cuando el sistema SIT es migrado a un servidor diferente al actual (77.37.74.122). '
    'Seguir esta guía garantiza que el sistema arranque correctamente, que las notificaciones '
    'por correo funcionen, que los documentos PDF se certifiquen y que los códigos QR '
    'apunten a la dirección pública correcta del nuevo servidor.')
note(doc,
    'Advertencia: omitir cualquiera de las configuraciones listadas puede causar que el '
    'sistema arranque pero funcione de forma incorrecta — por ejemplo, enviando correos '
    'con URLs inválidas, generando QR que no abren nada, o fallando en la generación de PDFs.',
    kind='warn')


# ── 2. RESUMEN DE CAMBIOS ─────────────────────────────────────────────────────
sec_head(doc, 2, 'Resumen de cambios requeridos')
body(doc,
    'La siguiente tabla muestra de un vistazo qué debe cambiarse, dónde se encuentra '
    'la configuración y cuál es su criticidad:')
table(doc,
    headers=['Componente', 'Archivo / Ubicación', 'Criticidad'],
    rows=[
        ('IP / dominio público del servidor',    'application.properties + Nginx', 'CRÍTICO'),
        ('URL base para códigos QR (PKI)',        'application.properties',         'CRÍTICO'),
        ('Ruta de LibreOffice',                  'application.properties',          'ALTO'),
        ('Ruta de plantilla Anexo 9.2',          'application.properties',          'ALTO'),
        ('Keystore PKI (sit-keystore.p12)',       'Archivo en servidor',             'ALTO'),
        ('Cadena de conexión a MongoDB',         'application.properties',          'MEDIO'),
        ('Credenciales de correo Gmail',         'application.properties',          'MEDIO'),
        ('Variable de entorno JWT secret',       'Servicio systemd',                'MEDIO'),
        ('Configuración de Nginx',               '/etc/nginx/conf.d/sit.conf',      'MEDIO'),
        ('Puerto en firewall',                   'firewall-cmd / ufw',              'BAJO'),
    ],
    col_widths=[Cm(6.5), Cm(5.5), Cm(2.5)]
)


# ── 3. APPLICATION.PROPERTIES ─────────────────────────────────────────────────
sec_head(doc, 3, 'Archivo application.properties')
body(doc,
    'Este es el archivo de configuración principal del backend Spring Boot. Se encuentra en '
    'src/main/resources/application.properties dentro del proyecto. Los cambios aquí '
    'requieren recompilar el JAR (./gradlew bootJar) y volver a subir al servidor, '
    'o bien pueden sobreescribirse con un archivo externo en el servidor sin recompilar '
    '(ver sección 3.5).')


# 3.1 URL base QR
sub_head(doc, '3.1  URL base para códigos QR de certificación')
body(doc,
    'Esta propiedad define la dirección pública que se embebe dentro del código QR de cada '
    'documento certificado. Si el servidor cambia de IP o se asigna un dominio, esta URL '
    'debe actualizarse antes de emitir nuevas certificaciones.')
code(doc,
    '# Valor actual (servidor viejo)\n'
    'sit.cert.base-url=http://77.37.74.122\n\n'
    '# Cambiar a la IP o dominio del nuevo servidor\n'
    'sit.cert.base-url=http://<NUEVA_IP_O_DOMINIO>')
note(doc,
    'Los documentos ya certificados con la URL anterior seguirán teniendo el QR apuntando '
    'al servidor viejo. Si ese servidor ya no estará disponible, los QR de documentos '
    'previos dejarán de funcionar. Considerar redirección en el servidor viejo si aplica.',
    kind='warn')


# 3.2 MongoDB
sub_head(doc, '3.2  Cadena de conexión a MongoDB')
body(doc,
    'Si la base de datos MongoDB también cambia de servidor, se debe actualizar la URI de conexión. '
    'Si MongoDB permanece en el mismo servidor (77.37.74.122), esta línea no cambia.')
code(doc,
    '# Valor actual\n'
    'spring.data.mongodb.uri=mongodb://77.37.74.122:27017/sit_titulacion'
    '?connectTimeoutMS=10000&serverSelectionTimeoutMS=5000&socketTimeoutMS=5000\n\n'
    '# Si MongoDB se mueve, cambiar solo la IP:\n'
    'spring.data.mongodb.uri=mongodb://<NUEVA_IP_MONGO>:27017/sit_titulacion'
    '?connectTimeoutMS=10000&serverSelectionTimeoutMS=5000&socketTimeoutMS=5000')


# 3.3 LibreOffice
sub_head(doc, '3.3  Ruta de LibreOffice')
body(doc,
    'El sistema usa LibreOffice para convertir el Anexo 9.2 (documento Word) a PDF. '
    'La ruta varía según el sistema operativo del servidor.')
code(doc,
    '# En Windows (desarrollo local)\n'
    'sit.soffice.path=C:/Program Files/LibreOffice/program/soffice.exe\n\n'
    '# En Linux (producción) — instalar con: sudo dnf install libreoffice\n'
    'sit.soffice.path=/usr/bin/soffice')
note(doc,
    'Verificar que LibreOffice esté instalado en el nuevo servidor antes de arrancar el '
    'sistema. Sin él, la generación del Anexo 9.2 fallará (los demás anexos no lo requieren).',
    kind='info')


# 3.4 Plantilla Anexo 9.2
sub_head(doc, '3.4  Ruta de la plantilla Anexo 9.2')
body(doc,
    'El sistema necesita el archivo Word de la plantilla del Anexo 9.2 en el servidor. '
    'Debe copiarse manualmente al nuevo servidor y ajustar la ruta en la configuración.')
code(doc,
    '# Valor actual (apunta al home del usuario)\n'
    'sit.anexo92.plantilla-docx=${user.home}/Downloads/Anexo9.2.docx\n\n'
    '# En producción Linux se recomienda una ruta fija:\n'
    'sit.anexo92.plantilla-docx=/opt/sit/Anexo9.2.docx')
body(doc, 'Comando para copiar la plantilla al nuevo servidor desde la PC de desarrollo:')
code(doc, 'scp ~/Downloads/Anexo9.2.docx root@<NUEVA_IP>:/opt/sit/')


# 3.5 Correo Gmail
sub_head(doc, '3.5  Credenciales de correo Gmail')
body(doc,
    'Las credenciales SMTP están definidas en application.properties. No cambian al migrar '
    'de servidor a menos que se quiera usar una cuenta diferente. Se listan aquí para '
    'tenerlas presentes en la revisión.')
code(doc,
    'spring.mail.username=l21920103@voaxaca.tecnm.mx\n'
    'spring.mail.password=wztcmdgdkajggmwh   # Contraseña de aplicación Google (16 chars)')
note(doc,
    'Si la cuenta de Gmail renueva su contraseña de aplicación, actualizar spring.mail.password '
    'con el nuevo valor de 16 caracteres sin espacios.',
    kind='info')


# 3.6 Sobreescritura sin recompilar
sub_head(doc, '3.6  Aplicar cambios sin recompilar el JAR')
body(doc,
    'Spring Boot permite sobreescribir propiedades colocando un archivo application.properties '
    'junto al JAR en el servidor. Las propiedades de ese archivo tienen prioridad sobre las '
    'empaquetadas dentro del JAR, evitando tener que recompilar y volver a subir el JAR '
    'cada vez que cambia una configuración.')
code(doc,
    '# Crear /opt/sit/application.properties en el servidor con solo las propiedades que cambian:\n\n'
    'sit.cert.base-url=http://<NUEVA_IP_O_DOMINIO>\n'
    'sit.soffice.path=/usr/bin/soffice\n'
    'sit.anexo92.plantilla-docx=/opt/sit/Anexo9.2.docx\n'
    'spring.data.mongodb.uri=mongodb://<IP_MONGO>:27017/sit_titulacion'
    '?connectTimeoutMS=10000&serverSelectionTimeoutMS=5000&socketTimeoutMS=5000')
note(doc,
    'Este archivo externo sobreescribe solo las propiedades que se listan; el resto sigue '
    'tomándose del JAR. Es la práctica recomendada para producción.',
    kind='ok')


# ── 4. KEYSTORE PKI ───────────────────────────────────────────────────────────
sec_head(doc, 4, 'Keystore PKI — sit-keystore.p12')
body(doc,
    'El archivo sit-keystore.p12 contiene el certificado X.509 y la clave privada que firma '
    'digitalmente los documentos PDF certificados. Se genera automáticamente al arrancar el '
    'sistema por primera vez y se guarda en el directorio home del usuario que ejecuta el '
    'servicio (/root/sit-keystore.p12 si se corre como root).')
note(doc,
    'IMPORTANTE: si se migra el servidor sin copiar este archivo, el sistema generará un '
    'keystore nuevo. Las firmas digitales de documentos previos seguirán siendo técnicamente '
    'válidas (están embebidas en el PDF), pero el nuevo certificado no coincidirá con el '
    'anterior — Adobe Reader podría mostrar advertencia de "certificado no confiable" en '
    'documentos firmados con el certificado viejo.',
    kind='danger')

sub_head(doc, '4.1  Cómo copiar el keystore al nuevo servidor')
body(doc, 'Ejecutar desde la PC de desarrollo o directamente entre servidores:')
code(doc,
    '# Desde el servidor viejo, copiar al nuevo:\n'
    'scp root@77.37.74.122:/root/sit-keystore.p12  root@<NUEVA_IP>:/root/\n\n'
    '# Verificar que llegó al nuevo servidor:\n'
    'ssh root@<NUEVA_IP> "ls -lh /root/sit-keystore.p12"')
note(doc,
    'Si la ruta del keystore se cambió en application.properties (sit.cert.keystore-path), '
    'copiar el archivo a la ruta configurada.',
    kind='info')


# ── 5. NGINX ──────────────────────────────────────────────────────────────────
sec_head(doc, 5, 'Configuración de Nginx')
body(doc,
    'El archivo /etc/nginx/conf.d/sit.conf contiene la configuración del proxy inverso '
    'que sirve el frontend y redirige las peticiones de la API al backend. '
    'Al cambiar de servidor debe actualizarse el campo server_name.')

sub_head(doc, '5.1  Archivo sit.conf completo')
code(doc,
    'server {\n'
    '    listen 80;\n'
    '    server_name <NUEVA_IP_O_DOMINIO>;   # <-- CAMBIAR AQUÍ\n\n'
    '    root /var/www/sit;\n'
    '    index index.html;\n\n'
    '    location / {\n'
    '        try_files $uri $uri/ /index.html;\n'
    '    }\n\n'
    '    location /api/ {\n'
    '        proxy_pass http://127.0.0.1:8081/api/;\n'
    '        proxy_set_header Host $host;\n'
    '        proxy_set_header X-Real-IP $remote_addr;\n'
    '    }\n'
    '}')

sub_head(doc, '5.2  Aplicar y verificar')
code(doc,
    '# Verificar sintaxis antes de reiniciar\n'
    'sudo nginx -t\n\n'
    '# Recargar configuración\n'
    'sudo systemctl reload nginx')

note(doc,
    'Si se asigna un dominio con HTTPS (SSL/TLS), se deberá agregar un bloque server adicional '
    'en puerto 443 con los certificados correspondientes (Let\'s Encrypt recomendado). '
    'Eso está fuera del alcance de esta guía.',
    kind='info')


# ── 6. SERVICIO SYSTEMD ───────────────────────────────────────────────────────
sec_head(doc, 6, 'Servicio systemd — sit.service')
body(doc,
    'El servicio que mantiene el backend activo en el servidor se define en '
    '/etc/systemd/system/sit.service. Generalmente no necesita cambios al migrar, '
    'salvo que el nuevo servidor use un usuario diferente o que se requiera pasar '
    'la variable de entorno del JWT secret.')

sub_head(doc, '6.1  Archivo sit.service completo (con variable de entorno)')
code(doc,
    '[Unit]\n'
    'Description=SIT Backend\n'
    'After=network.target\n\n'
    '[Service]\n'
    'Type=simple\n'
    'User=root\n'
    'WorkingDirectory=/opt/sit\n'
    'ExecStart=/usr/bin/java -jar /opt/sit/sit-0.0.1-SNAPSHOT.jar\n'
    'Environment="SIT_JWT_SECRET=<CLAVE_LARGA_MIN_32_CARACTERES>"\n'
    'Restart=on-failure\n'
    'RestartSec=10\n\n'
    '[Install]\n'
    'WantedBy=multi-user.target')
note(doc,
    'La línea Environment= es opcional si se acepta el valor por defecto del JWT definido '
    'en application.properties. En producción se recomienda definirla con una clave segura '
    'generada aleatoriamente (mínimo 32 caracteres).',
    kind='warn')

sub_head(doc, '6.2  Comandos para activar el servicio en el nuevo servidor')
code(doc,
    'sudo systemctl daemon-reload\n'
    'sudo systemctl enable sit\n'
    'sudo systemctl start sit\n'
    'sudo systemctl status sit   # Verificar que diga: active (running)')


# ── 7. FIREWALL Y PUERTOS ─────────────────────────────────────────────────────
sec_head(doc, 7, 'Firewall y puertos')
body(doc,
    'El sistema requiere que los siguientes puertos estén accesibles en el nuevo servidor:')
table(doc,
    headers=['Puerto', 'Protocolo', 'Uso', 'Debe ser público'],
    rows=[
        ('80',    'TCP', 'Nginx — frontend Angular y proxy /api',          'Sí'),
        ('443',   'TCP', 'HTTPS (si se configura SSL en el futuro)',         'Sí (opcional)'),
        ('8081',  'TCP', 'Backend Spring Boot (solo interno, vía Nginx)',   'No — solo localhost'),
        ('27017', 'TCP', 'MongoDB (si la BD está en el mismo servidor)',    'No — solo localhost'),
    ],
    col_widths=[Cm(2.0), Cm(2.5), Cm(8.5), Cm(3.5)]
)

sub_head(doc, '7.1  Abrir puerto 80 en sistemas con firewalld (CentOS / RHEL / Rocky)')
code(doc,
    'sudo firewall-cmd --permanent --add-service=http\n'
    'sudo firewall-cmd --reload\n'
    'sudo firewall-cmd --list-all   # Verificar que aparezca "http" en services')

sub_head(doc, '7.2  Abrir puerto 80 en sistemas con ufw (Ubuntu / Debian)')
code(doc,
    'sudo ufw allow 80/tcp\n'
    'sudo ufw reload\n'
    'sudo ufw status   # Verificar que aparezca 80/tcp ALLOW')


# ── 8. CHECKLIST ─────────────────────────────────────────────────────────────
sec_head(doc, 8, 'Checklist de migración')
body(doc,
    'Usar esta lista para verificar que todos los pasos se han completado antes de '
    'dar el nuevo servidor como operativo:')

table(doc,
    headers=['#', 'Tarea', 'Verificación'],
    rows=[
        ('1',  'Actualizar sit.cert.base-url en application.properties',
               'Abrir un documento certificado y escanear el QR — debe abrir el nuevo servidor'),
        ('2',  'Actualizar sit.soffice.path (ruta de LibreOffice en Linux)',
               'Generar un Anexo 9.2 desde el sistema y verificar que el PDF se descarga'),
        ('3',  'Copiar Anexo9.2.docx a /opt/sit/ y actualizar sit.anexo92.plantilla-docx',
               'Mismo que punto 2'),
        ('4',  'Copiar sit-keystore.p12 al directorio home del nuevo servidor',
               'Al arrancar, los logs no deben mostrar "Generando nuevo keystore"'),
        ('5',  'Actualizar server_name en /etc/nginx/conf.d/sit.conf',
               'sudo nginx -t devuelve "syntax is ok"'),
        ('6',  'Actualizar Environment JWT secret en sit.service (si se usa)',
               'El login funciona correctamente sin errores 401'),
        ('7',  'Abrir puerto 80 en el firewall',
               'http://<NUEVA_IP> carga la pantalla de login desde un navegador externo'),
        ('8',  'Verificar que MongoDB es accesible desde el nuevo servidor',
               'journalctl -u sit -f — no aparecen errores de conexión a MongoDB'),
        ('9',  'Probar login con usuario coordinador',
               'Acceso exitoso y lista de egresados visible'),
        ('10', 'Probar generación y descarga de un PDF certificado',
               'El PDF se descarga, abre en Adobe Reader y muestra firma digital válida'),
    ],
    col_widths=[Cm(0.7), Cm(7.5), Cm(8.3)]
)


# ── 9. COMANDOS ÚTILES ────────────────────────────────────────────────────────
sec_head(doc, 9, 'Comandos de diagnóstico en el servidor')
body(doc, 'Comandos para verificar el estado del sistema y diagnosticar problemas post-migración:')

sub_head(doc, 'Estado de los servicios')
code(doc,
    '# Estado del backend\n'
    'sudo systemctl status sit\n\n'
    '# Logs en tiempo real del backend\n'
    'journalctl -u sit -f\n\n'
    '# Últimas 100 líneas de log\n'
    'journalctl -u sit -n 100\n\n'
    '# Estado de Nginx\n'
    'sudo systemctl status nginx')

sub_head(doc, 'Verificación de conectividad')
code(doc,
    '# Verificar que el backend responde en el puerto 8081 (desde el mismo servidor)\n'
    'curl http://localhost:8081/api/auth/me\n\n'
    '# Verificar que el endpoint público de verificación responde\n'
    'curl http://localhost:8081/api/verificar/<UUID_DE_PRUEBA>\n\n'
    '# Verificar que Nginx sirve el frontend\n'
    'curl -I http://localhost')

sub_head(doc, 'LibreOffice')
code(doc,
    '# Verificar que soffice está instalado y en la ruta correcta\n'
    'which soffice\n'
    'soffice --version')


# ── 10. INFORMACIÓN DE REFERENCIA ─────────────────────────────────────────────
sec_head(doc, 10, 'Información de referencia del sistema actual')
body(doc,
    'Datos del servidor y configuración actuales, para referencia durante la migración:')
table(doc,
    headers=['Parámetro', 'Valor actual'],
    rows=[
        ('IP del servidor',               '77.37.74.122'),
        ('Puerto del backend',            '8081 (interno, expuesto por Nginx)'),
        ('Puerto público',                '80 (HTTP)'),
        ('Directorio del JAR',            '/opt/sit/'),
        ('Directorio del frontend',       '/var/www/sit/'),
        ('Servicio systemd',              'sit.service'),
        ('Base de datos',                 'MongoDB 27017 — sit_titulacion'),
        ('Colección principal',           'registro (documentos Egresado)'),
        ('Keystore PKI',                  '/root/sit-keystore.p12'),
        ('Plantilla Anexo 9.2',           '~/Downloads/Anexo9.2.docx  (debe moverse a /opt/sit/)'),
        ('URL base QR (actual)',          'http://77.37.74.122'),
        ('Java requerido',                'Java 21 (OpenJDK)'),
        ('LibreOffice requerido',         'Cualquier versión reciente'),
    ],
    col_widths=[Cm(6.0), Cm(10.5)]
)

doc.save('GUIA_MIGRACION_SERVIDOR.docx')
print('OK: GUIA_MIGRACION_SERVIDOR.docx generado correctamente.')
