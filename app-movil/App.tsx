import { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  type ScrollViewInstance,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Markdown from 'react-native-markdown-display';
import { buscarEstudiante, CODIGO_VALIDO, esLimite, Estudiante, nuevaSesion, preguntar } from './src/api';

const C = {
  fondo1: '#050d24',
  fondo2: '#0b2a6b',
  fondo3: '#1f5fd1',
  vidrio: 'rgba(255,255,255,0.10)',
  borde: 'rgba(255,255,255,0.28)',
  texto: '#f2f6ff',
  suave: '#a9bde6',
  acento: '#5aa2ff',
  acento2: '#8fd3ff',
  error: '#ff9a9a',
};

type Mensaje = { id: string; rol: 'usuario' | 'asistente' | 'error'; texto: string };

const ATAJOS = [
  { titulo: 'Matrícula', pregunta: '¿Qué materias puedo matricular el próximo semestre?' },
  { titulo: 'Estado académico', pregunta: '¿Cuál es mi promedio, mis créditos aprobados y mi avance?' },
  { titulo: 'Proyección', pregunta: '¿Cuántos semestres me faltan para graduarme?' },
  { titulo: 'Recomendaciones', pregunta: 'Dame recomendaciones para tener éxito en el programa según mi historial.' },
  { titulo: 'Calendario', pregunta: '¿Cuáles son las próximas fechas del calendario académico?' },
  { titulo: 'Noticias', pregunta: '¿Cuáles son las noticias más recientes de tecnología e ingeniería de sistemas?' },
];

const CLAVE_CODIGO = 'ultimo-codigo';

function Vidrio({ children, style }: { children: React.ReactNode; style?: object }) {
  return (
    <View style={[estilos.vidrioMarco, style]}>
      <BlurView intensity={40} tint="dark" style={StyleSheet.absoluteFill} />
      <LinearGradient
        colors={['rgba(255,255,255,0.22)', 'rgba(255,255,255,0.04)', 'rgba(255,255,255,0.10)']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={StyleSheet.absoluteFill}
      />
      <View style={estilos.vidrioContenido}>{children}</View>
    </View>
  );
}

function Fondo({ children }: { children: React.ReactNode }) {
  return (
    <LinearGradient colors={[C.fondo1, C.fondo2, C.fondo1]} style={{ flex: 1 }}>
      <View style={[estilos.burbuja, { top: -80, right: -60, backgroundColor: C.fondo3 }]} />
      <View style={[estilos.burbuja, { bottom: 60, left: -90, backgroundColor: '#2a7fff', opacity: 0.35 }]} />
      {children}
    </LinearGradient>
  );
}

function Entrada({ alEntrar }: { alEntrar: (e: Estudiante, sesion: string) => void }) {
  const [codigo, setCodigo] = useState('U00');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    AsyncStorage.getItem(CLAVE_CODIGO)
      .then((c) => c && setCodigo(c))
      .catch(() => {});
  }, []);

  const entrar = async () => {
    const limpio = codigo.trim().toUpperCase();
    if (!CODIGO_VALIDO.test(limpio)) {
      setError('El código debe ser U00 seguido de 6 números. Ejemplo: U00100001');
      return;
    }
    setError('');
    setCargando(true);
    try {
      const sesion = nuevaSesion();
      const estudiante = await buscarEstudiante(limpio, sesion);
      if (!estudiante) {
        setError('No encontramos ese código en Ingeniería de Sistemas.');
        return;
      }
      AsyncStorage.setItem(CLAVE_CODIGO, limpio).catch(() => {});
      alEntrar(estudiante, sesion);
    } catch (e: any) {
      setError(e.message ?? 'No se pudo consultar el código.');
    } finally {
      setCargando(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={estilos.centro}>
      <Text style={estilos.marca}>Asistente Académico</Text>
      <Text style={estilos.subtitulo}>Ingeniería de Sistemas</Text>
      <Vidrio style={{ width: '100%', marginTop: 28 }}>
        <Text style={estilos.etiqueta}>Código de estudiante</Text>
        <TextInput
          value={codigo}
          onChangeText={(t) => setCodigo(t.toUpperCase())}
          autoCapitalize="characters"
          autoCorrect={false}
          maxLength={9}
          placeholder="U00XXXXXX"
          placeholderTextColor={C.suave}
          style={estilos.campoCodigo}
          onSubmitEditing={entrar}
          returnKeyType="go"
        />
        {error ? <Text style={estilos.error}>{error}</Text> : null}
        <Pressable onPress={entrar} disabled={cargando} style={({ pressed }) => [estilos.boton, pressed && { opacity: 0.8 }]}>
          {cargando ? <ActivityIndicator color="#fff" /> : <Text style={estilos.botonTexto}>Entrar</Text>}
        </Pressable>
        <Text style={estilos.nota}>Con tu código el asistente conoce tu semestre, promedio y créditos.</Text>
      </Vidrio>
      <Text style={estilos.pie}>Datos simulados para el proyecto académico</Text>
    </KeyboardAvoidingView>
  );
}

function Panel({ e }: { e: Estudiante }) {
  const avance = Math.max(0, Math.min(100, Number(e.porcentaje_avance) || 0));
  return (
    <Vidrio style={{ marginHorizontal: 16, marginTop: 8 }}>
      <Text style={estilos.nombre}>{e.nombre}</Text>
      <Text style={estilos.suave}>
        {e.codigo} · Semestre {e.semestre_actual} · Matrícula {e.estado_matricula}
      </Text>
      <View style={estilos.metricas}>
        <Metrica valor={Number(e.promedio_historico).toFixed(2)} etiqueta="Promedio" />
        <Metrica valor={`${e.creditos_aprobados}/${e.creditos_plan}`} etiqueta="Créditos" />
        <Metrica valor={`${avance.toFixed(0)} %`} etiqueta="Avance" />
      </View>
      <View style={estilos.barra}>
        <LinearGradient
          colors={[C.acento, C.acento2]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={[estilos.barraRelleno, { width: `${avance}%` }]}
        />
      </View>
    </Vidrio>
  );
}

function Metrica({ valor, etiqueta }: { valor: string; etiqueta: string }) {
  return (
    <View style={{ alignItems: 'center', flex: 1 }}>
      <Text style={estilos.metricaValor}>{valor}</Text>
      <Text style={estilos.metricaEtiqueta}>{etiqueta}</Text>
    </View>
  );
}

function Chat({ estudiante, sesion, alSalir }: { estudiante: Estudiante; sesion: string; alSalir: () => void }) {
  const [mensajes, setMensajes] = useState<Mensaje[]>([
    {
      id: 'bienvenida',
      rol: 'asistente',
      texto: `Hola, **${estudiante.nombre.split(' ')[0]}**. Pregúntame por tu matrícula, tu estado académico, tu proyección o pide recomendaciones.`,
    },
  ]);
  const [texto, setTexto] = useState('');
  const [esperando, setEsperando] = useState(false);
  const [estado, setEstado] = useState('Consultando tu expediente…');
  const lista = useRef<ScrollViewInstance>(null);
  const montado = useRef(true);
  useEffect(() => () => void (montado.current = false), []);

  // Groq gratis admite pocas consultas por minuto: si se llena, la app espera y reintenta sola.
  const esperarConCuenta = async (segundos: number) => {
    for (let s = segundos; s > 0 && montado.current; s--) {
      setEstado(`La IA gratuita llegó a su límite por minuto. Reintento en ${s} s…`);
      await new Promise((r) => setTimeout(r, 1000));
    }
    setEstado('Consultando tu expediente…');
  };

  const enviar = async (pregunta: string) => {
    const limpia = pregunta.trim();
    if (!limpia || esperando) return;
    setTexto('');
    setMensajes((m) => [...m, { id: `u${Date.now()}`, rol: 'usuario', texto: limpia }]);
    setEsperando(true);
    setEstado('Consultando tu expediente…');
    try {
      let respuesta: string | null = null;
      for (let intento = 0; respuesta === null; intento++) {
        try {
          respuesta = await preguntar(limpia, sesion);
        } catch (e) {
          if (!esLimite(e) || intento >= 2 || !montado.current) throw e;
          await esperarConCuenta(intento === 0 ? 40 : 60);
        }
      }
      setMensajes((m) => [...m, { id: `a${Date.now()}`, rol: 'asistente', texto: respuesta as string }]);
    } catch (e: any) {
      const texto =
        esLimite(e)
          ? 'La IA sigue ocupada por el límite gratuito. Espera un minuto y vuelve a intentarlo.'
          : e.message ?? 'Error desconocido.';
      setMensajes((m) => [...m, { id: `e${Date.now()}`, rol: 'error', texto }]);
    } finally {
      setEsperando(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
      <View style={estilos.cabecera}>
        <View>
          <Text style={estilos.marcaPequena}>Asistente Académico</Text>
          <Text style={estilos.suave}>Ingeniería de Sistemas</Text>
        </View>
        <Pressable onPress={alSalir} style={estilos.botonSecundario}>
          <Text style={estilos.botonSecundarioTexto}>Cambiar código</Text>
        </Pressable>
      </View>

      <Panel e={estudiante} />

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ flexGrow: 0 }} contentContainerStyle={estilos.atajos}>
        {ATAJOS.map((a) => (
          <Pressable key={a.titulo} onPress={() => enviar(a.pregunta)} disabled={esperando} style={[estilos.chip, esperando && { opacity: 0.5 }]}>
            <Text style={estilos.chipTexto}>{a.titulo}</Text>
          </Pressable>
        ))}
      </ScrollView>

      <ScrollView
        ref={lista}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 16, gap: 10 }}
        onContentSizeChange={() => lista.current?.scrollToEnd({ animated: true })}
      >
        {mensajes.map((m) =>
          m.rol === 'usuario' ? (
            <View key={m.id} style={estilos.globoUsuario}>
              <Text style={estilos.textoUsuario}>{m.texto}</Text>
            </View>
          ) : (
            <Vidrio key={m.id} style={estilos.globoAsistente}>
              {m.rol === 'error' ? (
                <Text style={estilos.error}>{m.texto}</Text>
              ) : (
                <Markdown style={estilosMarkdown} rules={reglasMarkdown}>
                  {m.texto}
                </Markdown>
              )}
            </Vidrio>
          ),
        )}
        {esperando ? (
          <View style={estilos.pensando}>
            <ActivityIndicator color={C.acento2} />
            <Text style={[estilos.suave, { flex: 1 }]}>  {estado}</Text>
          </View>
        ) : null}
      </ScrollView>

      <View style={estilos.barraEntrada}>
        <TextInput
          value={texto}
          onChangeText={setTexto}
          placeholder="Escribe tu pregunta"
          placeholderTextColor={C.suave}
          style={estilos.campoMensaje}
          multiline
          maxLength={1000}
        />
        <Pressable
          onPress={() => enviar(texto)}
          disabled={esperando || !texto.trim()}
          style={[estilos.enviar, (esperando || !texto.trim()) && { opacity: 0.5 }]}
        >
          <Text style={estilos.botonTexto}>Enviar</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

export default function App() {
  const [sesion, setSesion] = useState<{ estudiante: Estudiante; id: string } | null>(null);
  return (
    <SafeAreaProvider>
      <Fondo>
        <StatusBar style="light" />
        <SafeAreaView style={{ flex: 1 }}>
          {sesion ? (
            <Chat key={sesion.id} estudiante={sesion.estudiante} sesion={sesion.id} alSalir={() => setSesion(null)} />
          ) : (
            <Entrada alEntrar={(estudiante, id) => setSesion({ estudiante, id })} />
          )}
        </SafeAreaView>
      </Fondo>
    </SafeAreaProvider>
  );
}

const estilos = StyleSheet.create({
  centro: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  burbuja: { position: 'absolute', width: 280, height: 280, borderRadius: 140, opacity: 0.45 },
  vidrioMarco: { borderRadius: 22, borderWidth: 1, borderColor: C.borde, overflow: 'hidden', backgroundColor: C.vidrio },
  vidrioContenido: { padding: 16 },
  marca: { color: C.texto, fontSize: 30, fontWeight: '800', textAlign: 'center' },
  marcaPequena: { color: C.texto, fontSize: 18, fontWeight: '800' },
  subtitulo: { color: C.acento2, fontSize: 16, marginTop: 4 },
  etiqueta: { color: C.suave, fontSize: 13, marginBottom: 8 },
  campoCodigo: {
    color: C.texto,
    fontSize: 24,
    letterSpacing: 3,
    borderWidth: 1,
    borderColor: C.borde,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 12,
    backgroundColor: 'rgba(0,0,0,0.25)',
  },
  error: { color: C.error, marginTop: 10 },
  boton: { marginTop: 16, backgroundColor: C.acento, borderRadius: 14, paddingVertical: 14, alignItems: 'center' },
  botonTexto: { color: '#fff', fontWeight: '700', fontSize: 16 },
  nota: { color: C.suave, fontSize: 12, marginTop: 12, textAlign: 'center' },
  pie: { color: C.suave, fontSize: 11, marginTop: 24, opacity: 0.8 },
  suave: { color: C.suave, fontSize: 13 },
  cabecera: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingTop: 8 },
  botonSecundario: { borderWidth: 1, borderColor: C.borde, borderRadius: 12, paddingHorizontal: 12, paddingVertical: 8 },
  botonSecundarioTexto: { color: C.texto, fontSize: 13 },
  nombre: { color: C.texto, fontSize: 18, fontWeight: '700' },
  metricas: { flexDirection: 'row', marginTop: 14 },
  metricaValor: { color: C.texto, fontSize: 20, fontWeight: '800' },
  metricaEtiqueta: { color: C.suave, fontSize: 12 },
  barra: { height: 8, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.15)', marginTop: 12, overflow: 'hidden' },
  barraRelleno: { height: 8, borderRadius: 4 },
  atajos: { paddingHorizontal: 16, paddingVertical: 12, gap: 8 },
  chip: {
    borderWidth: 1,
    borderColor: C.borde,
    backgroundColor: 'rgba(90,162,255,0.18)',
    borderRadius: 18,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  chipTexto: { color: C.texto, fontSize: 13, fontWeight: '600' },
  globoUsuario: {
    alignSelf: 'flex-end',
    maxWidth: '85%',
    backgroundColor: C.acento,
    borderRadius: 18,
    borderBottomRightRadius: 4,
    padding: 12,
  },
  textoUsuario: { color: '#fff', fontSize: 15 },
  globoAsistente: { alignSelf: 'flex-start', maxWidth: '95%' },
  pensando: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6 },
  barraEntrada: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 12,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.12)',
  },
  campoMensaje: {
    flex: 1,
    color: C.texto,
    maxHeight: 110,
    borderWidth: 1,
    borderColor: C.borde,
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
    backgroundColor: 'rgba(0,0,0,0.25)',
    fontSize: 15,
  },
  enviar: { backgroundColor: C.acento, borderRadius: 16, paddingHorizontal: 16, paddingVertical: 12 },
});

