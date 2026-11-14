<?php
/**
 * Title: UENF em números
 * Slug: uenf/numeros
 * Categories: uenf-secoes
 * Description: Texto institucional e contadores animados. Para alterar um número, basta editar o texto do parágrafo com o estilo "Contador animado".
 *
 * @package uenf-portal
 */

$uenf_numeros = array(
	array( '2', 'campi no Estado do Rio de Janeiro' ),
	array( '5', 'Bases Avançadas de Pesquisa' ),
	array( '14', 'Polos presenciais de Educação a Distância' ),
	array( '20', 'Cursos de Graduação distribuídos nos 2 campi e 14 polos EaD' ),
	array( '20', 'Áreas de Pesquisa e Desenvolvimento' ),
	array( '320', 'Projetos de Iniciação Científica e Tecnológica' ),
	array( '191', 'Projetos de Extensão' ),
	array( '7.500', 'Artigos Científicos Internacionais' ),
);
?>
<!-- wp:group {"align":"full","className":"uenf-secao uenf-numeros","gradient":"marinho","textColor":"base","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-secao uenf-numeros has-base-color has-marinho-gradient-background has-text-color has-background"><!-- wp:columns {"verticalAlignment":"center"} -->
<div class="wp-block-columns are-vertically-aligned-center"><!-- wp:column {"verticalAlignment":"center","width":"56%"} -->
<div class="wp-block-column is-vertically-aligned-center" style="flex-basis:56%"><!-- wp:paragraph {"className":"is-style-rotulo"} -->
<p class="is-style-rotulo">Institucional</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">UENF em números</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"uenf-numeros__texto"} -->
<p class="uenf-numeros__texto">Fundada há pouco mais de três décadas, a Universidade Estadual do Norte Fluminense Darcy Ribeiro (UENF) surgiu com a missão de transformar profundamente a realidade social, econômica e cultural das regiões Norte e Noroeste do Estado do Rio de Janeiro. Idealizada pelo visionário educador Darcy Ribeiro, concretizada sob a liderança do então governador Leonel Brizola e projetada pela genialidade arquitetônica de Oscar Niemeyer, a UENF representa um marco no interior do estado, unindo ensino, pesquisa, extensão e inovação tecnológica.</p>
<!-- /wp:paragraph -->

<!-- wp:group {"className":"uenf-numeros__grade","layout":{"type":"grid","minimumColumnWidth":"8rem"}} -->
<div class="wp-block-group uenf-numeros__grade"><?php foreach ( $uenf_numeros as $uenf_n ) : ?><!-- wp:group {"className":"uenf-numero","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-numero"><!-- wp:paragraph {"className":"is-style-contador"} -->
<p class="is-style-contador"><?php echo esc_html( $uenf_n[0] ); ?></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><?php echo esc_html( $uenf_n[1] ); ?></p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<?php endforeach; ?></div>
<!-- /wp:group --></div>
<!-- /wp:column -->

<!-- wp:column {"verticalAlignment":"center","width":"44%"} -->
<div class="wp-block-column is-vertically-aligned-center" style="flex-basis:44%"><!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/uenf-em-numeros.png' ) ); ?>" alt="Ilustração com fotos de estudantes e do campus da UENF"/></figure>
<!-- /wp:image --></div>
<!-- /wp:column --></div>
<!-- /wp:columns --></div>
<!-- /wp:group -->
