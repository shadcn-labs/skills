---
name: mastra-file-agents
description: >-
  Migrate Mastra agents built with new Agent and registered in a Mastra agents map to
  one directory per agent under src/mastra/agents. Use when the user asks for file-based
  agents, agentConfig, a per-directory agent layout, or a split of src/mastra/index.ts
  or agents.ts. Requires @mastra/core 1.48 or later.
compatibility: A Mastra project using @mastra/core 1.48.0 or later. File discovery requires mastra dev or mastra build.
---

# Migrate Mastra agents to file-based directories

Convert agents built with `new Agent({...})` and registered in a
`new Mastra({ agents: {...} })` map into one directory per agent under
`src/mastra/agents/<name>/`. Sibling files replace the old constructor options.

Preserve the agent's behavior. Move each option to the file that owns it, keep the
same model, instructions, tools, memory, skills, and subagents, and do not invent
config the agent did not have.

## Check discovery and collisions first

### Confirm the discovery path

The Mastra bundler discovers file-based agents during `mastra dev` and `mastra build`.
It does not discover them when an app imports the `mastra` instance directly, as a
library, custom server, or test might do. Confirm how the app runs before migrating.
Keep directly imported agents in code and explain why.

### Remove code collisions

Code registration wins when the same agent also exists in a file-based directory.
Mastra logs a warning and ignores the directory. The migration does not take effect
until Step 5 removes the agent from the `Mastra({ agents })` map.

## Workflow

Work one agent at a time. Copy this checklist and track it:

```
Migration progress for <agent>:
- [ ] Confirmed the app runs through mastra dev or mastra build
- [ ] Created src/mastra/agents/<name>/
- [ ] config.ts uses agentConfig and keeps the model plus remaining config
- [ ] Static instructions moved to instructions.md, or dynamic instructions stayed in config.ts
- [ ] Each tools/*.ts file has one default export and uses the tool key as its name
- [ ] Moved memory, workspace, skills, and subagents when present
- [ ] Removed the agent from the Mastra({ agents }) map
- [ ] Deleted dead imports and the old agent file when nothing else uses it
- [ ] Verified with mastra dev
```

### Step 1: find the code-based agents

Locate every `new Agent({...})` and how it is registered. Registration often lives
in `src/mastra/index.ts` inside `new Mastra({ agents: { ... } })`, but agents
may be defined in `src/mastra/agents/*.ts` files or a large `agents.ts` file and then
imported. Read the full `Agent` config for each agent so every option has a destination.
Record the key used in the `agents` map. That key controls registration and lookup in
`mastra.getAgent('weather')`, Studio, and the client SDK. It also becomes the directory name.

### Step 2: create the directory and split the config

For an agent registered as `agents: { weather: weatherAgent }`, create
`src/mastra/agents/weather/`.

Name the directory after the map key, not the `id`. The directory name becomes
the agent's registration/lookup key, so using the map key preserves every existing
`getAgent(...)` call and client reference. This matters when the map key differs
from the `id`. For `agents: { browserAgent }` with `new Agent({ id: 'browser-agent' })`,
name the folder `browserAgent`. Set `id` and `name` explicitly in `config.ts` to keep
the original `'browser-agent'` and `'Browser Agent'` values. If the map key and `id` already
match, both values default to the folder name and you can drop them.

#### config.ts

Move everything except inline instructions and tools into `config.ts`.
Use `agentConfig()` so the partial is typed and sibling files fill the rest:

```typescript
import { agentConfig } from '@mastra/core/agent'

export default agentConfig({
  model: 'openai/gpt-5.5',
  // instructions come from instructions.md
  // tools come from tools/*.ts
})
```

`model` is required. A missing model fails the build and names the directory.

#### instructions.md

If the original `instructions` was a string or an array of static strings or messages,
move the text into `instructions.md` and omit
`instructions` from config.ts. `instructions.md` wins over a static `instructions`
string, so leaving both is redundant.

