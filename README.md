# Laboratório isolado DAIR × GraniteDocling

Mini-app exclusivamente para verificar se o GraniteDocling (VLM visual gratuito) consegue rodar em CPU no Streamlit Community Cloud e ler as páginas `CARTEIRA DE INVESTIMENTOS` de um DAIR.

## O que ele faz
1. Recebe um DAIR PDF por upload.
2. Usa PyMuPDF apenas para localizar páginas que contêm `CARTEIRA DE INVESTIMENTOS` e mostrar um diagnóstico nativo.
3. Cria em memória um PDF somente com essas páginas.
4. Ao clicar no botão, executa `VlmPipelineOptions()` do Docling, cujo VLM padrão é GraniteDocling.
5. Exibe a saída Markdown, tempo e RAM do processo.
6. O arquivo temporário é apagado ao final.

## Deploy isolado no Streamlit Community Cloud
Crie um repositório separado contendo somente `app.py`, `requirements.txt` e este README. Faça o deploy apontando para `app.py`.

Não reutilize o repositório do Copiloto neste teste.

## Critério de aprovação
Para o DAIR de teste, comparar a saída GraniteDocling com a carteira conhecida, verificando CNPJ, nome, valor, percentual e fechamento do total. Além da precisão, registrar tempo e RAM. Se houver erro de instalação, OOM ou tempo impraticável, o VLM não é aprovado para rodar dentro do Streamlit e deve ser testado como serviço externo.
