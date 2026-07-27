/**
 * Runtime check for the mobile navigation.
 *
 * The section links are display:none above nothing and hidden below 48rem, so
 * a phone reaches them only through the disclosure button. That behaviour is
 * entirely script-driven, which means the built markup proves nothing on its
 * own — this executes the page's inline modules and drives the button.
 *
 *   node scripts/check_nav_runtime.mjs
 */

import { readFileSync } from 'node:fs';
import { JSDOM } from 'jsdom';

const DIST = new URL('../dist/', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const html = readFileSync(`${DIST}index.html`, 'utf8');

const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true });
const { window } = dom;
const doc = window.document;

// jsdom has no layout, so matchMedia always reports false. The nav script asks
// whether the viewport is wide; stub it to answer "phone".
window.matchMedia = (query) => ({
  matches: false,
  media: query,
  addEventListener() {},
  removeEventListener() {},
  addListener() {},
  removeListener() {},
  dispatchEvent: () => false,
});

// Run every inline module in document order; the nav logic lives in one of them.
for (const script of doc.querySelectorAll('script')) {
  if (script.src) continue;
  try {
    window.eval(script.textContent);
  } catch {
    /* modules that need imports are covered by check_chart_runtime.mjs */
  }
}

const failures = [];
const check = (label, ok, detail = '') => {
  if (!ok) failures.push(label);
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}${detail ? `  (${detail})` : ''}`);
};

const toggle = doc.querySelector('[data-nav-toggle]');
const menu = doc.querySelector('[data-nav]');
const links = [...doc.querySelectorAll('[data-nav] a')];

check('toggle button exists', Boolean(toggle));
check('nav exists', Boolean(menu));
check('all five section links present', links.length === 5, links.map((a) => a.textContent).join(', '));
check('button controls the nav by id', toggle?.getAttribute('aria-controls') === menu?.id, menu?.id);
check('starts collapsed', toggle?.getAttribute('aria-expanded') === 'false');
check('starts with no data-open', !menu?.hasAttribute('data-open'));

toggle?.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
check('opens on click', toggle?.getAttribute('aria-expanded') === 'true');
check('nav marked open', menu?.hasAttribute('data-open'));
check('label updates when open', /close/i.test(toggle?.getAttribute('aria-label') ?? ''), toggle?.getAttribute('aria-label'));

// Following a link must dismiss the panel that is covering the target.
links[0]?.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
check('closes after following a link', toggle?.getAttribute('aria-expanded') === 'false');

toggle?.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
doc.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
check('closes on Escape', toggle?.getAttribute('aria-expanded') === 'false');

toggle?.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
doc.body.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
check('closes on outside click', toggle?.getAttribute('aria-expanded') === 'false');

/*
 * Cascade order, checked against the compiled CSS.
 *
 * jsdom has no layout or media-query evaluation, so every assertion above
 * passed while the button was still visible on desktop: the base rule sat
 * after the desktop media query, and at equal specificity the later rule won.
 * The button showed on desktop and did nothing, because the panel styles it
 * drives are declared in the mobile query.
 */
const cssHref = doc.querySelector('link[rel="stylesheet"]')?.getAttribute('href');
if (cssHref) {
  const css = readFileSync(`${DIST}${cssHref.replace(/^\//, '')}`, 'utf8');
  const rules = [...css.matchAll(/\.nav-toggle\[data-astro-cid-\w+\]\{([^}]*)\}/g)];
  const base = rules.find((m) => m[1].includes('display:grid'));
  const hide = rules.find((m) => m[1].trim() === 'display:none');

  check('base toggle rule found in CSS', Boolean(base));
  check('desktop hide rule found in CSS', Boolean(hide));
  check(
    'desktop hide is declared after the base rule',
    Boolean(base && hide) && hide.index > base.index,
    `base@${base?.index} hide@${hide?.index}`,
  );
}

console.log();

// The page runs a requestAnimationFrame loop for the ticker, which jsdom keeps
// servicing forever — without tearing the window down and exiting explicitly,
// this process never returns.
dom.window.close();

if (failures.length) {
  console.error(`${failures.length} FAILED:\n  ` + failures.join('\n  '));
  process.exit(1);
}
console.log('All nav runtime checks passed.');
process.exit(0);
