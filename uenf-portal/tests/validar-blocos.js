// Valida no editor de blocos a marcação de padrões, modelos e partes do tema.
// Uso: WP_USER=... WP_PASS=... node tests/validar-blocos.js http://127.0.0.1:8080
const { chromium } = require('playwright');
(async () => {
  const base = process.argv[2] || 'http://127.0.0.1:8080';
  const usuario = process.env.WP_USER, senha = process.env.WP_PASS;
  if (!usuario || !senha) { console.error('Defina WP_USER e WP_PASS (usuário administrador do site de teste).'); process.exit(2); }
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(base + '/wp-login.php');
  await p.fill('#user_login', usuario); await p.fill('#user_pass', senha);
  await p.click('#wp-submit'); await p.waitForLoadState('networkidle');
  await p.goto(base + '/wp-admin/post-new.php?post_type=page', { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => window.wp && wp.blocks && wp.blocks.getBlockTypes().length > 50 && wp.apiFetch, null, { timeout: 60000 });
  const r = await p.evaluate(async () => {
    const out = [];
    const fontes = [];
    const pats = await wp.apiFetch({ path: '/wp/v2/block-patterns/patterns' });
    pats.filter(x => x.name.startsWith('uenf/')).forEach(x => fontes.push(['padrão ' + x.name, x.content]));
    for (const tipo of ['templates', 'template-parts']) {
      const ts = await wp.apiFetch({ path: '/wp/v2/' + tipo + '?per_page=100&context=edit' });
      ts.filter(x => x.theme === 'uenf-portal').forEach(x => fontes.push([tipo + ' ' + x.slug, x.content.raw]));
    }
    const logs = [];
    const orig = { e: console.error, w: console.warn, i: console.info, l: console.log };
    const walk = (blocks, fonte) => blocks.forEach(bl => {
      if (bl.name === 'core/missing') out.push(fonte + ' :: bloco desconhecido ' + (bl.attributes.originalName));
      if (!bl.isValid) out.push(fonte + ' :: INVÁLIDO ' + bl.name + ' :: ' + (bl.validationIssues || []).map(i => i.args.map(a => typeof a === 'string' ? a : JSON.stringify(a)).join(' ').slice(0, 700)).join(' || '));
      walk(bl.innerBlocks || [], fonte);
    });
    let total = 0;
    for (const [fonte, conteudo] of fontes) { const bs = wp.blocks.parse(conteudo); total += bs.length; walk(bs, fonte); }
    return { fontes: fontes.map(f => f[0]), total, out };
  });
  console.log(r.fontes.length + ' fontes verificadas:', r.fontes.join(', '));
  console.log(r.out.length ? r.out.join('\n') : 'Nenhum bloco inválido.');
  await b.close();
  process.exit(r.out.length ? 1 : 0);
})();
