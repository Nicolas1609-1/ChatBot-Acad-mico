from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,Flowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'Informe_final_Chatbot_Academico.pdf'
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('ArialBold','C:/Windows/Fonts/arialbd.ttf'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='Arial',fontSize=10.2,leading=15,spaceAfter=9,textColor=colors.HexColor('#263442')))
styles.add(ParagraphStyle(name='TitleFinal',fontName='ArialBold',fontSize=26,leading=31,spaceAfter=18,textColor=colors.black))
styles.add(ParagraphStyle(name='SectionFinal',fontName='ArialBold',fontSize=17,leading=22,spaceAfter=14,textColor=colors.black))
styles.add(ParagraphStyle(name='SubFinal',fontName='ArialBold',fontSize=11.5,leading=16,spaceBefore=9,spaceAfter=7,textColor=colors.black))
styles.add(ParagraphStyle(name='SmallFinal',fontName='Arial',fontSize=8.5,leading=12,spaceAfter=7,textColor=colors.HexColor('#526476')))
styles.add(ParagraphStyle(name='CellFinal',fontName='Arial',fontSize=9,leading=12,spaceAfter=0))
styles.add(ParagraphStyle(name='HeaderFinal',fontName='ArialBold',fontSize=9,leading=12,textColor=colors.white))
story=[]
def p(text,style='Body'):story.append(Paragraph(text,styles[style]))
def h(text):p(text,'SubFinal')
def page(title):
 if story:story.append(PageBreak())
 p(title,'SectionFinal')
