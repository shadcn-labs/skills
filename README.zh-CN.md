> English: [README.md](./README.md)

<p align="center">
  <img src="./assets/gh.png" alt="Shadcn Labs Skills banner" />
</p>

<h1 align="center">Skills</h1>

<div align="center">

面向 [Shadcn Labs](https://shadcnlabs.com) 的 Agent skills，可通过 [skills CLI](https://github.com/vercel-labs/skills) 安装。

</div>

## 安装

```bash
npx skills add shadcn-labs/skills
```

## Skills 概览

### launch-shadcn-registry

校验并发布自定义 shadcn/ui registry——通过目录级 pull request、社区收录以及针对各平台的发帖草稿完成上线。

```bash
npx skills add https://github.com/shadcn-labs/skills --skill launch-shadcn-registry
```

[![launch-shadcn-registry](https://shieldcn.dev/skills/installs/shadcn-labs/skills/launch-shadcn-registry.svg?variant=branded&size=xs&label=launch-shadcn-registry)](https://skills.sh/shadcn-labs/skills/launch-shadcn-registry)

### mastra-file-agents

将 Mastra agents 从 `Mastra({ agents })` 映射结构迁移为 `src/mastra/agents/` 下「每个 agent 一个目录」的组织方式。

```bash
npx skills add https://github.com/shadcn-labs/skills --skill mastra-file-agents
```

[!astra-file-agents](https://shieldcn.dev/skills/installs/shadcn-labs/skills/mastra-file-agents.svg?variant=branded&size=xs&label=mastra-file-agents)](https://skills.sh/shadcn-labs/skills/mastra-file-agents)

### tailwind-to-stylex

将 TailwindCSS 工具类迁移至 StyleX：把每个 class 解析为 CSS，用 `stylex.create` 重塑样式，再通过 `stylex.props` 或 `stylex.attrs` 应用。

```bash
npx skills add https://github.com/shadcn-labs/skills --skill tailwind-to-stylex
```

[![tailwind-to-stylex](https://shieldcn.dev/skills/installs/shadcn-labs/skills/tailwind-to-stylex.svg?variant=branded&size=xs&label=tailwind-to-stylex)](https://skills.sh/shadcn-labs/skills/tailwind-to-stylex)

### icon-set-generator

绘制一套真正「成套」的自定义 SVG 图标——锁定样式规范、光学尺寸包络、可复用部件库，并附带校验器与预览页。

```bash
npx skills add https://github.com/shadcn-labs/skills --skill icon-set-generator
```

[![icon-set-generator](https://shieldcn.dev/skills/installs/shadcn-labs/skills/icon-set-generator.svg?variant=branded&size=xs&label=icon-set-generator)](https://skills.sh/shadcn-labs/skills/icon-set-generator)

### icon-set-audit

审计现有 SVG 图标集的一致性——规范漂移、复用部件发散、近似重复、光学尺寸离群项——并按优先级给出修复清单。

```bash
npx skills add https://github.com/shadcn-labs/skills --skill icon-set-audit
```

[![icon-set-audit](https://shieldcn.dev/skills/installs/shadcn-labs/skills/icon-set-audit.svg?variant=branded&size=xs&label=icon-set-audit)](https://skills.sh/shadcn-labs/skills/icon-set-audit)

### icon-set-extend

向现有图标集新增图标，做到与原作难以区分——从文件自动推断样式规范与共享部件，支持 Lucide、Heroicons、Phosphor 等。

```bash
npx skills add https://github.com/shadcn-labs/skills --skill icon-set-extend
```

[![icon-set-extend](https://shieldcn.dev/skills/installs/shadcn-labs/skills/icon-set-extend.svg?variant=branded&size=xs&label=icon-set-extend)](https://skills.sh/shadcn-labs/skills/icon-set-extend)

## 许可证

基于 [MIT 许可证](LICENSE) 发布。
