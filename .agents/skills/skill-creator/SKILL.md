---
name: docs-i18n-zh
description: Translate English skill documentation to Simplified Chinese (zh-CN). Use when users request creating Chinese versions of SKILL.md files or README.md files for existing skills. Do not use for creating new skills, general translations, or other locales.
---

# Docs i18n zh

A skill for translating English skill documentation into Simplified Chinese.

The goal is to create `.zh-CN.md` variants of existing English skills while preserving structure, technical accuracy, and code integrity.

## Scope

This skill applies to:
- `skills/*/SKILL.md` → `skills/*/SKILL.zh-CN.md`
- `README.md` → `README.zh-CN.md`

Out of scope:
- `references/`
- `scripts/`
- `templates/`
- `evals/`
- Workflows
- Configuration files

## Rules

1. **English Source of Truth**: The English version is the canonical source. Do not translate content that does not exist in the English original.
2. **Mirror Structure**: The Chinese document must have the exact same structure (headings, lists, code blocks) as the English version.
3. **Keep Technical Elements in English**:
   - Code snippets
   - File paths
   - Command lines
   - URLs
   - Badge markup
   - Product names (e.g., Claude, Anthropic, shadcn)
   - Frontmatter `name` field (do not translate the identifier)
4. **Frontmatter Description**: Translate the `description` field value in the YAML frontmatter to Chinese. Keep the `name` field unchanged.
5. **Ambiguous Terms**: When a term is ambiguous or technical, keep the English term in parentheses after the Chinese translation. Example: "技能 (skill)".

## Process

1. Identify the source English file (e.g., `skills/my-skill/SKILL.md`).
2. Create the target file (e.g., `skills/my-skill/SKILL.zh-CN.md`).
3. Translate the content section-by-section, following the rules above.
4. Ensure all code blocks, paths, and commands remain in English.
5. Verify the frontmatter `name` is unchanged and `description` is translated.
6. Save the file.

## Example

**Input (English SKILL.md frontmatter):**