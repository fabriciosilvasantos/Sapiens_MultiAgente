<?php
/**
 * Title: Documentos e publicações
 * Slug: uenf/documentos
 * Categories: uenf-secoes
 * Description: Grade de cartões horizontais com ícone, título, descrição e seta, para documentos e serviços.
 *
 * @package uenf-portal
 */

$uenf_docs = array(
	array( 'documento', 'Boletim Oficial', 'Atos e publicações oficiais', 'https://uenf.br/reitoria/boletim-oficial/' ),
	array( 'documento', 'Plano de Desenvolvimento Institucional', 'PDI da Universidade', home_url( '/institucional/plano-de-desenvolvimento-institucional/' ) ),
	array( 'calendario', 'Calendário Acadêmico', 'Datas e prazos da graduação', 'https://uenf.br/graduacao/calendario-academico/' ),
	array( 'documento', 'Formulários da Graduação', 'Requerimentos e modelos', 'https://uenf.br/graduacao/formularios-graduacao/' ),
	array( 'documento', 'Taxas de serviços', 'Valores e orientações', home_url( '/servicos/taxas-de-servicos/' ) ),
	array( 'documento', 'Nossa marca', 'Manual e arquivos da marca UENF', home_url( '/institucional-2/nossa-marca/' ) ),
);
?>
<!-- wp:group {"align":"full","className":"uenf-secao","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-secao"><?php echo uenf_portal_cabecalho_secao( 'Documentos', 'Documentos e publicações', 'Publicações oficiais, calendários e modelos mais consultados.', 'Serviços', home_url( '/servicos/' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>

<!-- wp:group {"className":"uenf-documentos","layout":{"type":"grid","minimumColumnWidth":"18rem"}} -->
<div class="wp-block-group uenf-documentos"><?php foreach ( $uenf_docs as $uenf_d ) : ?><!-- wp:group {"className":"is-style-cartao-link uenf-cartao-horizontal uenf-icone-<?php echo esc_attr( $uenf_d[0] ); ?>","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao-link uenf-cartao-horizontal uenf-icone-<?php echo esc_attr( $uenf_d[0] ); ?>"><!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading"><a href="<?php echo esc_url( $uenf_d[3] ); ?>"><?php echo esc_html( $uenf_d[1] ); ?></a></h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><?php echo esc_html( $uenf_d[2] ); ?></p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<?php endforeach; ?></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
