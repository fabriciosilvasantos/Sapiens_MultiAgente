<?php
/**
 * Estilos de bloco e categorias de padrões.
 *
 * Os estilos aparecem no painel "Estilos" do editor; o visual está em
 * assets/css/tema.css e o comportamento (contador, banners) em assets/js/tema.js.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

add_action(
	'init',
	static function () {
		$estilos = array(
			'core/group'        => array(
				'cartao'          => 'Cartão',
				'cartao-link'     => 'Cartão clicável',
				'banner-rotativo' => 'Banners rotativos',
				'linha-edital'    => 'Linha de listagem',
				'cartao-escuro'   => 'Cartão escuro',
				'faixa-chamada'   => 'Faixa de chamada',
			),
			'core/paragraph'    => array(
				'rotulo'   => 'Rótulo de seção',
				'contador' => 'Contador animado',
			),
			'core/social-links' => array(
				'compartilhar' => 'Compartilhar esta página',
			),
			'core/buttons'      => array(
				'filtros' => 'Filtros (abas)',
			),
			'core/button'       => array(
				'seta'     => 'Link com seta',
				'contorno' => 'Contorno claro',
				'claro'    => 'Claro (sobre fundo escuro)',
				'bloco'    => 'Largura total, com contorno',
			),
			'core/list'         => array(
				'links'  => 'Lista de links',
				'chips'  => 'Chips (cursos)',
				'passos' => 'Passos numerados',
				'opcoes' => 'Opções com descrição',
			),
			'core/post-terms'   => array(
				'etiqueta' => 'Etiqueta',
				'selo'     => 'Selo de situação',
			),
		);

		foreach ( $estilos as $bloco => $lista ) {
			foreach ( $lista as $nome => $rotulo ) {
				register_block_style( $bloco, array( 'name' => $nome, 'label' => $rotulo ) );
			}
		}

		register_block_pattern_category( 'uenf', array( 'label' => 'UENF' ) );
		register_block_pattern_category( 'uenf-secoes', array( 'label' => 'UENF — Seções da página inicial' ) );
	}
);
