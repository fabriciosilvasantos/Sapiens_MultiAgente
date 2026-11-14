<?php
/**
 * Title: Formas de ingresso
 * Slug: uenf/ingresso
 * Categories: uenf-secoes
 * Description: Dois cartões: passos numerados do SiSU e as demais formas de ingresso, cada um com seu botão.
 *
 * @package uenf-portal
 */

$uenf_passos = array(
	array( 'Faça o ENEM', 'Use a nota da edição mais recente do Exame.' ),
	array( 'Inscreva-se no SiSU', 'Escolha a UENF e o curso desejado no portal do MEC.' ),
	array( 'Acompanhe a chamada', 'Verifique a aprovação e a lista de espera.' ),
	array( 'Faça a matrícula', 'Entregue a documentação nas datas divulgadas pela UENF.' ),
);
$uenf_outras = array(
	array( 'Transferência', 'Interna, entre cursos da UENF, ou externa, de outras instituições.' ),
	array( 'Reingresso', 'Retorno de ex-alunos aos cursos ou nova habilitação.' ),
	array( 'Portador de diploma', 'Nova graduação para quem já é diplomado.' ),
	array( 'CEDERJ', 'Vestibular para as licenciaturas a distância.' ),
);
?>
<!-- wp:group {"align":"full","className":"uenf-secao","backgroundColor":"superficie","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-secao has-superficie-background-color has-background"><?php echo uenf_portal_cabecalho_secao( 'Como ingressar', 'Formas de ingresso na UENF', 'Conheça os caminhos para se tornar estudante de graduação da Universidade.' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>

<!-- wp:columns {"className":"uenf-ingresso"} -->
<div class="wp-block-columns uenf-ingresso"><!-- wp:column -->
<div class="wp-block-column"><!-- wp:group {"className":"is-style-cartao uenf-ingresso__cartao uenf-icone-formatura","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao uenf-ingresso__cartao uenf-icone-formatura"><!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">SiSU</h3>
<!-- /wp:heading -->

<!-- wp:list {"ordered":true,"className":"is-style-passos"} -->
<ol class="wp-block-list is-style-passos"><?php foreach ( $uenf_passos as $uenf_p ) : ?><!-- wp:list-item -->
<li><strong><?php echo esc_html( $uenf_p[0] ); ?></strong><br><?php echo esc_html( $uenf_p[1] ); ?></li>
<!-- /wp:list-item -->

<?php endforeach; ?></ol>
<!-- /wp:list -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button {"width":100} -->
<div class="wp-block-button has-custom-width wp-block-button__width-100"><a class="wp-block-button__link wp-element-button" href="https://uenf.br/graduacao/sisu/">Acessar a página do SiSU</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group --></div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column"><!-- wp:group {"className":"is-style-cartao uenf-ingresso__cartao uenf-icone-caminhos","layout":{"type":"default"}} -->
<div class="wp-block-group is-style-cartao uenf-ingresso__cartao uenf-icone-caminhos"><!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Outras formas</h3>
<!-- /wp:heading -->

<!-- wp:list {"className":"is-style-opcoes"} -->
<ul class="wp-block-list is-style-opcoes"><?php foreach ( $uenf_outras as $uenf_o ) : ?><!-- wp:list-item -->
<li><strong><?php echo esc_html( $uenf_o[0] ); ?></strong><br><?php echo esc_html( $uenf_o[1] ); ?></li>
<!-- /wp:list-item -->

<?php endforeach; ?></ul>
<!-- /wp:list -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button {"width":100,"className":"is-style-bloco"} -->
<div class="wp-block-button has-custom-width wp-block-button__width-100 is-style-bloco"><a class="wp-block-button__link wp-element-button" href="https://uenf.br/graduacao/como-ingressar-na-uenf/">Ver todas as formas</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group --></div>
<!-- /wp:column --></div>
<!-- /wp:columns --></div>
<!-- /wp:group -->
