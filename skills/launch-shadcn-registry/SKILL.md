---
name: launch-shadcn-registry
description: >-
  Launch and promote a custom shadcn/ui registry. Validate registry.json, prepare or open
  directory pull requests, and draft posts for Reddit, X, Dev.to, and Hacker News. Use when
  the user wants to launch, list, submit, or announce a shadcn/ui registry, including requests
  about awesome-shadcn-ui, registry.directory, or a new @scope registry.
compatibility: Needs network access, curl, gh, and git. The user must be logged in through gh before creating pull requests.
---

# Launch a shadcn registry

Prepare directory submissions for a custom shadcn/ui registry, then write posts that fit each platform.

## Before you start

Confirm whether the user wants the full launch or only selected targets. Default to the full workflow unless they narrow the scope.

Collect or infer a registry profile. Ask for missing required fields before generating submissions. Use [templates/registry-profile.example.json](templates/registry-profile.example.json) as the shape and validate it against [templates/registry-profile.schema.json](templates/registry-profile.schema.json).

Required profile fields:

| Field | Purpose |
|-------|---------|
| `scope` | Registry scope such as `@ogimagecn` |
| `name` | Display name |
| `homepage` | Public project or documentation URL |
| `registryBaseUrl` | Base URL for JSON files with no trailing slash |
| `componentUrlPattern` | URL pattern with a `{name}` placeholder, such as `https://example.com/r/{name}.json` |
| `description` | One directory sentence of no more than 160 characters |
| `descriptionLong` | Two or three sentences for awesome lists and social posts |
| `githubUrl` | Source repo |
| `githubUsername` | For avatar URLs and filenames |
| `distribution` | `open-source` or `premium` |
| `categories` | Tags for shadcntemplates and awesome lists |
| `installExample` | Full install command such as `npx shadcn@latest add @scope/component-name` |
| `logo` | Optional inline SVG string; recommended for the official directory |
| `registryIndexPath` | Optional registry index path relative to `registryBaseUrl`; defaults to `/registry.json` |
| `sampleComponents` | Optional component slugs to validate during preflight, such as `["og-image"]` |
| `features` | Optional points for shadcntemplates and social posts |

## Workflow

Copy this checklist and track progress:

```
Launch Progress:
- [ ] Phase 1: Preflight validation
- [ ] Phase 2: Generate directory artifacts
- [ ] Phase 3: Open GitHub pull requests after user approval
- [ ] Phase 4: Draft social posts
- [ ] Phase 5: Post-launch follow-up
```

## Phase 1: preflight

Read [references/preflight.md](references/preflight.md) and run validation before generating any PRs.

```bash
bash scripts/validate-registry.sh <registryBaseUrl> [sample-component-name]
```

Fix all blockers before continuing. Common failures:

- `registry.json` not public or wrong path
- Component JSON 404
- Duplicate `@scope` in official directory
- `description` too long or marketing-heavy for official listing

Fetch the official directory to check duplicates:

```bash
curl -fsSL https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/directory.json | grep -i "<scope>"
```

## Phase 2: generate artifacts

Generate the requested submission files from the registry profile. Read only the references for those targets.

| Target | Reference | Output |
|--------|-----------|--------|
| Official shadcn-ui/ui | [references/shadcn-ui-official.md](references/shadcn-ui-official.md) | JSON entry + PR body |
| registry.directory | [references/registry-directory.md](references/registry-directory.md) | JSON entry + PR body |
| shadcntemplates | [references/shadcntemplates.md](references/shadcntemplates.md) | `content/{author}-{name}.md` |
| birobirobiro awesome | [references/awesome-birobirobiro.md](references/awesome-birobirobiro.md) | README table row |
| bytefer awesome | [references/awesome-bytefer.md](references/awesome-bytefer.md) | README table row |

Present artifacts grouped by repo. Include:

1. Exact file path to create or edit
2. Full content to add rather than a partial diff
3. Suggested PR title and body

### PR title convention

Use `feat(registry): add <scope>` for official shadcn-ui/ui. This matches [PR #10896](https://github.com/shadcn-ui/ui/pull/10896). Use `docs: add <name> to <section>` for awesome lists and `feat: add <name> registry` for registry.directory.

## Phase 3: open GitHub pull requests

Use `gh` for GitHub operations. Ask before creating each pull request unless the user already asked to open all of them.

Standard fork-and-PR flow per repo:

```bash
# Example: official shadcn-ui/ui
gh repo fork shadcn-ui/ui --clone=false
git clone https://github.com/<user>/ui.git /tmp/ui-registry-pr
cd /tmp/ui-registry-pr
git remote add upstream https://github.com/shadcn-ui/ui.git
git fetch upstream && git checkout -b feat/<scope>-directory upstream/main
# append the entry to apps/v4/registry/directory.json
git add apps/v4/registry/directory.json
git commit -m "feat(registry): add <scope>"
git push -u origin HEAD
gh pr create --repo shadcn-ui/ui --title "feat(registry): add <scope>" --body "$(cat <<'EOF'
## Summary
Adds <scope> to the community registry directory.

- Registry URL: `<componentUrlPattern>`
- Homepage: <homepage>
- Description: <description>

## Test plan
- [ ] `curl <registryBaseUrl>/registry.json` returns valid JSON
- [ ] `npx shadcn@latest add <installExample>` installs successfully
EOF
)"
```

Open pull requests in this order unless the user chooses otherwise:

1. Official `shadcn-ui/ui`, the most visible listing and the one most likely to need maintainer review
2. `rbadillap/registry.directory`
3. `shadcnblocks/shadcntemplates`
4. `birobirobiro/awesome-shadcn-ui` and `bytefer/awesome-shadcn-ui`, which can run in parallel

Track pull request URLs in the launch checklist. Do not describe the registry as published until it is live and at least one directory submission is open or merged.

## Phase 4: draft social posts

Read the platform references and produce ready-to-paste drafts. The user posts them manually.

| Platform | Reference |
|----------|-----------|
| Reddit r/shadcn | [references/social/reddit.md](references/social/reddit.md) |
| X | [references/social/x.md](references/social/x.md) |
| Dev.to | [references/social/devto.md](references/social/devto.md) |
| Hacker News | [references/social/hackernews.md](references/social/hackernews.md) |

Tailor each draft from the registry profile. Include the install command, homepage, and GitHub link. Avoid hype; lead with the concrete problem the registry solves.

Draft social posts after preflight passes. Suggest publishing them after the official directory pull request merges. At minimum, wait until `registry.json` is live.

## Phase 5: follow up

After PRs are open or merged:

1. Share the repository, pull request URL, and status for every submission
2. Remind the user to respond to review comments within 48 hours
3. After the official merge, update social drafts to mention that the registry is now listed in the shadcn registry directory
4. If a pull request is rejected, read the maintainer feedback and revise the description or registry format before resubmitting

## Rules

Guardrails not already implied by the phases above:

- Append the official `directory.json` entry to the end of the array.
- Use one registry profile for every submission. Do not invent conflicting descriptions without user approval.
- For premium registries on shadcntemplates, explain that the first listing is free and additional listings cost $100. Do not promise approval.

## Additional resources

- Registry profile schema: [templates/registry-profile.schema.json](templates/registry-profile.schema.json)
- Example profile: [templates/registry-profile.example.json](templates/registry-profile.example.json)
- Validation script: [scripts/validate-registry.sh](scripts/validate-registry.sh)
