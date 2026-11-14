// Testes funcionais de navegador (Playwright) do tema UENF Portal.
// Uso: WP_USER=<login do autor dos posts> node tests/funcional.js http://127.0.0.1:8080
// Pressupõe um site de teste com posts nas categorias "noticias" e "editais",
// páginas /noticias/, /editais/, /institucional/ e /institucional/sobre-a-uenf/ (modelo elementor_header_footer).
const { chromium } = require('playwright');
(async () => {
  const B = process.argv[2] || 'http://127.0.0.1:8080'; const b = await chromium.launch();
  const ok = (n, c, x='') => console.log((c ? 'OK   ' : 'FALHA') + ' ' + n + (x ? ' — ' + x : ''));
  const ctx = await b.newContext({ viewport: { width: 1366, height: 900 } }); const p = await ctx.newPage();
  const erros = []; p.on('pageerror', e => erros.push(e.message)); p.on('console', m => m.type() === 'error' && erros.push(m.text()));
  await p.goto(B + '/', { waitUntil: 'networkidle' });
  // banners
  ok('banner rotativo exibe exatamente um banner', await p.locator('.is-style-banner-rotativo > .uenf-banner:visible').count() === 1);
  ok('banner: versão desktop visível, mobile oculta', await p.locator('.uenf-banner .uenf-so-desktop:visible').count() === 1 && await p.locator('.uenf-banner .uenf-so-mobile:visible').count() === 0);
  // home queries
  const nNot = await p.locator('.uenf-destaque .wp-block-post, .uenf-lista-recentes .wp-block-post, .uenf-secao .uenf-grade-posts .wp-block-post').count();
  ok('home: 9 notícias', nNot === 9, String(nNot));
  const tit = await p.locator('.uenf-secao .wp-block-post-title').allTextContents();
  ok('home: notícias sem repetição', new Set(tit.slice(0, 9)).size === 9);
  ok('home: 9 editais', await p.locator('.uenf-lista-editais .wp-block-post').count() === 9);
  ok('home: destaque usa a 1ª imagem do conteúdo', await p.locator('.uenf-destaque__midia img').count() === 1);
  // modelos do Design System
  const filtros = p.locator('.uenf-secao .is-style-filtros');
  ok('filtros por categoria em Notícias e Editais, com o primeiro ativo', await filtros.count() === 2 && await filtros.nth(0).locator('.is-ativo a').count() === 1 && await filtros.nth(0).locator('a').count() >= 3, (await filtros.nth(0).locator('a').allTextContents()).join(' | '));
  const hrefFiltro = await filtros.nth(0).locator('a >> nth=1').getAttribute('href');
  ok('filtro aponta para o arquivo da categoria', /\/categoria\//.test(hrefFiltro), hrefFiltro);
  ok('botão "Mais notícias" abaixo da lista', await p.locator('.uenf-noticias__topo .is-style-bloco a').count() === 1);
  const selos = await p.locator('.uenf-lista-editais .uenf-selo').allTextContents();
  ok('editais: selo só para tags de situação', selos.length === 5 && !selos.join().includes('editalproppg'), selos.join(' | '));
  ok('cursos: 3 grupos e 21 cursos com link', await p.locator('.uenf-cursos__grupo').count() === 3 && await p.locator('.uenf-cursos .is-style-chips a').count() === 21 && await p.locator('.uenf-cursos .uenf-licenciatura').count() === 8);
  ok('pró-reitorias em cartões escuros', await p.locator('.uenf-pro-reitoria.is-style-cartao-escuro').count() === 4 && await p.locator('.uenf-pro-reitoria .is-style-links a').count() === 11);
  ok('formas de ingresso: 4 passos numerados + 4 opções', await p.locator('.is-style-passos li').count() === 4 && await p.locator('.is-style-opcoes li').count() === 4);
  ok('faixa "Já é estudante?" com 3 botões', await p.locator('.is-style-faixa-chamada .wp-block-button a').count() === 3);
  ok('documentos: 6 cartões clicáveis', await p.locator('.uenf-documentos .uenf-cartao-horizontal h3 a').count() === 6);
  // contadores
  const cont = p.locator('.is-style-contador'); const finais = ['2','5','14','20','20','320','191','7.500'];
  await cont.first().scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
  const meio = await cont.last().textContent(); await p.waitForTimeout(2600);
  const fim = await cont.allTextContents();
  ok('contadores animam e terminam no valor original', JSON.stringify(fim.map(s => s.trim())) === JSON.stringify(finais) && meio.trim() !== '7.500', 'meio=' + meio.trim() + ' fim=' + fim.join(','));
  // menu dropdown
  await p.evaluate(() => scrollTo(0, 0));
  await p.hover('.uenf-menu-principal .wp-block-navigation-submenu >> nth=0'); await p.waitForTimeout(400);
  ok('menu: submenu abre ao passar o mouse', await p.locator('.uenf-menu-principal .wp-block-navigation__submenu-container >> nth=0').locator('a:visible').count() === 11);
  ok('menu: 6 itens principais + 41 subitens', await p.locator('.uenf-menu-principal .wp-block-navigation__container > li:not(.uenf-so-sobreposicao)').count() === 6 && await p.locator('.uenf-menu-principal .wp-block-navigation__submenu-container a').count() === 41 + 0, String(await p.locator('.uenf-menu-principal .wp-block-navigation__submenu-container a').count()));
  ok('barra superior: 5 links + 4 redes', await p.locator('.uenf-menu-secundario a:visible').count() === 5 && await p.locator('.uenf-barra-superior .wp-social-link').count() === 4);
  // busca do cabeçalho
  await p.mouse.move(5, 500);
  await p.click('.uenf-busca-topo button'); await p.waitForTimeout(400);
  await p.fill('.uenf-busca-topo input[type=search]', 'edital'); await Promise.all([p.waitForURL(/s=edital/), p.keyboard.press('Enter')]); await p.waitForLoadState('networkidle');
  ok('busca do cabeçalho leva aos resultados', p.url().includes('s=edital') && await p.locator('.uenf-resultado').count() > 0, p.url() + ' ' + await p.locator('.uenf-resultado').count() + ' resultados');
  ok('busca: título e paginação', (await p.locator('h1').first().textContent()).toLowerCase().includes('edital') && await p.locator('.wp-block-query-pagination a').count() > 0, await p.locator('h1').first().textContent());
  // acessibilidade
  await p.click('.uenf-a11y__alternar'); await p.click('[data-acao="alto-contraste"]'); await p.click('[data-acao="aumentar"]'); await p.click('[data-acao="sublinhado"]');
  let st = await p.evaluate(() => [document.documentElement.className, document.documentElement.style.fontSize, getComputedStyle(document.querySelector('.wp-site-blocks')).backgroundColor]);
  ok('acessibilidade: alto contraste + texto maior + sublinhado', st[0].includes('uenf-a11y-alto-contraste') && st[0].includes('uenf-a11y-sublinhado') && st[1] === '110%' && st[2] === 'rgb(0, 0, 0)', st.join(' | '));
  
  await p.click('[data-acao="cinza"]');
  st = await p.evaluate(() => document.documentElement.className);
  ok('acessibilidade: modos de cor são exclusivos', st.includes('uenf-a11y-cinza') && !st.includes('alto-contraste'));
  await p.goto(B + '/noticias/', { waitUntil: 'networkidle' });
  st = await p.evaluate(() => [document.documentElement.className, document.documentElement.style.fontSize]);
  ok('acessibilidade: preferência persiste entre páginas', st[0].includes('uenf-a11y-cinza') && st[1] === '110%');
  await p.click('.uenf-a11y__alternar'); await p.click('[data-acao="redefinir"]');
  st = await p.evaluate(() => [document.documentElement.className, document.documentElement.style.fontSize]);
  ok('acessibilidade: redefinir limpa tudo', !st[0].includes('uenf-a11y') && st[1] === '');
  // listagem + paginação
  const pg1 = await p.locator('.uenf-grade-posts .wp-block-post-title').allTextContents();
  ok('página Notícias: 9 cartões + paginação', pg1.length === 9 && await p.locator('.wp-block-query-pagination-numbers a').count() > 0);
  const r = await p.goto(B + '/noticias/2/', { waitUntil: 'networkidle' });
  const pg2 = await p.locator('.uenf-grade-posts .wp-block-post-title').allTextContents();
  ok('URL antiga /noticias/2/ redireciona para a paginação nativa', p.url().includes('query-1-page=2') && pg2.length > 0 && pg2[0] !== pg1[0], p.url());
  ok('trilha de navegação presente', await p.locator('.uenf-trilha .wp-block-breadcrumbs a').count() >= 1, (await p.locator('.uenf-trilha').innerText()).replace(/\n/g, ' '));
  // post
  await p.goto(B + '/noticias/', { waitUntil: 'networkidle' });
  await p.click('.uenf-grade-posts .wp-block-post-title a >> nth=1'); await p.waitForLoadState('networkidle');
  const hrefs = await p.locator('.is-style-compartilhar a').evaluateAll(as => as.map(a => a.href));
  const enc = encodeURIComponent(p.url());
  ok('compartilhar: Facebook, LinkedIn e WhatsApp com a URL do post', hrefs.length === 3 && hrefs[0].startsWith('https://www.facebook.com/sharer/sharer.php?u=' + enc) && hrefs[1].includes('linkedin.com') && hrefs[1].includes(enc) && hrefs[2].includes('whatsapp'), hrefs[0]);
  const h1 = (await p.locator('h1').textContent()).trim();
  const rel = await p.locator('.uenf-relacionados .wp-block-post-title').allTextContents();
  ok('leia também: 4 posts, sem o post atual', rel.length === 4 && !rel.map(s => s.trim()).includes(h1));
  ok('post: data, autor e categoria com link', await p.locator('.uenf-meta--artigo a').count() === 3, (await p.locator('.uenf-meta--artigo').innerText()).replace(/\n/g, ' | '));
  ok('post: barra lateral com 3 notícias + 3 editais', await p.locator('.uenf-lateral .wp-block-post').count() === 6);
  ok('post: imagem do conteúdo não é duplicada no topo', await p.locator('.uenf-artigo > .wp-block-post-featured-image').count() === 0);
  // arquivos
  for (const [u, n] of [['/categoria/editais/', 'categoria'], ['/author/' + (process.env.WP_USER || 'admin') + '/', 'autor'], ['/2026/11/', 'data']]) {
    const rr = await p.goto(B + u, { waitUntil: 'networkidle' });
    ok('arquivo de ' + n, rr.status() === 200 && await p.locator('.uenf-grade-posts .wp-block-post').count() > 0, (await p.locator('h1').first().textContent()).trim());
  }
  // modelos legados
  await p.goto(B + '/institucional/sobre-a-uenf/', { waitUntil: 'networkidle' });
  ok('página com modelo antigo do Elementor usa "Página livre"', await p.locator('main.uenf-pagina-livre').count() === 1 && await p.locator('.uenf-lateral').count() === 0);
  await p.goto(B + '/institucional/', { waitUntil: 'networkidle' });
  ok('página padrão: título, conteúdo e barra lateral', await p.locator('.uenf-artigo h1').count() === 1 && await p.locator('.uenf-lateral').count() === 2);
  // 404
  const r4 = await p.goto(B + '/nao-existe/', { waitUntil: 'networkidle' });
  ok('404: mensagem, busca e botão para a página inicial', r4.status() === 404 && await p.locator('.uenf-nao-encontrada input[type=search]').count() === 1 && (await p.locator('.uenf-nao-encontrada .wp-block-button a').getAttribute('href')) === B + '/');
  // rodapé
  ok('rodapé: 8 contatos, 2 endereços, 4 redes', await p.locator('.uenf-rodape__contatos p').count() === 8 && await p.locator('.uenf-rodape a[href*="maps.app"]').count() === 2 && await p.locator('.uenf-rodape .wp-social-link').count() === 4);
  ok('link "pular para o conteúdo"', await p.locator('a.skip-link').count() === 1);
  // mobile
  const m = await b.newContext({ viewport: { width: 390, height: 800 } }); const q = await m.newPage(); q.on('pageerror', e => erros.push(e.message));
  await q.goto(B + '/', { waitUntil: 'networkidle' });
  ok('celular: banner mobile visível', await q.locator('.uenf-banner .uenf-so-mobile:visible').count() === 1 && await q.locator('.uenf-banner .uenf-so-desktop:visible').count() === 0);
  ok('celular: sem rolagem horizontal', await q.evaluate(() => document.documentElement.scrollWidth <= innerWidth), String(await q.evaluate(() => document.documentElement.scrollWidth)));
  await q.click('.uenf-menu-principal .wp-block-navigation__responsive-container-open'); await q.waitForTimeout(500);
  ok('celular: menu sobreposto com itens principais e links da barra superior', await q.locator('.uenf-menu-principal .is-menu-open .wp-block-navigation__container > li:visible').count() === 11);
  
  // acessibilidade (regressões da auditoria)
  await q.keyboard.press('Escape');
  await q.evaluate(() => localStorage.setItem('uenfA11y', JSON.stringify({ classes: ['cinza'], escala: 100 })));
  await q.reload({ waitUntil: 'networkidle' });
  await q.click('.uenf-menu-principal .wp-block-navigation__responsive-container-open'); await q.waitForTimeout(500);
  const alturaMenu = await q.evaluate(() => Math.round(document.querySelector('.uenf-menu-principal .wp-block-navigation__responsive-container.is-menu-open').getBoundingClientRect().height));
  ok('modo tons de cinza: menu sobreposto continua do tamanho da tela (rolável)', alturaMenu <= 800, alturaMenu + 'px');
  await q.keyboard.press('Escape'); await q.evaluate(() => localStorage.removeItem('uenfA11y'));
  await p.goto(B + '/', { waitUntil: 'networkidle' });
  const niveis = await p.evaluate(() => [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => h.offsetParent).map(h => +h.tagName[1]));
  ok('títulos sem salto de nível na página inicial', niveis[0] === 1 && niveis.filter(n => n === 1).length === 1 && niveis.every((n, i) => i === 0 || n - niveis[i - 1] <= 1), niveis.join(''));
  await p.goto(B + '/noticias/', { waitUntil: 'networkidle' });
  const niveis2 = await p.evaluate(() => [...document.querySelectorAll('main h1,main h2,main h3')].map(h => +h.tagName[1]));
  ok('títulos sem salto de nível na listagem', niveis2.every((n, i) => i === 0 || n - niveis2[i - 1] <= 1), niveis2.join(''));
  await p.goto(B + '/', { waitUntil: 'networkidle' });
  ok('links sem nome acessível: nenhum', await p.evaluate(() => [...document.querySelectorAll('.wp-site-blocks a[href]')].filter(a => !a.getAttribute('aria-hidden') && !(a.textContent || '').trim() && !a.getAttribute('aria-label') && !a.querySelector('img[alt]:not([alt=""])')).length) === 0);
  await p.focus('.uenf-hero__busca input[type=search]');
  ok('busca da abertura mostra foco', await p.evaluate(() => getComputedStyle(document.querySelector('.uenf-hero__busca .wp-block-search__inside-wrapper')).outlineStyle) === 'solid');
  ok('filtro ativo com aria-current', await p.locator('.is-style-filtros .is-ativo a[aria-current="true"]').count() === 2);
  ok('barra de acessibilidade é região nomeada no início da página', await p.evaluate(() => { const a = document.querySelector('aside.uenf-a11y[aria-label]'); return !!a && a.compareDocumentPosition(document.querySelector('.wp-site-blocks')) & Node.DOCUMENT_POSITION_FOLLOWING; }) > 0);
  ok('contador: leitor de tela recebe o valor final durante a animação', await p.evaluate(async () => { const el = [...document.querySelectorAll('.is-style-contador')].pop(); el.scrollIntoView(); await new Promise(r => setTimeout(r, 500)); const sr = el.querySelector('.screen-reader-text'); return sr ? sr.textContent : el.textContent; }) === '7.500');
  const t = await b.newContext({ viewport: { width: 820, height: 1000 } }); const tp = await t.newPage();
  await tp.goto(B + '/', { waitUntil: 'networkidle' });
  ok('tablet: menu sobreposto, sem rolagem horizontal', await tp.locator('.uenf-menu-principal .wp-block-navigation__responsive-container-open:visible').count() === 1 && await tp.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  
  const reais = erros.filter(e => !/status of 404/.test(e)); ok('sem erros de JavaScript', reais.length === 0, erros.slice(0, 3).join(' / '));
  await b.close();
})();
