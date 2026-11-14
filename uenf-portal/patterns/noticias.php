<?php
/**
 * Title: Últimas notícias
 * Slug: uenf/noticias
 * Categories: uenf-secoes, posts
 * Description: Notícia em destaque, lista das mais recentes e grade de cartões (9 notícias, como no portal anterior).
 *
 * @package uenf-portal
 */

$uenf_tax = uenf_portal_tax_query( 'noticias' );
$uenf_q   = static fn ( int $id, int $por_pagina, int $desloc ) => '{"queryId":' . $id . ',"query":{"perPage":' . $por_pagina . ',"pages":0,"offset":' . $desloc . ',"postType":"post","order":"desc","orderBy":"date","inherit":false' . $uenf_tax . '}';
?>
<!-- wp:group {"align":"full","className":"uenf-secao","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-secao"><?php echo uenf_portal_cabecalho_secao( 'Notícias', 'Últimas notícias', 'Acompanhe as novidades, eventos e comunicados da UENF.', 'Todas as notícias', home_url( '/noticias/' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>

<!-- wp:columns {"className":"uenf-noticias__topo"} -->
<div class="wp-block-columns uenf-noticias__topo"><!-- wp:column {"width":"56%"} -->
<div class="wp-block-column" style="flex-basis:56%"><!-- wp:query <?php echo $uenf_q( 11, 1, 0 ); // phpcs:ignore ?>,"className":"uenf-destaque"} -->
<div class="wp-block-query uenf-destaque"><!-- wp:post-template -->
<!-- wp:group {"className":"is-style-cartao uenf-destaque__cartao","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao uenf-destaque__cartao"><!-- wp:group {"className":"uenf-destaque__midia","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-destaque__midia"><!-- wp:post-featured-image {"isLink":true} /-->

<!-- wp:paragraph {"className":"uenf-destaque__selo"} -->
<p class="uenf-destaque__selo">Destaque</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<!-- wp:group {"className":"uenf-destaque__corpo","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-destaque__corpo"><!-- wp:group {"className":"uenf-meta","layout":{"type":"flex","flexWrap":"wrap"}} -->
<div class="wp-block-group uenf-meta"><!-- wp:post-terms {"term":"category","className":"is-style-etiqueta"} /-->

<!-- wp:post-date {"format":"j \\d\\e F \\d\\e Y"} /--></div>
<!-- /wp:group -->

<!-- wp:post-title {"level":3,"isLink":true} /-->

<!-- wp:post-excerpt {"excerptLength":32} /-->

<!-- wp:read-more {"content":"Ler matéria completa","className":"uenf-link-seta"} /--></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
<!-- /wp:post-template --></div>
<!-- /wp:query --></div>
<!-- /wp:column -->

<!-- wp:column {"width":"44%"} -->
<div class="wp-block-column" style="flex-basis:44%"><!-- wp:query <?php echo $uenf_q( 12, 5, 1 ); // phpcs:ignore ?>,"className":"uenf-lista-recentes"} -->
<div class="wp-block-query uenf-lista-recentes"><!-- wp:post-template -->
<!-- wp:group {"className":"uenf-lista-recentes__item","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-lista-recentes__item"><!-- wp:post-terms {"term":"category","className":"is-style-etiqueta"} /-->

<!-- wp:post-title {"level":3,"isLink":true} /-->

<!-- wp:post-date {"format":"j \\d\\e F \\d\\e Y"} /--></div>
<!-- /wp:group -->
<!-- /wp:post-template --></div>
<!-- /wp:query --></div>
<!-- /wp:column --></div>
<!-- /wp:columns -->

<!-- wp:query <?php echo $uenf_q( 13, 3, 6 ); // phpcs:ignore ?>,"className":"uenf-grade-posts"} -->
<div class="wp-block-query uenf-grade-posts"><!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
<?php echo uenf_portal_cartao_post(); // phpcs:ignore ?>

<!-- /wp:post-template --></div>
<!-- /wp:query --></div>
<!-- /wp:group -->
