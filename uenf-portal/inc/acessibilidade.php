<?php
/**
 * Barra de acessibilidade (substitui o plugin One Click Accessibility).
 *
 * Mesmas opções do portal anterior: aumentar/diminuir texto, tons de cinza,
 * alto contraste, contraste negativo, fundo claro, sublinhar links,
 * fonte legível e redefinir. A escolha fica salva no navegador do visitante.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

add_action(
	'wp_footer',
	static function () {
		$opcoes = array(
			'aumentar'      => 'Aumentar texto',
			'diminuir'      => 'Diminuir texto',
			'cinza'         => 'Tons de cinza',
			'alto-contraste' => 'Alto contraste',
			'negativo'      => 'Contraste negativo',
			'fundo-claro'   => 'Fundo claro',
			'sublinhado'    => 'Sublinhar links',
			'fonte-legivel' => 'Fonte legível',
			'redefinir'     => 'Redefinir',
		);
		?>
		<div class="uenf-a11y" data-uenf-a11y>
			<button type="button" class="uenf-a11y__alternar" aria-expanded="false" aria-controls="uenf-a11y-painel">
				<svg aria-hidden="true" viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><circle cx="12" cy="4.5" r="2"/><path d="M3.5 7.5h17v2H15v4l2 7-1.9.6-2.3-6.1h-1.6L8.9 21.1 7 20.5l2-7v-4H3.5z"/></svg>
				<span class="screen-reader-text"><?php echo esc_html( 'Abrir a barra de acessibilidade' ); ?></span>
			</button>
			<div class="uenf-a11y__painel" id="uenf-a11y-painel" role="group" aria-label="<?php echo esc_attr( 'Acessibilidade UENF' ); ?>" hidden>
				<p class="uenf-a11y__titulo"><?php echo esc_html( 'Acessibilidade UENF' ); ?></p>
				<ul>
					<?php foreach ( $opcoes as $acao => $rotulo ) : ?>
						<li><button type="button" data-acao="<?php echo esc_attr( $acao ); ?>"<?php echo in_array( $acao, array( 'aumentar', 'diminuir', 'redefinir' ), true ) ? '' : ' aria-pressed="false"'; ?>><?php echo esc_html( $rotulo ); ?></button></li>
					<?php endforeach; ?>
				</ul>
			</div>
		</div>
		<?php
	}
);

/**
 * Aplica as preferências salvas antes da primeira pintura, evitando "piscar".
 */
add_action(
	'wp_head',
	static function () {
		?>
		<script>
		(function(){try{var p=JSON.parse(localStorage.getItem('uenfA11y')||'{}'),h=document.documentElement,ok=['cinza','alto-contraste','negativo','fundo-claro','sublinhado','fonte-legivel'],e=parseInt(p.escala,10);(Array.isArray(p.classes)?p.classes:[]).forEach(function(c){if(ok.indexOf(c)>-1){h.classList.add('uenf-a11y-'+c)}});if(e>=80&&e<=160&&e!==100){h.style.fontSize=e+'%'}}catch(e){}})();
		</script>
		<?php
	},
	1
);
