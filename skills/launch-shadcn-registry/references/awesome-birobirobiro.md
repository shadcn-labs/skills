# birobirobiro/awesome-shadcn-ui

- Repository: https://github.com/birobirobiro/awesome-shadcn-ui
- File: `README.md`
- Site: https://awesome-shadcn-ui.vercel.app

The site also has a submission form.

## Section selection

Add registries to the **Registries** table, not **Libs and Components**.

If the resource is broader than a registry, confirm whether **Libs and Components** or **Tools** fits better.

## Row format

```markdown
| scope-slug | <one factual sentence from descriptionLong> | [Link](<homepage>) | <ISO-8601 UTC timestamp> |
```

### Example

```markdown
| ogimagecn | Customizable Open Graph image components installed through the shadcn CLI. | [Link](https://ogimagecn.vercel.app) | 2026-06-16T12:00:00.000Z |
```

### Field rules

| Column | Source |
|--------|--------|
| Name | Lowercase slug without `@`, such as `ogimagecn` |
| Description | `profile.descriptionLong` or `profile.description` |
| Link | `profile.homepage` |
| Date | Current UTC time in `YYYY-MM-DDTHH:mm:ss.000Z` format |

Insert the row in **alphabetical order** within the Registries table if the table is sorted; otherwise append before the next `##` section.

## PR details

- Title: `docs: add <name> to Registries`
- Body:

```markdown
## Summary

Adds <name> at <homepage> to the Registries section.

## Checklist

- [ ] Resource is shadcn/ui related
- [ ] Registry is publicly accessible
- [ ] Link works
```

## Alternative: website submission

The user can submit through https://awesome-shadcn-ui.vercel.app/ instead of opening a pull request. Prefer a pull request when they want a visible review trail.
