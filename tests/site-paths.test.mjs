import test from 'node:test';
import assert from 'node:assert/strict';
import {createSitePaths} from '../src/lib/site-paths.mjs';

test('GitHub Pages paths cover home, nested pages, photos, query strings, and fragments', () => {
  const {withBase, withoutBase} = createSitePaths('/TLCCR/');
  assert.equal(withBase('/'), '/TLCCR/');
  assert.equal(withBase('/inquiries/field-trip/'), '/TLCCR/inquiries/field-trip/');
  assert.equal(withBase('/images/uploads/swans.jpg'), '/TLCCR/images/uploads/swans.jpg');
  assert.equal(withBase('/events/?category=visit#details'), '/TLCCR/events/?category=visit#details');
  assert.equal(withBase('/TLCCR/animals/'), '/TLCCR/animals/');
  assert.equal(withoutBase('/TLCCR/animals/the-birds/'), '/animals/the-birds/');
  assert.equal(withoutBase('/TLCCR'), '/');
  assert.equal(withoutBase('/TLCCR-other/'), '/TLCCR-other/');
});

test('external links, phone/email links, fragments, and domain-root builds remain intact', () => {
  for (const base of ['/', '/TLCCR/']) {
    const {withBase} = createSitePaths(base);
    for (const value of ['https://crittercreekranch.org/book-a-tour/', '//example.org/photo.jpg', 'mailto:contact@example.org', 'tel:7722878572', '#concept-main', '?view=grid']) assert.equal(withBase(value), value);
  }
  assert.equal(createSitePaths('/').withBase('/animals/'), '/animals/');
  assert.equal(createSitePaths('/').withoutBase('/animals/'), '/animals/');
});
