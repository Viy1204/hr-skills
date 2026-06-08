---
name: liepin-cli
description: >-
  猎聘（lpt.liepin.com）招聘者端自动化 CLI：登录、人才搜索、简历详情、推荐/人才库、聊天列表/记录、
  主动打招呼。当用户提到猎聘、liepin、招聘自动化、候选人搜索、批量打招呼、向候选人主动发消息等场景时
  立即触发本 skill；典型说法："用猎聘搜一下前端"、"猎聘打招呼"、"猎聘的简历怎么导出"、"看
  一下聊天记录"、"猎聘的推荐候选人"。它封装了 `liepin` CLI 的常用子命令（search / resume /
  recommend / talent / chatlist / chatmsg / greet / joblist），适用于猎聘上有账号、需要反复搜索
  / 浏览 / 主动触达候选人的 HR 或招聘场景。

  边界（这些不走本 skill）：Boss 直聘的同类操作走 `boss-cli`；不需要猎聘账号的公开页面抓取；
  仅查询已下载的简历文件本身。
compatibility: 需要 Node.js ≥ 20、Chrome 或 Edge 浏览器（自动检测安装路径）
metadata:
  requires:
    bins: ["liepin"]
---

# 猎聘 CLI (`liepin-cli`)

## What this is

- **包名**：`@viyzhu/liepin-cli`（npm 全局安装后得到 `liepin` 命令）
- **本质**：本地 Node/TypeScript CLI，通过 **puppeteer-core** 驱动本机已安装的 Chrome/Edge（**不**自带浏览器内核），模拟招聘者端操作 `lpt.liepin.com`
- **不是**托管 API：智能体在本机终端跑 `liepin`，用户需已登录（或调用 `liepin login`）

## Prerequisites

- **Node.js** ≥ 20
- **Chrome / Edge**：自动检测 Windows / macOS / Linux 常见安装路径；检测失败时手动设置 `CHROME_PATH`
  ```bash
  # macOS
  export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  ```
- **凭据**：不要把账号 cookie、token 等敏感信息提交到仓库。猎聘通过 `liepin login` 在本地浏览器登录即可

## How to run

- **交互式 REPL**：直接 `liepin`（无参数）→ `liepin> ` 提示符
- **一次性命令**：`liepin <subcommand> ...`，执行完即退出

## 常用子命令

### 登录

```bash
liepin login
```

### 搜索人才

```bash
# 基础搜索
liepin search 前端工程师

# 带筛选条件
liepin search 前端工程师 --city 北京 --experience 3-5年 --salary 20-30K
```

### 查看简历

```bash
# resumeId = search / recommend / talent 返回的 resume_id
liepin resume <resumeId>
```

### 推荐 / 人才库

```bash
liepin recommend      # 平台推荐候选人
liepin talent         # 个人人才库
liepin joblist        # 当前账号下的职位列表（取 jobId 用于 greet）
```

### 主动打招呼（重点）

> 这一步是 `boss-cli` 不擅长、但猎聘上招聘方每天都做的事：拿到候选人 ID 后一键打招呼。

```bash
# userId = search / recommend / talent 返回的 user_id
liepin greet <userId> --ejobId <jobId>
```

`--ejobId` 强烈建议传，作用是关联到具体职位 + 触发平台对招呼语 / 权限的校验。

### 聊天管理

```bash
liepin chatlist                          # 聊天列表
liepin chatmsg <oppositeImId>            # 与某候选人的聊天记录（imId = chatlist 返回的 im_id）
```

## 命令参数

| 命令 | 参数 | 说明 |
|------|------|------|
| `search` | `query` | 关键词（必填） |
| | `--city` | 城市（如：北京、上海） |
| | `--experience` | 工作经验（如：3-5年） |
| | `--salary` | 薪资范围（如：20-30K） |
| | `--degree` | 学历（如：本科） |
| | `--page` | 页码 |
| | `--limit` | 返回条数 |
| `resume` | `resumeId` | 简历 ID（`search` / `recommend` / `talent` 返回的 `resume_id`，必填） |
| `chatmsg` | `oppositeImId` | 对方 imId（`chatlist` 返回的 `im_id`，必填） |
| `greet` | `userId` | 候选人 `user_id`（必填） |
| | `--ejobId` | 关联职位 ID（强烈建议传） |

## 故障排除

### Chrome 未找到（自动检测失败）

```bash
export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Windows 常见路径
# set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

### 登录失败

1. 确认 Chrome 已安装并能正常打开
2. 检查网络
3. 手动在浏览器登录一次后再用 CLI（Cookie 可能因过期被踢）

### 被猎聘检测为自动化

- 增加 `--delay` 之类的间隔参数（若有），或自行降低调用频率
- 减少同一会话内 `search` / `greet` 连续触发次数
- 必要时加代理

## When not to use this skill

- Boss 直聘的同类操作：走 `boss-cli`
- 不需要登录就能访问的公开页面抓取：直接 web fetch / scrape
- 已下载到本地的简历文件本身的解析 / 抽取：这是简历解析 skill 的事，与本 skill 无关
