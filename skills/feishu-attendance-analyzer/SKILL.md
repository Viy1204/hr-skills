---
name: feishu-attendance-analyzer
description: >
  飞书考勤数据分析：从飞书考勤统计接口拉取全员打卡记录，分析平均下班时间排行榜、
  异常预警（连续加班、深夜打卡、作息异常）、部门对比等多维度报表，输出终端排行榜 +
  Excel 报表 + 自包含可视化 HTML 报表。当用户提到"考勤分析""谁下班最晚""加班排行"
  "打卡统计""考勤报表""谁经常加班""考勤异常""部门考勤对比"时，必须使用此 skill；
  即使只说"看看大家几点下班""谁最卷"也应触发。依赖 feishu-roster 提供在职员工工号清单。
  边界（这些不走本 skill）：单纯拉花名册/在职名单走 feishu-roster；把组织结构画成架构图走
  feishu-org-chart；本 skill 只统计有打卡记录的员工，免打卡员工不在统计范围内，也不涉及
  请假/审批/排班数据。
compatibility: 需要 lark-cli（已登录并开通考勤统计权限）、Python(openpyxl)，依赖 feishu-roster 产出的 roster.json
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 飞书考勤数据分析

从飞书考勤统计 API 拉取全员打卡数据，生成多维度分析报表。

## 前置条件

1. Bot 应用需开通 `attendance:task:readonly` 和 `ehr:employee:readonly` scope
2. 花名册数据依赖 `feishu-roster` skill（用于获取员工工号列表）
3. Python 需安装 `openpyxl`（`pip install openpyxl`）

## 用法

```bash
# 默认：近30天，终端+Excel双输出
python scripts/analyze_attendance.py

# 指定天数
python scripts/analyze_attendance.py --days 7
python scripts/analyze_attendance.py --days 90

# 指定日期范围
python scripts/analyze_attendance.py --start 20260501 --end 20260531

# 仅输出 Excel（不打印终端）
python scripts/analyze_attendance.py --excel-only

# 不生成 HTML 报表
python scripts/analyze_attendance.py --no-html

# 自定义输出目录
python scripts/analyze_attendance.py --out-dir ./attendance_report
```

## 输出内容

### 1. 终端排行榜（默认）

按平均下班时间从晚到早排序，显示 TOP 20：
- 姓名、平均下班时间、打卡天数、最早/最晚记录

### 2. Excel 报表

生成 `考勤分析_<日期>.xlsx`，包含以下 Sheet：

| Sheet | 内容 |
|-------|------|
| 平均下班排行 | 全员平均下班时间排名 |
| 异常预警 | 连续加班、深夜打卡(21:00后)、打卡缺失 |
| 部门对比 | 各部门平均下班时间对比 |
| 打卡明细 | 每人每日打卡时间明细 |

### 3. HTML 报表

生成 `考勤分析_<日期>.html`，自包含、可离线直接用浏览器打开，便于转发/截图。包含：
- 概览卡片：在职人数、有考勤数据人数、异常预警数
- 平均下班排行：全员表格，前三名高亮，附相对时长条形可视化
- 异常预警：按严重程度（高/中/低）分色卡片
- 部门对比：各部门平均下班时间条形对比

加 `--no-html` 可跳过 HTML 生成。

### 4. 异常预警规则

| 异常类型 | 触发条件 |
|----------|----------|
| 深夜打卡 | 下班时间 ≥ 21:00 |
| 连续加班 | 连续 3 天以上下班时间 ≥ 19:30 |
| 打卡缺失 | 出勤天数内有多天无下班打卡记录 |
| 作息异常 | 下班时间波动大（标准差 > 60 分钟） |

## 工作流程

1. **拉花名册**：调用 `feishu-roster` skill 获取在职员工工号列表
2. **拉考勤统计**：通过 `attendance/v1/user_stats_datas/query` API 批量查询（每批 200 人）
3. **解析打卡时间**：从统计字段 `51503-1-2`（下午打卡）中提取 PunchTime
4. **聚合分析**：按 user_id 聚合，计算每人平均下班时间、最早/最晚、标准差
5. **异常检测**：按规则标记异常
6. **输出**：终端打印 + Excel 文件 + HTML 报表

## 数据源说明

- **花名册**：来自 `ehr/v1/employees`（bot 身份），提供工号、姓名、部门
- **考勤统计**：来自 `attendance/v1/user_stats_datas/query`（bot 身份），提供每日打卡时间
- **打卡时间字段**：统计 code `51503-1-2` 的 features 中 `PunchTime` 字段（格式 HH:MM）
- **注意**：只有需要打卡的员工才有数据，免打卡员工不在此统计范围内

## 限制

- 每批最多查 200 人，超过自动分批
- 日期范围不超过 31 天
- 仅统计有考勤打卡记录的员工（免打卡员工不在统计中）
- 需要 bot 身份调用，user token 不支持统计 API
