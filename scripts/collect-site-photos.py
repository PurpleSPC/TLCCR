"""Archive public Critter Creek photos with provenance and duplicate detection.

Uses the public WordPress media index plus page HTML, linked CSS, and sitemaps.
Only requests the ranch's own public host. Never reads form-upload directories.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, UnidentifiedImageError

BASE = 'https://crittercreekranch.org'
ROOT = Path(__file__).resolve().parents[2]
PHOTO_ROOT = ROOT / 'Photos'
DEST = PHOTO_ROOT / 'From-current-site'
DEST.mkdir(parents=True, exist_ok=True)
USER_AGENT = 'CritterCreekRedesignAssetCollector/1.0 (public photo migration)'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}
references = defaultdict(set)
image_alts = defaultdict(set)
page_report = []
failures = []


def clean_url(value, relative_to=BASE):
    value = html.unescape(str(value)).replace('\\/', '/').strip(' \t\r\n\'"')
    url = urllib.parse.urljoin(relative_to, value)
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ('http', 'https') or parsed.hostname not in ('crittercreekranch.org', 'www.crittercreekranch.org'):
        return None
    path = urllib.parse.unquote(parsed.path)
    if '/wpforms/' in path.lower() or '/wp-admin/' in path.lower():
        return None
    return BASE + urllib.parse.quote(path, safe='/@:+,;=-_.~()')


def image_key(url):
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
    # WordPress thumbnail and retina filenames are alternative sizes of one photo.
    return re.sub(r'-\d+x\d+(?=\.[^.]+$)', '', path).lower()


def get(url, timeout=35, retries=2):
    if not clean_url(url):
        raise ValueError('Outside the public ranch host or excluded upload directory')
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if not clean_url(response.url):
                    raise ValueError('Redirected outside the ranch host')
                return response.read(), dict(response.headers.items()), response.url
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt + 1 == retries:
                raise
            time.sleep(1)


def add_image(url, source, alt=''):
    normalized = clean_url(url, source)
    if normalized and '/wp-content/uploads/' in normalized and Path(urllib.parse.urlsplit(normalized).path).suffix.lower() in IMAGE_EXTENSIONS:
        references[normalized].add(source)
        if alt:
            image_alts[normalized].add(html.unescape(alt))


class PageParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.links = set()
        self.stylesheets = set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        for field in ('src', 'data-src', 'data-lazy-src', 'data-original', 'data-full', 'data-large_image', 'href', 'content'):
            value = attrs.get(field)
            if value:
                add_image(value, self.source, attrs.get('alt', ''))
        for field in ('srcset', 'data-srcset', 'data-lazy-srcset'):
            for candidate in (attrs.get(field) or '').split(','):
                if candidate.strip():
                    add_image(candidate.strip().split()[0], self.source, attrs.get('alt', ''))
        if tag == 'a' and attrs.get('href'):
            link = clean_url(attrs['href'], self.source)
            if link:
                self.links.add(link)
        if tag == 'link' and 'stylesheet' in attrs.get('rel', '') and attrs.get('href'):
            link = clean_url(attrs['href'], self.source)
            if link:
                self.stylesheets.add(link)


def extract_images(text, source):
    decoded = html.unescape(text).replace('\\/', '/')
    for value in re.findall(r'''(?:https?:)?//(?:www\.)?crittercreekranch\.org/[^\s<>"'()\\]+''', decoded, re.I):
        add_image(value, source)
    for value in re.findall(r'''url\(\s*["']?([^\s"')]+)''', decoded, re.I):
        add_image(value, source)


def api_entries(kind):
    entries = []
    page = 1
    while True:
        fields = 'id,date,link,source_url,media_type,mime_type,media_details,alt_text,title,caption,post' if kind == 'media' else 'id,link,title,content'
        url = f'{BASE}/wp-json/wp/v2/{kind}?per_page=100&page={page}&_fields={fields}'
        try:
            body, headers, _ = get(url)
            data = json.loads(body)
            if not isinstance(data, list):
                raise ValueError('Expected a public WordPress collection')
        except Exception as error:
            failures.append({'stage': f'{kind} index', 'url': url, 'error': str(error)})
            break
        entries.extend(data)
        print(f'Indexed {kind} page {page}: {len(data)} entries', flush=True)
        total_pages = int(next((value for key, value in headers.items() if key.lower() == 'x-wp-totalpages'), '1'))
        if page >= total_pages or not data:
            break
        page += 1
    return entries


print('Reading public media inventory...', flush=True)
media = api_entries('media')
attachment_pages = {clean_url(item.get('link', '')) for item in media}
api_pages = api_entries('pages') + api_entries('posts')
page_queue = deque([BASE + '/'])
for item in api_pages:
    source = clean_url(item.get('link', ''))
    if source:
        page_queue.append(source)
        rendered = item.get('content', {}).get('rendered', '')
        parser = PageParser(source)
        parser.feed(rendered)
        extract_images(rendered, source)

# The robots file advertises the site's canonical sitemap index.
sitemap_queue = deque([BASE + '/sitemap_index.xml'])
seen_sitemaps = set()
while sitemap_queue:
    sitemap = sitemap_queue.popleft()
    if sitemap in seen_sitemaps:
        continue
    seen_sitemaps.add(sitemap)
    try:
        body, _, _ = get(sitemap)
        tree = ET.fromstring(body)
        is_index = tree.tag.endswith('sitemapindex')
        for node in tree.iter():
            if not node.tag.endswith('loc') or not node.text:
                continue
            url = clean_url(node.text)
            if not url:
                continue
            if is_index:
                if 'attachment' not in url:
                    sitemap_queue.append(url)
            elif Path(urllib.parse.urlsplit(url).path).suffix.lower() in IMAGE_EXTENSIONS:
                add_image(url, sitemap)
            elif url not in attachment_pages and '/wp-content/' not in url:
                page_queue.append(url)
    except Exception as error:
        failures.append({'stage': 'sitemap', 'url': sitemap, 'error': str(error)})

seen_pages = set()
stylesheets = set()
while page_queue:
    source = page_queue.popleft()
    if source in seen_pages or source in attachment_pages:
        continue
    if re.search(r'/wp-json/|/feed/|/wp-content/|/author/|/tag/|/category/', source):
        continue
    if Path(urllib.parse.urlsplit(source).path).suffix.lower() not in ('', '.html', '.htm', '.php'):
        continue
    seen_pages.add(source)
    try:
        body, headers, final_url = get(source)
        text = body.decode('utf-8', errors='replace')
        parser = PageParser(source)
        parser.feed(text)
        extract_images(text, source)
        stylesheets.update(parser.stylesheets)
        page_queue.extend(sorted(parser.links - seen_pages - attachment_pages))
        page_report.append({'url': source, 'status': 'ok', 'final_url': final_url})
    except Exception as error:
        page_report.append({'url': source, 'status': 'failed', 'error': str(error)})
        failures.append({'stage': 'page', 'url': source, 'error': str(error)})
    print(f'Crawled page {len(seen_pages)}: {source}', flush=True)

for stylesheet in sorted(stylesheets):
    try:
        body, _, _ = get(stylesheet)
        extract_images(body.decode('utf-8', errors='replace'), stylesheet)
    except Exception as error:
        failures.append({'stage': 'stylesheet', 'url': stylesheet, 'error': str(error)})

# Select one original per WordPress media entry, plus images discovered only in HTML/CSS.
assets = {}
variant_to_original = {}
for item in media:
    if item.get('media_type') != 'image' or not item.get('source_url'):
        continue
    source = clean_url(item['source_url'])
    if not source or Path(urllib.parse.urlsplit(source).path).suffix.lower() not in IMAGE_EXTENSIONS:
        continue
    details = item.get('media_details') or {}
    original = details.get('original_image')
    download_url = clean_url(urllib.parse.urljoin(source, original)) if original else source
    if not download_url:
        continue
    variants = {source, download_url}
    for size in (details.get('sizes') or {}).values():
        if isinstance(size, dict) and size.get('source_url'):
            normalized = clean_url(size['source_url'])
            if normalized:
                variants.add(normalized)
    for variant in variants:
        variant_to_original[image_key(variant)] = download_url
    title = html.unescape(re.sub('<[^>]+>', '', item.get('title', {}).get('rendered', '')))
    caption = html.unescape(re.sub('<[^>]+>', '', item.get('caption', {}).get('rendered', ''))).strip()
    assets.setdefault(download_url, {'url': download_url, 'fallback_url': source, 'media_ids': [], 'title': title, 'caption': caption, 'alt': item.get('alt_text', ''), 'source_pages': set()})
    assets[download_url]['media_ids'].append(item['id'])

for url, pages in references.items():
    original = variant_to_original.get(image_key(url))
    if not original:
        # A full-size path exposed only in a gallery is worth trying before a thumbnail.
        original = re.sub(r'-\d+x\d+(?=\.[^.]+$)', '', url)
    asset = assets.setdefault(original, {'url': original, 'fallback_url': url, 'media_ids': [], 'title': '', 'caption': '', 'alt': '; '.join(sorted(image_alts[url])), 'source_pages': set()})
    asset['source_pages'].update(pages)

for asset in assets.values():
    asset['source_pages'] = sorted(asset['source_pages'])

inventory_path = DEST / 'crawl-inventory.json'
inventory_path.write_text(json.dumps({'media_index_entries': len(media), 'pages': page_report, 'assets': list(assets.values())}, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Inventory ready: {len(media)} media entries, {len(seen_pages)} pages, {len(assets)} original image candidates.', flush=True)

existing_by_hash = {}
for path in PHOTO_ROOT.rglob('*'):
    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
        existing_by_hash[hashlib.sha256(path.read_bytes()).hexdigest()] = str(path.relative_to(ROOT))
known_by_url = {}
for manifest_name in ('sources.json', 'photo-library.json'):
    manifest = DEST / manifest_name
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding='utf-8-sig'))
        entries = data if isinstance(data, list) else data.get('images', [])
        for item in entries:
            url = item.get('source') or item.get('url')
            file = item.get('file')
            if url and file:
                path = ROOT / file
                if not path.exists():
                    path = DEST / file
                if path.exists():
                    known_by_url[clean_url(url)] = path

lock = threading.Lock()


def describe(data):
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        return image.size, image.format


def collect(asset):
    result = dict(asset)
    url = asset['url']
    try:
        known = known_by_url.get(url)
        if known:
            data = known.read_bytes()
            (width, height), file_format = describe(data)
            result.update(status='already-present', file=str(known.relative_to(ROOT)), width=width, height=height, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            return result
        try:
            data, _, actual_url = get(url)
        except Exception:
            if asset['fallback_url'] == url:
                raise
            data, _, actual_url = get(asset['fallback_url'])
        (width, height), file_format = describe(data)
        digest = hashlib.sha256(data).hexdigest()
        result.update(width=width, height=height, bytes=len(data), sha256=digest, downloaded_from=actual_url)
        name = Path(urllib.parse.unquote(urllib.parse.urlsplit(actual_url).path)).name
        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
        # Keep substantial site graphics separate from photos. Tiny UI art is indexed only.
        graphic = bool(re.search(r'logo|favicon|placeholder|icon|signature|button|badge|payment|credit.card|paypal|stripe|arrow|elementor', name, re.I))
        if width < 120 or height < 100 or max(width, height) < 240:
            result.update(status='skipped-small-asset', file=None)
            return result
        folder = DEST / 'Other-assets' if graphic else DEST
        folder.mkdir(exist_ok=True)
        with lock:
            if digest in existing_by_hash:
                result.update(status='duplicate', file=existing_by_hash[digest])
                return result
            path = folder / name
            if path.exists():
                path = folder / f'{path.stem}-{digest[:8]}{path.suffix}'
            path.write_bytes(data)
            existing_by_hash[digest] = str(path.relative_to(ROOT))
        result.update(status='downloaded-graphic' if graphic else 'downloaded', file=str(path.relative_to(ROOT)))
    except Exception as error:
        result.update(status='failed', error=str(error), file=None)
    return result


results = []
print('Downloading photos with four concurrent requests...', flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    tasks = {pool.submit(collect, asset): asset for asset in assets.values()}
    for task in as_completed(tasks):
        result = task.result()
        results.append(result)
        if result['status'] == 'failed':
            print(f"Failed: {result['url']}: {result['error']}", flush=True)
        if len(results) % 20 == 0 or len(results) == len(tasks):
            counts = {status: sum(item['status'] == status for item in results) for status in sorted({item['status'] for item in results})}
            print(f'Processed {len(results)}/{len(tasks)}: {counts}', flush=True)
            (DEST / 'photo-library.partial.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')

results.sort(key=lambda item: item['url'])
summary = {status: sum(item['status'] == status for item in results) for status in sorted({item['status'] for item in results})}
report = {'collected_at': datetime.now(timezone.utc).isoformat(), 'site': BASE, 'media_index_entries': len(media), 'pages_crawled': len(page_report), 'summary': summary, 'crawl_failures': failures, 'images': results}
(DEST / 'photo-library.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
with (DEST / 'photo-library.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    keys = ['file', 'status', 'width', 'height', 'bytes', 'title', 'alt', 'caption', 'url', 'source_pages', 'sha256']
    writer = csv.DictWriter(handle, fieldnames=keys, extrasaction='ignore')
    writer.writeheader()
    for result in results:
        writer.writerow({**result, 'source_pages': ' | '.join(result['source_pages'])})
print(json.dumps({'media_entries': len(media), 'pages_crawled': len(page_report), 'image_candidates': len(results), 'summary': summary, 'crawl_failures': len(failures)}, indent=2), flush=True)
