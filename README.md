# hr-skills

通用 HR 业务场景的 Agent Skills 集合。每个 skill 都是基于真实招聘 / 组织管理 / HR 自动化工作流打磨的、可被 Claude Code（以及兼容 Agent Skills 规范的工具）直接加载使用的工具。

## 收录的 Skills

| Skill | 适用场景 | 来源 |
|---|---|---|
| [`boss-cli`](skills/boss-cli) | Boss 直聘（zhipin.com）聊天 / 打招呼 / 在线简历 / OCR | [@joohw/boss-cli](https://www.npmjs.com/package/@joohw/boss-cli) |
| [`feishu-org-chart`](skills/feishu-org-chart) | 飞书通讯录拉部门树 + 飞书画板渲染组织架构图 | 飞书 contact API + dagre + 画板 DSL |
| [`liepin-cli`](skills/liepin-cli) | 猎聘（liepin.com）人才搜索 / 简历 / 打招呼 / 聊天 | [@viyzhu/liepin-cli](https://www.npmjs.com/package/@viyzhu/liepin-cli) |

## 什么是 Agent Skill

Anthropic 的开放仓库 [anthropics/skills](https://github.com/anthropics/skills) 定义 skill 为**包含 `SKILL.md` 的文件夹**（YAML frontmatter + 正文）。跨工具的规范见 [agentskills.io](https://agentskills.io)。本仓库的每个 skill 都遵循同样的 frontmatter + body 模式，可在 Claude Code、Cursor、Claude Code plugins 以及其他 Agent Skills host 中复用。

## 安装方式

### Claude Code / 兼容工具

将整个 `skills/<skill-name>/` 目录复制或软链到你的 skills 目录：

- 全局：`~/.claude/skills/<skill-name>/`
- 项目内：`<your-project>/.claude/skills/<skill-name>/`

复制后重启 Claude Code，skill 会自动出现在可用技能列表中。

### 单独克隆一个 skill

```bash
# 例子：只克隆 boss-cli
git clone --depth 1 https://github.com/Viy1204/hr-skills.git
cp -r hr-skills/skills/boss-cli ~/.claude/skills/
```

## 贡献

新 skill 同样放在 `skills/` 下、以 `SKILL.md` 为入口。提交前请确认：

- YAML frontmatter 含 `name`（kebab-case，与目录名一致）和 `description`（包含触发词、场景、边界）
- 正文有 "What this is" / "Prerequisites" / "How to run" / "When not to use" 等基础段落
- 不含个人 token、内网 IP、未脱敏的花名册 / 业务数据
