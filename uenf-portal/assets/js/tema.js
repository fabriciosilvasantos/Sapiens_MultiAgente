/**
 * UENF Portal — comportamentos do tema (sem dependências).
 *
 * 1. Contador animado  → parágrafo com o estilo "Contador animado"
 * 2. Banners rotativos → grupo com o estilo "Banners rotativos"
 * 3. Cursos recolhidos no celular
 * 4. Barra de acessibilidade
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

			// Leitores de tela recebem só o valor final; a animação é decorativa.
			var real = document.createElement( 'span' );
			real.className = 'screen-reader-text';
			real.textContent = texto;
			var visual = document.createElement( 'span' );
			visual.setAttribute( 'aria-hidden', 'true' );
			el.textContent = '';
			el.appendChild( real );
			el.appendChild( visual );

			function quadro( agora ) {
				if ( inicio === null ) {
					inicio = agora;
				}
				var progresso = Math.min( ( agora - inicio ) / duracao, 1 );
				var suave = 1 - Math.pow( 1 - progresso, 3 );
				visual.textContent = partes[ 1 ] + formato.format( Math.round( alvo * suave ) ) + partes[ 3 ];
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

	/* ------------------------------------- 3. Cursos recolhidos no celular */

	// Sem JavaScript, todos os cursos aparecem. Com ele, cada grupo ganha um botão
	// que só é exibido em telas estreitas (ver tema.css, "Cursos recolhidos").
	function iniciarCursos() {
		document.querySelectorAll( '.uenf-cursos__grupo' ).forEach( function ( grupo, indice ) {
			var lista = grupo.querySelector( '.is-style-chips' );
			if ( ! lista ) {
				return;
			}
			var total = lista.querySelectorAll( 'li' ).length;
			var titulo = grupo.querySelector( 'h3' );
			var nome = titulo ? titulo.textContent.trim() : '';
			lista.id = lista.id || 'uenf-cursos-lista-' + ( indice + 1 );

			var botao = document.createElement( 'button' );
			botao.type = 'button';
			botao.className = 'uenf-cursos__alternar';
			botao.setAttribute( 'aria-controls', lista.id );

			function definir( aberto ) {
				grupo.classList.toggle( 'is-recolhido', ! aberto );
				botao.setAttribute( 'aria-expanded', aberto ? 'true' : 'false' );
				botao.textContent = aberto ? 'Ocultar cursos' : 'Ver ' + ( total === 1 ? 'o curso' : 'os ' + total + ' cursos' );
				if ( nome ) {
					var contexto = document.createElement( 'span' );
					contexto.className = 'screen-reader-text';
					contexto.textContent = ' — ' + nome;
					botao.appendChild( contexto );
				}
			}

			botao.addEventListener( 'click', function () {
				definir( grupo.classList.contains( 'is-recolhido' ) );
			} );

			lista.parentNode.insertBefore( botao, lista );
			definir( false );
		} );
	}

	/* ------------------------------------------ 4. Barra de acessibilidade */

	function iniciarAcessibilidade() {
		var barra = document.querySelector( '[data-uenf-a11y]' );
		if ( ! barra ) {
			return;
		}

		var raiz = document.documentElement;
		var alternar = barra.querySelector( '.uenf-a11y__alternar' );
		var painel = barra.querySelector( '.uenf-a11y__painel' );
		var rotulo = alternar.querySelector( '.screen-reader-text' );
		var status = barra.querySelector( '[data-uenf-a11y-status]' );
		var CHAVE = 'uenfA11y';
		var EXCLUSIVOS = [ 'cinza', 'alto-contraste', 'negativo', 'fundo-claro' ];
		var MODOS = EXCLUSIVOS.concat( [ 'sublinhado', 'fonte-legivel' ] );
		var estado = { classes: [], escala: 100 };

		try {
			var salvo = JSON.parse( window.localStorage.getItem( CHAVE ) || '{}' );
			var escala = parseInt( salvo.escala, 10 );
			// Só valores conhecidos: o armazenamento é compartilhado com outros sites do domínio.
			estado.classes = ( Array.isArray( salvo.classes ) ? salvo.classes : [] ).filter( function ( classe ) {
				return MODOS.indexOf( classe ) > -1;
			} );
			estado.escala = escala >= 80 && escala <= 160 ? escala : 100;
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
			rotulo.textContent = aberto ? 'Fechar a barra de acessibilidade' : 'Abrir a barra de acessibilidade';
		}

		function anunciar( mensagem ) {
			if ( status ) {
				status.textContent = mensagem;
			}
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

			if ( acao === 'aumentar' || acao === 'diminuir' ) {
				anunciar( 'Texto em ' + estado.escala + '%' + ( estado.escala === 160 || estado.escala === 80 ? ' (limite)' : '' ) );
			} else if ( acao === 'redefinir' ) {
				anunciar( 'Preferências de acessibilidade redefinidas' );
			} else {
				anunciar( botao.textContent + ( estado.classes.indexOf( acao ) > -1 ? ' ativado' : ' desativado' ) );
			}
		} );

		aplicar();
	}

	function iniciar() {
		iniciarBanners();
		iniciarContadores();
		iniciarCursos();
		iniciarAcessibilidade();
	}

	if ( document.readyState === 'loading' ) {
		document.addEventListener( 'DOMContentLoaded', iniciar );
	} else {
		iniciar();
	}
} )();
