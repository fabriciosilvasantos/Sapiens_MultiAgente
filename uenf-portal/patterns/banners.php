<?php
/**
 * Title: Banners rotativos
 * Slug: uenf/banners
 * Categories: uenf-secoes, banner
 * Description: Cada grupo interno é um banner (imagem para computador + imagem para celular, ambas com link). A cada visita um banner é sorteado. Substitui o plugin AdRotate.
 *
 * @package uenf-portal
 */

$uenf_link = home_url( '/noticias/uenf-abre-processo-seletivo-para-ingresso-no-colegio-universitario-de-aplicacao-antonio-sarlo/' );
$uenf_base = 'https://uenf.br/portal/wp-content/uploads/2026/10/';
?>
<!-- wp:group {"align":"full","className":"is-style-banner-rotativo","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull is-style-banner-rotativo"><!-- wp:group {"className":"uenf-banner","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-banner"><!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"uenf-so-desktop"} -->
<figure class="wp-block-image size-full uenf-so-desktop"><a href="<?php echo esc_url( $uenf_link ); ?>"><img src="<?php echo esc_url( $uenf_base . 'BANNER-ANTONIO-SARLO-1920-x-400.png' ); ?>" alt="Estude no Antônio Sarlo: renovação de matrícula e processo seletivo 2027"/></a></figure>
<!-- /wp:image -->

<!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"uenf-so-mobile"} -->
<figure class="wp-block-image size-full uenf-so-mobile"><a href="<?php echo esc_url( $uenf_link ); ?>"><img src="<?php echo esc_url( $uenf_base . 'BANNER-ANTONIO-SARLO-900-x-400.png' ); ?>" alt="Estude no Antônio Sarlo: renovação de matrícula e processo seletivo 2027"/></a></figure>
<!-- /wp:image --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
