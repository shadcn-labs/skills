# Preflight validation

Run these checks before generating directory PRs or social drafts.

## Registry requirements

The registry must be publicly accessible with no authentication:

| Endpoint | Required | Example |
|----------|----------|---------|
| Registry index | `{registryBaseUrl}/registry.json` | `https://ogimagecn.vercel.app/r/registry.json` |
| Component files | `{componentUrlPattern}` with real component name | `https://ogimagecn.vercel.app/r/og-image.json` |

Custom `registry_url` paths are allowed. For example, registry.directory entries can set `registry_url` explicitly. The index must still resolve without authentication.

## Automated validation

```bash
bash scripts/validate-registry.sh <registryBaseUrl> [component-name]
```

The script checks:

1. `registry.json` returns HTTP 200 and valid JSON
2. Registry index contains at least one item or documents its components
3. Optional sample component JSON returns 200
4. Response is not HTML error page

## Manual checks

### CLI install smoke test

```bash
npx shadcn@latest add <full-url-or-scope/component> --dry-run
```

Or install into a throwaway test project if the user has one.

### Duplicate detection

Search the official directory for the scope name:

```bash
curl -fsSL https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/directory.json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print([x['name'] for x in d if '@yourscope' in x.get('name','').lower()])"
```

Also search community lists if the registry was previously submitted under a different name.

### Description quality

Official directory descriptions should be:

- One sentence, factual
- No claims such as "best", "#1", or "revolutionary"
- Explain what components the registry provides

### Logo for the official directory

If including `logo` in the official entry:

- Inline SVG only, matching `apps/v4/registry/directory.json`
- Smaller than 8 KB where practical
- Works in light and dark contexts if possible

### GitHub metadata

For registry.directory, prefer including:

- `github_url` for the source or registry repository
- `github_profile` set to `https://github.com/{username}.png`

## Blockers

- `registry.json` missing or returns non-JSON
- All sampled component URLs 404
- Duplicate `@scope` already in official directory
- Site homepage down
- Registry requires auth headers or cookies

## Warnings

- No `logo` for the official entry; the entry can still be submitted
- Only one component in the registry; this may be intentional for a narrow registry
- Premium distribution on shadcntemplates; review and fees may apply to additional premium listings
- Official PR may take days for maintainer review
