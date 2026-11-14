<?php
/**
 * Imagem de destaque de reserva.
 *
 * As notícias do portal raramente têm imagem destacada definida. Quando o bloco
 * "Imagem destacada do post", em uma listagem (cartões, destaques), não tem
 * o que mostrar, usa-se a primeira imagem do conteúdo, de modo que cartões e
 * destaques continuem ilustrados. Na página do próprio post nada muda, para
 * não repetir a imagem que já aparece no texto.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

add_filter(
	'render_block_core/post-featured-image',
	static function ( string $html, array $bloco, WP_Block $instancia ): string {
		if ( '' !== trim( $html ) ) {
			return $html;
		}

		$post_id = (int) ( $instancia->context['postId'] ?? 0 );
		if ( is_singular() && get_queried_object_id() === $post_id ) {
			return $html;
		}
		$post    = $post_id ? get_post( $post_id ) : null;
		if ( ! $post ) {
			return $html;
		}

		$tags = new WP_HTML_Tag_Processor( $post->post_content );
		if ( ! $tags->next_tag( 'img' ) || ! $tags->get_attribute( 'src' ) ) {
			return $html;
		}

		$imagem = sprintf(
			'<img src="%s" alt="%s" loading="lazy" decoding="async" />',
			esc_url( $tags->get_attribute( 'src' ) ),
			esc_attr( (string) $tags->get_attribute( 'alt' ) )
		);

		if ( ! empty( $bloco['attrs']['isLink'] ) ) {
			$imagem = sprintf( '<a href="%s" tabindex="-1" aria-hidden="true">%s</a>', esc_url( get_permalink( $post ) ), $imagem );
		}

		$classe = 'wp-block-post-featured-image uenf-imagem-do-conteudo';
		if ( ! empty( $bloco['attrs']['className'] ) ) {
			$classe .= ' ' . $bloco['attrs']['className'];
		}
		return '<figure class="' . esc_attr( $classe ) . '">' . $imagem . '</figure>';
	},
	10,
	3
);
