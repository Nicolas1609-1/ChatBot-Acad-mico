CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS public.rag_sistemas_vectores (
id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
embedding vector(1536),
text text NOT NULL,
metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);
ALTER TABLE public.rag_sistemas_vectores ENABLE ROW LEVEL SECURITY;
COMMENT ON TABLE public.rag_sistemas_vectores IS 'RAG del prototipo de Sistemas: material del profesor y reglas sinteticas, sin datos de estudiantes.';
DELETE FROM public.rag_sistemas_vectores WHERE metadata->>'corpus'='sistemas_v1';
SELECT true AS preparado;
