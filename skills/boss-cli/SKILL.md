---
name: boss-cli
description: >-
  Automates Boss 直聘 (zhipin.com) in a real Chrome/Edge via Puppeteer and CDP:
  login, chat list, open candidate chat, online resume screenshot, and optional
  Baidu OCR. Use when the user mentions boss-cli, Boss 直聘 automation, 招聘
  聊天, 候选人, 在线简历截图, or running the `boss` CLI.
---

# Boss 直聘 CLI (`boss-cli`)

## What this is

- **Repository**: local Node/TypeScript CLI (`boss` binary) that drives **already installed** Chrome or Edge with **puppeteer-core** (no bundled browser).
- **Not** a hosted API: the agent runs `boss` in a terminal with network access; the user must be logged in (or use `login`).

## Alignment with Anthropic “Agent Skills”

Anthropic’s open repo [anthropics/skills](https://github.com/anthropics/skills) defines skills as **folders with `SKILL.md`** (YAML frontmatter + instructions). The cross-tool spec lives at [agentskills.io](https://agentskills.io). This file follows the same **frontmatter + body** pattern so it can be reused in Cursor, Claude Code plugins, or other Agent Skills hosts.

## Agent Skill 安装路径

- **`boss skill`** 仅输出 Skill 说明，不安装；**`boss skill install`**（无附加参数）才复制到 **`~/.agents/skills/boss-cli/`**（Windows：`%USERPROFILE%\.agents\skills\boss-cli`）。**`boss skill uninstall`** 移除该目录。根目录可用 `BOSS_AGENT_SKILLS_DIR` 覆盖。

## Prerequisites

- **Build**: `npm install` then `npm run build`; entry is `dist/cli/index.js` (see `package.json` `bin`).
- **Chrome/Edge path**: set `CHROME_PATH` or `PUPPETEER_EXECUTABLE_PATH` if auto-detection fails (Windows common paths are tried).
- **Headless mode**: `BOSS_BROWSER_HEADLESS=true`（或 `1` / `yes` / `y`）启用无头模式；**`login` 命令强制有头**，环境变量对其无效。容器 / CI 场景必开。
- **Credentials**: never commit secrets. Config goes to **`%USERPROFILE%\.boss-cli\.env`** and/or **cwd `.env`** (loaded in that order; cwd overrides). Baidu OCR needs `API_KEY` + `SECRET_KEY` when `BOSS_RESUME_OCR` is enabled.

## How to run

- **Interactive REPL** (default): run `node dist/cli/index.js` or `boss` **with no arguments** → `boss> ` prompt.
- **One-shot**: `boss <subcommand> ...` (non-interactive; exits after the command).

## Subcommands (normalize short names)

| Intent | Example | 备注 |
|--------|---------|------|
| Login | `login` | 强制有头 |
| Show help / version | `help` / `version`（也支持 `ver` / `-v` / `--version`）| |
| List candidates | `list [--unread]` | `--unread` 只看未读（角标 >0）|
| Open chat with candidate | `chat <姓名> [--strict]` | `--strict` 精确匹配；仅用于已建立联系的候选人 |
| Per-chat actions | `action <op> [--remark <备注>]` | 操作：`resume` / `not-fit` / `remark` / `agree-resume` / `request-attachment-resume` / `history` / `wechat`；`remark` 必须带 `--remark` |
| Send message | `send [--text <内容>] [--request-resume]` | `--request-resume` 发送后自动「求简历」|
| List positions | `positions` | 含开放/待开放/已关闭状态 |
| Fetch JD detail | `jd <name>` | 抓职位详情，缓存为项目目录同名 `.md` |
| Recommend candidates | `recommend [岗位关键字]` | 可选参数先在岗位下拉模糊匹配并切换 |
| Preview online resume | `preview <姓名> [--job <岗位关键字>]` | 平台对在线简历每日次数有限，**按需使用**|
| **主动打招呼** | `greet <姓名> [--job <岗位关键字>]` | 须先在推荐/深度搜索页加载候选人列表；**会消耗打招呼次数且单次成本较高，谨慎使用**|
| Deep search | `deep-search [岗位关键字]`（别名 `deepsearch`）| 进入深度搜索页，输出当前匹配列表；不会点击「立即匹配」|

Exact flags and `--action` values are defined in `src/cli/cliRouter.ts` and `help` output.

## Automation notes for the agent

1. Prefer **documented env vars** over hardcoding paths; read `src/config.ts` and `src/browser/cdp_browser.ts` for directories and viewport defaults.
2. **Online resume + OCR**: flow lives in `src/toolset/open_chat.ts` and `src/ocr/`; failures should surface real errors (Baidu quota, missing keys, network).
3. **Puppeteer `evaluate`**: this project prefers **string scripts** for `page.evaluate` / `waitForFunction` to avoid build artifacts like `__name is not defined` in the browser context (see `AGENTS.md`).
4. Do not add silent fallbacks; match project rules in `AGENTS.md`.

## When not to use this skill

- Tasks that only need public web scraping without a logged-in Boss account.
- Headless-only sandboxes where Chrome cannot run or CDP cannot attach (unless the user explicitly uses headless and accepts limits).