// Las tablas de las respuestas se deslizan horizontalmente para no aplastar columnas.
const reglasMarkdown = {
  table: (node: { key: string }, children: React.ReactNode) => (
    <ScrollView key={node.key} horizontal showsHorizontalScrollIndicator style={{ marginVertical: 6 }}>
      <View style={estilosMarkdown.table}>{children}</View>
    </ScrollView>
  ),
};

const estilosMarkdown = StyleSheet.create({
  body: { color: C.texto, fontSize: 15, lineHeight: 21 },
  strong: { fontWeight: '800', color: '#ffffff' },
  em: { color: C.suave },
  link: { color: C.acento2 },
  bullet_list: { marginVertical: 4 },
  table: { borderColor: C.borde, borderWidth: 1, borderRadius: 6 },
  tr: { borderColor: C.borde, borderBottomWidth: 1 },
  th: { padding: 6, fontWeight: '700', width: 130 },
  td: { padding: 6, width: 130 },
  code_inline: { backgroundColor: 'rgba(0,0,0,0.3)', color: C.acento2 },
  code_block: { backgroundColor: 'rgba(0,0,0,0.3)', color: C.texto, borderColor: C.borde },
  fence: { backgroundColor: 'rgba(0,0,0,0.3)', color: C.texto, borderColor: C.borde },
  blockquote: {
    backgroundColor: 'rgba(90,162,255,0.12)',
    borderLeftColor: C.acento,
    borderLeftWidth: 3,
    paddingHorizontal: 10,
    marginVertical: 6,
  },
  hr: { backgroundColor: C.borde },
});
