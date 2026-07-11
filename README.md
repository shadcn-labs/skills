<div align="center">

# Shadcn Labs Skills

Agent skills for [Shadcn Labs](https://shadcnlabs.com). Install with the [skills CLI](https://github.com/vercel-labs/skills).

[![launch-shadcn-registry](https://shieldcn.dev/skills/installs/shadcn-labs/skills/launch-shadcn-registry.svg?variant=branded&size=xs&label=launch-shadcn-registry)](https://skills.sh/shadcn-labs/skills/launch-shadcn-registry)
[![mastra-file-agents](https://shieldcn.dev/skills/installs/shadcn-labs/skills/mastra-file-agents.svg?variant=branded&size=xs&label=mastra-file-agents)](https://skills.sh/shadcn-labs/skills/mastra-file-agents)
[![tailwind-to-stylex](https://shieldcn.dev/skills/installs/shadcn-labs/skills/tailwind-to-stylex.svg?variant=branded&size=xs&label=tailwind-to-stylex)](https://skills.sh/shadcn-labs/skills/tailwind-to-stylex)

</div>

## Install

```bash
npx skills add shadcn-labs/skills
```

## Skill Overview

### launch-shadcn-registry

Launch and promote a custom shadcn/ui registry — directory PRs, community listings, and social drafts.

```bash
npx skills add https://github.com/shadcn-labs/skills --skill launch-shadcn-registry
```

### mastra-file-agents

Migrate Mastra code-based agents (`new Agent(...)` in a `Mastra({ agents })` map) to the file-based convention — one directory per agent under `src/mastra/agents/`.

```bash
npx skills add https://github.com/shadcn-labs/skills --skill mastra-file-agents
```

### tailwind-to-stylex

Migrate TailwindCSS utility classes to StyleX — resolve classes to CSS, reshape into `stylex.create`, and apply with `stylex.props` / `stylex.attrs` across React and other StyleX-supported frameworks.

```bash
npx skills add https://github.com/shadcn-labs/skills --skill tailwind-to-stylex
```

## License

Published under the [MIT license](LICENSE).
