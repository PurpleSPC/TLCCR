# TLCCR · Critter Creek Sanctuary Ranch

[![Checks and Pages deployment](https://github.com/PurpleSPC/TLCCR/actions/workflows/pages.yml/badge.svg)](https://github.com/PurpleSPC/TLCCR/actions/workflows/pages.yml)

First working design, built with Astro 7, TypeScript, and Keystatic. All source is in this folder. Original photographs remain in `../Photos`; web copies are in `public/images/uploads`.

Prepared for GitHub Pages at `/TLCCR/`. See [HOSTING.md](./HOSTING.md) for first publication, automated checks, staff editing, and current form-preview limitations.

## Run locally

Requires Node 24 and pnpm 11.25.0.

On this computer, double-click **Start preview.cmd** in this folder to run the website and editor without typing a command. Keep its window open, then use the addresses below. Close the preview with Ctrl+C when finished.

```sh
pnpm install
pnpm dev
```

- Website: http://127.0.0.1:4321/
- Content studio: http://127.0.0.1:4321/keystatic/
- Visit-type chooser: http://127.0.0.1:4321/schedule/
- Inquiry forms: `/inquiries/visit/`, `/inquiries/volunteer/`, and `/inquiries/field-trip/` (local preview only; see [FORMS.md](./FORMS.md)).
- Check source: `pnpm check`
- Test event rules: `pnpm test`
- Build static output: `pnpm build`
- Preview the build: `pnpm preview`

On this computer, the bundled pnpm command is:

```powershell
& 'C:\Users\steve\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' dev
```

`ASTRO_TELEMETRY_DISABLED=1` can be set when running in a restricted environment.

## Editing and publishing

See [STAFF-GUIDE.md](./STAFF-GUIDE.md). Keystatic is a real local filesystem editor in this milestone. Saving updates the local content files, and reloading the dev website shows the change. It does not publish anything to the internet.

The production build deliberately excludes the local editing interface and write API. Shared staff access will require authenticated GitHub/Keystatic Cloud storage (or another approved hosted CMS), a content repository, and a hosting build connection. Those accounts and connections have not been provisioned. Never deploy the local filesystem editor as a public write endpoint.

The static site can be hosted independently of the CMS. No hosting account, payment service, or live domain has been changed. Do not use the prototype as the public site until the launch work below is complete.

## Content model

- **Homepage**: headline, introductory line, and slideshow photos/captions/focus.
- **Animals**: title/name, type, image/alt text, introduction, story, care message, order, and draft/published status.
- **Events**: title, date, time, location, category, image, summary, details, registration URL, and draft/published status.
- **Pages**: title, headline, intro, image, ordered text sections, email call to action, and draft/published status.
- **Contact & links**: address, phone, email, approved donation destination, application and waiver links.

Keep existing page slugs `visit`, `education`, `volunteer`, `support`, and `about`, because navigation uses these routes. Animal and event slugs are used for permanent URLs. Add redirects if published slugs change.

`reader` is shared by page templates and Keystatic, so the editor schema is also the website's content contract. Draft animal/page/event entries are excluded from public routes. Event lists and detail routes are generated only for published events on or after the ranch's current Eastern calendar date at build time. A live static deployment needs a daily rebuild to roll over past events; a published content change also needs a rebuild. Set up both before launch.

## Launch work

The selected Farm Journal design is now the homepage at `/`. Every public page uses `FarmLayout.astro`, the real logo, the green header, the barn-red footer, Fraunces headings, and the farm palette. The design comparison routes and earlier prototype layout have been removed. See [DESIGN.md](./DESIGN.md). Run `node scripts/verify-build.mjs` after building to check links and shared branding.

See [PROJECT-NOTES.md](./PROJECT-NOTES.md) for the content sources, open decisions, and production acceptance criteria. The lockfile records exact installed versions. Images can be regenerated with `node scripts/prepare-assets.mjs` if the original files are available.
