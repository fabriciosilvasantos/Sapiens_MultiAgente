# UENF Portal — tema de blocos (Gutenberg)

Tema WordPress para o portal da UENF (`uenf.br/portal`) que substitui
**OceanWP + Elementor / Elementor Pro** por recursos nativos do WordPress:
modelos, partes de modelo, padrões e blocos do editor (Gutenberg). O visual segue
o modelo criado para a Pró-Reitoria de Graduação (abertura azul-marinho com busca,
cartões, rótulos com traço dourado, rodapé escuro).

Requisitos: WordPress 6.9+ (testado no 7.1) e PHP 8.0+. Não há etapa de build.

**Tema base.** O destino previsto é o UENF STI Theme (o mesmo de `uenf.br/cct`). Enquanto o
código dele não está disponível, este tema funciona sozinho. As seções são padrões FSE
independentes do cabeçalho e do rodapé, de modo que a troca do tema base exige portar apenas
`parts/header.html`, `parts/footer.html` e os presets de `theme.json`.

## Instalação

1. Copie a pasta `uenf-portal/` para `wp-content/themes/` (ou compacte-a em `.zip` e
   envie em **Aparência → Temas → Adicionar**).
2. Ative o tema. Faça isso primeiro em uma cópia de homologação do site.
3. Confira os itens de "Migração" abaixo e só então desative os plugins antigos.

## O que substitui o quê

| No site atual | No tema novo (nativo) |
|---|---|
| Cabeçalho e rodapé (Elementor Header & Footer) | Partes de modelo **Cabeçalho** e **Rodapé** |
| Menu principal + menu secundário (widgets de menu) | Bloco **Navegação** (menu suspenso no computador, sobreposto abaixo de 1024 px) |
| Botão de busca (HFE) | Bloco **Pesquisar** (cabeçalho, abertura da home, página de busca e 404) |
| Banner rotativo com versões desktop/celular (AdRotate) | Parte de modelo **Banners rotativos**: cada grupo é um banner; um é sorteado por visita |
| Grades de Notícias e Editais (Loop Grid do Elementor Pro) | Bloco **Loop de consulta** (9 notícias e 9 editais na home; páginas `/noticias/` e `/editais/` com paginação) |
| Contadores "UENF em números" (widget Counter) | Parágrafo com o estilo de bloco **Contador animado** |
| Modelo de post/página com barra lateral (Theme Builder) | Modelos **Posts individuais** e **Páginas** + parte **Barra lateral** |
| Botões de compartilhar (Share Buttons) | Bloco **Ícones sociais** com o estilo **Compartilhar esta página** |
| "Leia também" (Contextual Related Posts) | Padrão **Leia também** (Loop de consulta filtrado pelas categorias do post) |
| Trilha de navegação (Breadcrumbs do Elementor/Yoast) | Bloco nativo **Breadcrumbs** |
| Resultados de busca e página 404 (Theme Builder) | Modelos **Resultados da pesquisa** e **404** |
| Barra de acessibilidade (One Click Accessibility) | Barra do próprio tema, com as mesmas 9 opções |
| Fontes do Google carregadas pelo Elementor | Fonte Inter servida pelo próprio site (sem chamadas externas) |

## Modelos do Design System da Graduação

