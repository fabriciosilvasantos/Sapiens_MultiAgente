<?php
/**
 * Title: Página não encontrada
 * Slug: uenf/nao-encontrada
 * Categories: uenf
 * Inserter: no
 * Description: Mensagem de erro 404 com busca e botão para a página inicial.
 *
 * @package uenf-portal
 */

?>
<!-- wp:group {"className":"uenf-nao-encontrada","layout":{"type":"constrained","contentSize":"640px"}} -->
<div class="wp-block-group uenf-nao-encontrada"><!-- wp:paragraph {"className":"is-style-rotulo"} -->
<p class="is-style-rotulo">Erro 404</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 class="wp-block-heading">Esta página não foi encontrada</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>O endereço pode ter mudado ou a página pode ter sido removida. Faça uma busca ou volte para a página inicial.</p>
<!-- /wp:paragraph -->

<!-- wp:search {"label":"Pesquisar","showLabel":false,"placeholder":"Buscar no portal…","buttonText":"Pesquisar","buttonPosition":"button-inside","buttonUseIcon":true,"className":"uenf-busca-pagina"} /-->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="<?php echo esc_url( home_url( '/' ) ); ?>">Voltar para a página inicial</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group -->
