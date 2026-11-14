/**
 * UENF Portal — comportamentos do tema (sem dependências).
 *
 * 1. Contador animado  → parágrafo com o estilo "Contador animado"
 * 2. Banners rotativos → grupo com o estilo "Banners rotativos"
 * 3. Barra de acessibilidade
 */
( function () {
	'use strict';

	var reduzMovimento = window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches;

	/* ------------------------------------------------ 1. Contador animado */

	function iniciarContadores() {
		var contadores = document.querySelectorAll( '.is-style-contador' );
		if ( ! contadores.length ) {
			return;
		}

		var formato = new Intl.NumberFormat( 'pt-BR' );

		function animar( el ) {
			var texto = el.textContent.trim();
			// Aceita prefixo/sufixo (ex.: "+ 7.500", "95%"); anima só o número.
			var partes = texto.match( /^(\D*)([\d.]+)(.*)$/ );
			if ( ! partes ) {
				return;
			}
			var alvo = parseInt( partes[ 2 ].replace( /\./g, '' ), 10 );
			if ( ! alvo || reduzMovimento ) {
				return;
			}

			var duracao = 1600;
			var inicio = null;
			el.setAttribute( 'aria-label', texto );

			function quadro( agora ) {
				if ( inicio === null ) {
					inicio = agora;
				}
				var progresso = Math.min( ( agora - inicio ) / duracao, 1 );
				var suave = 1 - Math.pow( 1 - progresso, 3 );
				el.textContent = partes[ 1 ] + formato.format( Math.round( alvo * suave ) ) + partes[ 3 ];
				if ( progresso < 1 ) {
					window.requestAnimationFrame( quadro );
				} else {
					el.textContent = texto;
				}
			}
			window.requestAnimationFrame( quadro );
		}

		if ( ! ( 'IntersectionObserver' in window ) ) {
			return;
		}
		var observador = new IntersectionObserver(
			function ( entradas ) {
				entradas.forEach( function ( entrada ) {
					if ( entrada.isIntersecting ) {
						observador.unobserve( entrada.target );
						animar( entrada.target );
					}
				} );
			},
			{ threshold: 0.6 }
		);
		contadores.forEach( function ( el ) {
			observador.observe( el );
		} );
	}

	/* ----------------------------------------------- 2. Banners rotativos */

	function iniciarBanners() {
		document.querySelectorAll( '.is-style-banner-rotativo' ).forEach( function ( grupo ) {
			var banners = grupo.querySelectorAll( ':scope > .uenf-banner' );
			if ( ! banners.length ) {
				return;
			}
			var sorteado = banners[ Math.floor( Math.random() * banners.length ) ];
			sorteado.classList.add( 'is-ativo' );
			grupo.setAttribute( 'data-uenf-pronto', '' );
		} );
	}

	/* ------------------------------------------ 3. Barra de acessibilidade */

	function iniciarAcessibilidade() {
		var barra = document.querySelector( '[data-uenf-a11y]' );
		if ( ! barra ) {
			return;
		}

		var raiz = document.documentElement;
		var alternar = barra.querySelector( '.uenf-a11y__alternar' );
		var painel = barra.querySelector( '.uenf-a11y__painel' );
		var CHAVE = 'uenfA11y';
		var EXCLUSIVOS = [ 'cinza', 'alto-contraste', 'negativo', 'fundo-claro' ];
		var estado = { classes: [], escala: 100 };

		try {
			var salvo = JSON.parse( window.localStorage.getItem( CHAVE ) || '{}' );
			estado.classes = Array.isArray( salvo.classes ) ? salvo.classes : [];
			estado.escala = salvo.escala || 100;
		} catch ( e ) {}

		function salvar() {
			try {
				window.localStorage.setItem( CHAVE, JSON.stringify( estado ) );
			} catch ( e ) {}
		}

		function aplicar() {
			Array.prototype.slice.call( raiz.classList ).forEach( function ( classe ) {
				if ( classe.indexOf( 'uenf-a11y-' ) === 0 ) {
					raiz.classList.remove( classe );
				}
			} );
			estado.classes.forEach( function ( classe ) {
				raiz.classList.add( 'uenf-a11y-' + classe );
			} );
			raiz.style.fontSize = estado.escala === 100 ? '' : estado.escala + '%';

			painel.querySelectorAll( 'button[aria-pressed]' ).forEach( function ( botao ) {
				botao.setAttribute( 'aria-pressed', estado.classes.indexOf( botao.dataset.acao ) > -1 ? 'true' : 'false' );
			} );
		}

		function abrir( aberto ) {
			painel.hidden = ! aberto;
			alternar.setAttribute( 'aria-expanded', aberto ? 'true' : 'false' );
		}

		alternar.addEventListener( 'click', function () {
			abrir( painel.hidden );
		} );

		barra.addEventListener( 'keydown', function ( evento ) {
			if ( evento.key === 'Escape' && ! painel.hidden ) {
				abrir( false );
				alternar.focus();
			}
		} );

		document.addEventListener( 'click', function ( evento ) {
			if ( ! painel.hidden && ! barra.contains( evento.target ) ) {
				abrir( false );
			}
		} );

		painel.addEventListener( 'click', function ( evento ) {
			var botao = evento.target.closest( 'button[data-acao]' );
			if ( ! botao ) {
				return;
			}
			var acao = botao.dataset.acao;

			if ( acao === 'aumentar' ) {
				estado.escala = Math.min( estado.escala + 10, 160 );
			} else if ( acao === 'diminuir' ) {
				estado.escala = Math.max( estado.escala - 10, 80 );
			} else if ( acao === 'redefinir' ) {
				estado = { classes: [], escala: 100 };
			} else {
				var ativo = estado.classes.indexOf( acao ) > -1;
				// Os modos de cor são mutuamente exclusivos.
				estado.classes = estado.classes.filter( function ( classe ) {
					return classe !== acao && ( EXCLUSIVOS.indexOf( acao ) === -1 || EXCLUSIVOS.indexOf( classe ) === -1 );
				} );
				if ( ! ativo ) {
					estado.classes.push( acao );
				}
			}
			aplicar();
			salvar();
		} );

		aplicar();
	}

	function iniciar() {
		iniciarBanners();
		iniciarContadores();
		iniciarAcessibilidade();
	}

	if ( document.readyState === 'loading' ) {
		document.addEventListener( 'DOMContentLoaded', iniciar );
	} else {
		iniciar();
	}
} )();
