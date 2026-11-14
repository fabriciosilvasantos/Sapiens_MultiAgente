<?php
/**
 * Title: Rodapé do portal
 * Slug: uenf/rodape
 * Categories: footer, uenf
 * Block Types: core/template-part/footer
 * Description: Logotipo, redes sociais, endereços dos campi e contatos.
 *
 * @package uenf-portal
 */

$uenf_contatos = array(
	array( 'Assessoria de Comunicação', '(22) 2739-7119', 'uenf@uenf.br' ),
	array( 'Reitoria', '(22) 2739-7003', 'reitoria@uenf.br' ),
	array( 'Pró-Reitoria de Graduação', '(22) 2748-6040', 'prograd@uenf.br' ),
	array( 'Pró-Reitoria de Extensão', '(22) 2739-7007', 'proex@uenf.br' ),
	array( 'Pró-Reitoria de Pesquisa e Pós-Graduação', '(22) 2739-7012', 'proppg@uenf.br' ),
	array( 'Pró-Reitoria de Assuntos Comunitários', '(22) 2748-6054', 'proac@uenf.br' ),
	array( 'Recepção LENEP', '(22) 3399-3000', '' ),
	array( 'Recepção LAMET', '(22) 3399-3001', '' ),
);
?>
<!-- wp:group {"align":"full","className":"uenf-rodape","backgroundColor":"marinho-900","textColor":"base","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-rodape has-base-color has-marinho-900-background-color has-text-color has-background"><!-- wp:columns {"className":"uenf-rodape__colunas"} -->
<div class="wp-block-columns uenf-rodape__colunas"><!-- wp:column {"width":"26%"} -->
<div class="wp-block-column" style="flex-basis:26%"><!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"uenf-rodape__logo"} -->
<figure class="wp-block-image size-full uenf-rodape__logo"><a href="<?php echo esc_url( home_url( '/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/logo-uenf-vertical-branco.png' ) ); ?>" alt="Universidade Estadual do Norte Fluminense Darcy Ribeiro"/></a></figure>
<!-- /wp:image -->

<!-- wp:social-links {"iconColor":"base","iconColorValue":"#FFFFFF","className":"is-style-logos-only uenf-rodape__redes"} -->
<ul class="wp-block-social-links has-icon-color is-style-logos-only uenf-rodape__redes"><!-- wp:social-link {"url":"https://www.facebook.com/uenfoficial","service":"facebook"} /-->

<!-- wp:social-link {"url":"https://www.instagram.com/uenf_oficial","service":"instagram"} /-->

<!-- wp:social-link {"url":"https://www.youtube.com/@UENFTV","service":"youtube"} /-->

<!-- wp:social-link {"url":"https://www.linkedin.com/school/uenf-universidade-estadual-do-norte-fluminense/","service":"linkedin"} /--></ul>
<!-- /wp:social-links --></div>
<!-- /wp:column -->

<!-- wp:column {"width":"28%"} -->
<div class="wp-block-column" style="flex-basis:28%"><!-- wp:heading {"className":"uenf-rodape__titulo"} -->
<h2 class="wp-block-heading uenf-rodape__titulo">Endereços</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>UENF campus Campos dos Goytacazes</strong><br><a href="https://maps.app.goo.gl/YHKj5sVQEXWx4pb38">Av. Alberto Lamego, 2000<br>Parque Califórnia, Campos – RJ, Brasil<br>CEP: 28013-602</a></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>UENF campus Macaé</strong><br><a href="https://maps.app.goo.gl/6hHoZqWPhsqF4Gjn8">Rua Hermenegildo Adolpho<br>Parque Bellavista, Imboassica, Macaé – RJ, Brasil<br>CEP: 27925-310</a></p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column {"width":"46%"} -->
<div class="wp-block-column" style="flex-basis:46%"><!-- wp:heading {"className":"uenf-rodape__titulo"} -->
<h2 class="wp-block-heading uenf-rodape__titulo">Contatos</h2>
<!-- /wp:heading -->

<!-- wp:group {"className":"uenf-rodape__contatos","layout":{"type":"grid","minimumColumnWidth":"14rem"}} -->
<div class="wp-block-group uenf-rodape__contatos"><?php foreach ( $uenf_contatos as $uenf_c ) : ?><!-- wp:paragraph -->
<p><strong><?php echo esc_html( $uenf_c[0] ); ?></strong><br><a href="tel:+55<?php echo esc_attr( preg_replace( '/\D/', '', $uenf_c[1] ) ); ?>"><?php echo esc_html( $uenf_c[1] ); ?></a><?php if ( $uenf_c[2] ) : ?> | <a href="<?php echo esc_url( 'mailto:' . $uenf_c[2] ); ?>"><?php echo esc_html( $uenf_c[2] ); ?></a><?php endif; ?></p>
<!-- /wp:paragraph -->

<?php endforeach; ?></div>
<!-- /wp:group --></div>
<!-- /wp:column --></div>
<!-- /wp:columns -->

<!-- wp:group {"className":"uenf-rodape__base","layout":{"type":"flex","flexWrap":"wrap","justifyContent":"space-between"}} -->
<div class="wp-block-group uenf-rodape__base"><!-- wp:paragraph -->
<p>© <?php echo esc_html( gmdate( 'Y' ) ); ?> UENF — Universidade Estadual do Norte Fluminense Darcy Ribeiro</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><a href="https://uenf.br/reitoria/transparencia/">Transparência</a> · <a href="https://www.rj.gov.br/ouverj">OuvERJ</a> · <a href="https://lista.uenf.br/">Lista telefônica</a></p>
<!-- /wp:paragraph --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
