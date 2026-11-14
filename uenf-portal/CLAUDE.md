# Portal UENF — guia para agentes

Reconstrução de `uenf.br/portal` sem Elementor Pro, com Gutenberg e recursos nativos do WordPress.
Este diretório é independente do SAPIENS (o resto do repositório).

## Decisões já tomadas (não reabrir)

1. **Sem construtores de página.** Só blocos, padrões, modelos e `theme.json`. Sem jQuery, sem build.
2. **Tema base: UENF STI Theme** (`uenf_sti_theme`, o mesmo de `uenf.br/cct`; fonte em
   `git.uenf.br/web/uenf_sti_theme`). O portal deve rodar sobre ele (tema-filho ou padrões),
   reaproveitando cabeçalho, menu lateral, busca, painel de atalhos e rodapé do tema base.
   O `uenf-portal/` atual é um tema de blocos independente: é a referência funcional e visual
   a ser portada, não o destino final.
3. **Referência visual: modelo da Pró-Reitoria de Graduação.** Abertura azul-marinho com busca e
   atalhos, cartões de acesso rápido, rótulo de seção com traço dourado, notícia em destaque + lista
   com filtros por categoria, linhas de edital com data e selo de situação, cartões escuros de
   programas, faixa de chamada ("Já é estudante?"), grade de documentos, rodapé escuro em colunas.
4. **Manter todas as funcionalidades do portal atual** (lista em `README.md`, tabela "O que substitui o quê").

## O que se sabe do tema base (só pelos arquivos públicos)

- Tema clássico em PHP (`header.php`, `front-page.php`, `page.php`, `single.php`) com `theme.json` v2,
  `inc/component-engine/`, componentes `menu-sti-uenf`, `search-uenf`, `shortcut-panel`, testes PHPUnit.
- `theme.json`: conteúdo 1200px / largo 1400px; paleta `primaria #1d3771`, `secundaria #2c5aa0`,
  `texto #333`, `acento #0693e3`, `destaque #ff6600`, `fundo-claro #f8f9fa`, `fundo-escuro #212529`;
  tamanhos `pequeno … gigante` (14–48px); espaçamentos `mini … gigante` (4–64px).
- CSS: variáveis `--bs-uenf-blue`, `--primary-color`, `--heading-color #26557d`; fonte Ubuntu.
- Já traz padrões próprios (FAQ em abas/sanfona, tabela de preços) em `css/patterns.css` e `js/patterns.js`.
- **Ainda não temos o código-fonte.** Antes de portar, leia o tema real; não presuma ganchos,
  áreas de widget ou modelos de página.

## Convenções

- Tudo em pt-BR: nomes de funções (`uenf_portal_*`), classes CSS (`uenf-*`), estilos de bloco, textos.
- Marcação de bloco precisa abrir sem aviso de "conteúdo inválido" no editor.
- Categorias são localizadas por slug (`noticias`, `editais`), nunca por ID.
- CSS em `assets/css/tema.css` (também carregado no editor); cores e tamanhos vêm dos presets do `theme.json`.
- JS sem dependências em `assets/js/tema.js`; respeitar `prefers-reduced-motion`.
- Saída PHP sempre escapada (`esc_html`, `esc_url`, `esc_attr`).

## Verificação (obrigatória antes de concluir qualquer mudança)

```bash
for f in $(git ls-files 'uenf-portal/*.php'); do php -l "$f"; done
# com um WordPress de teste no ar e o tema ativo:
WP_USER=... WP_PASS=... node uenf-portal/tests/validar-blocos.js http://127.0.0.1:8080
WP_USER=... node uenf-portal/tests/funcional.js http://127.0.0.1:8080
```

Site de teste: WordPress + plugin SQLite Database Integration + `php -S 127.0.0.1:8080`, com posts
importados de `https://uenf.br/portal/wp-json/wp/v2/posts`. Após criar ou renomear um arquivo em
`patterns/`, limpe o cache de padrões (`wp_get_theme()->delete_pattern_cache()`).

## Time de agentes (`.claude/agents/`)

| Agente | Papel | Edita? |
|---|---|---|
| `wp-theme-architect` | Arquitetura sobre o UENF STI Theme, `theme.json`, hierarquia de modelos, PHP | sim |
| `wp-block-developer` | Padrões, marcação de blocos, Loop de consulta, estilos de bloco, JS | sim |
| `ux-ui-designer` | Sistema visual a partir do modelo da Graduação, layout responsivo, CSS | sim |
| `wp-migration-specialist` | Inventário do site atual, Elementor → blocos, URLs, plugins a aposentar | sim |
| `ux-accessibility-auditor` | WCAG 2.2 AA / eMAG, teclado, contraste, leitor de tela | não |
| `wp-security-performance-reviewer` | Segurança, LGPD e desempenho do tema | não |
| `wp-qa-tester` | Testes de navegador, validação no editor, regressão visual | só `tests/` |

Fluxo: `ux-ui-designer` define → `wp-theme-architect` e `wp-block-developer` implementam →
`wp-qa-tester` verifica → os dois revisores auditam → correções voltam a quem implementou.
