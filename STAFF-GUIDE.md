# Editing the Critter Creek website

This first version includes a working local content studio. The developer starts the site; you edit in your browser. Remote staff sign-in and online publishing will be connected before launch.

## Open the studio

Go to http://127.0.0.1:4321/keystatic/ while the local preview is running.

On this computer, double-click **Start preview.cmd** in the project folder to start the preview, and leave its window open while editing.

The left menu groups work into **Your website** and **Life at the ranch**. You do not need to edit code or JSON files.

## Update an animal

1. Choose **Animals**, then choose the animal you want to change. Choose **Add** to create another profile.
2. Enter a confirmed name (or a descriptive title), animal type, and short introduction.
3. Upload a photograph and write its description. A good description explains the important visible details without starting with “image of.”
4. Write the story in short paragraphs. Leave an empty line between paragraphs.
5. Set **Display order** to control the order of profiles on the animals page. A lower number appears first.
6. Leave **Publication status** as **Draft** until the entry is approved. Select **Published** when ready, then **Save**.
7. Reload the animal page in the local website to review the result.

Do not guess animal names, rescue backgrounds, ages, or medical conditions. The starter profiles use group titles until individual details are confirmed.

## Add an event

1. Choose **Events** → **Add**.
2. Fill in the event title, date, time, location, category, and summary. Include “Eastern” in the time so visitors know the time zone.
3. Add full details, a photo if available, and an approved registration link if there is one. Without a registration link, the website offers an email inquiry.
4. Save as **Draft** while planning. Drafts do not appear to visitors.
5. Confirm the details with the ranch team, change status to **Published**, and save.
6. Review the events list and the event's detail page in the local website.

The example event is intentionally a draft. It is not a real announcement. Event dates are interpreted in the ranch's Eastern time zone. Past events are excluded when the site is built. Online daily updates will be configured with hosting.

## Change a page or the homepage

Choose **Pages**, then the page. Edit its headline, introduction, photo, and text sections. The section list lets you add or reorder sections. Keep the existing URL/slug when changing an existing page.

Choose **Homepage** to update the main headline and small introductory line. Put the second part of the headline on a new line to give it the red italic treatment.

The **Farm homepage slideshow** list starts with five photos: two of horses, one emu, one of goats, and one of swans. Open an entry to replace its photo or edit its caption and photo description. Drag entries to reorder them. Use **Photo focus** to keep the animals visible in the wide frame, then review the homepage at http://127.0.0.1:4321/ on both a computer and phone. Save and reload the preview to see changes. All pages share the same farm theme, logo, header, and footer.

The slideshow rotates every six seconds. Visitors can pause it, select a photo, use the arrows, or swipe on a touch screen. Manual navigation pauses rotation until Play is selected. Visitors who prefer reduced motion start with rotation paused.

Choose **Contact & links** to update contact information or the approved donation link. Leaving the donation link empty keeps the support button pointed at an email inquiry instead of sending visitors to an unconfirmed payment destination.

## Preview the inquiry forms

Use **Schedule a visit** on the Farm Journal homepage to choose meeting the animals, prospective volunteering, or a school trip. Fill in the matching form and choose **Review my request** to see a summary. **Edit my details** keeps your answers; **Start a new request** clears them.

These forms are explicitly a local preview for now. They do not send emails or save requests, so staff will not receive an inquiry from them. The existing live website's booking form remains in operation. Delivery and request handling will be connected before launch.

## What Save means in this version

Save writes to this computer's project folder. Reload the local website to review your edits. **Save does not publish the site online.** The hosted version will connect authenticated staff editing to a review and deployment workflow.

For GitHub Pages, approved source changes are committed and pushed to `main`; the workflow then checks and rebuilds the site. A daily rebuild keeps event lists current. Online staff sign-in is not provided by Pages. See HOSTING.md.

Before making content public, verify facts, photo permissions, dates, links, and spelling. An event's registration page and any donor payment page should be tested by the ranch team before launch.
