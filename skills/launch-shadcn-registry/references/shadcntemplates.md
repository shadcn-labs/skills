# shadcntemplates

- Repository: https://github.com/shadcnblocks/shadcntemplates
- Directory: `content/`
- Site: https://shadcntemplates.com

## File naming

Create `content/{author}-{templatename}.md`.

- Set `author` to a lowercase, space-free version of `profile.githubUsername`.
- Set `templatename` to a lowercase, hyphenated slug from `profile.name`.

Example: `aniket-508-ogimagecn.md`

## Open-source listing template

```markdown
---
title: Display Name
author: github-username
avatarUrl: https://github.com/username.png
createdAt: '2026-06-16T12:00:00.000Z'
demoUrl: 'https://example.com'
description: >-
  Two to three sentences describing the registry. Mention shadcn/ui compatibility
  and what components or blocks are included.
distribution: open-source
githubUrl: 'https://github.com/org/repo'
category:
  - react
  - nextjs
  - tailwind
  - shadcn-registry
  - component-library
---

## Overview

<profile.descriptionLong expanded into 1 short paragraph>

## Features

- Install with `npx shadcn@latest add @scope/component`
- Components are copied into the project
- <Feature name>: <specific value>
```

## Premium listing

Use this only when `profile.distribution` is `premium`:

```markdown
---
title: Display Name
author: github-username
avatarUrl: 'https://...'
demoUrl: 'https://example.com'
price: 0
affiliateUrl: 'https://example.com'
description: Short premium description
distribution: premium
themeKey: author-slug
category:
  - react
  - shadcn-registry
  - shadcn-ui
---
```

Each user gets one free premium listing. The repository README states that additional premium listings cost $100. Maintainers review every premium listing before publishing it.

## PR details

- Title: `docs: add <name> to shadcntemplates`
- Body: A short summary with homepage and GitHub links.

## Category guidance

Always include `shadcn-registry`. Add from `profile.categories` as applicable:

- `component-library`, `block-library`, `ui-kit`, `landing-page`, `nextjs`, `react`, `tailwind`, `astro`
