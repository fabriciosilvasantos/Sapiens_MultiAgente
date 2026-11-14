<?php
/**
 * Compatibilidade com o conteúdo do portal anterior (OceanWP + Elementor).
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

/**
 * Páginas que usavam modelos do Elementor/Essential Blocks passam a usar os
 * modelos equivalentes do tema, sem precisar editar página por página.
 */
function uenf_portal_modelos_legados( array $hierarquia ): array {
	$mapa = array(
		'elementor_header_footer'                 => 'pagina-livre',
		'elementor_canvas'                        => 'pagina-livre',
		'elementor_theme'                         => 'page',
		'essential-blocks-fullwidth-template.php' => 'pagina-livre',
		'essential-blocks-blank-template.php'     => 'pagina-livre',
	);

	foreach ( $hierarquia as $i => $modelo ) {
		if ( isset( $mapa[ $modelo ] ) ) {
			$hierarquia[ $i ] = $mapa[ $modelo ];
		}
	}
	return $hierarquia;
}
add_filter( 'page_template_hierarchy', 'uenf_portal_modelos_legados' );
add_filter( 'single_template_hierarchy', 'uenf_portal_modelos_legados' );
add_filter( 'singular_template_hierarchy', 'uenf_portal_modelos_legados' );
