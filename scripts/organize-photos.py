"""Copy reviewed photographs into the user's existing, overlapping categories.

No original is moved, renamed, rewritten, or deleted. Identical source bytes are
grouped once per category; a manifest retains every original path. Run without
--copy to review the plan. --verify checks a completed organization.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'Photos' / 'From-current-site'
REPORT_DIR = ROOT / 'Photos' / 'Organization'
REPORT_DIR.mkdir(exist_ok=True)
REVIEW = json.loads(Path(__file__).with_name('photo-category-review.json').read_text(encoding='utf-8'))
CATEGORIES = REVIEW['category_folders']
DESTINATIONS = {label: ARCHIVE / folder for label, folder in CATEGORIES.items()}
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif', '.heic', '.tif', '.tiff', '.bmp'}
SKIP_FOLDERS = {'node_modules', '.pnpm-store', '.git', '.astro', 'review', 'contact-sheets', 'theme-assets', 'other-assets', 'organization'}


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def numbers(expression):
    values = set()
    for part in expression.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = map(int, part.split('-'))
            values.update(range(start, end + 1))
        else:
            values.add(int(part))
    return values


def relative(path):
    return path.relative_to(ROOT).as_posix()


parser = argparse.ArgumentParser()
parser.add_argument('--copy', action='store_true')
parser.add_argument('--verify', action='store_true')
args = parser.parse_args()

if args.verify:
    manifest = json.loads((REPORT_DIR / 'classification.json').read_text(encoding='utf-8'))
    problems = []
    for photo in manifest['photos']:
        for alias in photo['original_paths']:
            original = ROOT / alias
            if not original.is_file() or digest(original) != photo['sha256']:
                problems.append(f'Original missing/changed: {alias}')
        for label, target in photo['category_copies'].items():
            target_path = ROOT / target
            if not target_path.is_file() or digest(target_path) != photo['sha256']:
                problems.append(f'Category copy missing/changed: {label}: {target}')
    assert not problems, '\n'.join(problems)
    print(f"Verified {len(manifest['photos'])} distinct source files, all original paths unchanged, and all {sum(len(p['category_copies']) for p in manifest['photos'])} category copies byte-identical.")
    raise SystemExit(0)

site_index = json.loads((ARCHIVE / 'Contact-sheets' / 'index.json').read_text(encoding='utf-8'))
site_by_path = {(ROOT / entry['file']).resolve(): entry for entry in site_index}
site_categories = {entry['reference']: set() for entry in site_index}
reviewed = set()
for batch in REVIEW['site_contact_sheet_reviews']:
    scope = numbers(batch['references'])
    assert not scope & reviewed, 'Contact sheet ranges overlap'
    reviewed.update(scope)
    for label in CATEGORIES:
        selected = numbers(batch.get(label, ''))
        assert selected <= scope, f'{label} contains references outside its reviewed batch'
        for number in selected:
            site_categories[number].add(label)
assert reviewed == set(site_categories), 'Every site photograph must have been visually reviewed'

paths = []
excluded = []
for folder, directories, files in os.walk(ROOT):
    folder_path = Path(folder)
    kept = []
    for directory in directories:
        child = folder_path / directory
        if directory.lower() in SKIP_FOLDERS:
            excluded.append({'path': relative(child), 'reason': 'Derived previews, dependency files, branding, or theme demo assets'})
        else:
            kept.append(directory)
    directories[:] = kept
    for filename in files:
        path = folder_path / filename
        if path.suffix.lower() not in EXTENSIONS:
            continue
        if 'contact-sheet' in filename.lower() or 'logo' in filename.lower() or 'favicon' in filename.lower():
            excluded.append({'path': relative(path), 'reason': 'Contact sheet or branding graphic, not an original photograph'})
            continue
        paths.append(path)

# Prefer a source photograph over a prior category copy or a generated web copy.
def source_priority(path):
    category_copy = any(path.is_relative_to(destination) for destination in DESTINATIONS.values())
    in_photos = path.is_relative_to(ROOT / 'Photos')
    return (category_copy, not in_photos, '/dist/' in path.as_posix().lower(), relative(path).lower())

paths.sort(key=source_priority)
photos = {}
for index, path in enumerate(paths, 1):
    checksum = digest(path)
    record = photos.setdefault(checksum, {'sha256': checksum, 'source': relative(path), 'original_paths': [], 'categories': set(), 'site_references': [], 'evidence': [], 'category_copies': {}})
    record['original_paths'].append(relative(path))
    site = site_by_path.get(path.resolve())
    if site:
        number = site['reference']
        record['categories'].update(site_categories[number])
        record['site_references'].append(number)
        record['evidence'].append(f'Visual review: site contact-sheet reference {number:03d}')
    if path.parent == ROOT / 'Photos':
        for label, filenames in REVIEW['local_photo_categories'].items():
            if path.name in filenames:
                record['categories'].add(label)
                record['evidence'].append('Visual review: original local ranch photographs')
    if path.name in REVIEW['web_photo_originals'] and '/images/uploads/' in path.as_posix():
        original_name = REVIEW['web_photo_originals'][path.name]
        for label, filenames in REVIEW['local_photo_categories'].items():
            if original_name in filenames:
                record['categories'].add(label)
        record['evidence'].append(f'Web copy of visually reviewed {original_name}')
    for label, destination in DESTINATIONS.items():
        if path.is_relative_to(destination):
            record['categories'].add(label)
            record['evidence'].append(f'Preserved existing user assignment: {label}')
    if index % 200 == 0:
        print(f'Inventoried {index}/{len(paths)} source paths', flush=True)

unclassified = [record['source'] for record in photos.values() if not record['categories']]
planned_counts = Counter(label for photo in photos.values() for label in photo['categories'])
summary = {'unique_photos': len(photos), 'source_paths_including_existing_copies': len(paths), 'category_counts': dict(planned_counts), 'unclassified': unclassified}
(REPORT_DIR / 'plan.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2), flush=True)
if not args.copy:
    raise SystemExit(0)
assert not unclassified, 'Classify remaining photos before copying'

# Snapshot the original hashes before any copy. This also documents the user's
# existing category copies, which must remain byte-for-byte unchanged.
snapshot_path = REPORT_DIR / 'original-snapshot.json'
snapshot = [{'path': alias, 'sha256': photo['sha256']} for photo in photos.values() for alias in photo['original_paths']]
if not snapshot_path.exists():
    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')

existing = {}
for label, destination in DESTINATIONS.items():
    assert destination.resolve().is_relative_to((ROOT / 'Photos').resolve())
    destination.mkdir(exist_ok=True)
    existing[label] = {digest(path): path for path in destination.iterdir() if path.is_file() and path.suffix.lower() in EXTENSIONS}
copied = Counter()
reused = Counter()
for index, photo in enumerate(photos.values(), 1):
    source = ROOT / photo['source']
    for label in sorted(photo['categories']):
        if photo['sha256'] in existing[label]:
            target = existing[label][photo['sha256']]
            reused[label] += 1
        else:
            target = DESTINATIONS[label] / source.name
            if target.exists():
                target = target.with_name(f'{target.stem}--{photo["sha256"][:10]}{target.suffix}')
            assert not target.exists(), f'Will not overwrite {target}'
            shutil.copy2(source, target)
            assert digest(target) == photo['sha256'], f'Copy differs: {target}'
            existing[label][photo['sha256']] = target
            copied[label] += 1
        photo['category_copies'][label] = relative(target)
    photo['categories'] = sorted(photo['categories'])
    photo['evidence'] = sorted(set(photo['evidence']))
    if index % 200 == 0:
        print(f'Copied categories for {index}/{len(photos)} photos', flush=True)

result = {'organized_at': datetime.now(timezone.utc).isoformat(), 'rules': {
    'Animals': 'Visible animals, including animal care, animal encounters, nests, and animal education images.',
    'People': 'Visible people, volunteers, staff, visitors, portraits, or clear hands-on animal interactions; preserves prior user selections.',
    'Christmas': 'Holiday decorations, Christmas events, festive animal outfits, and associated decorating work from the holiday gallery.',
    'Farm pics': 'Grounds, ponds, landscapes, barns, infrastructure, enclosures, paddocks, and ranch work in context.',
    'History': REVIEW['history_definition'],
}, 'category_folders': {label: relative(path) for label, path in DESTINATIONS.items()}, 'summary': summary, 'new_copies': dict(copied), 'existing_copies_reused': dict(reused), 'excluded': excluded, 'photos': list(photos.values())}
(REPORT_DIR / 'classification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
with (REPORT_DIR / 'classification.csv').open('w', encoding='utf-8-sig', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['source', 'categories', 'site_reference', 'original_paths', 'category_copies', 'sha256'])
    writer.writeheader()
    for photo in photos.values():
        writer.writerow({'source': photo['source'], 'categories': ' | '.join(photo['categories']), 'site_reference': ' | '.join(str(number) for number in photo['site_references']), 'original_paths': ' | '.join(photo['original_paths']), 'category_copies': ' | '.join(f'{label}: {path}' for label, path in photo['category_copies'].items()), 'sha256': photo['sha256']})
readme = f'''# Photo organization

Organized {len(photos)} distinct photo/image files from the working folder into overlapping categories. Every original remains in its original location. Byte-identical copies were grouped once per category, with all original paths recorded in `classification.csv` and `classification.json`.

Existing category folders under `Photos/From-current-site` were used: Animals, People, Christmas, Farm, and History. The existing `Farm` folder is the user's “farm pics” category. Previous user assignments were retained. No existing file was overwritten.

History means archival/founder photos, including `Box3-IMG491.jpg`, the 1997 aerial identified by the user. That aerial is also in Farm. Modern ranch photos were not labeled History simply because their upload was old.

Theme/demo photos, logos, generated website screenshots, and contact-sheet composites were kept separate. Videos were not copied because this request concerns photos. Original local photos and web-optimized photo variants are included; exact duplicate files across the working folder are represented by one category copy.

## Category counts

'''
readme += '\n'.join(f'- {label}: {planned_counts[label]}' for label in CATEGORIES)
readme += '\n\nCategories intentionally overlap. Use the CSV catalog to find an original or see all of its assigned categories.\n'
(REPORT_DIR / 'README.md').write_text(readme, encoding='utf-8')
print(json.dumps({'new_copies': dict(copied), 'reused_existing_copies': dict(reused), 'classification': relative(REPORT_DIR / 'classification.csv')}, indent=2), flush=True)
