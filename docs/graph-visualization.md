# Visualizando o Grafo do Foam

Este documento descreve como gerar e publicar o grafo de notas do Foam criado no repositório.

## O que foi adicionado

- `tools/generate_graph.py`: script que varre os arquivos `.md`, extrai wikilinks (`[[Note]]`) e links Markdown para construir `web/data/graph.json`.
- `web/index.html`: visualizador interativo que carrega `web/data/graph.json` e renderiza o grafo com `vis-network`.
- `.github/workflows/publish-graph.yml`: GitHub Action que executa o gerador e publica `web/` no `gh-pages` (usando `peaceiris/actions-gh-pages`).

## Como gerar localmente

1. Abra um terminal na raiz do repositório:

```powershell
cd 'C:\Users\Lucas\Documents\FoamStd\foam-template'
python .\tools\generate_graph.py
```

Isto cria/atualiza `web/data/graph.json`.

2. Sirva a pasta `web` localmente e abra `index.html` no navegador:

```powershell
cd .\web
python -m http.server 8000
# depois abra http://localhost:8000
```

A página mostrará o grafo. Dê duplo-clique em um nó para abrir o arquivo associado. Quando publicada via GitHub Pages a página tentará abrir o conteúdo raw no GitHub.

## Publicação automática (GitHub Actions)

O workflow `.github/workflows/publish-graph.yml` roda em cada push na `main`:

- Executa `python tools/generate_graph.py` para atualizar `web/data/graph.json`.
- Publica a pasta `web/` no branch `gh-pages` (site disponível em `https://<owner>.github.io/<repo>/`).

Nota: verifique as configurações de GitHub Pages se usar domínio customizado.

## Melhorias e limitações

- O gerador faz heurísticas simples para resolver wikilinks: combina com filenames, com o `title` do frontmatter e com `aliases` (quando presentes). Pode precisar de ajustes para casos complexos (slugs, espaços, aliases múltiplos).
- `web/index.html` tenta gerar a URL raw do GitHub quando hospedado como GitHub Pages; se isso não funcionar, abre o caminho relativo.
- O script evita atravessar pastas ocultas (ex.: `.git`, `.venv`).

## Próximos passos recomendados

- Se você usa aliases ou títulos complexos, posso melhorar a normalização (remover acentos, mapear espaços/underscores, etc.).
- Incluir no workflow uma etapa para instalar dependências adicionais caso você queira usar Graphviz/SVG em vez de JSON + vis.

---

Se quiser, eu adiciono um pequeno README/Badge no `readme.md` apontando para a página do grafo gerado.
