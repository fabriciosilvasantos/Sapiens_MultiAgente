<?php
/**
 * Apoio aos blocos "Loop de consulta" usados nos modelos.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

/**
 * ID de uma categoria a partir do slug (0 se não existir).
 *
 * Os padrões usam o slug para montar as consultas, de modo que o tema funciona
 * em qualquer instalação, independentemente dos IDs dos termos.
 */
function uenf_portal_categoria_id( string $slug ): int {
	$termo = get_category_by_slug( $slug );
	return $termo ? (int) $termo->term_id : 0;
}

/**
 * Trecho JSON de "taxQuery" para uma categoria, pronto para o atributo do bloco.
 */
function uenf_portal_tax_query( string $slug ): string {
	$id = uenf_portal_categoria_id( $slug );
	return $id ? ',"taxQuery":{"category":[' . $id . ']}' : '';
}

/**
 * "Leia também": um Loop de consulta com "namespace":"uenf/relacionados"
 * lista posts das mesmas categorias do post atual, excluindo ele próprio.
 * Substitui o plugin Contextual Related Posts.
 */
add_filter(
	'render_block_data',
	static function ( array $bloco ): array {
		if ( 'core/query' === ( $bloco['blockName'] ?? '' ) && 'uenf/relacionados' === ( $bloco['attrs']['namespace'] ?? '' ) ) {
			$GLOBALS['uenf_portal_relacionados'][ (int) ( $bloco['attrs']['queryId'] ?? 0 ) ] = true;
		}
		return $bloco;
	}
);

add_filter(
	'query_loop_block_query_vars',
	static function ( array $query, WP_Block $bloco ): array {
		$id_consulta = (int) ( $bloco->context['queryId'] ?? 0 );
		if ( empty( $GLOBALS['uenf_portal_relacionados'][ $id_consulta ] ) || ! is_singular() ) {
			return $query;
		}

		$post_id    = get_queried_object_id();
		$categorias = wp_get_post_categories( $post_id );

		$query['post__not_in']        = array( $post_id );
		$query['ignore_sticky_posts'] = true;
		if ( $categorias ) {
			$query['category__in'] = $categorias;
		}
		return $query;
	},
	10,
	2
);

/**
 * URLs antigas de paginação (/noticias/2/, /editais/3/) geradas pelo Elementor
 * passam a apontar para a paginação nativa do Loop de consulta.
 */
add_action(
	'template_redirect',
	static function () {
		$pagina = (int) trim( (string) get_query_var( 'page' ), '/' );
		if ( $pagina < 2 ) {
			return;
		}

		// O WordPress marca essas URLs como 404 (a página não tem <!--nextpage-->),
		// por isso a verificação é feita pelo objeto consultado, não por is_page().
		$objeto = get_queried_object();
		if ( $objeto instanceof WP_Post && 'page' === $objeto->post_type && in_array( $objeto->post_name, array( 'noticias', 'editais' ), true ) ) {
			$destino = add_query_arg(
				'query-' . UENF_PORTAL_CONSULTA_PRINCIPAL . '-page',
				$pagina,
				get_permalink( $objeto )
			);
			wp_safe_redirect( $destino, 301 );
			exit;
		}
	},
	1
);
