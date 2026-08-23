# Choosing what to draw

The inventory is a design decision, not a shopping list. A set of 18 icons that covers every
place the UI needs one is worth more than 40 icons with duplicates and a missing checkout mark.
Propose and approve the list during Step 2.

## How to build the list

**Walk the product, not the categories.** Review each described screen, including navigation,
settings, empty states, error states, and the email footer. Record every place that needs a
mark. This catches icons that checklists miss, such as no-results and loading states.

**One concept, one icon.** Merge pairs that would produce the same drawing. Common examples are
`edit` with `pencil`, `settings` with `gear`, and `remove` with `trash`. One drawing can serve
several semantic aliases.

**Name by object, not by meaning.** `magnifying-glass` and `trash-can` stay accurate when the
UI repurposes them. Semantic names such as `search` and `delete` lose accuracy after reuse. If
the project wants semantic names, keep the object name as the filename and record aliases in
`style-spec.json`. One drawing can
then serve `search`, `find`, and `filter-results`.

**Sanity-check the size.** 15 to 25 covers most marketing sites. 25 to 40 covers an app with real
navigation. Past 40, ask whether the long tail needs bespoke drawings. A stock library can
cover generic actions while the custom set carries product-specific marks.

## Category checklist

Use to find gaps once you've walked the product, not as the starting point.

**Navigation.** Menu, close, chevron, arrow, external link, back, home, search. Use one drawing
for each directional family and rotate it four ways.

**Status and feedback.** Check, alert-triangle, info-circle, error-circle, loading/spinner,
empty state, lock. Every status icon needs to survive being tinted a semantic colour, so keep
these silhouettes especially clear.

**Objects.** File, folder, image, calendar, clock, tag, card, box, envelope. This is where the
registry pays off; nearly all of them share the same rounded container.

**Actions.** Plus, minus, edit, trash, download, upload, share, copy, filter, sort, refresh,
settings.

**People and social.** User, users, avatar placeholder, and each linked platform mark. Ship
official platform logos and exclude them from the house-style validator.

**Communication.** Phone, mail, message, map-pin, chat.

**Commerce.** Cart, bag, credit card, banknote, receipt, truck/delivery, return.

## Domain starting points

Each list is a prompt for the conversation, not a spec. Combine with the categories above.

**SaaS and dashboards.** Chart-bar, chart-line, activity, database, server, key, api, webhook,
integration, team, billing, usage-meter, export, audit-log.

**Fintech.** Banknote, credit-card, wallet, transfer, chart-candlestick, shield-check, receipt,
invoice, percentage, exchange, ledger, statement.

**Health and clinics.** Stethoscope, heart-pulse, calendar-check, pill, syringe, clipboard-list,
tooth, first-aid, appointment, prescription, lab-flask.

**E-commerce.** Cart, bag, tag, truck, return, star-rating, wishlist-heart, size-guide,
gift, discount, package, storefront.

**Trades and field services.** Wrench, pipe, boiler, electrical-plug, drill, hard-hat, van,
quote-document, emergency-callout, warranty-badge, before-after.

**Education.** Book, graduation-cap, certificate, lesson-play, quiz, progress, calendar-term,
library, mentor, assignment.

**Real estate.** House, key, floor-plan, area/sqm, bed, bath, parking, map-pin, viewing-calendar,
mortgage-calculator.

**Developer tooling.** Terminal, branch, commit, pull-request, package, container, log, deploy,
rollback, environment, secret, cli.

**Restaurants and hospitality.** Menu-card, table-booking, chef-hat, delivery-bike, opening-hours,
allergen, wine-glass, takeaway-bag, review-star.

**Legal and professional services.** Scales, gavel, document-signed, shield, briefcase, case-file,
consultation, contract, court, notary-seal.

## Icons to think twice about

- **Readable text.** A document icon with words or a chart with axis labels turns to noise at
  16px. Keep the object shape and remove the text.
- **Photorealistic objects.** A specific car model or branded device dates fast and
  they're hard to hold in one style.
- **Emoji-adjacent faces.** Smileys carry established visual language and
  they will fight the rest of the set unless the whole set is playful.
- **Concepts with no agreed picture.** Terms such as "synergy", "innovation", and "quality"
  usually collapse into a generic lightbulb or rocket. Ask what concrete object should carry
  the meaning.
