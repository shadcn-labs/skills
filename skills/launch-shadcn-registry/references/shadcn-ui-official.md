# Official shadcn-ui/ui directory

- Repository: https://github.com/shadcn-ui/ui
- File: `apps/v4/registry/directory.json`
- Example pull request: https://github.com/shadcn-ui/ui/pull/10896

## Entry format

Append a new object at the **end** of the JSON array:

```json
{
  "name": "@scope",
  "homepage": "https://example.com",
  "url": "https://example.com/r/{name}.json",
  "description": "One sentence describing what the registry provides.",
  "logo": "<svg>...</svg>"
}
```

### Field rules

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Scoped name with an `@` prefix, such as `@ogimagecn` |
| `homepage` | Yes | Public docs or marketing site |
| `url` | Yes | Component JSON pattern; must use `{name}` placeholder |
| `description` | Yes | Single sentence of about 160 characters or fewer |
| `logo` | Recommended | Inline SVG string; see existing entries for style |

Do not reorder or edit existing entries. Append only.

## PR details

- Branch: `feat/<scope-without-at>-directory`
- Title: `feat(registry): add @scope`
- Commit: `feat(registry): add @scope`

Use this body:

```markdown
## Summary

Adds `@scope` to the community registry directory.

- Registry URL: `https://example.com/r/{name}.json`
- Homepage: https://example.com
- Description: <description>

## Test plan

- [ ] `curl https://example.com/r/registry.json` returns valid JSON
- [ ] `npx shadcn@latest add @scope/<sample-component>` installs successfully
```

## Review expectations

- A shadcn/ui maintainer must approve the pull request
- The change should contain one new JSON object
- Vercel deploy preview may require team authorization on first contribution
- Response time varies; follow up politely after three to five business days

## Mapping from registry profile

```
name        ← profile.scope
homepage    ← profile.homepage
url         ← profile.componentUrlPattern
description ← profile.description
logo        ← profile.logo when present
```
