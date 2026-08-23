# Dev.to

The user publishes through the Dev.to editor. Prepare a complete draft they can edit.

## Title templates

```
Building a shadcn/ui Registry for {Use Case}
```

```
How I launched {name}, a shadcn-compatible component registry
```

## Tags

Choose four relevant tags from `react`, `tailwindcss`, `opensource`, `webdev`, `nextjs`, `typescript`, and `shadcn`.

## Article template

```markdown
---
title: Building a shadcn/ui Registry for {Use Case}
published: false
tags: react, tailwindcss, opensource, webdev
---

I kept running into {specific problem} in my React projects. I built {name}, a shadcn-compatible registry for {use case}, because the existing options did not fit shadcn's copy-and-edit model.

## What it is

{name} at {homepage} distributes {component summary} through the shadcn CLI. The CLI writes the component source into your project, so you can inspect and edit it.

## Quick start

Add the registry to your project, then install a component:

\`\`\`bash
{installExample}
\`\`\`

Browse all components at {homepage}.

## What's included

- {Component A}: {one concrete sentence}
- {Component B}: {one concrete sentence}
- {Component C}: {one concrete sentence}

## How registries work

shadcn registries expose a `registry.json` index and one JSON file per component. The CLI fetches those files and copies their source into your project. This registry index lives at:

\`\`\`
{registryBaseUrl}/registry.json
\`\`\`

## Repo and feedback

Source: {githubUrl}

If you try it, open an issue for {one specific area where feedback would help}.
```

## Tone

- Write it as a tutorial or build log, not a product announcement
- Include real install commands and at least one code snippet if a component has a simple usage example
- Mention the official directory listing only after the pull request merges
