<?php
/**
 * Title: Ouvidoria e Transparência
 * Slug: uenf/canais
 * Categories: uenf-secoes
 * Description: Selos com link para a OuvERJ e para o portal de Transparência da UENF.
 *
 * @package uenf-portal
 */

?>
<!-- wp:group {"align":"full","className":"uenf-canais","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-canais"><!-- wp:group {"layout":{"type":"flex","flexWrap":"wrap","justifyContent":"center"}} -->
<div class="wp-block-group"><!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"uenf-canal"} -->
<figure class="wp-block-image size-full uenf-canal"><a href="https://www.rj.gov.br/ouverj"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/ouverj.png' ) ); ?>" alt="OuvERJ — Ouvidoria do Estado do Rio de Janeiro"/></a></figure>
<!-- /wp:image -->

<!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"uenf-canal"} -->
<figure class="wp-block-image size-full uenf-canal"><a href="https://uenf.br/reitoria/transparencia"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/transparencia-uenf.jpg' ) ); ?>" alt="Transparência UENF"/></a></figure>
<!-- /wp:image --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
