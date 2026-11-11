import test from 'node:test';
import assert from 'node:assert/strict';
import {validateInquiry,inquiryToday} from '../src/lib/inquiries.mjs';

const contact = {firstName:'Farm',lastName:'Tester',email:'test@example.com'};
const visit = {...contact,confirmEmail:'TEST@example.com',phone:'(772) 555-0100',adults:'2',children:'0',preferredDate:'2026-11-12',preferredTime:'10:30',heardAbout:'Word of Mouth'};
const today = '2026-11-10';

test('a complete visit request accepts a matching email regardless of case', () => {
  assert.deepEqual(validateInquiry('visit',visit,today),{});
  assert.ok(validateInquiry('visit',{...visit,confirmEmail:'someone@example.com'},today).confirmEmail);
});
test('tour party sizes reject empty groups, fractions, and source-form limit violations', () => {
  assert.ok(validateInquiry('visit',{...visit,adults:'0',children:'0'},today).adults);
  assert.ok(validateInquiry('visit',{...visit,adults:'1.5'},today).adults);
  assert.ok(validateInquiry('visit',{...visit,adults:'11'},today).adults);
  assert.ok(validateInquiry('visit',{...visit,children:'21'},today).children);
});
test('preferred dates reject impossible and past calendar days without requiring a date', () => {
  assert.ok(validateInquiry('visit',{...visit,preferredDate:'2026-02-30'},today).preferredDate);
  assert.ok(validateInquiry('visit',{...visit,preferredDate:'2026-11-09'},today).preferredDate);
  assert.deepEqual(validateInquiry('visit',{...visit,preferredDate:'',preferredTime:''},today),{});
});
test('phone checks allow common international formatting and reject incomplete numbers', () => {
  assert.deepEqual(validateInquiry('visit',{...visit,phone:'+44 20 7946 0958'},today),{});
  assert.ok(validateInquiry('visit',{...visit,phone:'123'},today).phone);
  assert.ok(validateInquiry('visit',{...visit,secondaryPhone:'call me'},today).secondaryPhone);
});
test('volunteer inquiries require contact basics without a full application or phone number', () => {
  assert.deepEqual(validateInquiry('volunteer',contact,today),{});
  assert.ok(validateInquiry('volunteer',{...contact,firstName:'  '},today).firstName);
});
test('school trip inquiries require group details and a positive student estimate', () => {
  const trip = {...contact,organization:'Example School',ages:'Grades 3–4',students:'24',chaperones:'3'};
  assert.deepEqual(validateInquiry('field-trip',trip,today),{});
  assert.ok(validateInquiry('field-trip',{...trip,students:'0'},today).students);
  assert.ok(validateInquiry('field-trip',{...trip,organization:''},today).organization);
});
test('email and optional source fields reject malformed values', () => {
  assert.ok(validateInquiry('volunteer',{...contact,email:'invalid'},today).email);
  assert.ok(validateInquiry('visit',{...visit,heardAbout:'unlisted'},today).heardAbout);
  assert.deepEqual(validateInquiry('visit',{...visit,heardAbout:'Other',heardOther:'A local newsletter'},today),{});
});
test('the minimum visit date follows the farm’s Eastern calendar rather than UTC', () => {
  assert.equal(inquiryToday(new Date('2026-11-11T01:00:00Z')),'2026-11-10');
});
