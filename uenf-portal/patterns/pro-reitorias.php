<?php
/**
 * Title: Pró-Reitorias
 * Slug: uenf/pro-reitorias
 * Categories: uenf-secoes
 * Description: Quatro cartões escuros com imagem para as Pró-Reitorias e seus principais links.
 *
 * @package uenf-portal
 */

$uenf_pr = array(
	array(
		'Graduação',
		'https://uenf.br/graduacao/',
		'pro-reitoria-graduacao.jpg',
		array(
			array( 'Calendário Acadêmico', 'https://uenf.br/graduacao/institucional/calendario-academico/' ),
			array( 'Perguntas Frequentes', 'https://uenf.br/graduacao/perguntas-e-respostas/' ),
			array( 'Sistema Acadêmico', 'https://academico.uenf.br/usuarios/sign_in' ),
		),
	),
	array(
		'Pós-Graduação',
		'https://uenf.br/posgraduacao/',
		'pro-reitoria-pos-graduacao.jpg',
		array(
			array( 'Mestrado e Doutorado', 'https://uenf.br/posgraduacao/programas/pos-graduacao/' ),
			array( 'PROAP/CAPES', 'https://uenf.br/posgraduacao/proap-capes/' ),
			array( 'Sistema Acadêmico', 'https://academico.uenf.br/usuarios/sign_in' ),
		),
	),
	array(
		'Extensão',
		'https://uenf.br/extensao/',
		'pro-reitoria-extensao.jpg',
		array(
			array( 'Projetos', 'https://uenf.br/extensao/projetos/' ),
			array( 'Rede Nacional de Extensão (RENEX)', 'https://uenf.br/extensao/renex/' ),
		),
	),
	array(
		'Assuntos Comunitários',
		'https://uenf.br/proac/',
		'pro-reitoria-assuntos-comunitarios.jpg',
		array(
			array( 'Ações', 'https://uenf.br/proac/acoes-da-proac/' ),
			array( 'Infográficos', 'https://uenf.br/proac/infografico/' ),
			array( 'Projetos', 'https://uenf.br/proac/eventos/projetos/' ),
		),
	),
);
?>
<!-- wp:group {"align":"full","className":"uenf-secao","backgroundColor":"superficie","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-secao has-superficie-background-color has-background"><?php echo uenf_portal_cabecalho_secao( 'Pró-Reitorias', 'Pró-Reitorias', 'Ensino, pesquisa, extensão e vida universitária na UENF.' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>

<!-- wp:group {"className":"uenf-pro-reitorias","layout":{"type":"grid","minimumColumnWidth":"15rem"}} -->
<div class="wp-block-group uenf-pro-reitorias"><?php foreach ( $uenf_pr as $uenf_p ) : ?><!-- wp:group {"className":"is-style-cartao-escuro uenf-pro-reitoria","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao-escuro uenf-pro-reitoria"><!-- wp:image {"sizeSlug":"full","linkDestination":"custom"} -->
<figure class="wp-block-image size-full"><a href="<?php echo esc_url( $uenf_p[1] ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/' . $uenf_p[2] ) ); ?>" alt=""/></a></figure>
<!-- /wp:image -->

<!-- wp:group {"className":"uenf-pro-reitoria__corpo","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-pro-reitoria__corpo"><!-- wp:paragraph {"className":"uenf-cartao-escuro__rotulo"} -->
<p class="uenf-cartao-escuro__rotulo">Pró-Reitoria</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading"><a href="<?php echo esc_url( $uenf_p[1] ); ?>"><?php echo esc_html( $uenf_p[0] ); ?></a></h3>
<!-- /wp:heading -->

<!-- wp:list {"className":"is-style-links"} -->
<ul class="wp-block-list is-style-links"><?php foreach ( $uenf_p[3] as $uenf_l ) : ?><!-- wp:list-item -->
<li><a href="<?php echo esc_url( $uenf_l[1] ); ?>"><?php echo esc_html( $uenf_l[0] ); ?></a></li>
<!-- /wp:list-item -->

<?php endforeach; ?></ul>
<!-- /wp:list --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->

<?php endforeach; ?></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
