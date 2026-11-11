# Host TLCCR on GitHub Pages

Repository: https://github.com/PurpleSPC/TLCCR

The site is prepared for https://purplespc.github.io/TLCCR/. The existing Critter Creek domain and WordPress site remain unchanged.

## First publication

1. In the repository, open **Settings → Pages**.
2. Under **Build and deployment**, choose **GitHub Actions** as the source.
3. Open **Actions → Check and deploy GitHub Pages → Run workflow** and select `main`.
4. Wait for the build and deploy jobs to turn green. The deployment shows the published URL.

Before Pages is enabled, the workflow builds and checks the site but skips publishing. After Pages is enabled, pushes to `main`, manual runs, and the daily scheduled rebuild publish verified changes. Pull requests run checks without deploying. The daily rebuild removes past events using the farm's Eastern calendar date.

The workflow uses Node 24 and pnpm 11.25.0, installs from the committed lockfile, runs Astro checks and tests, builds the site, and verifies all generated internal links and image URLs. It needs no personal access token in the repository.

## Editing content

Run the local preview with **Start preview.cmd**, then edit at http://127.0.0.1:4321/keystatic/. See STAFF-GUIDE.md. Saving changes this computer's source files. Commit and push approved changes to `main` to rebuild the hosted site.

GitHub Pages serves static files. It does not run the local Keystatic editor or provide online staff sign-in. A shared hosted CMS remains a separate configuration step. The production build excludes the editor and its write API.

## Inquiry forms

Visit, volunteer, and school-trip forms are intentionally labeled **FORM PREVIEW**. They validate and display answers but do not deliver, store, or book requests. Phone and email contact links work. Connect an approved receiving service before relying on online inquiries. See FORMS.md.

## Local checks

```sh
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm build
pnpm verify:build
```

To reproduce the project subdirectory on Windows PowerShell:

```powershell
$env:BASE_PATH='/TLCCR/'
$env:SITE_URL='https://purplespc.github.io'
pnpm build
pnpm verify:build
pnpm preview
```

Open the preview's printed local address with `/TLCCR/` appended. Clear those environment variables to return to a root-path preview. Normal development stays at `/`, so local editing routes keep working.

Production photos use generated WebP copies. Original source JPEGs are preserved; newly uploaded JPEGs are optimized during each build. WebP derivatives, local tools, credentials, dependencies, build output, review captures, and the original photo archive are excluded from source control.

## Future custom domain

Do this only when the ranch authorizes a domain cutover. Add repository **Actions variables** `SITE_URL` (the approved full origin) and `BASE_PATH` (`/` for a domain root), configure the custom domain under Pages, and update its DNS. Internal routes and metadata adapt to those values. Do not change the existing domain or remove WordPress until current application/waiver links and historical URLs have a migration plan.

Official references: [Astro GitHub Pages guide](https://docs.astro.build/en/guides/deploy/github/) and [GitHub custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
