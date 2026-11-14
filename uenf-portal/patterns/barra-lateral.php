<?php
/**
 * Title: Barra lateral — Notícias e Editais
 * Slug: uenf/barra-lateral
 * Categories: uenf
 * Description: Últimas três notícias e últimos três editais, com botões para as listagens.
 *
 * @package uenf-portal
 */

$uenf_blocos = array(
	array( 'Notícias', 'noticias', 31, 'Mais notícias' ),
	array( 'Editais', 'editais', 32, 'Mais editais' ),
);
foreach ( $uenf_blocos as $uenf_b ) :
	?>
<!-- wp:group {"className":"is-style-cartao uenf-lateral","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao uenf-lateral"><!-- wp:heading {"className":"is-style-rotulo"} -->
<h2 class="wp-block-heading is-style-rotulo"><?php echo esc_html( $uenf_b[0] ); ?></h2>
<!-- /wp:heading -->

<!-- wp:query {"queryId":<?php echo (int) $uenf_b[2]; ?>,"query":{"perPage":3,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false<?php echo uenf_portal_tax_query( $uenf_b[1] ); // phpcs:ignore ?>},"className":"uenf-lateral__lista"} -->
<div class="wp-block-query uenf-lateral__lista"><!-- wp:post-template -->
<!-- wp:post-title {"level":3,"isLink":true} /-->

<!-- wp:post-excerpt {"excerptLength":14} /-->
<!-- /wp:post-template --></div>
<!-- /wp:query -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button {"className":"is-style-seta"} -->
<div class="wp-block-button is-style-seta"><a class="wp-block-button__link wp-element-button" href="<?php echo esc_url( home_url( '/' . $uenf_b[1] . '/' ) ); ?>"><?php echo esc_html( $uenf_b[3] ); ?></a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group -->

	<?php
endforeach;
