import io, os, re, time, tempfile
import pandas as pd
import psutil
import streamlit as st
import fitz

st.set_page_config(page_title='DAIR — Laboratório GraniteDocling', layout='wide')
st.title('Laboratório isolado — DAIR × GraniteDocling')
st.caption('Teste independente. Não usa nem altera o Copiloto RPPS.')

CNPJ_RE = re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b')
MONEY_RE = re.compile(r'R\$\s*[\d\.]+,\d{2}')
PCT_RE = re.compile(r'\b\d{1,3},\d{2}%')

def mb():
    return psutil.Process(os.getpid()).memory_info().rss / 1024**2

def find_portfolio_pages(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    pages=[]
    for i,p in enumerate(doc):
        txt=p.get_text('text') or ''
        if 'CARTEIRA DE INVESTIMENTOS' in txt.upper():
            pages.append(i)
    return pages

def native_lines(pdf_bytes, pages):
    doc=fitz.open(stream=pdf_bytes,filetype='pdf')
    out=[]
    for i in pages:
        txt=doc[i].get_text('text') or ''
        for line in txt.splitlines():
            c=CNPJ_RE.findall(line); m=MONEY_RE.findall(line); p=PCT_RE.findall(line)
            if c or m:
                out.append({'pagina':i+1,'linha_nativa':line.strip(),'cnpj':' | '.join(c),'valor':' | '.join(m),'percentual':' | '.join(p)})
    return pd.DataFrame(out)

@st.cache_resource(show_spinner=False)
def load_docling():
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import VlmPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.pipeline.vlm_pipeline import VlmPipeline
    opts = VlmPipelineOptions()
    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_cls=VlmPipeline, pipeline_options=opts)})

def make_subset(pdf_bytes, pages):
    src=fitz.open(stream=pdf_bytes,filetype='pdf'); dst=fitz.open()
    for p in pages: dst.insert_pdf(src, from_page=p, to_page=p)
    return dst.tobytes()

up=st.file_uploader('Envie um DAIR em PDF', type=['pdf'])
if up:
    data=up.getvalue()
    pages=find_portfolio_pages(data)
    st.write('Páginas detectadas como carteira:', ', '.join(str(x+1) for x in pages) if pages else 'nenhuma')
    if not pages:
        st.error('Não encontrei “CARTEIRA DE INVESTIMENTOS”.'); st.stop()
    nat=native_lines(data,pages)
    st.subheader('Leitura nativa — diagnóstico')
    st.dataframe(nat, use_container_width=True)

    if st.button('Rodar GraniteDocling (CPU)', type='primary'):
        before=mb(); t0=time.perf_counter()
        try:
            subset=make_subset(data,pages)
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                f.write(subset); path=f.name
            with st.spinner('Carregando GraniteDocling e interpretando somente as páginas da carteira...'):
                conv=load_docling()
                loaded=mb()
                result=conv.convert(path)
                after=mb()
            elapsed=time.perf_counter()-t0
            st.success('GraniteDocling executado.')
            c1,c2,c3=st.columns(3)
            c1.metric('Tempo total',f'{elapsed:.1f} s')
            c2.metric('RAM após carga',f'{loaded:.0f} MB')
            c3.metric('RAM após conversão',f'{after:.0f} MB')
            md=result.document.export_to_markdown()
            st.subheader('Saída visual estruturada (Markdown)')
            st.code(md, language='markdown')
            st.download_button('Baixar saída GraniteDocling', md, file_name='granite_docling_saida.md')
            st.info('Critério do laboratório: conferir CNPJ, fundo, valor e % e se o total da carteira fecha com o DAIR.')
        except Exception as e:
            st.error('O GraniteDocling não conseguiu executar neste ambiente.')
            st.exception(e)
        finally:
            try: os.unlink(path)
            except Exception: pass
