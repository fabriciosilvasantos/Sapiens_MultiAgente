<?php
/**
 * Menus iniciais do portal (os mesmos itens do site anterior).
 *
 * São usados apenas para montar o conteúdo inicial do bloco Navegação nos
 * padrões de cabeçalho. Depois de salvo no Editor do Site, o menu passa a ser
 * gerenciado normalmente em Aparência → Editor → Navegação.
 *
 * @package uenf-portal
 */

defined( 'ABSPATH' ) || exit;

/**
 * Menu principal. Caminhos iniciados por "/" são relativos ao portal.
 */
function uenf_portal_menu_principal(): array {
	return array(
		array(
			'Institucional',
			'/institucional/',
			array(
				array( 'Sobre a UENF', '/institucional/sobre-a-uenf/' ),
				array( 'Nossa marca', '/institucional-2/nossa-marca/' ),
				array( 'Reitoria', 'https://uenf.br/reitoria/' ),
				array( 'Plano de Desenvolvimento Institucional – PDI', '/institucional/plano-de-desenvolvimento-institucional/' ),
				array( 'Pró-Reitorias', '/institucional/pro-reitorias/' ),
				array( 'Diretorias da Reitoria', '/institucional/diretorias-da-reitoria/' ),
				array( 'Centros', '/institucional/centros-e-laboratorios/' ),
				array( 'Prefeitura da UENF', 'https://uenf.br/prefeitura/' ),
				array( 'Assessoria de Assuntos Internacionais e Interinstitucionais – ASSAII', 'https://uenf.br/reitoria/assaii/' ),
				array( 'Diretoria de Cultura', 'https://uenf.br/reitoria/diretoriadecultura/' ),
				array( 'Boletim Epidemiológico', '/wp-content/uploads/2022/12/boletim-epidemiologico-2022-2.pdf' ),
			),
		),
		array(
			'Ensino',
			'/ensino/',
			array(
				array( 'Pró-Reitoria de Graduação', 'https://uenf.br/graduacao/' ),
				array( 'Pró-Reitoria de Pesquisa e Pós-Graduação', 'https://uenf.br/posgraduacao/' ),
				array( 'Calendário Acadêmico', 'https://uenf.br/graduacao/calendario-academico/' ),
				array( 'Secretaria Acadêmica', 'https://www.uenf.br/reitoria/secacad/' ),
				array( 'Iniciação à Docência (PIBID)', 'https://uenf.br/graduacao/programa/pibid/' ),
				array( 'Bibliotecas', '/ensino/bibliotecas/' ),
			),
		),
		array( 'Extensão', 'https://uenf.br/extensao/' ),
		array(
			'Pesquisa e Inovação',
			'/pesquisa-e-inovacao/',
			array(
				array( 'Pró-Reitoria de Pesquisa e Pós-Graduação', 'https://uenf.br/posgraduacao/' ),
				array( 'Iniciação Científica', '/pesquisa-e-inovacao/iniciacao-cientifica/' ),
				array( 'Agência UENF de Inovação – AgeInov', 'https://uenf.br/reitoria/agenciainovacao/' ),
			),
		),
		array(
			'Serviços',
			'/servicos/',
			array(
				array( 'Serviços Internos', '/servicos/servicos-internos/' ),
				array( 'Serviços Gerais', '/servicos/servicos-gerais/' ),
				array( 'Hospital Veterinário', 'http://www.uenf.br/portal/index.php/br/ensino/hospital-veterinario.html' ),
				array( 'Empresas Juniores', '/servicos/empresas-juniores/' ),
				array( 'Estágio', '/extensao/estagio/' ),
				array( 'Lista Telefônica', 'https://lista.uenf.br/' ),
				array( 'Taxas de serviços', '/servicos/taxas-de-servicos/' ),
				array( 'Comissão Interna de Biossegurança da UENF', 'https://uenf.br/reitoria/cibio/' ),
			),
		),
		array(
			'Transparência',
			'https://uenf.br/reitoria/transparencia/',
			array(
				array( 'Institucional', 'https://uenf.br/reitoria/transparencia/1-institucional/' ),
				array( 'Ações e Programas', 'https://uenf.br/reitoria/transparencia/2-acoes-e-programas/' ),
				array( 'Participação Social', 'https://uenf.br/reitoria/transparencia/3-participacao-social/' ),
				array( 'Auditorias', 'https://uenf.br/reitoria/transparencia/4-auditorias/' ),
				array( 'Convênios e Transferências', 'https://uenf.br/reitoria/transparencia/5-convenios-e-transferencias/' ),
				array( 'Receitas e Despesas', 'https://uenf.br/reitoria/transparencia/6-receitas-e-despesas/' ),
				array( 'Licitações e Contratos', 'https://uenf.br/reitoria/transparencia/7-licitacoes-e-contratos/' ),
				array( 'Servidores', 'https://uenf.br/reitoria/transparencia/8-servidores/' ),
				array( 'Informações Classificadas', 'https://uenf.br/reitoria/transparencia/9-informacoes-classificadas/' ),
				array( 'Serviço de Informação ao Cidadão (SIC)', 'https://uenf.br/reitoria/transparencia/10-servico-de-informacao-ao-cidadao-sic/' ),
				array( 'Perguntas Frequentes', 'https://uenf.br/reitoria/transparencia/11-perguntas-frequentes/' ),
				array( 'Dados Abertos', 'https://uenf.br/reitoria/transparencia/12-dados-abertos/' ),
				array( 'Boletim Oficial', 'https://uenf.br/reitoria/boletim-oficial/' ),
			),
		),
	);
}

/**
 * Links da barra superior (menu secundário do portal anterior).
 */
function uenf_portal_menu_secundario(): array {
	return array(
		array( 'Portal da Transparência', 'http://www.governoaberto.rj.gov.br/' ),
		array( 'OuvERJ', 'https://www.rj.gov.br/ouverj' ),
		array( 'Rádio UENF', 'https://radio.uenf.br/' ),
		array( 'Boletim Oficial', 'https://uenf.br/reitoria/boletim-oficial/' ),
		array( 'Período de Defeso Eleitoral', '/wp-content/uploads/2026/07/PERIODO-DE-DEFESO-ELEITORAL-Cartilha-1.pdf' ),
	);
}

/**
 * URL final de um item de menu.
 */
function uenf_portal_url( string $caminho ): string {
	return str_starts_with( $caminho, '/' ) ? home_url( $caminho ) : $caminho;
}

/**
 * Marcação de blocos (navigation-link / navigation-submenu) para uma lista de itens.
 *
 * @param array  $itens  Itens no formato [ rótulo, URL, filhos? ].
 * @param string $classe Classe CSS extra aplicada a cada item do primeiro nível.
 */
function uenf_portal_blocos_menu( array $itens, string $classe = '' ): string {
	$saida = '';
	foreach ( $itens as $item ) {
		$attrs = array(
			'label' => $item[0],
			'url'   => uenf_portal_url( $item[1] ),
			'kind'  => 'custom',
		);
		if ( $classe ) {
			$attrs['className'] = $classe;
		}
		$json = wp_json_encode( $attrs, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG | JSON_HEX_AMP );

		if ( empty( $item[2] ) ) {
			$saida .= "<!-- wp:navigation-link {$json} /-->\n";
		} else {
			$saida .= "<!-- wp:navigation-submenu {$json} -->\n" . uenf_portal_blocos_menu( $item[2] ) . "<!-- /wp:navigation-submenu -->\n";
		}
	}
	return $saida;
}
