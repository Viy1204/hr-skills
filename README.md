# hr-skills

通用 HR 业务场景的 Agent Skills 集合。每个 skill 都是基于真实招聘 / 组织管理 / HR 自动化工作流打磨的、可被兼容 [Agent Skills 规范](https://agentskills.io) 的 AI Agent 直接加载使用的工具。

## 收录的 Skills

| Skill | 适用场景 | 来源 |
|---|---|---|
| [`boss-cli`](skills/boss-cli) | Boss 直聘（zhipin.com）聊天 / 打招呼 / 在线简历 / OCR | [@joohw/boss-cli](https://www.npmjs.com/package/@joohw/boss-cli) |
| [`feishu-attendance-analyzer`](skills/feishu-attendance-analyzer) | 飞书全员考勤分析：平均下班排行 / 加班异常预警 / 部门对比，输出终端 + Excel + 可视化 HTML | 飞书 attendance 统计 API |
| [`feishu-org-chart`](skills/feishu-org-chart) | 飞书通讯录拉部门树 + 飞书画板渲染组织架构图 | 飞书 contact API + dagre + 画板 DSL |
| [`feishu-roster`](skills/feishu-roster) | 飞书人事(标准版)实时拉员工花名册（含入职/转正/试用期/部门/上级），导出 Excel + JSON | 飞书 ehr API + contact API |
| [`liepin-cli`](skills/liepin-cli) | 猎聘（liepin.com）人才搜索 / 简历 / 打招呼 / 聊天 | [@viyzhu/liepin-cli](https://www.npmjs.com/package/@viyzhu/liepin-cli) |

## 什么是 Agent Skill

Anthropic 的开放仓库 [anthropics/skills](https://github.com/anthropics/skills) 定义 skill 为**包含 `SKILL.md` 的文件夹**（YAML frontmatter + 正文）。跨工具的统一规范见 [agentskills.io](https://agentskills.io)。本仓库的每个 skill 都遵循同样的 frontmatter + body 模式。

### 兼容的 Agent

由于遵循通用规范，本仓库的 skill 适用于任何实现了 Agent Skills 加载机制的 AI Agent，覆盖但不限于：

- **Claude Code**（Anthropic）
- **Codex CLI / Codex IDE**（OpenAI）
- **Pi**
- **OpenCode**
- **MiniMax Code**
- **WorkBuddy**
- **Cherry Studio**（在其「Skills / 插件」目录加载即可）

具体到某款 agent 的安装路径可能略有不同（见下表），但 skill 文件本身是同一份 `SKILL.md`，**不需要为不同 agent 维护多份副本**。

## 安装

### 方式一：直接复制给你的 AI Agent（推荐）

把下面这段话直接发给支持 Agent Skills 的 AI Agent，让它帮你装：

```
请帮我安装这个仓库里的所有 skill：https://github.com/Viy1204/hr-skills
具体做法：把仓库的 skills/<skill-name>/ 目录复制到本机的 agent skills 目录，
并按你所在平台的约定完成注册。装完后请告诉我装到了哪、有没有依赖需要补装。
```

Agent 会自行决定：放在全局还是项目内、是否需要软链、是否需要装 npm 全局依赖（如 `@joohw/boss-cli`、`@viyzhu/liepin-cli`）。

### 方式二：自己手动安装

把 `skills/<skill-name>/` 目录复制到你的 agent skills 目录：

- **Claude Code**：全局 `~/.claude/skills/<skill-name>/`，项目内 `<your-project>/.claude/skills/<skill-name>/`
- **Codex CLI**：参考 [codex skills 文档](https://github.com/openai/codex) 的 skills 加载路径
- **Pi / OpenCode / MiniMax Code / WorkBuddy / Cherry Studio**：参见各自文档中的 "skills 目录" 一节

复制后重启 agent，skill 会自动出现在可用技能列表中。

### 方式三：只克隆某一个 skill

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
