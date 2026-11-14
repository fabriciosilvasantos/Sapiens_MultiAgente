<?php
/**
 * Title: Cursos de graduação
 * Slug: uenf/cursos
 * Categories: uenf-secoes
 * Description: Cursos agrupados por campus/modalidade, em chips com legenda (bacharelado e licenciatura). Cada grupo é uma lista com o estilo "Chips".
 *
 * @package uenf-portal
 */

$uenf_g = 'https://uenf.br/graduacao/';
// [ nome, URL, é licenciatura? ]
$uenf_grupos = array(
	array(
		'Campus Leonel Brizola',
		'Campos dos Goytacazes — presencial',
		array(
			array( 'Administração Pública', $uenf_g . 'administracao-publica/', false ),
			array( 'Agronomia', $uenf_g . 'agronomia/', false ),
			array( 'Biologia (Licenciatura)', $uenf_g . 'licenciatura-biologia/', true ),
			array( 'Ciência da Computação', 'https://cc.uenf.br/', false ),
			array( 'Ciências Biológicas (Bacharelado)', $uenf_g . 'biologia/', false ),
			array( 'Ciências Sociais', $uenf_g . 'ciencias-sociais/', false ),
			array( 'Engenharia Civil', $uenf_g . 'engenharia-civil/', false ),
			array( 'Engenharia de Alimentos', $uenf_g . 'engenharia-de-alimentos/', false ),
			array( 'Engenharia Metalúrgica e de Materiais', $uenf_g . 'engenharia-de-materiais/', false ),
			array( 'Engenharia de Produção', $uenf_g . 'engenharia-de-producao/', false ),
			array( 'Física (Licenciatura)', $uenf_g . 'licenciatura-fisica/', true ),
			array( 'Matemática (Licenciatura)', 'https://uenf.br/posgraduacao/licenciatura-matematica/', true ),
			array( 'Medicina Veterinária', $uenf_g . 'medicina-veterinaria/', false ),
			array( 'Pedagogia (Licenciatura)', $uenf_g . 'pedagogia/', true ),
			array( 'Química (Licenciatura)', $uenf_g . 'licenciatura-quimica/', true ),
			array( 'Zootecnia', $uenf_g . 'zootecnia/', false ),
		),
	),
	array(
		'Campus Professor Carlos Alberto Dias',
		'Macaé — presencial',
		array(
			array( 'Engenharia de Exploração e Produção de Petróleo', 'https://uenf.br/cct/lenep/graduacao/', false ),
			array( 'Engenharia Meteorológica', 'https://lamet.uenf.br/grad', false ),
		),
	),
	array(
		'Educação a Distância',
		'Consórcio CEDERJ — semipresencial',
		array(
			array( 'Pedagogia (Licenciatura)', 'https://www.cecierj.edu.br/consorcio-cederj/cursos/pedagogia/', true ),
			array( 'Ciências Biológicas (Licenciatura)', 'https://www.cecierj.edu.br/consorcio-cederj/cursos/ciencias-biologicas/', true ),
			array( 'Química (Licenciatura)', 'https://www.cecierj.edu.br/consorcio-cederj/cursos/quimica/', true ),
		),
	),
);
?>
<!-- wp:group {"align":"full","className":"uenf-secao uenf-cursos","layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull uenf-secao uenf-cursos"><?php echo uenf_portal_cabecalho_secao( 'Nossos cursos', 'Cursos de graduação', 'Cursos presenciais nos campi de Campos dos Goytacazes e Macaé, além de licenciaturas a distância pelo Consórcio CEDERJ.', 'Todos os cursos', $uenf_g . 'cursos-de-graduacao/' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>

<!-- wp:paragraph {"className":"uenf-cursos__legenda"} -->
<p class="uenf-cursos__legenda"><span class="uenf-ponto"></span>Bacharelado <span class="uenf-ponto uenf-ponto--licenciatura"></span>Licenciatura</p>
<!-- /wp:paragraph -->

<?php foreach ( $uenf_grupos as $uenf_grupo ) : ?>
<!-- wp:group {"className":"uenf-cursos__grupo","layout":{"type":"default"}} -->
<div class="wp-block-group uenf-cursos__grupo"><!-- wp:group {"className":"uenf-cursos__topo","layout":{"type":"flex","flexWrap":"nowrap","justifyContent":"space-between"}} -->
<div class="wp-block-group uenf-cursos__topo"><!-- wp:group {"layout":{"type":"default"}} -->
<div class="wp-block-group"><!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading"><?php echo esc_html( $uenf_grupo[0] ); ?></h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><?php echo esc_html( $uenf_grupo[1] ); ?></p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<!-- wp:paragraph {"className":"uenf-cursos__total"} -->
<p class="uenf-cursos__total"><?php echo esc_html( count( $uenf_grupo[2] ) . ' cursos' ); ?></p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<!-- wp:list {"className":"is-style-chips"} -->
<ul class="wp-block-list is-style-chips"><?php foreach ( $uenf_grupo[2] as $uenf_curso ) : ?><!-- wp:list-item<?php echo $uenf_curso[2] ? ' {"className":"uenf-licenciatura"}' : ''; ?> -->
<li<?php echo $uenf_curso[2] ? ' class="uenf-licenciatura"' : ''; ?>><a href="<?php echo esc_url( $uenf_curso[1] ); ?>"><?php echo esc_html( $uenf_curso[0] ); ?></a></li>
<!-- /wp:list-item -->

<?php endforeach; ?></ul>
<!-- /wp:list --></div>
<!-- /wp:group -->

<?php endforeach; ?></div>
<!-- /wp:group -->
