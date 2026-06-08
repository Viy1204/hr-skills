# 飞书 contact API、权限与上传细节

## contact v3 端点

| 用途 | 端点 | 关键参数 |
|---|---|---|
| 部门树（含各级子部门） | `GET /open-apis/contact/v3/departments/{root}/children` | `fetch_child=true`、`department_id_type=open_department_id`；`root=0` 取全公司 |
| 部门直属成员 | `GET /open-apis/contact/v3/users/find_by_department` | `department_id`、`department_id_type=open_department_id`、`user_id_type=open_id` |

要点：
- `find_by_department` **只返回该部门的直属成员**，不含子部门成员 —— 必须对每个部门分别调用。
- 这两个接口都支持分页，`lark-cli` 加 `--page-all` 自动翻页（进度走 stderr，合并 JSON 走 stdout）。
- 部门对象里的 `parent_department_id`（根为 `"0"`）和 `leader_user_id` 是画层级与标负责人的关键字段。

## 权限（最容易卡住的环节）

需要的 scope（在开发者后台「权限管理」开通）：
- `contact:department.base:readonly` —— 读**部门名称**、`parent_department_id`（**没有它部门只返回 open_department_id**）
- `contact:department.organize:readonly` —— 部门组织架构遍历
- `contact:user.base:readonly` —— 成员基础信息
- 嫌细可直接开 `contact:contact:readonly` 覆盖

三步缺一不可（缺任意一步都拿不到部门名称/层级）：
1. **开通 scope** 并**创建发布新版本**，等企业管理员（admin.feishu.cn）审核通过。
2. **配置通讯录数据权限范围**：应用「数据权限 / 通讯录权限范围」设为「全部成员、全部部门」（或至少目标部门）。光有 scope、范围为空仍报 `no dept authority`。
3. **重新授权**：`lark-cli auth login --scope "contact:department.base:readonly,contact:department.organize:readonly,contact:user.department:readonly"`
   —— 注意 `--domain all` **不一定**把部门 scope 带进 token，用 `--scope` 显式点名最稳。授权后 `lark-cli auth status` 里应能看到这些 scope。

身份选择：组织架构通常用 `--as user`（受该用户的通讯录可见范围限制，HR/管理员一般可见全员）。`--as bot` 常因应用通讯录范围为空报 `no dept authority`。

## 岗位字段说明

`find_by_department` 与用户详情接口在多数企业**不返回 job_title**（需要额外字段权限，且要求飞书后台维护了职位）。因此岗位优先从**花名册 Excel 按姓名匹配**（见 gen_chart.py 的 `--roster`）。匹配不上的人（多为新入职、英文昵称）只显示姓名，要在交付时如实告知用户。

## 上传画板细节

1. 转 OpenAPI 格式：`whiteboard-cli -i diagram.json -t openapi -o openapi.json -F json`
   —— `-t openapi` 输出走 `-o` 文件，**不是 stdout**（写 `> file` 会得到空文件）。
2. 取 board_token：`lark-cli docs +create --api-version v2 --doc-format xml --content '<h1>标题</h1><whiteboard type="blank"></whiteboard>' --as user`
   —— 从 `data.new_blocks[]` 里 `block_type=="whiteboard"` 的条目取 `block_token`。不要外层包 `<docx>`（会被转义）。
3. dry-run 探测：`lark-cli whiteboard +update --whiteboard-token <T> --source @openapi.json --input_format raw --overwrite --dry-run --as user`
   —— 日志若出现 `XX whiteboard nodes will be deleted` 说明画板非空，**先问用户**再覆盖。
4. 正式上传：去掉 `--dry-run`，加 `--idempotent-token "<10+字符唯一串>"`。
   —— `--source` 引用文件必须用 `@` 前缀（`--source @openapi.json`），否则把文件名当字面数据。
5. 验证：`lark-cli docs +media-download --type whiteboard --token <T> --output thumb --as user` 下载缩略图肉眼核对。

> 画板一经上传不可增量修改，更新即用新数据覆盖重传。

## Windows / Git Bash 坑（脚本已规避，手敲命令时注意）

- 直接在 Git Bash 跑 `lark-cli api GET /open-apis/...`，MSYS 会把 `/open-apis/...` 篡改成 `C:/Program Files/Git/open-apis/...` → 404。手敲时前缀 `MSYS_NO_PATHCONV=1`。`pull_org.py` 经 subprocess 调用，不触发此转换。
- Python 在 Windows 打开**含中文路径**的文件会因编码错位 `FileNotFoundError`：先用 `cp` 把花名册复制成 ASCII 文件名再读。
- Python 写文本文件用 `newline="\n"`，否则混入 `\r` 会污染后续按行读取（如部门 ID 列表带回车导致 API 报错）。
