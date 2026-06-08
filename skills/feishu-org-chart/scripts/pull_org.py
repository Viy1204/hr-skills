# -*- coding: utf-8 -*-
"""
用飞书 contact/v3 原生 API 拉取「完整部门树 + 每个部门的直属成员」，落盘到 --out-dir。

为什么用 Python 调 lark-cli 而不是直接在 Git Bash 里跑：Git Bash(MSYS) 会把
`/open-apis/...` 这类参数当成路径篡改成 Windows 绝对路径，导致 404。subprocess 经
cmd.exe / sh 执行不会触发这个转换，从根上避开这个坑。params 用 @临时文件传，避开 JSON 引号转义。

产出：
  <out-dir>/departments_raw.json
  <out-dir>/members/<open_department_id>.json

用法：
  python pull_org.py --out-dir ./org-data [--as user] [--root 0]
"""
import argparse, json, os, subprocess, sys, tempfile

sys.stdout.reconfigure(encoding="utf-8")


def api(path, params, ident):
    """调用 lark-cli api GET，返回解析后的 JSON（失败返回 None）。"""
    pf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(params, pf)
    pf.close()
    try:
        cmd = f'lark-cli api GET {path} --params @"{pf.name}" --page-all --as {ident} --format json'
        r = subprocess.run(cmd, shell=True, capture_output=True)
        out = r.stdout.decode("utf-8", "replace").strip()
        if not out:
            return None
        return json.loads(out)
    except Exception as e:
        sys.stderr.write(f"[warn] {path}: {e}\n")
        return None
    finally:
        os.unlink(pf.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--as", dest="ident", default="user", choices=["user", "bot"])
    ap.add_argument("--root", default="0", help="根部门 open_department_id，默认 0=全公司")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.out_dir, "members"), exist_ok=True)

    # 1) 部门树（fetch_child=true 一次递归取全部层级）
    dep = api(f"/open-apis/contact/v3/departments/{args.root}/children",
              {"fetch_child": True, "department_id_type": "open_department_id"}, args.ident)
    if not dep or dep.get("code") != 0:
        sys.stderr.write("拉取部门树失败。检查：1) lark-cli 已登录；2) 应用有 "
                         "contact:department.base:readonly 等 scope 且已 auth login 显式授权；"
                         "3) 通讯录数据权限范围已设为全部部门。详见 references/api-and-auth.md\n")
        sys.stderr.write(json.dumps(dep, ensure_ascii=False)[:500] + "\n")
        sys.exit(1)
    items = dep["data"]["items"]
    # 校验拿到了部门名称（缺 scope 时只返回 open_department_id）
    if items and not items[0].get("name"):
        sys.stderr.write("部门返回缺少 name 字段——通讯录部门读取权限不足。"
                         "见 references/api-and-auth.md 配置权限后重试。\n")
        sys.exit(1)
    json.dump(dep, open(os.path.join(args.out_dir, "departments_raw.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"departments: {len(items)}")

    # 2) 每个部门的直属成员
    empty = {"code": 0, "data": {"items": []}}
    for i, d in enumerate(items, 1):
        did = d["open_department_id"]
        res = api("/open-apis/contact/v3/users/find_by_department",
                  {"department_id": did, "department_id_type": "open_department_id",
                   "user_id_type": "open_id"}, args.ident)
        if not res:
            res = empty
        json.dump(res, open(os.path.join(args.out_dir, "members", f"{did}.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"  [{i}/{len(items)}] {d.get('name','?')}: "
              f"{len(res.get('data',{}).get('items',[]) or [])}人")

    print("done.")


if __name__ == "__main__":
    main()
