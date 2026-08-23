# bytefer/awesome-shadcn-ui

- Repository: https://github.com/bytefer/awesome-shadcn-ui
- File: `README.md`

## Section selection

| Registry type | Section |
|---------------|---------|
| Component/block registry | **UI Libs** |
| Dev tool / generator | **Tools** |
| Starter template | **Templates** |

Default to **UI Libs** for shadcn registries.

## Row format

```markdown
| Display Name | <one-sentence description> | <homepage> |
```

No date column. Link is a plain URL, not markdown.

### Example

```markdown
| OG Image CN | Customizable Open Graph image components installed through the shadcn CLI. | https://ogimagecn.vercel.app/ |
```

### Field rules

| Column | Source |
|--------|--------|
| Name | `profile.name` |
| Description | `profile.description` |
| Link | Full URL from `profile.homepage` |

Insert alphabetically by name within the chosen section if sorted; otherwise append.

## PR details

- Title: `docs: add <name>`
- Body:

```markdown
Adds <name> to the <section> section.

Homepage: <homepage>
GitHub: <githubUrl>
```

## Submitting to both awesome lists

birobirobiro's list has dated entries and a dedicated Registries section. Submit to both during a full launch, but tell the user that bytefer's list may merge more slowly.
