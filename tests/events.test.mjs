import test from 'node:test';
import assert from 'node:assert/strict';
import { easternDate, visibleEvents, formatEventDate } from '../src/lib/events.mjs';

test('event visibility follows the ranch date when UTC has reached tomorrow', () => {
  const now = new Date('2026-11-11T01:00:00Z');
  assert.equal(easternDate(now), '2026-11-10');
  const event = (slug, status, date) => ({ slug, entry: { status, date } });
  const events = [event('future', 'published', '2026-11-12'), event('draft', 'draft', '2026-11-12'), event('yesterday', 'published', '2026-11-09'), event('today', 'published', '2026-11-10')];
  assert.deepEqual(visibleEvents(events, now).map(event => event.slug), ['today', 'future']);
});
test('dates remain on the selected calendar day through daylight saving changes', () => {
  assert.equal(formatEventDate('2027-03-14'), 'March 14, 2027');
  assert.equal(formatEventDate('2027-11-07'), 'November 7, 2027');
});
