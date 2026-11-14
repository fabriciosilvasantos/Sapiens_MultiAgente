<?php
/**
 * Title: Editais e chamadas
 * Slug: uenf/editais
 * Categories: uenf-secoes, posts
 * Description: Filtros por categoria e lista dos editais mais recentes, com data e selo de situação (tags aberto, resultado, em-breve, encerrado).
 *
 * @package uenf-portal
 */

?>
<!-- wp:group {"align":"full","className":"uenf-secao","backgroundColor":"superficie-2","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-secao has-superficie-2-background-color has-background"><?php echo uenf_portal_cabecalho_secao( 'Editais', 'Editais e chamadas', 'Processos seletivos, concursos, bolsas e resultados.', 'Todos os editais', home_url( '/editais/' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>

<?php
echo uenf_portal_filtros( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	'Todos',
	home_url( '/editais/' ),
	array(
		array( 'Concursos', 'concursos' ),
		array( 'Graduação', 'graduacao' ),
		array( 'Pós-Graduação', 'pos-graduacao' ),
		array( 'Extensão', 'extensao' ),
		array( 'Assuntos Comunitários', 'assuntos-comunitarios' ),
	)
);
?>

<!-- wp:query {"queryId":21,"query":{"perPage":9,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false<?php echo uenf_portal_tax_query( 'editais' ); // phpcs:ignore ?>},"className":"uenf-lista-editais"} -->
<div class="wp-block-query uenf-lista-editais"><!-- wp:post-template -->
<!-- wp:group {"className":"is-style-linha-edital","layout":{"type":"flex","flexWrap":"nowrap","justifyContent":"space-between"}} -->
<div class="wp-block-group is-style-linha-edital"><!-- wp:group {"className":"uenf-linha-edital__texto","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-linha-edital__texto"><!-- wp:post-title {"level":3,"isLink":true} /-->

<!-- wp:post-excerpt {"excerptLength":16} /--></div>
<!-- /wp:group -->

<!-- wp:group {"className":"uenf-linha-edital__data","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-linha-edital__data"><!-- wp:paragraph -->
<p>Publicado em</p>
<!-- /wp:paragraph -->

<!-- wp:post-date {"format":"d/m/Y"} /--></div>
<!-- /wp:group -->

<!-- wp:post-terms {"term":"post_tag","className":"is-style-selo"} /--></div>
<!-- /wp:group -->
<!-- /wp:post-template --></div>
<!-- /wp:query --></div>
<!-- /wp:group -->
