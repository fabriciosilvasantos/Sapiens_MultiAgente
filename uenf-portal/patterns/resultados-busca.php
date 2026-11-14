<?php
/**
 * Title: Resultados da busca
 * Slug: uenf/resultados-busca
 * Categories: uenf, posts
 * Inserter: no
 * Description: Lista de resultados (título e resumo) com paginação.
 *
 * @package uenf-portal
 */

?>
<!-- wp:query {"queryId":<?php echo (int) UENF_PORTAL_CONSULTA_PRINCIPAL; ?>,"query":{"perPage":9,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":true},"className":"uenf-resultados"} -->
<div class="wp-block-query uenf-resultados"><!-- wp:post-template -->
<!-- wp:group {"className":"uenf-resultado","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-resultado"><!-- wp:post-title {"level":2,"isLink":true} /-->

<!-- wp:post-excerpt {"excerptLength":40} /--></div>
<!-- /wp:group -->
<!-- /wp:post-template -->

<?php echo uenf_portal_paginacao(); // phpcs:ignore ?>


<!-- wp:query-no-results -->
<!-- wp:paragraph -->
<p>Nenhum resultado encontrado. Tente outros termos.</p>
<!-- /wp:paragraph -->
<!-- /wp:query-no-results --></div>
<!-- /wp:query -->
