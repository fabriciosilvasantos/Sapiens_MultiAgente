<?php
/**
 * UENF Portal — tema de blocos.
 *
 * Tudo o que é conteúdo ou layout vive em modelos, partes de modelo e padrões
 * editáveis no Editor do Site. Este arquivo só registra o que o editor de
 * blocos não oferece sozinho (estilos de bloco, consultas relacionadas,
 * compartilhamento, barra de acessibilidade e compatibilidade com o site antigo).
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

define( 'UENF_PORTAL_VERSAO', wp_get_theme( 'uenf-portal' )->get( 'Version' ) ?: '1.0.0' );

/** ID de consulta fixo da listagem principal (Notícias/Editais), usado na paginação. */
define( 'UENF_PORTAL_CONSULTA_PRINCIPAL', 1 );

require get_theme_file_path( 'inc/menus.php' );
require get_theme_file_path( 'inc/trechos.php' );
require get_theme_file_path( 'inc/blocos.php' );
require get_theme_file_path( 'inc/imagem-destaque.php' );
require get_theme_file_path( 'inc/consultas.php' );
require get_theme_file_path( 'inc/compartilhar.php' );
require get_theme_file_path( 'inc/situacao.php' );
require get_theme_file_path( 'inc/acessibilidade.php' );
require get_theme_file_path( 'inc/compatibilidade.php' );

add_action(
	'after_setup_theme',
	static function () {
		add_editor_style( 'assets/css/tema.css' );
		add_theme_support( 'responsive-embeds' );
		add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	}
);

add_action(
	'wp_enqueue_scripts',
	static function () {
		wp_enqueue_style( 'uenf-portal', get_theme_file_uri( 'assets/css/tema.css' ), array(), UENF_PORTAL_VERSAO );
		wp_enqueue_script(
			'uenf-portal',
			get_theme_file_uri( 'assets/js/tema.js' ),
			array(),
			UENF_PORTAL_VERSAO,
			array( 'strategy' => 'defer', 'in_footer' => true )
		);
	}
);

/** Resumos terminam em reticências, como no portal anterior. */
add_filter( 'excerpt_more', static fn () => '…' );
