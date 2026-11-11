export const inquiryTypes = {
  visit: { title: 'Book a visit', reason: 'Meet the animals', eyebrow: 'A little closer to the animals', headline: 'Your next farm day starts here.', intro: 'Tell us who is coming and when you would like to visit. The farm will work with you to confirm the details.', photo: '/images/concepts/encounter.jpg', alt: 'A young boy feeds a goat on the grass.', color: 'red' },
  volunteer: { title: 'Volunteer inquiry', reason: 'Prospective volunteer', eyebrow: 'Good hearts. Helping hands.', headline: 'A little of your time. A lot of good.', intro: 'Interested in lending a hand? Start with a few details about yourself, your interests, and when you might be available.', photo: '/images/uploads/action-volunteer.jpg', alt: 'A volunteer gently holds a crested chicken.', color: 'green' },
  'field-trip': { title: 'School trip inquiry', reason: 'School trip', eyebrow: 'Curiosity belongs here', headline: 'Bring your questions to the farm.', intro: 'Tell us a little about your school or group. We can talk through a visit that brings learning to life.', photo: '/images/concepts/people.jpg', alt: 'Young visitors gather around a miniature horse.', color: 'blue' },
};

/** @returns {string} */
export function inquiryToday(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', year:'numeric', month:'2-digit', day:'2-digit' }).formatToParts(now);
  return ['year','month','day'].map(type => parts.find(p => p.type === type)?.value).join('-');
}

/**
 * Validation is shared by the preview and focused tests; a production receiver
 * must repeat these checks before accepting or delivering a request.
 * @param {string} kind
 * @param {Record<string,string>} values
 * @param {string} today
 * @returns {Record<string,string>}
 */
export function validateInquiry(kind, values, today = inquiryToday()) {
  const errors = {};
  const value = name => (values[name] ?? '').trim();
  const required = (name, message) => { if (!value(name)) errors[name] = message; };
  required('firstName','Enter your first name.');
  required('lastName','Enter your last name.');
  required('email','Enter your email address.');
  if (value('email') && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value('email'))) errors.email = 'Enter a valid email address.';
  if (kind === 'visit') {
    required('confirmEmail','Confirm your email address.');
    if (value('confirmEmail') && value('confirmEmail').toLowerCase() !== value('email').toLowerCase()) errors.confirmEmail = 'The email addresses need to match.';
    required('phone','Enter a phone number so the farm can reach you.');
  }
  for (const name of ['phone','secondaryPhone']) {
    if (value(name) && !/^[+\d\s().-]+$/.test(value(name))) errors[name] = 'Use a phone number with country or area code.';
    const digits = value(name).replace(/\D/g,'').length;
    if (value(name) && (digits < 7 || digits > 15)) errors[name] = 'Enter a complete phone number, including the area code.';
  }
  const count = (name, min, max, message) => {
    const raw = value(name);
    if (!/^\d+$/.test(raw) || Number(raw) < min || Number(raw) > max) errors[name] = message;
  };
  if (kind === 'visit') {
    count('adults',0,10,'Enter a whole number of adults from 0 to 10.');
    count('children',0,20,'Enter a whole number of children from 0 to 20.');
    if (!errors.adults && !errors.children && Number(value('adults')) + Number(value('children')) === 0) errors.adults = 'Include at least one person in your visit.';
    const sources = ['','Social Media','Word of Mouth','Previous Tour','Google','Facebook','Other'];
    if (!sources.includes(value('heardAbout'))) errors.heardAbout = 'Choose one of the listed options.';
  }
  if (kind === 'field-trip') {
    required('organization','Enter the school or group name.');
    required('ages','Tell us the students’ grades or approximate ages.');
    count('students',1,1000,'Enter an estimated student count from 1 to 1,000.');
    if (value('chaperones')) count('chaperones',0,1000,'Enter a whole number from 0 to 1,000.');
  }
  const date = value('preferredDate');
  if (date) {
    const parsed = new Date(`${date}T12:00:00Z`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !Number.isFinite(parsed.getTime()) || parsed.toISOString().slice(0,10) !== date) errors.preferredDate = 'Choose a valid date.';
    else if (date < today) errors.preferredDate = 'Choose today or a future date.';
  }
  if (value('preferredTime') && !/^([01]\d|2[0-3]):[0-5]\d$/.test(value('preferredTime'))) errors.preferredTime = 'Choose a valid time.';
  for (const [name, text] of Object.entries(values)) {
    if (text.length > (['message','availability'].includes(name) ? 3000 : 200)) errors[name] = 'Please shorten this answer.';
  }
  return errors;
}
