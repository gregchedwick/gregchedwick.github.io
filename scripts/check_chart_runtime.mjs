/**
 * Runtime check for the Netflix chart.
 *
 * The chart re-renders its rows in the browser, so verifying dist/index.html
 * proves nothing about what a visitor actually sees — that markup is replaced
 * the moment the script runs. This loads the built page in a DOM, executes the
 * bundle, and asserts against the post-render tree.
 *
 * It exists because a real bug shipped this way: rows built with
 * document.createElement carry none of Astro's scoping attributes, so the
 * scoped CSS never matched and the bars had no width or height at all.
 *
 *   node scripts/check_chart_runtime.mjs
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { JSDOM } from 'jsdom';

const DIST = new URL('../dist/', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');

const html = readFileSync(join(DIST, 'index.html'), 'utf8');
const bundle = readdirSync(join(DIST, '_astro')).find(
  (f) => f.startsWith('NetflixDashboard') && f.endsWith('.js'),
);
if (!bundle) throw new Error('No NetflixDashboard bundle found in dist/_astro');

const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true });
const { window } = dom;

// The bundle is an ES module importing the JSON payload; inline it so the
// module graph resolves without a server.
const data = readFileSync(new URL('../src/data/netflix-ads.json', import.meta.url), 'utf8');
let code = readFileSync(join(DIST, '_astro', bundle), 'utf8');
code = code.replace(/^import\s+(\w+)\s+from\s*"[^"]+";?/m, `const $1 = ${data};`);

window.eval(code);

const failures = [];
const check = (label, ok, detail = '') => {
  if (!ok) failures.push(`${label}${detail ? ` — ${detail}` : ''}`);
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}${detail ? `  (${detail})` : ''}`);
};

const doc = window.document;
const rows = [...doc.querySelectorAll('[data-titles] .bar-row')];
check('rows rendered', rows.length > 0, `${rows.length} rows`);

// The crux: cloned rows must keep the scoping attribute or no CSS applies.
const cid = Object.keys(doc.querySelector('.panel').attributes).length
  ? [...doc.querySelector('.panel').attributes].map((a) => a.name).find((n) => n.startsWith('data-astro-cid'))
  : null;
check('scope attribute known', Boolean(cid), cid ?? 'none');

for (const sel of ['.bar-row__track', '.bar-row__bar', '.bar-row__title', '.bar-row__value', '.bar-row__meta']) {
  const el = rows[0]?.querySelector(sel);
  check(`${sel} exists`, Boolean(el));
  check(`${sel} carries ${cid}`, Boolean(el?.hasAttribute(cid)));
}

const widths = rows.map((r) => r.querySelector('.bar-row__bar')?.style.getPropertyValue('--pct'));
check('every bar has a width', widths.every((w) => w && w !== '0%'), `first: ${widths[0]}`);
check('exactly one clipped bar', rows.filter((r) => r.querySelector('.bar-row__bar')?.dataset.clipped === 'true').length === 1);

// Tooltip children must be server-rendered for the same reason.
const head = doc.querySelector('[data-tip-head]');
const body = doc.querySelector('[data-tip-body]');
check('tooltip head carries scope', Boolean(head?.hasAttribute(cid)));
check('tooltip body carries scope', Boolean(body?.hasAttribute(cid)));

// Re-sorting must keep all of the above true.
doc.querySelector('[data-sort="hoursViewed"]').click();
const after = [...doc.querySelectorAll('[data-titles] .bar-row')];
check('re-sort keeps scope attribute', after.every((r) => r.querySelector('.bar-row__bar')?.hasAttribute(cid)));
check('re-sort keeps widths', after.every((r) => {
  const w = r.querySelector('.bar-row__bar')?.style.getPropertyValue('--pct');
  return w && w !== '0%';
}));
check('re-sort updates heading',
  doc.querySelector('[data-title-heading]').textContent === 'Top Titles by Hours Viewed',
  doc.querySelector('[data-title-heading]').textContent);

console.log();
if (failures.length) {
  console.error(`${failures.length} FAILED:\n  ` + failures.join('\n  '));
  process.exit(1);
}
console.log('All runtime checks passed.');