Além das funções do portal atual, a página inicial adota os modelos do Design System da
Pró-Reitoria de Graduação. Todos são padrões de blocos (categoria "UENF — Seções da página
inicial") e podem ser usados em qualquer página:

| Modelo | Padrão | Como editar |
|---|---|---|
| Abertura com busca e atalhos | `uenf/hero` | Texto, botões de atalho |
| Cartões de acesso rápido | `uenf/acesso-rapido` | Título, texto e link de cada cartão |
| Notícia em destaque + lista, com filtros | `uenf/noticias` | Filtros são botões com o estilo **Filtros (abas)**; cada um leva à listagem da categoria |
| Cursos em chips por campus | `uenf/cursos` | Lista com o estilo **Chips (cursos)**; a classe `uenf-licenciatura` no item muda a cor do ponto |
| Cartões escuros (Pró-Reitorias) | `uenf/pro-reitorias` | Grupo com o estilo **Cartão escuro** |
| Linhas de edital com data e selo | `uenf/editais` | O selo vem das tags do post: `aberto`, `resultado`, `em-breve`, `encerrado`, `retificado`, `continuo` |
| Formas de ingresso | `uenf/ingresso` | Listas com os estilos **Passos numerados** e **Opções com descrição** |
| Faixa de chamada | `uenf/chamada-estudante` | Grupo com o estilo **Faixa de chamada** |
| Grade de documentos | `uenf/documentos` | Cartões clicáveis horizontais |

Os filtros são links para as listagens (funcionam sem JavaScript); não filtram a lista na
própria página. Categorias inexistentes no site são omitidas automaticamente.

Também foram preservados: todos os itens dos dois menus, links das redes sociais,
cartões das Pró-Reitorias, faixa do concurso, selos OuvERJ/Transparência,
endereços e contatos do rodapé, arquivos por categoria, autor e data.

## Como editar (sem código)

Tudo fica em **Aparência → Editor**:

- **Página inicial** — modelo *Página inicial*. Cada seção é um padrão da categoria
  "UENF — Seções da página inicial" e pode ser movida, duplicada ou removida.
- **Menus** — *Navegação*. Os menus vêm preenchidos com os itens atuais.
- **Banners** — *Padrões → Partes de modelo → Banners rotativos*. Para um novo banner,
  duplique um grupo "banner" e troque as duas imagens (computador e celular) e o link.
  Com um único grupo o banner fica fixo.
- **Números** — edite o texto do parágrafo; a animação usa o número digitado
  (aceita prefixo/sufixo, ex.: `+ 7.500` ou `95%`).
- **Cores, tipografia e espaçamentos** — *Estilos* (definidos em `theme.json`).

Estilos de bloco disponíveis no painel "Estilos" do editor: Cartão, Cartão clicável,
Cartão escuro, Faixa de chamada, Linha de listagem e Banners rotativos (Grupo); Rótulo de
seção e Contador animado (Parágrafo); Filtros (Botões); Link com seta, Contorno claro, Claro
e Largura total (Botão); Lista de links, Chips, Passos numerados e Opções com descrição
(Lista); Etiqueta e Selo de situação (Categorias/Tags); Compartilhar esta página (Ícones sociais).

## Migração do site atual

O conteúdo das páginas e notícias **já é feito em blocos** e não precisa ser refeito.
Levantamento feito em 14/11/2026 nas 60 páginas publicadas:

- **Feitas no Elementor:** apenas `Principal` (substituída pelo modelo de página
  inicial do tema) e `/portfolio/` (página de teste; refazer em blocos ou excluir).
- **Usam Essential Blocks** (plugin do Gutenberg, não depende do Elementor):
  `/semana-academica-2025/`, `/portfolio-agiuenf/`, `/espaco-da-ciencia-baleia-jubarte/`,
  `/sisu-2026-uenf/` e `/institucional/sobre-a-uenf/`. **Mantenha o plugin ativo**;
  trocar esses blocos pelos nativos pode ser feito depois, página a página.
- Páginas com os modelos antigos `elementor_header_footer`, `elementor_canvas` ou
  de largura total do Essential Blocks passam automaticamente a usar o modelo
  **Página livre** do tema (`inc/compatibilidade.php`).
- URLs antigas de paginação (`/noticias/2/`, `/editais/3/`) redirecionam (301) para a
  paginação nativa.
- As listagens localizam as categorias pelos slugs `noticias` e `editais`.

Depois de validar em homologação, podem ser desativados: Elementor, Elementor Pro,
Elementor Header & Footer Builder, Essential Addons for Elementor, Ocean Extra,
AdRotate, Contextual Related Posts e One Click Accessibility; e removido o tema OceanWP.
Continuam: Yoast SEO, Safe SVG, Essential Blocks e Timeline Block.

Pontos de atenção:

- As imagens dos banners e da faixa do concurso apontam para arquivos já existentes
  em `uenf.br/portal/wp-content/uploads/`.
- As faixas decorativas do topo das páginas internas (foto dos estudantes e arte da
  Rádio UENF) não foram mantidas; o link da Rádio continua na barra superior.
- Se o Contextual Related Posts continuar ativo, remova o padrão "Leia também" do
  modelo de post para não duplicar a seção.
- Notícias sem imagem destacada usam a primeira imagem do texto nos cartões
  (`inc/imagem-destaque.php`).

## Estrutura

```
theme.json            cores, tipografia (Inter), espaçamentos e estilos globais
templates/            página inicial, post, página, notícias, editais, arquivo, busca, 404,
                      largura total e página livre
parts/                cabeçalho, rodapé, banners, barra lateral e trilha
patterns/             seções da home, cabeçalho, rodapé, listagens e "Leia também"
inc/                  menus iniciais, estilos de bloco, consultas, compartilhamento,
                      acessibilidade e compatibilidade com o site antigo
assets/               CSS, JavaScript (sem dependências), fontes e imagens
tests/                validação dos blocos no editor e testes funcionais (Playwright)
CLAUDE.md             contexto e convenções para o time de agentes
```
