/** Dates belong to the ranch's Eastern time zone, independent of the build host. */
export function easternDate(now = new Date()) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(now);
}
/** @template {{entry: {status: string, date: string | null}}} T @param {T[]} events */
export function visibleEvents(events, now = new Date()) {
  const today = easternDate(now);
  return events.filter(event => event.entry.status === 'published' && event.entry.date && event.entry.date >= today)
    .sort((a, b) => (a.entry.date || '').localeCompare(b.entry.date || ''));
}
export function formatEventDate(date) {
  return new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'long', day: 'numeric', year: 'numeric' }).format(new Date(`${date}T12:00:00-05:00`));
}
