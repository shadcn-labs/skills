# registry.directory

- Repository: https://github.com/rbadillap/registry.directory
- File: `apps/web/public/directory.json`
- Site: https://registry.directory

## Entry format

Append to the `registries` array inside the root object:

```json
{
  "name": "Display Name",
  "description": "One or two sentences about the registry.",
  "url": "https://example.com/",
  "registry_url": "https://example.com/r/registry.json",
  "github_url": "https://github.com/org/repo",
  "github_profile": "https://github.com/username.png"
}
```

### Field rules

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Human-readable and may differ from `@scope` |
| `description` | Yes | Clear, factual |
| `url` | Yes | Homepage; trailing slash is optional |
| `registry_url` | Yes* | Full path to `registry.json`; required when the path is not `/r/registry.json` |
| `github_url` | Recommended | Repo link for card avatar |
| `github_profile` | Recommended | `https://github.com/{username}.png` |

\*Include `registry_url` even when the default would work. The explicit path removes ambiguity.

## PR details

- Branch: `feat/add-<slug>-registry`
- Title: `feat: add <name> registry`
- Commit: `feat: add <name> registry`

Use this body:

```markdown
## Summary

Adds <name> to the registry directory.

- Homepage: <homepage>
- Registry: <registry_url>
- GitHub: <githubUrl>

## Checklist

- [ ] `registry.json` is publicly accessible
- [ ] Component JSON files resolve at documented paths
- [ ] Registry works with shadcn CLI
```

## Mapping from registry profile

```
name           ← profile.name
description    ← profile.description or profile.descriptionLong; trim to about 200 characters
url            ← profile.homepage
registry_url   ← profile.registryBaseUrl + "/registry.json"; adjust for a custom path
github_url     ← profile.githubUrl
github_profile ← https://github.com/{profile.githubUsername}.png
```
