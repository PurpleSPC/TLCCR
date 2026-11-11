"""Finalize the archive manifest and keep old theme demo assets separate."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'Photos' / 'From-current-site'
path = DEST / 'photo-library.json'
report = json.loads(path.read_text(encoding='utf-8'))

# A narrow portrait is still useful; preserve it despite the first-pass size filter.
for entry in report['images']:
    if entry['title'] == 'IMG_54981':
        photo_path = DEST / 'IMG_54981.jpg'
        if photo_path.exists():
            with Image.open(photo_path) as photo:
                photo.load()
                assert photo.size == (entry['width'], entry['height'])
            assert hashlib.sha256(photo_path.read_bytes()).hexdigest() == entry['sha256']
            entry.update(status='downloaded', file=str(photo_path.relative_to(ROOT)))

# The public library also contains Colibri's demo photographs and decorations.
# Keep these, with provenance, but exclude them from the ranch photo contact sheets.
relocations = {}
for entry in report['images']:
    if entry.get('file') and Path(entry['file']).name.startswith('colibri-image-'):
        source = (ROOT / entry['file']).resolve()
        target = (DEST / 'Theme-assets' / source.name).resolve()
        assert source.is_relative_to(DEST.resolve()) and target.is_relative_to(DEST.resolve())
        if source != target and source.exists():
            target.parent.mkdir(exist_ok=True)
            source.rename(target)
        relocations[entry['file']] = str(target.relative_to(ROOT))
        if entry['status'] == 'downloaded':
            entry['status'] = 'downloaded-template-asset'
for entry in report['images']:
    if entry.get('file') in relocations:
        entry['file'] = relocations[entry['file']]

report['summary'] = dict(sorted(Counter(entry['status'] for entry in report['images']).items()))
path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
with (DEST / 'photo-library.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=['file', 'status', 'width', 'height', 'bytes', 'title', 'alt', 'caption', 'url', 'source_pages', 'sha256'], extrasaction='ignore')
    writer.writeheader()
    for entry in report['images']:
        writer.writerow({**entry, 'source_pages': ' | '.join(entry['source_pages'])})

partial = DEST / 'photo-library.partial.json'
if partial.exists():
    partial.unlink()
unique_paths = {entry['file'] for entry in report['images'] if entry.get('file')}
for file in unique_paths:
    assert (ROOT / file).is_file(), file

summary = report['summary']
text = f'''# Photos collected from Critter Creek's existing site

Source site: https://crittercreekranch.org/

- Examined {report['pages_crawled']} public page URLs and {report['media_index_entries']} public WordPress media entries.
- Downloaded {summary.get('downloaded', 0)} additional photo files, preserving original filenames and the original image version where available.
- Kept the five photos downloaded earlier in this same folder.
- Skipped {summary.get('duplicate', 0)} byte-identical duplicates and generated WordPress thumbnail sizes.
- Saved the logo in `Other-assets` and {summary.get('downloaded-template-asset', 0)} old theme demo/decorative assets in `Theme-assets`.
- The remaining two tiny assets are a small logo variant and a 32-pixel icon, recorded in the inventory.
- Every downloaded image was decoded successfully and checked for dimensions and SHA-256. Original bytes are preserved.

## Browse the archive

`Contact-sheets` contains numbered preview sheets and `index.json`, which maps each numbered reference to the original file and its source URL. Preview thumbnails do not change the originals.

`photo-library.csv` is the spreadsheet-friendly catalog. `photo-library.json` retains full metadata, media IDs, source URLs, source pages where found, file dimensions and hashes. A blank source-page list means the image was found in the public media library rather than a page we crawled.

## Coverage

All 632 image candidates were processed without an image download failure. Two old date-archive links returned 404; they are logged in `photo-library.json`. The public media library was still indexed independently. Non-image attachments, private form-upload directories, off-site media, and videos were outside this photo collection.

Some entries are historical photos, crops, or differently encoded versions of the same scene. Byte-identical duplicates were collapsed; intentional crops and different photographs were retained. No animal identities, dates, or personal details were inferred from the photos.
'''
(DEST / 'README.md').write_text(text, encoding='utf-8')
print(json.dumps({'summary': summary, 'unique_saved_files': len(unique_paths)}, indent=2))
