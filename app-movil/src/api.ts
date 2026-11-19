// Cliente del webhook del chatbot académico.
// La app no guarda claves: habla con el proxy del servidor, que reenvía a n8n.

export const API_BASE = process.env.EXPO_PUBLIC_API_BASE ?? 'https://academico.nicolas16.life';

export type Estudiante = {
  codigo: string;
  nombre: string;
  programa: string;
  creditos_plan: number;
  semestre_actual: number;
  estado_matricula: string;
  porcentaje_avance: number;
  creditos_aprobados: number;
  promedio_historico: number;
};

export const CODIGO_VALIDO = /^U00[0-9]{6}$/;

export function nuevaSesion(): string {
  const letras = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let id = 'movil-';
  for (let i = 0; i < 24; i++) id += letras[Math.floor(Math.random() * letras.length)];
  return id;
}

async function post(ruta: string, cuerpo: unknown, msTimeout: number) {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), msTimeout);
  try {
    const respuesta = await fetch(API_BASE + ruta, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(cuerpo),
      signal: control.signal,
    });
    let datos: any = null;
    try {
      datos = await respuesta.json();
    } catch {
      // respuesta sin JSON
    }
    if (!respuesta.ok) {
      throw new Error(datos?.error ?? `El servidor respondió ${respuesta.status}.`);
    }
    return datos;
  } catch (e: any) {
    if (e?.name === 'AbortError') throw new Error('La consulta tardó demasiado. Intenta de nuevo.');
    if (e instanceof TypeError) throw new Error('Sin conexión con el servidor. Revisa tu internet.');
    throw e;
  } finally {
    clearTimeout(temporizador);
  }
}

export async function buscarEstudiante(codigo: string, sessionId: string): Promise<Estudiante | null> {
  const datos = await post('/api/student', { codigo, sessionId }, 30000);
  return datos?.encontrado ? (datos.estudiante as Estudiante) : null;
}

// n8n devuelve este texto cuando Groq alcanza su límite de tokens por minuto.
export class LimiteIA extends Error {
  esLimite = true;
}
export const esLimite = (e: unknown) => (e as { esLimite?: boolean } | null)?.esLimite === true;

export async function preguntar(chatInput: string, sessionId: string): Promise<string> {
  let datos: any;
  try {
    datos = await post('/api/chat', { chatInput, sessionId }, 130000);
  } catch (e: any) {
    if (/limite|l[ií]mite|en curso/i.test(e?.message ?? '')) throw new LimiteIA(e.message);
    throw e;
  }
  if (typeof datos?.output !== 'string') throw new Error('El asistente no devolvió respuesta.');
  if (datos.output.startsWith('No pude completar la consulta porque el servicio de IA')) {
    throw new LimiteIA(datos.output);
  }
  return datos.output;
}
