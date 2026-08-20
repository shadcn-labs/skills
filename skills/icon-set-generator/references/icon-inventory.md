# Choosing what to draw

The inventory is a design decision, not a shopping list. A set of 18 icons that covers every
place the UI needs one is worth more than 40 icons where three are near-duplicates and the one
the checkout page needs is missing. Propose the list before drawing (Step 2) and get it agreed.

## How to build the list

**Walk the product, not the categories.** Go screen by screen through what the user described
— landing page, nav, dashboard, settings, empty states, error states, the email footer. Every
place something needs a mark, note it. This catches the ones checklists miss: the empty-state
illustration mark, the "no results" glyph, the loading indicator.

**One concept, one icon.** If two proposed icons would be drawn nearly identically (`edit` and
`pencil`, `settings` and `gear`, `remove` and `trash`), pick one name and use it in both
places. Near-duplicates are where a set starts looking sloppy, and they double the maintenance.

**Name by object, not by meaning.** `magnifying-glass` and `trash-can` stay accurate when the
UI repurposes them; `search` and `delete` don't. If the project wants semantic names, keep the
object name as the filename and record the semantic aliases in `style-spec.json` — that way one
drawing can serve `search`, `find` and `filter-results` without being duplicated.

**Sanity-check the size.** 15–25 covers most marketing sites. 25–40 covers an app with real
navigation. Past 40, ask whether the long tail is genuinely bespoke or whether those could come
from an existing library while the custom set carries the distinctive ones — a smaller set
drawn well beats a large set drawn evenly-mediocre.

## Category checklist

Use to find gaps once you've walked the product, not as the starting point.

**Navigation** — menu, close, chevron (one drawing, four rotations), arrow (ditto), external
link, back, home, search.

**Status and feedback** — check, alert-triangle, info-circle, error-circle, loading/spinner,
empty state, lock. Every status icon needs to survive being tinted a semantic colour, so keep
these silhouettes especially clear.

**Objects** — file, folder, image, calendar, clock, tag, card, box, envelope. This is where the
registry pays off; nearly all of them share the same rounded container.

**Actions** — plus, minus, edit, trash, download, upload, share, copy, filter, sort, refresh,
settings.

**People and social** — user, users, avatar placeholder, plus whichever platform marks the
project actually links to. Platform logos are trademarks with their own construction — don't
redraw them in the set's style, ship the official marks and keep them out of the validator run.

**Communication** — phone, mail, message, map-pin, chat.

**Commerce** — cart, bag, credit card, banknote, receipt, truck/delivery, return.

## Domain starting points

Each list is a prompt for the conversation, not a spec. Combine with the categories above.

**SaaS / dashboard** — chart-bar, chart-line, activity, database, server, key, api, webhook,
integration, team, billing, usage-meter, export, audit-log.

**Fintech** — banknote, credit-card, wallet, transfer, chart-candlestick, shield-check, receipt,
invoice, percentage, exchange, ledger, statement.

**Health / clinic** — stethoscope, heart-pulse, calendar-check, pill, syringe, clipboard-list,
tooth, first-aid, appointment, prescription, lab-flask.

**E-commerce** — cart, bag, tag, truck, return, star-rating, wishlist-heart, size-guide,
gift, discount, package, storefront.

**Trades / field services** — wrench, pipe, boiler, electrical-plug, drill, hard-hat, van,
quote-document, emergency-callout, warranty-badge, before-after.

**Education** — book, graduation-cap, certificate, lesson-play, quiz, progress, calendar-term,
library, mentor, assignment.

**Real estate** — house, key, floor-plan, area/sqm, bed, bath, parking, map-pin, viewing-calendar,
mortgage-calculator.

**Developer tooling** — terminal, branch, commit, pull-request, package, container, log, deploy,
rollback, environment, secret, cli.

**Restaurant / hospitality** — menu-card, table-booking, chef-hat, delivery-bike, opening-hours,
allergen, wine-glass, takeaway-bag, review-star.

**Legal / professional** — scales, gavel, document-signed, shield, briefcase, case-file,
consultation, contract, court, notary-seal.

## Icons to think twice about

- **Anything that needs text to be legible** — a document icon with readable words on it, a
  chart with axis labels. At 16px the text is noise. Suggest the shape alone.
- **Photorealistic objects** — a specific make of car, a branded device. They date fast and
  they're hard to hold in one style.
- **Emoji-adjacent faces** — smileys have an enormous amount of established visual language and
  they will fight the rest of the set unless the whole set is playful.
- **Concepts with no agreed picture** — "synergy", "innovation", "quality". If you can't name
  the object, the icon will be a lightbulb or a rocket like everyone else's. Push back and ask
  what the user actually wants that mark to say.
