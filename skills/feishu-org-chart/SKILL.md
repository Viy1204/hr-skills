---
name: feishu-org-chart
description: >
  从飞书通讯录实时拉取部门树和成员，在飞书画板上画出公司组织架构图——展示部门层级、每个员工，
  可叠加岗位（按花名册姓名匹配）、标注部门负责人，并嵌入飞书云文档交付。当用户想把公司/团队的
  组织结构、部门层级、汇报关系可视化成一张层级图时就用本 skill，典型说法："画组织架构图""组织结构图"
  "org chart""部门架构图""把团队画成图""各部门都有谁画出来""标上每个组的 leader""谁汇报给谁画成图"——
  即使没明说"飞书"或"画板"也应触发；HR 做全员架构图、招人后重出架构图等场景同样适用。它封装了
  contact API 拉数、岗位匹配、dagre 自动布局、画板上传的全流程，并规避了权限配置与 Windows 路径的坑。
  边界（这些不走本 skill）：单纯查某个人的部门/open_id 走 lark-contact；把已有的图/截图/mermaid
  渲染或下载成图片、总结飞书文档内容、画业务流程图、做组织架构 PPT、用 HTML 搭可交互组织网页，均非本 skill。
compatibility: 需要 lark-cli（已登录）、@larksuite/whiteboard-cli、Python(openpyxl 可选)
metadata:
  requires:
    bins: ["lark-cli", "python"]
---

# 飞书组织架构图

把飞书通讯录的部门树 + 成员，画成一张层级清晰、细到每个人的组织架构图，传到飞书画板。

## 为什么这么设计

组织架构动辄几十个部门、上百人，层级也不规整。手工 flex 树有「每父 ≤5 子、≤4 层」的硬限制，撑不住；
所以用 **dagre 自动布局**：每个部门做成一张卡片（部门名 + 人数 + 成员逐行列出 + 负责人标注），
部门之间按 `parent_department_id` 连父子，引擎自动排版。员工作为卡片内的文字行出现，既「细到每个人」
又不会让连线爆炸。岗位飞书 API 一般取不到，从花名册按姓名补。

## 前置检查

1. `lark-cli auth status` 确认已登录。组织架构读取要求应用具备通讯录**部门**读取权限——
   这是最容易卡住的地方，**先读 `references/api-and-auth.md` 的「权限」一节**确认 scope、
   数据范围、重新授权都到位。`pull_org.py` 会在权限不足（部门无 name）时明确报错并指向该文档。
2. `npx -y @larksuite/whiteboard-cli@^0.2.11 --version` 确认画板 CLI 可用。
3. 选定产物目录，如 `./org-chart/`，本指南下面用 `$DIR` 指代。

## 流程

### 第 1 步 · 拉数据

```bash
python scripts/pull_org.py --out-dir $DIR/data --as user
```
产出 `$DIR/data/departments_raw.json` 和 `$DIR/data/members/*.json`。脚本会逐部门打印人数。
若报权限错误，按 `references/api-and-auth.md` 配好权限再重试，别绕过。

### 第 2 步 · 生成画板 DSL

岗位来源：飞书 API 通常不返回岗位。若用户有花名册 Excel，用 `--roster` 按姓名补岗位
（先确认姓名列、岗位列的列号，0 基）；Windows 上若花名册路径含中文，先 `cp` 成 ASCII 文件名再传入。

```bash
# 有花名册（示例：姓名在第2列=index1，岗位在第5列=index4）
python scripts/gen_chart.py --data-dir $DIR/data --company-name "公司名" \
    --roster roster.xlsx --name-col 1 --title-col 4 --out $DIR/diagram.json
# 没有花名册（只显示姓名）
python scripts/gen_chart.py --data-dir $DIR/data --company-name "公司名" --out $DIR/diagram.json
```
脚本会打印 `title_matched=N`，即多少人匹配到岗位。匹配不上的人只显示姓名，交付时如实告知用户。

### 第 3 步 · 本地渲染预览（先给用户看）

```bash
npx -y @larksuite/whiteboard-cli@^0.2.11 -i $DIR/diagram.json -o $DIR/diagram.png
```
看一眼：层级对不对、有无文字截断、连线是否清晰。图通常很宽（一级部门多时尤甚），属正常。
有问题按 `references/api-and-auth.md` 末尾的症状或 lark-whiteboard-cli skill 的症状表调整后重渲。
**确认无误再上传**——画板一经上传不可增量改。

### 第 4 步 · 建文档承载画板并上传

飞书 CLI 无法创建独立画板，画板必须嵌在云文档里。完整命令与 dry-run 拦截规则见
`references/api-and-auth.md` 的「上传画板细节」。要点：
1. `whiteboard-cli ... -t openapi -o $DIR/openapi.json` 转格式（输出走 `-o`，不是 stdout）。
2. `lark-cli docs +create --api-version v2 ...` 建文档+空白画板块，取 `block_token`。
3. `lark-cli whiteboard +update --source @$DIR/openapi.json --input_format raw --overwrite --dry-run` 探测，
   非空则先问用户；空则去掉 `--dry-run` 加 `--idempotent-token` 正式传。
4. 下载缩略图肉眼复核，把文档链接交给用户。

## 交付时说清楚

- 数据口径：实时飞书通讯录 + 抓取日期；岗位来自花名册（说明匹配率、未匹配名单）。
- 文档链接 + 画板不可增量修改（更新=覆盖重传）。
- 文档文件名默认可能是「Untitled」（文档内 H1 标题是对的），如需改名让用户在飞书里手动改。

## 调整方向（按用户需求）

- 配色/分层：`gen_chart.py` 的 `TIER` 按部门深度配色，可改。
- 节点信息：默认「姓名 + 岗位 +（负责人）」，可只留姓名或加更多字段（需在 pull 时多取字段）。
- 想按业务线分组、或只画到部门/团队层不到人：相应裁剪 `gen_chart.py` 的成员行或部门集合。
