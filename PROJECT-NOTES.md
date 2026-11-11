# Project brief and launch notes

## Objective

Increase meaningful engagement: completed visit inquiries, educational inquiries, volunteer applications, and donations. The animals lead the storytelling. The selected Farm Journal design uses cream, farm green, barn red, gold, and sky blue, with editorial type and four clear paths to action.

## This milestone

- Responsive homepage and four primary action pages.
- Animal directory and four group profiles using actual project photos.
- Events directory, generated event detail pages, and a genuine empty state when nothing is scheduled.
- Our story, contact, and not-found pages.
- Local staff content studio with drafts and image uploads.
- Existing volunteer application and visitor waiver linked. Visit, volunteer, and school-trip forms now offer local review previews; support inquiries still use email and phone links.
- Static production build with no public content-write API.

No online forms pretend to submit. No payment processing is connected. No invented animal names, individual histories, event dates, testimonials, donation impact figures, or visitor counts are presented.

## Source material reviewed

Reviewed November 10, 2026. Existing content is a starting source; current operational details still require ranch confirmation.

- https://crittercreekranch.org/ — mission, visit arrangements, contact details, founders and Toby's Legacy.
- https://crittercreekranch.org/tobys-legacy/ — Milly and Dick Olson, Toby, the ranch's origins.
- https://crittercreekranch.org/volunteer/ — daily care and maintenance, community service.
- https://crittercreekranch.org/apply-to-volunteer/ — application and stated age requirements.
- https://crittercreekranch.org/i-did-not-know-that/ — horse care and educational storytelling.
- https://crittercreekranch.org/black-swans/ — historical swan story; no breeding or scientific claims were carried into the prototype.

Photos come from the supplied parent `Photos` folder and the existing ranch-site archive. Web copies are in `public/images`; original photo archives remain outside this repository. Production builds generate optimized WebP copies without changing source JPEGs. No stock or AI-generated animal photos are used.

## Confirm with the ranch

1. Animal names, which individuals are pictured, current residency, approved biographies and care stories.
2. Visit availability, fees, group limits, opening arrangements, access needs, waiver version, weather policy and visitor guidance.
3. Educational program availability, ages, format, length, fees, supervision and learning goals.
4. Current volunteer age rules, orientation, tasks, scheduling, group arrangements and application handling.
5. Donation provider, account ownership, recurring giving, approved impact wording, required disclosures and receipt process.
6. Actual events, their registration methods, capacity management and cancellation procedures.
7. Branding/logo approval, photo permissions, and any additional photos of staff, volunteers or educational groups.

## Production work after design review

The Farm Journal design is now the homepage at `/`, with one shared layout/logo/header/footer across all public pages. Design comparison routes and the previous prototype layout are removed. Historical screenshots are preserved in `review/design-history/`; see DESIGN.md for the current structure. Inquiry submissions remain local previews.

- Provision the content repository, authenticated staff accounts, CMS production storage and permissions.
- Connect preview and production deployments to approved content changes. Add a daily build for event expiry and keep draft previews separate from the public site.
- Inquiry forms are designed in explicit local-preview mode at Steve's request. Before live delivery, choose the receiving inbox/service, then configure server-side validation, spam controls, verified delivery, privacy copy, and a real success/error flow. See FORMS.md.
- Confirm and test donation and registration destinations. Preserve the existing donation operation during migration.
- Add privacy and required nonprofit disclosures using ranch-approved text.
- Audit existing URLs and implement permanent redirects. In particular retain or redirect `/tobys-legacy/`, `/i-did-not-know-that/`, `/apply-to-volunteer/`, `/work/`, historical stories and gallery URLs. Rehost needed files before retiring WordPress; the existing application and waiver currently rely on that server.
- Add sitemap, share images/canonical domain review, analytics and agreed conversion events. Email-button clicks alone are not completed inquiries; completed outcomes require records from the form/booking/payment tools or staff tracking.
- Optimize newly uploaded images in the build/media pipeline, review fonts and image focal points, finish keyboard/contrast/screen-reader checks and representative device testing.
- Have staff create and publish an animal and event through the hosted editor in staging, verify rollback, then plan the domain cutover.

## Technical references

- https://docs.astro.build/en/concepts/why-astro/
- https://keystatic.com/docs/installation-astro
- https://keystatic.com/docs/reader-api
- https://keystatic.com/docs/fields/image
- https://keystatic.com/docs/recipes/astro-disable-admin-ui-in-production
