---
name: feishu-roster
description: >
  从飞书人事(标准版)的 ehr/v1/employees 接口实时拉取公司员工花名册——含姓名/工号/人员类型(正式/实习/顾问/外包/临时)、
  在职状态、入职日期、转正日期、试用期、部门、职务、职级、工作地点、直属上级、手机、邮箱，映射部门名后导出 Excel + JSON。
  这是飞书后台「花名册」页导出按钮背后的同一个 API，能拿到通讯录拿不到的入职/转正/试用期等人事字段。当用户需要
  "最新花名册""在职名单""员工清单""谁在某个部门""最近入职了谁""某人转正了吗/还在不在试用期""导出在职人员"时触发；
  做组织盘点、算绩效/奖金、核对人员异动等需要权威人员名单的场景，都应先用本 skill 拉一份实时数据，而不是翻可能过期的
  本地导出 xlsx。边界（这些不走本 skill）：薪资不在此接口（飞书人事 OpenAPI 不返回敏感字段，需另给薪资表）；单纯按
  姓名/邮箱查某个人的部门或 open_id 走 lark-contact；把人员关系画成组织架构图走 feishu-org-chart。
compatibility: 需要 lark-cli（已登录并配好应用权限）、Python(openpyxl)
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 飞书花名册实时提取

把飞书人事(标准版)的员工花名册实时拉成结构化的 Excel + JSON，作为后续一切人员相关分析的权威数据源。

## 这个 skill 解决什么

本地导出的花名册 xlsx 会过期（文件名带的是导出那一刻的时间戳）。**权威且永远最新的数据源是飞书人事(标准版)的
`ehr/v1/employees` 接口**——它就是飞书后台「花名册」页那个导出按钮背后的 API，能拿到通讯录拿不到的
**入职日期、人员类型、转正日期、试用期**。做组织盘点、算奖金/绩效、核对人员异动时，先用本 skill 拉一份当下的
花名册，再叠加业务数据。

> ⚠️ **薪资不在此接口**（敏感字段，飞书人事 OpenAPI 不返回）。需要月薪折算金额时，请用户另给薪资表。

## 前置检查

1. `lark-cli auth status` 确认已登录（部门名映射用的是 user 身份）。
2. 应用（bot）需开通 `ehr:employee:readonly`，否则拉花名册会报 `app_scope_not_applied`——去开发者后台开通即可，
   bot scope 点开即生效，无需重新 auth login。
3. 部门名映射走通讯录 `contact:department.base:readonly`（user 身份）。缺这个 scope 脚本不报错，只是「部门」列
   回退成 department_id。
4. 装好 `openpyxl`（`pip install openpyxl`）用于导出 Excel。

| 调用 | 身份 | scope |
|---|---|---|
| `ehr/v1/employees`（花名册主体） | `--as bot` | `ehr:employee:readonly` |
| `contact/v3/departments`（部门名映射） | `--as user` | `contact:department.base:readonly` |

## 用法

直接跑脚本（已把 Windows/MSYS 路径、相对路径、分页、双身份等坑全部踩平）：

```bash
# 默认拉在职(status=2)全部人员，导出 Excel + JSON
python scripts/pull_roster.py --out-dir ./roster

# 含离职/待入职等全部状态
python scripts/pull_roster.py --out-dir ./roster --status 1,2,3,4,5

# 自定义 Excel 文件名
python scripts/pull_roster.py --out-dir ./roster --xlsx-name "花名册_最新.xlsx"
```

产出：
- `roster.json` —— 结构化数据（含 `pulled_at` 时间戳、`count`、`rows`），后续脚本直接读它
- `花名册_<日期>.xlsx` —— 实习生行标黄，冻结首行，列宽已调

跑完把人数、人员类型分布、Excel 路径报给用户。需要按部门/入职时间筛选或交叉其他数据时，**读 `roster.json` 用
Python 处理，不要重复调 API**。

## 字段与枚举

`roster.json` 每行字段：姓名 / 工号 / 人员类型 / 在职状态 / 入职日期 / 转正日期 / 试用期(月) / 部门 / 职务 /
职级 / 工作地点 / 直属上级 / 手机 / 邮箱。

- **人员类型**：1 正式 / 2 实习 / 3 顾问 / 4 外包 / 5 临时
- **在职状态**：1 待入职 / 2 在职 / 3 取消入职 / 4 待离职 / 5 离职

## 典型用法

- **判断是否转正 / 还在试用期**：拿该人 `转正日期` 和当天比较——转正日期在未来＝仍在试用期。这是判断奖金参与
  资格、转正提醒等的客观依据。
- **最近入职**：按 `入职日期` 排序，或筛 `--status 1,2`。
- **某部门有谁**：读 `roster.json` 按「部门」过滤。
- **人员异动核对**：和上一次的 `roster.json` 对比 `工号` 集合，找出新增 / 离开。

## 不适用（走别的 skill）

- 只想按姓名 / 邮箱查某个人的部门、open_id、联系方式 → `lark-contact`。
- 把部门层级 / 汇报关系画成组织架构图 → `feishu-org-chart`。
- 要薪资数据 → 本接口不返回，需用户另给薪资表。

## 实现说明（脚本已处理，了解即可）

- ehr 接口用 tenant_access_token，必须 `--as bot`。
- Git Bash(MSYS) 会把 `/open-apis/...` 篡改成 Windows 路径导致 404 —— 脚本在子进程环境强制 `MSYS_NO_PATHCONV=1`。
- lark-cli `--params @file` 只认 cwd 内的相对路径 —— 脚本把参数文件写进 out-dir 并以 cwd=out-dir 调用。
- `--page-all` 的进度行会混进 stdout —— 解析时从首个 `{` 截断。
