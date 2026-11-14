<?php
/**
 * Botões de compartilhamento com o bloco nativo "Ícones sociais".
 *
 * Um bloco Ícones sociais com o estilo "Compartilhar esta página" tem os links
 * trocados pelo endereço de compartilhamento da página atual em cada rede.
 * Basta adicionar o ícone da rede (com qualquer URL, ex.: "#") no editor.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

add_filter(
	'render_block_core/social-links',
	static function ( string $html, array $bloco ): string {
		if ( ! str_contains( $bloco['attrs']['className'] ?? '', 'is-style-compartilhar' ) ) {
			return $html;
		}

		$url    = rawurlencode( (string) get_permalink() );
		$titulo = rawurlencode( wp_strip_all_tags( get_the_title() ) );

		$destinos = array(
			'facebook' => 'https://www.facebook.com/sharer/sharer.php?u=' . $url,
			'linkedin' => 'https://www.linkedin.com/sharing/share-offsite/?url=' . $url,
			'whatsapp' => 'https://api.whatsapp.com/send?text=' . $titulo . '%20' . $url,
			'x'        => 'https://x.com/intent/post?url=' . $url . '&text=' . $titulo,
			'twitter'  => 'https://x.com/intent/post?url=' . $url . '&text=' . $titulo,
			'telegram' => 'https://t.me/share/url?url=' . $url . '&text=' . $titulo,
			'bluesky'  => 'https://bsky.app/intent/compose?text=' . $titulo . '%20' . $url,
			'threads'  => 'https://www.threads.net/intent/post?text=' . $titulo . '%20' . $url,
			'mail'     => 'mailto:?subject=' . $titulo . '&body=' . $url,
		);

		$tags    = new WP_HTML_Tag_Processor( $html );
		$servico = '';
		while ( $tags->next_tag() ) {
			if ( 'LI' === $tags->get_tag() ) {
				$servico = '';
				foreach ( $tags->class_list() as $classe ) {
					if ( str_starts_with( $classe, 'wp-social-link-' ) ) {
						$servico = substr( $classe, strlen( 'wp-social-link-' ) );
					}
				}
			} elseif ( 'A' === $tags->get_tag() && isset( $destinos[ $servico ] ) ) {
				$tags->set_attribute( 'href', $destinos[ $servico ] );
				if ( 'mail' !== $servico ) {
					$tags->set_attribute( 'target', '_blank' );
					$tags->set_attribute( 'rel', 'noopener noreferrer nofollow' );
				}
			}
		}
		return $tags->get_updated_html();
	},
	10,
	2
);
