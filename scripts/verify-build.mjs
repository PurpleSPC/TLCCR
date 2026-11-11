import { readFile, readdir, access } from 'node:fs/promises';
import { resolve, join, extname } from 'node:path';
import assert from 'node:assert/strict';
const root = resolve('dist');
const configuredBase = process.env.BASE_PATH || (process.env.GITHUB_ACTIONS === 'true' && process.env.GITHUB_REPOSITORY ? `/${process.env.GITHUB_REPOSITORY.split('/')[1]}/` : '/');
const base = `/${configuredBase.split('/').filter(Boolean).join('/')}`;
const prefix = base === '/' ? '' : base;
const files = [];
async function walk(dir) { for (const item of await readdir(dir, { withFileTypes: true })) { const path = join(dir, item.name); if (item.isDirectory()) await walk(path); else files.push(path); } }
await walk(root);
const exactFiles = new Set(files);
const pages = files.filter(file => extname(file) === '.html');
const missing = [];
let sharedHeader;
let sharedFooter;
for (const path of pages) {
  const html = await readFile(path, 'utf8');
  assert(!html.includes('/design-options/'), `Removed design routes remain linked in ${path}`);
  assert(!path.includes('design-options'), 'Design comparison routes must not be built.');
  assert(html.includes('class="journal"'), `Farm theme missing from ${path}`);
  assert(!html.includes('design study'), `Design-study metadata remains in ${path}`);
  assert.equal((html.match(/<h1[ >]/g) || []).length, 1, `Expected one page heading in ${path}`);
  const header = html.match(/<header class="concept-header">[\s\S]*?<\/header>/)?.[0].replace(/ aria-current="page"/g, '');
  const footer = html.match(/<footer class="concept-footer">[\s\S]*?<\/footer>/)?.[0];
  assert(header?.includes(`href="${prefix}/"`) && header.includes(`${prefix}/images/brand/critter-creek-logo-white.png`), `Shared farm logo/header missing in ${path}`);
  assert(footer?.includes("It's the pets' house, we just pay the mortgage!"), `Shared footer missing in ${path}`);
  sharedHeader ??= header;
  sharedFooter ??= footer;
  assert.equal(header, sharedHeader, `Header differs on ${path}`);
  assert.equal(footer, sharedFooter, `Footer differs on ${path}`);
  for (const match of html.matchAll(/(?:href|src|poster)="(\/[^"#?]*)(?:[?#][^"]*)?"/g)) {
    const href = decodeURIComponent(match[1]);
    if (href.startsWith('//')) continue;
    assert(!prefix || href.startsWith(`${prefix}/`), `URL escapes the GitHub Pages project path in ${path}: ${href}`);
    const local = prefix ? href.slice(prefix.length) : href;
    const target = join(root, local, local.endsWith('/') ? 'index.html' : '');
    assert(exactFiles.has(target), `Missing file or filename-case mismatch in ${path}: ${href}`);
    try { await access(target); } catch { missing.push({ page: path.slice(root.length), href }); }
  }
  for (const match of html.matchAll(/href="#[^"]+"|aria-(?:controls|labelledby|describedby)="([^"]+)"/g)) {
    const ids = match[1] ? match[1].split(/\s+/) : [match[0].slice(7,-1)];
    for (const id of ids) assert(html.includes(`id="${id}"`), `Missing fragment or accessibility target ${id} in ${path}`);
  }
  const canonical = html.match(/rel="canonical" href="([^"]+)"/)?.[1];
  assert(canonical && new URL(canonical).pathname.startsWith(`${prefix}/`), `Invalid canonical path in ${path}`);
  const shareImage = html.match(/property="og:image" content="([^"]+)"/)?.[1];
  assert(shareImage && new URL(shareImage).pathname.startsWith(`${prefix}/images/`), `Invalid share image in ${path}`);
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match=>match[1]);
  assert.equal(new Set(ids).size, ids.length, `Duplicate element IDs in ${path}`);
  assert(!html.includes('localhost:') && !html.includes('127.0.0.1:'), `Local preview URL leaked into ${path}`);
  assert(!/\b(?:src|href)="[A-Z]:[\\/]/.test(html), `Local file path leaked into ${path}`);
}
assert.deepEqual(missing, [], `Missing local page links or assets: ${JSON.stringify(missing)}`);
assert(!files.some(file => /[\\/]keystatic[\\/]/.test(file)), 'Local editor must not be published.');
const events = await readFile(join(root, 'events/index.html'), 'utf8');
assert(!events.includes('Example event'), 'Draft event leaked into the public page.');
assert(!files.some(file => file.includes('staff-example')), 'Draft event detail route leaked into the build.');
console.log(`Verified ${pages.length} pages: all local links/assets resolve, draft event is hidden, and local editor is excluded.`);
const homepage = await readFile(join(root, 'index.html'), 'utf8');
assert(homepage.includes('A little farm.') && homepage.includes('A bigger story.'), 'Selected homepage not promoted.');
assert(homepage.includes('data-schedule-visit') && homepage.includes('id="visit-chooser"'), 'Homepage visit chooser is missing.');
assert(/slideshow-swans\.(?:jpg|webp)/.test(homepage) && /slideshow-horses-creek\.(?:jpg|webp)/.test(homepage), 'Homepage slideshow not retained.');
console.log('Farm Journal is the homepage; every page shares its theme, logo, header, and footer.');
console.log(`Checked URL prefix ${prefix || '/'}, metadata, fragments, accessibility references, and unique IDs.`);
