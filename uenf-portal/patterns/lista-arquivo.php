<?php
/**
 * Title: Listagem de arquivo
 * Slug: uenf/lista-arquivo
 * Categories: uenf, posts
 * Inserter: no
 * Description: Grade de posts da consulta atual (categorias, tags, autores, datas), com paginação.
 *
 * @package uenf-portal
 */

?>
<!-- wp:query {"queryId":<?php echo (int) UENF_PORTAL_CONSULTA_PRINCIPAL; ?>,"query":{"perPage":9,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":true},"className":"uenf-grade-posts"} -->
<div class="wp-block-query uenf-grade-posts"><!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
<?php echo uenf_portal_cartao_post( 18, 2 ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>

<!-- /wp:post-template -->

<?php echo uenf_portal_paginacao(); // phpcs:ignore ?>


<!-- wp:query-no-results -->
<!-- wp:paragraph -->
<p>Nenhuma publicação encontrada.</p>
<!-- /wp:paragraph -->
<!-- /wp:query-no-results --></div>
<!-- /wp:query -->
