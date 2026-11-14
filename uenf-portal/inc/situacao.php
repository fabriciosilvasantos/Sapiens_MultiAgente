<?php
/**
 * Selo de situação dos editais (Aberto, Resultado, Em breve…).
 *
 * O bloco nativo "Tags do post" com o estilo "Selo de situação" mostra apenas
 * as tags que representam uma situação e as desenha como selo colorido.
 * Para marcar um edital, basta adicionar ao post uma das tags abaixo.
 * Posts sem nenhuma dessas tags não exibem selo.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

/**
 * Slugs de tag tratados como situação => variação de cor do selo.
 */
function uenf_portal_situacoes(): array {
	return (array) apply_filters(
		'uenf_portal_situacoes',
		array(
			'aberto'     => 'positivo',
			'abertas'    => 'positivo',
			'continuo'   => 'positivo',
			'em-breve'   => 'aviso',
			'retificado' => 'aviso',
			'resultado'  => 'neutro',
			'encerrado'  => 'neutro',
		)
	);
}

add_filter(
	'render_block_core/post-terms',
	static function ( string $html, array $bloco, WP_Block $instancia ): string {
		if ( ! str_contains( $bloco['attrs']['className'] ?? '', 'is-style-selo' ) ) {
			return $html;
		}

		$post_id = (int) ( $instancia->context['postId'] ?? 0 );
		$termos  = $post_id ? get_the_terms( $post_id, $bloco['attrs']['term'] ?? 'post_tag' ) : false;
		if ( ! $termos || is_wp_error( $termos ) ) {
			return '';
		}

		$situacoes = uenf_portal_situacoes();
		$selos     = '';
		foreach ( $termos as $termo ) {
			if ( isset( $situacoes[ $termo->slug ] ) ) {
				$selos .= sprintf(
					'<a class="uenf-selo uenf-selo--%s" href="%s" rel="tag">%s</a>',
					esc_attr( $situacoes[ $termo->slug ] ),
					esc_url( get_term_link( $termo ) ),
					esc_html( $termo->name )
				);
			}
		}

		return $selos ? '<div class="wp-block-post-terms is-style-selo">' . $selos . '</div>' : '';
	},
	10,
	3
);
