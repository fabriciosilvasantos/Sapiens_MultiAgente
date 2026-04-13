# Análise de Interface e UX: Foco Mobile First

Esta análise avalia a interface atual do SAPIENS sob a ótica do design **Mobile First**, identificando pontos de atrito para usuários em dispositivos móveis e sugerindo melhorias concretas.

## 📱 Diagnóstico Atual

Embora o uso do Bootstrap 5 garanta uma responsividade técnica (os elementos se ajustam à tela), a **experiência de uso** em mobile apresenta desafios:

1.  **Navegação por Abas (`resultados.html`)**:
    *   **Problema**: O uso de `nav-pills nav-fill` com 5 itens (Resumo, Descritiva, Diagnóstica, Preditiva, Prescritiva) faz com que, em telas pequenas, os botões se empilhem verticalmente. Isso empurra o conteúdo principal para baixo, obrigando o usuário a rolar a tela antes mesmo de ver o resultado.
    *   **Impacto**: Perda de contexto e frustração na navegação.

2.  **Área de Upload (`analise.html`)**:
    *   **Problema**: A área de "Drag & Drop" possui `padding: 40px`. Em mobile, "arrastar arquivos" não é natural. O espaço vertical é desperdiçado com uma instrução pouco útil para toque.
    *   **Impacto**: O formulário fica desnecessariamente longo.

3.  **Tabelas de Dados**:
    *   **Problema**: Tabelas com muitas colunas (comuns em análises descritivas) exigem rolagem horizontal (`table-responsive`), o que é uma experiência pobre em mobile.
    *   **Impacto**: Dificuldade de leitura e comparação de dados.

4.  **Feedback de Progresso (`progresso.html`)**:
    *   **Problema**: A lista de etapas é extensa verticalmente. Em mobile, o usuário pode não ver a barra de progresso e a etapa atual simultaneamente sem rolar.

## 🚀 Sugestões de Melhoria (Mobile First)

### 1. Transformação da Navegação (Resultados)
Substituir as abas empilhadas por um componente mais eficiente em mobile.

*   **Solução A (Offcanvas/Menu)**: Um botão fixo "Seções do Relatório" que abre um menu lateral ou inferior (bottom sheet) para trocar de seção.
*   **Solução B (Scroll Horizontal)**: Manter as abas em uma única linha com rolagem horizontal (`flex-nowrap` + `overflow-auto`), estilo "Stories" ou menus de apps nativos (ex: YouTube, Instagram).
    *   *Recomendação*: **Scroll Horizontal** é mais fluido para descoberta de conteúdo.

### 2. Otimização do Upload
Adaptar a interface de upload para o contexto de toque.

*   **Alteração**: Detectar mobile (via CSS media query) e:
    *   Reduzir o padding da área de upload.
    *   Ocultar o texto/ícone de "Arraste e solte".
    *   Transformar o botão "Selecionar Arquivos" em um botão de largura total (`btn-block`), grande e fácil de tocar (thumb-friendly).
    *   Permitir uso da câmera diretamente (atributo `capture` no input) para digitalizar documentos físicos.

### 3. Cards vs. Tabelas
Para a Análise Descritiva:
*   **Alteração**: Em telas menores (`< 768px`), transformar cada linha da tabela em um **Card**.
    *   Ex: Em vez de uma linha com "Média | Mediana | Desvio", criar um card para cada variável com esses dados listados verticalmente.

### 4. Bottom Navigation (App-like Feel)
Considerar mover a navegação principal (Início, Análise, Sobre) do topo (Hambúrguer) para uma **Barra de Navegação Inferior** fixa.
*   **Benefício**: Facilita o uso com uma mão (zona do polegar).
*   **Implementação**: Uma `navbar fixed-bottom` visível apenas em mobile.

### 5. Melhorias Visuais e de Toque
*   **Tamanho de Toque**: Garantir que todos os botões e links tenham área de toque mínima de 44x44px.
*   **Inputs**: Aumentar o tamanho da fonte dos inputs para 16px para evitar que o iOS dê zoom automático ao focar.
*   **Sticky Actions**: Manter o botão de ação principal ("Iniciar Análise" ou "Baixar Relatório") fixo na parte inferior da tela (sticky footer) para que esteja sempre acessível.

## 🎨 Exemplo de Código (CSS Sugerido)

```css
/* Melhoria para Abas com Scroll Horizontal */
@media (max-width: 768px) {
    .nav-pills {
        flex-wrap: nowrap;
        overflow-x: auto;
        white-space: nowrap;
        padding-bottom: 5px; /* Espaço para scrollbar invisível */
        -webkit-overflow-scrolling: touch; /* Scroll suave no iOS */
    }
    
    .nav-pills .nav-link {
        flex: 0 0 auto; /* Não encolher */
        margin-right: 10px;
    }

    /* Upload Area Compacta */
    .file-upload-area {
        padding: 20px !important;
    }
    
    .file-upload-area i.fa-3x {
        font-size: 1.5em; /* Ícone menor */
    }
}
```
