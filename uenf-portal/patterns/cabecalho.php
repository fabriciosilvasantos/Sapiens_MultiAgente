<?php
/**
 * Title: Cabeçalho do portal
 * Slug: uenf/cabecalho
 * Categories: header, uenf
 * Block Types: core/template-part/header
 * Description: Barra superior com links rápidos e redes sociais, logotipo, menu principal e busca.
 *
 * @package uenf-portal
 */

$uenf_secundario = uenf_portal_menu_secundario();
?>
<!-- wp:group {"align":"full","className":"uenf-barra-superior","backgroundColor":"marinho-900","textColor":"base","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-barra-superior has-base-color has-marinho-900-background-color has-text-color has-background"><!-- wp:group {"layout":{"type":"flex","flexWrap":"nowrap","justifyContent":"space-between"}} -->
<div class="wp-block-group"><!-- wp:navigation {"overlayMenu":"never","className":"uenf-menu-secundario","ariaLabel":"Acesso rápido","layout":{"type":"flex","justifyContent":"left"}} -->
<?php echo uenf_portal_blocos_menu( $uenf_secundario ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
<!-- /wp:navigation -->

<!-- wp:social-links {"iconColor":"base","iconColorValue":"#FFFFFF","size":"has-small-icon-size","className":"is-style-logos-only"} -->
<ul class="wp-block-social-links has-small-icon-size has-icon-color is-style-logos-only"><!-- wp:social-link {"url":"https://www.facebook.com/uenfoficial/","service":"facebook"} /-->

<!-- wp:social-link {"url":"https://www.instagram.com/uenf_oficial/","service":"instagram"} /-->

<!-- wp:social-link {"url":"https://www.youtube.com/@UENFTV","service":"youtube"} /-->

<!-- wp:social-link {"url":"https://www.linkedin.com/school/uenf-universidade-estadual-do-norte-fluminense/","service":"linkedin"} /--></ul>
<!-- /wp:social-links --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->

<!-- wp:group {"align":"full","className":"uenf-barra-principal","backgroundColor":"base","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-barra-principal has-base-background-color has-background"><!-- wp:group {"layout":{"type":"flex","flexWrap":"nowrap","justifyContent":"space-between"}} -->
<div class="wp-block-group"><!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"uenf-logo"} -->
<figure class="wp-block-image size-full uenf-logo"><a href="<?php echo esc_url( home_url( '/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/logo-uenf-azul.png' ) ); ?>" alt="UENF — página inicial"/></a></figure>
<!-- /wp:image -->

<!-- wp:group {"className":"uenf-barra-principal__acoes","layout":{"type":"flex","flexWrap":"nowrap"}} -->
<div class="wp-block-group uenf-barra-principal__acoes"><!-- wp:navigation {"overlayMenu":"mobile","className":"uenf-menu-principal","ariaLabel":"Menu principal","overlayBackgroundColor":"marinho","overlayTextColor":"base"} -->
<?php
echo uenf_portal_blocos_menu( uenf_portal_menu_principal() ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
echo uenf_portal_blocos_menu( $uenf_secundario, 'uenf-so-sobreposicao' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
?>
<!-- /wp:navigation -->

<!-- wp:search {"label":"Pesquisar","showLabel":false,"placeholder":"Buscar no portal…","buttonText":"Pesquisar","buttonPosition":"button-only","buttonUseIcon":true,"className":"uenf-busca-topo"} /--></div>
<!-- /wp:group --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