def table(headers,rows,widths):
 data=[[Paragraph(str(c),styles['HeaderFinal']) for c in headers]]+[[Paragraph(str(c),styles['CellFinal']) for c in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#264F73')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F1F6FA')]),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
 story.append(t);story.append(Spacer(1,12))
class Diagram(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=468;self.height=195
 def draw(self):
  c=self.canv;c.setFont('Arial',9)
  boxes=[(0,145,135,40,'Navegador de PC'),(165,145,135,40,'Cloudflare HTTPS'),(330,145,135,40,'Servidor web y proxy'),(330,75,135,40,'Agente n8n y Groq'),(0,5,135,40,'PostgreSQL y pgvector'),(165,5,135,40,'FastMCP de lectura'),(330,5,135,40,'Sheets y noticias UNAB')]
  for x,y,w,hh,label in boxes:
   c.setFillColor(colors.HexColor('#EDF4FA'));c.setStrokeColor(colors.HexColor('#A9BDCF'));c.roundRect(x,y,w,hh,6,fill=1,stroke=1);c.setFillColor(colors.HexColor('#203C54'));c.drawCentredString(x+w/2,y+16,label)
  c.setStrokeColor(colors.HexColor('#547C9F'))
  for x1,y1,x2,y2 in [(135,165,165,165),(300,165,330,165),(397,145,397,115),(350,75,232,45),(397,75,397,45),(232,5,135,25),(350,75,70,45)]:c.line(x1,y1,x2,y2)
def footer(c,d):
 c.setFont('Arial',8);c.setFillColor(colors.HexColor('#64768A'));c.drawString(54,34,'Chatbot académico de Ingeniería de Sistemas');c.drawRightString(558,34,f'{d.page}')
p('Chatbot de apoyo académico de Ingeniería de Sistemas','TitleFinal')
p('Informe técnico y manual de operación','SectionFinal')
p('Nicolás Javier Abello Suárez<br/>Ingeniería de Sistemas<br/>18 de noviembre de 2026','Body')
p('<b>Portal del proyecto</b><br/><link href="https://academico.nicolas16.life/" color="#245E8A">https://academico.nicolas16.life/</link>')
h('Resumen del resultado')
p('Se implementó un asistente web que consulta el expediente académico de un estudiante, calcula su avance y orienta la selección de materias y la proyección de semestres. La conversación y las integraciones se ejecutan en n8n Cloud. El portal está desplegado en un servidor Linux y publicado con HTTPS mediante Cloudflare Tunnel.')
p('El sistema integra PostgreSQL, recuperación documental RAG con pgvector, calendario de Google Sheets, noticias de la UNAB y herramientas FastMCP de solo lectura. Los expedientes, notas, plan simplificado y calendario son simulados; las noticias proceden de publicaciones institucionales. El portal conserva esta distinción.')
h('Objetivo')
p('Apoyar al estudiante de Ingeniería de Sistemas en la consulta de matrícula, promedio, créditos, historial, prerrequisitos y posibles periodos restantes, utilizando fuentes consultables en lugar de atribuir datos personales al conocimiento del modelo.')
table(['Elemento','Alcance implementado'],[['Estudiantes','13 expedientes simulados identificados con U00 y seis cifras'],['Plan académico','32 materias y 110 créditos en un plan simplificado'],['Interfaz','Portal de PC con vidrio translúcido azul y app Android (Expo), ambas con entrada por código'],['Integraciones','n8n, Groq, PostgreSQL, pgvector, Google Sheets y FastMCP']],[135,333])
p('Alcance acordado: portal web para PC y aplicación Android hecha con Expo que usa el mismo servidor y el mismo agente. El video de demostración permanece aplazado. El proyecto no se presenta como un sistema institucional de matrícula.','SmallFinal')
page('Arquitectura y organización de los flujos')
story.append(Diagram());story.append(Spacer(1,10))
p('El navegador se comunica con el servidor web mediante Cloudflare. El servidor consulta el perfil por una ruta fija de n8n, asocia la sesión al código validado y envía las preguntas al chat. n8n valida la entrada, selecciona herramientas con el agente y revisa la salida antes de devolver la respuesta.')
p('El agente conserva las consultas personales de expediente y proyección en herramientas SQL parametrizadas vinculadas al perfil elegido. El cliente MCP utiliza las herramientas de plan y noticias. Se excluyen del cliente MCP las funciones personales para evitar rutas duplicadas y conservar la vinculación del expediente.')
table(['Flujo de n8n','Función'],[['Chatbot Academico','Identificación del estudiante, conversación, memoria, herramientas y validaciones'],['Preparar Base Academica Demo','Semilla inicial del esquema y datos simulados'],['Sistemas Preparar proyeccion de semestres','Función de simulación, migraciones de códigos y perfiles adicionales'],['RAG Sistemas Indexar documentos','Fragmentación, embeddings e indexación documental'],['Sistemas Actualizar noticias UNAB','Sincronización diaria y actualización sin duplicados'],['Sistemas Preparar calendario DEMO','Preparación y verificación del calendario utilizado por el agente']],[204,264])
p('Los flujos de preparación se ejecutan por separado para que cada pregunta no vuelva a cargar datos ni regenere embeddings. La conversación permanece en un flujo principal. Las noticias se actualizan diariamente a las 08:00 en la zona America/Bogota.')
page('Datos académicos e identificación del estudiante')
p('El código público tiene el formato U00 seguido de seis números. No codifica el semestre ni el promedio: esos valores se consultan en la base. Los códigos disponibles van de U00100001 a U00100013. Una columna institucional vincula los códigos públicos a las claves internas existentes sin cambiar notas ni relaciones.')
table(['Código','Nombre','Semestre','Promedio','Créditos'],[['U00100001','Ana Ejemplo','3','3,50','22'],['U00100002','Bruno Ejemplo','4','4,01','40'],['U00100011','Laura Ejemplo','2','4,00','13'],['U00100012','Mateo Ejemplo','5','4,09','54'],['U00100013','Sofía Ejemplo','7','3,82','81']],[105,128,65,80,90])
h('Modelo relacional')
p('Las tablas estudiantes y materias contienen los perfiles y asignaturas. prerrequisitos relaciona cada materia con sus requisitos. matriculas registra estado y periodo por estudiante. historial almacena intentos, nota y estado de cada asignatura. Las claves foráneas mantienen la relación entre estudiantes, matrículas e historial.')
p('La vista v_resumen entrega matrícula, semestre actual, promedio histórico y créditos aprobados. v_materias_pendientes identifica asignaturas no aprobadas y el cumplimiento de sus prerrequisitos. noticias y estado_fuentes conservan publicaciones y la última sincronización exitosa.')
h('Cálculo y proyección')
p('El promedio histórico se pondera por créditos e incluye intentos reprobados. Los créditos aprobados se cuentan una sola vez por asignatura. El avance es créditos aprobados dividido por 110, multiplicado por 100.')
p('La función proyectar_semestres selecciona materias elegibles con una carga máxima de 18 créditos por periodo. Incluye las materias en curso en el primer periodo y solo considera satisfecho un prerrequisito después de aprobarlo en un periodo anterior. Las recomendaciones distinguen materias en curso de nuevas candidatas. Para el próximo semestre el agente presenta el segundo periodo de la proyección, que supone aprobar las materias en curso.')
p('La proyección es una simulación voraz y no garantiza el mínimo de semestres. Supone aprobar todas las materias seleccionadas, oferta en cada periodo y ausencia de conflictos de horario o cupos. No incorpora requisitos externos al plan simplificado. Para Ana, el resultado verificado es seis periodos simulados, incluido el actual.')
page('Recuperación documental calendario y noticias')
h('RAG institucional')
p('La recuperación documental utiliza 96 fragmentos guardados en PostgreSQL con pgvector. Se emplean embeddings text-embedding-3-small de 1536 dimensiones mediante Gateway de n8n, similitud coseno y tres resultados por consulta. Los fragmentos tienen hasta 1200 caracteres, con solapamiento de 180 y separación por estructura Markdown.')
p('El corpus incluye un manual del escenario académico y dos documentos facilitados por el profesor: un FAQ y una propuesta de competencias digitales. Provienen del repositorio clima-Biing26-UCC-Ibague; no se incorporaron registros del clima. El repositorio se utilizó como fuente documental, no como tema del chatbot.')
p('El agente debe responder con los fragmentos pertinentes y citar título y enlace de origen. La propuesta de julio de 2025 es material de referencia y no acredita por sí misma normativa vigente. Los tres pilares descritos son Competencias Digitales Básicas, Analítica y Contenido Digital, y Tecnologías Transformativas.')
h('Calendario académico')
p('El calendario se consulta desde Google Sheets mediante una operación de lectura. Contiene seis eventos simulados del periodo 2027-1. Las preguntas sobre fechas deben utilizar esta fuente, no la memoria ni los documentos RAG. Las fechas no constituyen un calendario oficial de la universidad.')
h('Noticias de Ingeniería de Sistemas')
p('El flujo programado consume la API pública de WordPress de la UNAB, categoría de Ingeniería de Sistemas. Normaliza títulos y resúmenes y actualiza registros por identificador de publicación. La actualización no crea duplicados y registra su finalización exitosa. Se conservan fecha, enlace y momento de consulta.')
p('FastMCP consulta las noticias almacenadas y devuelve la marca de sincronización. El agente advierte cuando la fuente supera 48 horas sin actualizarse. Una noticia curricular no modifica automáticamente el plan simulado de 110 créditos, ni confirma cupos o inscripciones.')
h('Modelo y uso de cuota')
p('La generación utiliza openai/gpt-oss-120b a través de Groq. Se limita la salida a 1400 tokens y se recupera como máximo una búsqueda RAG por mensaje. La memoria usa dos interacciones recientes, con un máximo de 1200 tokens de historial, y el agente vuelve a consultar la herramienta en cada turno en lugar de responder datos desde la memoria. Estas medidas reducen consumo, pero no eliminan los límites del proveedor; ante una falla se devuelve un mensaje de indisponibilidad sin inventar resultados.')
page('Despliegue seguridad y operación')
p('La aplicación reside en /home/nicolas/chatbot-academico. El servicio chatbot-academico-web.service atiende el portal y proxy en el puerto 8091. Cloudflare publica academico.nicolas16.life con HTTPS hacia esa aplicación. El despliegue conserva los otros servicios existentes del servidor.')
p('FastMCP funciona como chatbot-academico-mcp.service, con arranque automático y escucha en 127.0.0.1:9000. El proxy transmite únicamente la ruta fija /mcp. Las solicitudes requieren Bearer Auth; el servicio verifica el hash SHA-256 del token. El token identifica a n8n como servicio, no a un alumno real.')
table(['Control','Implementación'],[['Acceso a PostgreSQL de MCP','Rol dedicado de lectura sin superusuario, creación de roles o bases ni BYPASSRLS'],['Transporte a PostgreSQL','TLS verify-full con certificado CA de Supabase'],['Consultas','SQL fijo parametrizado, transacción de lectura y timeout de cinco segundos'],['Sesión del portal','Código validado en el servidor; nueva sesión al cambiar de estudiante; caducidad de dos horas'],['Entrada y salida','Límites de tamaño, patrones de claves conocidas, revisión de salida y mensajes de error controlados'],['Secretos','Archivos privados del servidor y credenciales de n8n; no se incluyen en frontend ni documento']],[145,323])
h('Operación básica')
p('Para revisar disponibilidad se consulta /health. Los servicios se administran con systemctl --user. La preparación de datos, indexación RAG y migraciones no deben ejecutarse con cada consulta. El instalador comprueba que los archivos permanezcan dentro de la carpeta del proyecto y preserva la configuración privada.')
h('Límites de acceso')
p('La web es pública y trabaja con expedientes simulados. Un código U00 selecciona un perfil; no es contraseña ni autenticación institucional. Los visitantes pueden consumir cuota de IA. El chatbot no matricula asignaturas, no cambia notas y no garantiza graduación. Antes de usar datos reales se requiere identidad institucional, autorización por expediente y revisión integral de privacidad y permisos.')
page('Verificación y resultados')
table(['Verificación','Resultado observado'],[['Expediente por código','Ana devuelve 3,50 y 22 créditos; Mateo devuelve 4,09 y 54'],['Perfiles adicionales','Laura, Mateo y Sofía consultados por el dominio HTTPS'],['Proyección','Ana obtiene seis periodos con límite de 18 créditos y prerrequisitos'],['RAG','Respuesta sobre tres pilares con referencia exacta al material del profesor'],['Próximo semestre','Mateo: S602, S603, S604, S701 y S703, 18 créditos, coherente con la proyección'],['Calendario','Lectura de los eventos del periodo 2027-1 desde Sheets'],['Noticias mediante n8n y MCP','Ejecución 63 usó la herramienta MCP y devolvió publicación, fecha y enlace'],['MCP sobre HTTPS','Descubrimiento de cuatro herramientas y consulta real del perfil U00100012'],['Autenticación MCP','Solicitud sin token devuelve HTTP 401'],['Rol de lectura','INSERT en estudiantes no permitido; conexión con lectura activada'],['Aplicación móvil','Panel de Mateo 4,09 / 54 créditos / 49 % y respuestas del agente contra el servidor real'],['Pruebas automatizadas','15 de protocolo web, 14 de gateway y 14 de FastMCP aprobadas']],[170,298])
h('Cómo utilizar el portal')
p('1. Abrir https://academico.nicolas16.life/. 2. Ingresar un código existente, por ejemplo U00100012. 3. Consultar promedio, historial, créditos, materias pendientes o proyección. 4. Usar Cambiar estudiante para seleccionar otro perfil sin conservar los mensajes visibles de la sesión anterior.')
h('Aplicación móvil')
p('La carpeta app-movil contiene la aplicación Android hecha con Expo (React Native). El estudiante entra con su código U00, ve su panel con promedio, créditos y avance, usa atajos de Matrícula, Proyección, Recomendaciones, Calendario y Noticias, y conversa con el mismo agente de n8n. La app habla solo con academico.nicolas16.life; el servidor fija el destino, valida el código y limita las consultas. Si Groq alcanza su límite por minuto, la app espera y reintenta sola. Para abrirla: npx expo start en app-movil y escanear el QR con Expo Go.')
h('Conclusión')
p('La entrega web integra orientación personalizada y fuentes documentales con consultas verificables. n8n coordina la conversación, mientras PostgreSQL y FastMCP devuelven datos estructurados. La distinción entre simulación académica, material del profesor y noticias institucionales permite interpretar las respuestas sin atribuirles autoridad administrativa.')
p('La aplicación móvil reutiliza el servidor y el agente del portal, sin guardar claves en el teléfono. El video está aplazado. La validación se realizó sobre datos sintéticos y no demuestra preparación para operar con expedientes reales de estudiantes.')
page('Evidencia del portal y fuentes')
p('Portal publicado por Cloudflare, con entrada por código y consulta del expediente seleccionado. La captura muestra una respuesta verificada para Mateo. El diseño conserva vidrio translúcido, reflejos y acentos azules.')
image=ROOT/'verificacion/cloudflare-perfil-mateo.jpg'
if image.exists():
 iw,ih=ImageReader(str(image)).getSize();story.append(Image(str(image),width=468,height=468*ih/iw));story.append(Spacer(1,13))
h('Fuentes y documentación de referencia')
refs=[('Material del profesor','https://github.com/adiacla/clima-Biing26-UCC-Ibague'),('Documentación de n8n','https://docs.n8n.io/'),('FastMCP','https://gofastmcp.com/'),('PostgreSQL','https://www.postgresql.org/docs/'),('Conexión de Supabase','https://supabase.com/docs/guides/database/connecting-to-postgres'),('Cloudflare Tunnel','https://developers.cloudflare.com/tunnel/'),('Noticias UNAB','https://unab.edu.co/')]
for name,url in refs:p(f'{name}: <link href="{url}" color="#245E8A">{url}</link>','SmallFinal')
p('Repositorio de referencia fijado al commit 9a01d6d4779579c464115543008defb216ad703e. Los respaldos de los workflows, scripts SQL y documentación operativa se incluyen en el paquete del proyecto. Las credenciales quedan fuera del informe y del paquete.','SmallFinal')
SimpleDocTemplate(str(OUT),pagesize=(612,792),rightMargin=72,leftMargin=72,topMargin=52,bottomMargin=52,title='Chatbot de apoyo académico de Ingeniería de Sistemas',author='Nicolás Javier Abello Suárez').build(story,onFirstPage=footer,onLaterPages=footer)
qa=ROOT/'verificacion/informe_final';qa.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(OUT))
for i in range(len(pdf)):pdf[i].render(scale=1.3).to_pil().save(qa/f'page-{i+1}.png')
print('PDF:',OUT,'Paginas:',len(pdf))
