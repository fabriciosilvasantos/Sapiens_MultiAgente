<?php
/**
 * Trechos de marcação de blocos reutilizados pelos padrões do tema.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

/**
 * Cabeçalho de seção: rótulo, título, descrição e (opcional) link "ver todos".
 */
function uenf_portal_cabecalho_secao( string $rotulo, string $titulo, string $descricao = '', string $link_texto = '', string $link_url = '' ): string {
	$html  = '<!-- wp:group {"className":"uenf-secao__topo","layout":{"type":"flex","flexWrap":"wrap","justifyContent":"space-between","verticalAlignment":"bottom"}} -->' . "\n";
	$html .= '<div class="wp-block-group uenf-secao__topo"><!-- wp:group {"className":"uenf-secao__titulo","layout":{"type":"default"}} -->' . "\n";
	$html .= '<div class="wp-block-group uenf-secao__titulo"><!-- wp:paragraph {"className":"is-style-rotulo"} -->' . "\n";
	$html .= '<p class="is-style-rotulo">' . esc_html( $rotulo ) . '</p>' . "\n<!-- /wp:paragraph -->\n\n";
	$html .= "<!-- wp:heading -->\n" . '<h2 class="wp-block-heading">' . esc_html( $titulo ) . "</h2>\n<!-- /wp:heading -->";
	if ( $descricao ) {
		$html .= "\n\n" . '<!-- wp:paragraph {"className":"uenf-secao__descricao"} -->' . "\n" . '<p class="uenf-secao__descricao">' . esc_html( $descricao ) . "</p>\n<!-- /wp:paragraph -->";
	}
	$html .= "</div>\n<!-- /wp:group -->";
	if ( $link_texto ) {
		$html .= "\n\n<!-- wp:buttons -->\n" . '<div class="wp-block-buttons"><!-- wp:button {"className":"is-style-seta"} -->' . "\n";
		$html .= '<div class="wp-block-button is-style-seta"><a class="wp-block-button__link wp-element-button" href="' . esc_url( $link_url ) . '">' . esc_html( $link_texto ) . "</a></div>\n<!-- /wp:button --></div>\n<!-- /wp:buttons -->";
	}
	$html .= "</div>\n<!-- /wp:group -->\n";
	return $html;
}

/**
 * Cartão de post para grades (categoria, título, resumo e data).
 */
function uenf_portal_cartao_post( int $palavras = 18 ): string {
	return '<!-- wp:group {"className":"is-style-cartao uenf-cartao-post","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao uenf-cartao-post"><!-- wp:post-terms {"term":"category","className":"is-style-etiqueta"} /-->

<!-- wp:post-title {"level":3,"isLink":true} /-->

<!-- wp:post-excerpt {"excerptLength":' . $palavras . '} /-->

<!-- wp:post-date {"format":"d/m/Y"} /--></div>
<!-- /wp:group -->';
}

/**
 * Paginação numérica padrão das listagens.
 */
function uenf_portal_paginacao(): string {
	return '<!-- wp:query-pagination {"paginationArrow":"arrow","layout":{"type":"flex","justifyContent":"center"}} -->
<!-- wp:query-pagination-previous {"label":"Anterior"} /-->

<!-- wp:query-pagination-numbers /-->

<!-- wp:query-pagination-next {"label":"Próxima"} /-->
<!-- /wp:query-pagination -->';
}

/**
 * Listagem paginada de uma categoria (páginas "Notícias" e "Editais").
 */
function uenf_portal_lista_categoria( string $slug ): string {
	return '<!-- wp:query {"queryId":' . UENF_PORTAL_CONSULTA_PRINCIPAL . ',"query":{"perPage":9,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false' . uenf_portal_tax_query( $slug ) . '},"className":"uenf-grade-posts"} -->
<div class="wp-block-query uenf-grade-posts"><!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
' . uenf_portal_cartao_post() . '
<!-- /wp:post-template -->

' . uenf_portal_paginacao() . '

<!-- wp:query-no-results -->
<!-- wp:paragraph -->
<p>Nenhuma publicação encontrada.</p>
<!-- /wp:paragraph -->
<!-- /wp:query-no-results --></div>
<!-- /wp:query -->';
}
