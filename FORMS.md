# Visit, volunteer, and school-trip inquiries

Implemented November 10, 2026. Steve explicitly chose **local preview submissions only**. Nothing is emailed, posted to a delivery service, written to a database, or stored in browser storage.

## Routes and navigation

- The selected homepage's **Schedule a visit** button opens a native dialog with **Meet the animals**, **Prospective volunteer**, and **School trip** choices.
- `/schedule/` provides the same choices as a full page when JavaScript or the dialog API is unavailable.
- `/inquiries/visit/`, `/inquiries/volunteer/`, and `/inquiries/field-trip/` contain the forms.
- Existing Visit, Education, Volunteer, and Contact calls to action link to their corresponding form. The farm-logo home link returns to the selected Farm Journal homepage.

## Source for visit details

The live [Book a Tour form](https://crittercreekranch.org/book-a-tour/) was inspected in the browser. It requests first and last name, email and confirmation, a date and time, phone, an optional secondary phone, adult and child counts, and referral source. Its adult slider runs from 0 to 10, with a default of 1; its child slider runs from 0 to 20, with a default of 0. Referral choices are Social Media, Word of Mouth, Previous Tour, Google, Facebook, and Other.

The new visit form uses clearly labeled number fields instead of sliders, retains the original count limits, requires at least one visitor, and reveals an optional follow-up field when Other is selected. Dates and times remain optional preferences. The farm must confirm availability; these forms do not reserve a time or process payment. Date validation uses the farm's Eastern calendar day. The live form's CAPTCHA was not reproduced in the local preview.

## Basic inquiry fields

Volunteer inquiries collect first/last name and email, optional phone, interests, availability, and a short message. This is an initial inquiry rather than the existing full volunteer application.

School-trip inquiries collect contact name/email, optional phone, school/group name, grades or ages, estimated students, optional chaperone count and preferred date, and questions or learning goals. Student/chaperone field bounds are input safeguards, not approved farm capacity. No student names, birth dates, references, or emergency contacts are requested.

## Preview behavior

**Review my request** runs client-side validation and displays the entered details. The page explicitly states that nothing has been sent. **Edit my details** preserves the answers; **Start a new request** clears them. Reloading or leaving the page does not persist submitted data. The form button stays disabled until the preview script is initialized.

Review values and validation messages are rendered as text, not HTML. Errors appear next to labeled fields and in a focusable summary. The dialog supports Escape, native focus containment, restored trigger focus, and a scrollable layout on small screens.

## Verified

Ten automated tests cover inquiry validation and existing event rules. Browser checks cover the three forms, required fields, email mismatch, referral follow-up, count validation, review/edit/reset, literal text rendering, modal Escape/focus, fallback routing, mobile layouts, and missing horizontal overflow. No tests send real requests.

## Before live delivery

Choose the receiving inbox and a delivery service when the project is ready. Add a real receiving endpoint with server-side validation, spam protection, approved privacy wording, and honest delivery-success/failure handling. Keep the existing live WordPress booking form operating during this local design work.
