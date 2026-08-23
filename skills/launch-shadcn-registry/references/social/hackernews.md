# Hacker News and Show HN

The user posts manually at https://news.ycombinator.com/submit. Use Show HN only for work they built and can discuss.

## Title template

```
Show HN: {Name}, {concrete benefit without hype}
```

### Good titles

```
Show HN: OG Image CN, a shadcn registry for Open Graph image components
```

```
Show HN: TermCN, terminal-styled React components for the shadcn CLI
```

### Titles to avoid

```
Show HN: The best shadcn component library ever
```

```
Show HN: My new startup's UI kit
```

## First comment from the author

Post immediately after submission as a comment on your thread:

```markdown
Hi HN, I'm {githubUsername}, the author of {name}.

I built this because {specific problem in one or two sentences}.

It's a shadcn/ui registry: components install via CLI and live in your repo as source. Index: {registryBaseUrl}/registry.json

Try it:
{installExample}

Source: {githubUrl}
Site: {homepage}

I'm happy to answer questions about {one or two technical topics}.
```

## Guidelines

- Explain the implementation and tradeoffs instead of writing marketing copy
- Reply to comments during the first few hours
- If timing is flexible, weekday mornings in the United States are a reasonable starting point
- Never ask for upvotes
- Mention a YC connection only when it is true
- Link the source repository when the project is open source

## When not to post Show HN

- Registry is not yet live because `registry.json` fails
- It's a thin wrapper with no original work
- User only wants directory listings, not HN exposure
