<?php
/**
 * Title: Abertura com busca
 * Slug: uenf/hero
 * Categories: uenf-secoes, banner
 * Description: Faixa de abertura da página inicial com título, busca e atalhos.
 *
 * @package uenf-portal
 */

$uenf_atalhos = array(
	array( 'Notícias', home_url( '/noticias/' ) ),
	array( 'Editais', home_url( '/editais/' ) ),
	array( 'Graduação', 'https://uenf.br/graduacao/' ),
	array( 'Pós-Graduação', 'https://uenf.br/posgraduacao/' ),
	array( 'Extensão', 'https://uenf.br/extensao/' ),
	array( 'Sobre a UENF', home_url( '/institucional/sobre-a-uenf/' ) ),
);
?>
<!-- wp:group {"align":"full","className":"uenf-hero","gradient":"marinho","textColor":"base","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-hero has-base-color has-marinho-gradient-background has-text-color has-background"><!-- wp:group {"className":"uenf-hero__conteudo","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-hero__conteudo"><!-- wp:heading {"level":1,"className":"uenf-hero__titulo"} -->
<h1 class="wp-block-heading uenf-hero__titulo">Universidade Estadual do Norte Fluminense <mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-dourado-color">Darcy Ribeiro</mark></h1>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"uenf-hero__texto"} -->
<p class="uenf-hero__texto">Ensino, pesquisa, extensão e inovação em uma universidade pública e gratuita, a serviço do Norte e Noroeste Fluminense.</p>
<!-- /wp:paragraph -->

<!-- wp:search {"label":"Pesquisar no portal","showLabel":false,"placeholder":"Buscar notícias, editais, serviços…","buttonText":"Pesquisar","buttonPosition":"button-inside","buttonUseIcon":true,"className":"uenf-hero__busca"} /-->

<!-- wp:buttons {"className":"uenf-hero__atalhos"} -->
<div class="wp-block-buttons uenf-hero__atalhos"><?php foreach ( $uenf_atalhos as $uenf_a ) : ?><!-- wp:button {"className":"is-style-contorno"} -->
<div class="wp-block-button is-style-contorno"><a class="wp-block-button__link wp-element-button" href="<?php echo esc_url( $uenf_a[1] ); ?>"><?php echo esc_html( $uenf_a[0] ); ?></a></div>
<!-- /wp:button -->

<?php endforeach; ?></div>
<!-- /wp:buttons --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
