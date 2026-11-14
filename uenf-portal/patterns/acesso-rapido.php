<?php
/**
 * Title: Acesso rápido
 * Slug: uenf/acesso-rapido
 * Categories: uenf-secoes
 * Description: Cartões de atalho para os serviços mais procurados.
 *
 * @package uenf-portal
 */

$uenf_cartoes = array(
	array( 'sistema', 'Sistema Acadêmico', 'Matrícula, histórico e declarações', 'https://academico.uenf.br/usuarios/sign_in' ),
	array( 'calendario', 'Calendário Acadêmico', 'Datas e prazos da graduação', 'https://uenf.br/graduacao/calendario-academico/' ),
	array( 'livro', 'Bibliotecas', 'Acervo, consultas e serviços', home_url( '/ensino/bibliotecas/' ) ),
	array( 'telefone', 'Lista Telefônica', 'Ramais e setores da universidade', 'https://lista.uenf.br/' ),
	array( 'documento', 'Boletim Oficial', 'Atos e publicações oficiais', 'https://uenf.br/reitoria/boletim-oficial/' ),
);
?>
<!-- wp:group {"align":"full","className":"uenf-acesso-rapido","backgroundColor":"superficie","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-acesso-rapido has-superficie-background-color has-background"><!-- wp:group {"className":"uenf-acesso-rapido__grade","layout":{"type":"grid","minimumColumnWidth":"11rem"}} -->
<div class="wp-block-group uenf-acesso-rapido__grade"><?php foreach ( $uenf_cartoes as $uenf_c ) : ?><!-- wp:group {"className":"is-style-cartao-link uenf-icone-<?php echo esc_attr( $uenf_c[0] ); ?>","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao-link uenf-icone-<?php echo esc_attr( $uenf_c[0] ); ?>"><!-- wp:heading -->
<h2 class="wp-block-heading"><a href="<?php echo esc_url( $uenf_c[3] ); ?>"><?php echo esc_html( $uenf_c[1] ); ?></a></h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><?php echo esc_html( $uenf_c[2] ); ?></p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<?php endforeach; ?></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
