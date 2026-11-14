<?php
/**
 * Title: Leia também (posts relacionados)
 * Slug: uenf/relacionados
 * Categories: uenf, posts
 * Description: Quatro publicações das mesmas categorias do post atual.
 *
 * @package uenf-portal
 */

?>
<!-- wp:query {"queryId":41,"query":{"perPage":4,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false},"namespace":"uenf/relacionados","className":"uenf-relacionados"} -->
<div class="wp-block-query uenf-relacionados"><!-- wp:heading -->
<h2 class="wp-block-heading">Leia também</h2>
<!-- /wp:heading -->

<!-- wp:post-template {"layout":{"type":"grid","columnCount":4}} -->
<!-- wp:group {"className":"uenf-relacionado","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-relacionado"><!-- wp:post-featured-image {"isLink":true} /-->

<!-- wp:post-title {"level":3,"isLink":true} /--></div>
<!-- /wp:group -->
<!-- /wp:post-template --></div>
<!-- /wp:query -->
