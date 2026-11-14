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

		// Nunca expor imagem de conteúdo não publicado ou protegido por senha.
		$post = $post_id ? get_post( $post_id ) : null;
		if ( ! $post || 'publish' !== $post->post_status || post_password_required( $post ) ) {
			return $html;
		}

		$tags = new WP_HTML_Tag_Processor( $post->post_content );
		if ( ! $tags->next_tag( 'img' ) ) {
			return $html;
		}

		// Imagem da biblioteca de mídia: usa um tamanho intermediário, com srcset e dimensões.
		$imagem = '';
		if ( preg_match( '/\bwp-image-(\d+)\b/', (string) $tags->get_attribute( 'class' ), $achado ) ) {
			$imagem = wp_get_attachment_image( (int) $achado[1], 'medium_large', false, array( 'loading' => 'lazy' ) );
		}

		if ( ! $imagem ) {
			$src = esc_url( (string) $tags->get_attribute( 'src' ) );
			if ( ! $src ) {
				return $html;
			}
			$imagem = sprintf(
				'<img src="%s" alt="%s" loading="lazy" decoding="async" />',
				$src,
				esc_attr( (string) $tags->get_attribute( 'alt' ) )
			);
		}

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

/**
 * Imagens estáticas dos padrões (bloco Imagem sem ID de mídia): acrescenta
 * largura/altura para as que vêm do tema, evitando salto de layout, e
 * carregamento tardio para todas, exceto o logotipo do cabeçalho. Com isso a
 * versão de banner oculta para o dispositivo (computador/celular) não é baixada.
 */
add_filter(
	'render_block_core/image',
	static function ( string $html, array $bloco ): string {
		if ( ! empty( $bloco['attrs']['id'] ) ) {
			return $html; // Imagens da biblioteca já são tratadas pelo WordPress.
		}

		$tags = new WP_HTML_Tag_Processor( $html );
		if ( ! $tags->next_tag( 'img' ) ) {
			return $html;
		}

		$src  = (string) $tags->get_attribute( 'src' );
		$base = get_theme_file_uri( 'assets/images/' );

		if ( str_starts_with( $src, $base ) && null === $tags->get_attribute( 'width' ) ) {
			static $tamanhos = array();
			$arquivo = get_theme_file_path( 'assets/images/' . basename( (string) wp_parse_url( $src, PHP_URL_PATH ) ) );
			if ( ! isset( $tamanhos[ $arquivo ] ) ) {
				$tamanhos[ $arquivo ] = is_readable( $arquivo ) ? wp_getimagesize( $arquivo ) : false;
			}
			if ( $tamanhos[ $arquivo ] ) {
				$tags->set_attribute( 'width', (string) $tamanhos[ $arquivo ][0] );
				$tags->set_attribute( 'height', (string) $tamanhos[ $arquivo ][1] );
			}
		}

		if ( null === $tags->get_attribute( 'loading' ) && ! str_contains( $bloco['attrs']['className'] ?? '', 'uenf-logo' ) ) {
			$tags->set_attribute( 'loading', 'lazy' );
			$tags->set_attribute( 'decoding', 'async' );
		}
		return $tags->get_updated_html();
	},
	10,
	2
);