If the original `instructions` was a function that reads runtime context, it cannot
live in `instructions.md`. Keep it in `config.ts` because
dynamic function instructions win over `instructions.md`. See `references/mapping.md`.

### Step 3: split out the tools

Each tool gets its own file under `tools/` with a default export for the
`createTool()` call. The filename becomes the tool key, so use
the key from the original `tools` map or the tool's `id`. If the original was
`tools: { get_weather: getWeatherTool }`, the file must be `tools/get_weather.ts`.

```typescript
import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

export default createTool({
  id: 'get_weather',
  description: 'Get the current weather for a city',
  inputSchema: z.object({ city: z.string() }),
  execute: async ({ context }) => ({ city: context.city, tempC: 21 }),
})
```

Tools from `tools/*.ts` merge with any `config.tools`. On a key collision
`config.tools` wins and Mastra logs a warning, so don't list a tool in both places. If
`config.tools` is a function, Mastra ignores discovered tool files. In that case,
keep tools in config.ts and say so. Test files such as `*.test.ts` and `*.spec.ts`
are ignored by discovery.

Not every tool is a `createTool()`. Provider-native tools such as
`openai.tools.webSearch({})` and other pre-built tool objects don't fit the
`createTool()` shape. Either leave them inline in `config.tools`, or default-export
the tool object from a `tools/<key>.ts` file. Mastra discovers either form. When in doubt,
keeping a provider tool in `config.tools` is the simplest faithful move. Reserve
`tools/*.ts` files for the project's own `createTool()` definitions.

If a tool is shared by multiple agents, don't force it into one agent's `tools/`.
Keep the shared tool in a common module and reference it from `config.tools`, or
duplicate deliberately. Note the choice for the user.

### Step 4: handle the remaining configuration

Memory, workspace, skills, and subagents each have their own file/directory and
precedence rules. When the agent you're migrating uses any of them, read
[references/mapping.md](references/mapping.md) for the exact mapping, including dynamic
configuration, subagent descriptions, and seed files.
Do not drop these during migration. Losing an agent's memory or subagent silently
changes behavior.

### Step 5: remove the code registration

This completes the migration. Delete the agent's entry from the
`Mastra({ agents: {...} })` map, then remove imports and definitions that are now
unused. If the old `new Agent(...)` lived in its own file and nothing else imports
it, delete that file.

Keep an agent registered in code when the app imports it directly, registers it
dynamically, or shares the instance elsewhere. Code and file-based agents can coexist.

### Step 6: verify

Run the app through the CLI so the bundler discovers the new directories:

```bash
npx mastra dev
```

`npx mastra build` is a good non-interactive check when you can't start the dev
server. It runs the same discovery and fails on missing models, missing
subagent descriptions, or unresolved directories. If dependencies aren't installed
in your environment, say so and mark verification as structural only rather than
claiming it runs.

Confirm each migrated agent still appears under its original registration key and
responds. Check that no "code agent overrides file-based" or "config.X wins" warnings
appear. Those warnings signal a leftover collision or redundant config entry. Fix
warnings before calling it done.

## Mapping cheat sheet

| `new Agent({...})` option | File-based location |
| --- | --- |
| agents map key | Directory name; preserves the registration and lookup key |
| `id` / `name` | Default to directory name; set them in `config.ts` when they differ from the folder |
| `model` | Required in `config.ts` |
| static `instructions` | `instructions.md` |
| instruction function | Keep in `config.ts` |
| `description` | `config.ts`; required for subagents |
| `tools: { key: createTool(...) }` | `tools/<key>.ts` as a default export |
| provider or pre-built tools | Keep in `config.tools`, or default-export from `tools/<key>.ts` |
| `skills` | `skills/`; see references/mapping.md |
| `memory` | `memory.ts`; see references/mapping.md |
| `workspace` | `workspace.ts` + `workspace/` seed files |
| delegated `agents` | `subagents/<childId>/` |
| everything else | `config.ts` via `agentConfig()` |
