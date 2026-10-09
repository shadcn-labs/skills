# AGENTS.md

This repo ships a collection of agent skills. This file is the single repo guide for agents and human contributors — there is no `CLAUDE.md`; agents that look for one fall back to `AGENTS.md` natively. Inspired by [mattpocock/skills](https://github.com/mattpocock/skills/blob/main/CLAUDE.md), simplified for this repo.

## Repo layout

Each skill lives in its own folder under `skills/`:

```
skills/<skill-name>/
  SKILL.md          # required — the skill itself
  SKILL.zh-CN.md    # optional — Simplified Chinese translation, same structure
  references/       # optional — long-form detail the SKILL.md links out to
  scripts/          # optional — runnable helper scripts
  templates/        # optional — JSON templates and schemas
  evals/            # optional — eval cases
```

Outside `skills/`, the repo root holds the READMEs, the manifests (`skills-lock.json`, `skills.sh.json`), and `scripts/` for repo tooling.

## Skill conventions

- `SKILL.md` starts with frontmatter: `name` and `description`. The description states what the skill is for and when to reach for it — it is what agents match on, so keep it specific.
- Keep `SKILL.md` focused: instructions, not background. Detail goes in `references/`, linked from the skill.

## README sync

Every skill has a matching `### <skill-name>` section in the root `README.md` containing:

1. a one-line description,
2. the install command — `npx skills add https://github.com/shadcn-labs/skills --skill <skill-name>`,
3. the skills.sh install badge, linked to `https://skills.sh/shadcn-labs/skills/<skill-name>`.

Use an existing section as the template. `README.zh-CN.md` mirrors the same sections.

## Validation

- Any JSON a skill ships (`templates/`, `evals/` schemas) must parse — run it through a JSON parser before committing.
- Every relative link must resolve, whether it sits in `SKILL.md` or in a file under `references/`, and each link is resolved from the file that contains it — re-check them after moving files.
