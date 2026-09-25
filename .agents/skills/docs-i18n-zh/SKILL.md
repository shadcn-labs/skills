---
name: docs-i18n-zh
description: Translate skills/*/SKILL.md and the root README.md into Simplified Chinese (zh-CN), mirroring the English source structure.
---

# docs-i18n-zh

Translate this repo's documentation into Simplified Chinese.

## Scope

Only two document families:

- `skills/<skill>/SKILL.md` → `skills/<skill>/SKILL.zh-CN.md`
- Root `README.md` → `README.zh-CN.md`

Out of scope: `references/`, `scripts/`, `templates/`, `evals/`, workflow files, and config files. Never create zh-CN variants of those.

## Rules

- English is the source of truth. Always translate from the current English file.
- Mirror the source structure section-for-section: same headings, same order, same list depth, same tables.
- Frontmatter: translate `description`; keep `name` in English.
- Keep in English, byte-for-byte: code blocks, inline code, file paths, shell commands, URLs, badge and HTML markup, product names.
- Write concise, natural Chinese. Use Chinese punctuation in prose.
- On first ambiguous use, put the English term in parentheses after the Chinese rendering, e.g. 模型上下文协议（Model Context Protocol）.

## Cross-linking

One line at the top of each file, above everything else:

- English file: `> 中文版: [SKILL.zh-CN.md](SKILL.zh-CN.md)` (or `README.zh-CN.md`)
- zh-CN file: `> English: [SKILL.md](SKILL.md)` (or `README.md`)

## Process

1. Read the English source file fully before translating anything.
2. If `SKILL.zh-CN.md` / `README.zh-CN.md` already exists, update it in place against the current English source (do not append a second translation).
3. Add or refresh the cross-link line on both sides.
4. Report the files created and updated when done.

## Never

- Never edit `references/`, `scripts/`, `templates/`, or `evals/` content while translating.
- Never list this skill for distribution: not in `skills/`, not in the root README skill table, not in `skills.sh.json`. It is agent harness tooling only.
- Never translate `name` fields, file paths, commands, URLs, or markup.
