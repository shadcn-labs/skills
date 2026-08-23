# Configuration mapping and precedence

Read this when the agent you're migrating uses memory, a workspace, skills, or
subagents, or when `config.ts` uses functions for `instructions`, `tools`,
`skills`, or `agents`. The core workflow for config, instructions, and tools lives in
SKILL.md; this file covers the rest and the precedence traps that silently drop
behavior during a migration.

## Contents

- [Instruction value types](#instructions)
- [Memory](#memory)
- [Skills](#skills)
- [Workspace and seed files](#workspace)
- [Subagents](#subagents)
- [Precedence rules reference](#precedence)
- [Common migration mistakes](#mistakes)

<a id="instructions"></a>
## Instructions

- Move strings, arrays of strings, and system-message objects into `instructions.md`.
  Omit `instructions` from `config.ts` because `instructions.md` wins over a static value.
- Keep an instruction function such as `instructions: ({ runtimeContext }) => ...`
  in `config.ts`. A function cannot be expressed in `instructions.md`, and the function
  takes precedence.
- If neither an `instructions.md` nor an `instructions` value exists, the build
  fails for that agent. Never leave an agent with no instructions.

<a id="memory"></a>
## Memory

Move a `memory` instance into `memory.ts` as the default export:

```typescript
import { Memory } from '@mastra/memory'

export default new Memory()
```

Copy the original storage, vector store, processors, and options such as `lastMessages`
and `semanticRecall`. If the original agent built `Memory` inline, move that same
construction into `memory.ts`.

Precedence: `config.memory` wins over `memory.ts`, and a warning is logged when both
are present. Pick one home for memory and prefer `memory.ts`. If neither is present,
the agent has no memory by default, so don't accidentally
drop an agent that previously had memory.

<a id="skills"></a>
## Skills

Skills go under `skills/`. Mastra supports three layouts and inlines each at build time:

1. Put `createSkill()` in a `.ts` file and default-export it. Use this when the original
   agent already called `createSkill(...)` in code. Move each skill into its own file:

   ```typescript
   import { createSkill } from '@mastra/core/skills'

   export default createSkill({
     name: 'forecasting',
     description: 'Use when the user asks about multi-day forecasts.',
     instructions: 'Summarize the forecast day by day and call out precipitation.',
   })
   ```

2. A packaged `skills/<skill>/SKILL.md` uses frontmatter for `name` and
   `description`, the body is the instructions, and files under `references/` are
   inlined. Use when a skill has substantial instructions and reference material.

3. In a flat `skills/<skill>.md`, the filename is the skill name and the body is the
   instructions. Use for a short, single-purpose skill.

Precedence: discovered skills merge with `config.skills`. On a name collision,
`config.skills` wins and Mastra logs a warning. When `config.skills` is a function,
Mastra ignores discovered skills. Keep those skills in `config.ts`.

<a id="workspace"></a>
## Workspace and seed files

Move a `Workspace` instance into `workspace.ts` as the default export:

```typescript
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace'

export default new Workspace({
  name: 'weather-workspace',
  filesystem: new LocalFilesystem({ basePath: './data/weather' }),
  sandbox: new LocalSandbox({ workingDirectory: './data/weather' }),
})
```

If the agent had no workspace, a discovered file-based agent gets a default workspace.
It contains a filesystem and shell sandbox rooted at the agent's `workspace/` directory.
Do not add one unless the original agent needs custom workspace behavior.

Precedence: `config.workspace` wins over `workspace.ts`, which wins over the default.

To ship starting files with the agent, add a `workspace/` directory. Mastra copies every
file under it into the agent's default workspace at build time.

```text
src/mastra/agents/weather/
  config.ts
  workspace/
    README.md
    data/cities.json
```

<a id="subagents"></a>
## Subagents

If a supervisor delegates to child agents through its `agents` map or delegation tools,
migrate each child into `subagents/<childId>/` under the parent. A subagent directory
uses the same layout as a top-level agent. It can contain `config.ts`, `instructions.md`, `tools/`, `skills/`,
`memory.ts`, `workspace.ts`, `workspace/`.

```text
src/mastra/agents/
  supervisor/
    config.ts
    instructions.md
    subagents/
      researcher/
        config.ts        # set a non-empty description
        instructions.md
        tools/
          search.ts
```

The directory name becomes the delegation tool name the model sees. In the example,
the supervisor sees `researcher`.

Key rules:

- Set a non-empty `description` in every subagent's `config.ts`. The model reads it
  when deciding whether to delegate, and a missing description fails the build.

  ```typescript
  import { agentConfig } from '@mastra/core/agent'

  export default agentConfig({
    model: 'openai/gpt-5.5',
    description: 'Researches a topic and returns cited findings.',
  })
  ```

- Subagents are isolated. A subagent inherits no tools, skills, or workspace from its
  parent. Copy the child agent's own tools into the subagent directory.
- Nesting is allowed up to three levels, from supervisor depth zero through depth two. A
  `subagents/` directory deeper than that is ignored with a warning.
- A subagent id that collides with one of the parent's tool keys is a build error.
- A duplicate subagent id under the same parent is a build error.
- Subagents from `subagents/` merge with `config.agents`. On an id collision,
  `config.agents` wins and Mastra logs a warning. When `config.agents` is a function,
  Mastra ignores discovered subagents.

<a id="precedence"></a>
## Precedence rules reference

These precedence rules govern coexistence:

- **Code registration wins.** If an agent name exists in both code and the
  filesystem, Mastra keeps the code-registered agent and logs a warning. Remove
  the code registration to finish a migration.
- **A folder can hold a code agent.** If `config.ts` exports a configured
  `new Agent({ id, ... })`, that instance is used as-is and sibling
  `instructions.md`, `tools/`, `skills/`, `memory.ts`, `workspace.ts`, `subagents/`
  are ignored with warnings. Prefer `agentConfig()` so sibling files are respected.
- **Instruction precedence.** Dynamic function instructions in `config.ts` win over
  `instructions.md`; otherwise `instructions.md` wins over a static `instructions`
  string. The build fails if neither exists.
- **Model requirement.** A missing `model` fails the build and names the agent directory.
- **Tool precedence.** `tools/*.ts` merge with `config.tools`. On collision,
  `config.tools` wins and Mastra logs a warning. When `config.tools` is a function,
  Mastra ignores discovered tools.
- **Skill precedence.** `skills/` merge with `config.skills`. On collision,
  `config.skills` wins and Mastra logs a warning. When `config.skills` is a function,
  Mastra ignores discovered skills.
- **Memory precedence.** `config.memory` wins over `memory.ts` and triggers a warning
  when both exist. If neither exists, the agent has no memory.
- **Workspace precedence.** `config.workspace` wins over `workspace.ts`, which wins over
  the default workspace.
- **Subagent precedence.** `subagents/` merge with `config.agents`. On id collision,
  `config.agents` wins and Mastra logs a warning. A tool-key collision or duplicate id
  fails the build.

<a id="mistakes"></a>
## Common migration mistakes

- **Leaving the code registration in place.** The code agent wins, so the new files do
  nothing. The migration looks done but changed nothing.
- **Migrating a directly-imported agent.** If the app does `import { mastra }` and
  runs without the Mastra CLI, file-based agents aren't discovered. Keep those in code.
- **Naming the directory after the `id` instead of the map key.** The directory name
  becomes the agent's registration/lookup key. For `agents: { browserAgent }` with
  `id: 'browser-agent'`, naming the folder `browser-agent` silently changes the key
  from `browserAgent` to `browser-agent`, breaking `getAgent('browserAgent')` and
  client references. Use the map key `browserAgent` as the folder, and set
  `id`/`name` explicitly to keep their original values.
- **Renaming tool files.** The filename is the tool key. `getWeather.ts` for a tool
  keyed `get_weather` changes the key and breaks references.
- **Forcing a provider tool into the `createTool()` shape.** Tools like
  `openai.tools.webSearch({})` aren't `createTool()` calls. Keep them in
  `config.tools`, or default-export the object from `tools/<key>.ts`. Don't rewrite
  them as `createTool()`.
- **Turning a dynamic instruction/tool/skill/agents function into files.** Functions
  can't be statically merged; discovered files are ignored. Keep functions in config.
- **Dropping memory or subagents.** These options can be easy to miss in a large
  constructor. Search the original agent definition for every option before deleting it.
- **Setting the same thing in two places.** A tool in both `config.tools` and `tools/`
  triggers a "config wins" warning. Pick one home for each setting.
