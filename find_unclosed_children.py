#!/usr/bin/env python3
"""
查询"父需求已关闭但子需求未关闭"的情况
==========================================
逻辑：
1. 分页查询所有2026年以前创建的、非关闭状态(非rejected)的需求
2. 筛选出有 parent_id 的子需求
3. 批量查询这些子需求的父需求状态
4. 找出父需求状态为 rejected(已关闭) 的情况
"""

import requests
import time
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

# ==================== 配置区 ====================
WORKSPACE_ID = "20398362"
BASE_URL = "https://api.tapd.cn"
BATCH_SIZE = 200
REQUEST_DELAY = 0.1

# 需求中非关闭的所有状态
NON_CLOSED_STATUSES = [
    "planning", "status_5", "status_6", "audited", "status_19",
    "status_4", "developing", "product_experience", "for_test",
    "status_20", "status_22", "status_23", "status_2", "status_16",
    "status_10", "status_21", "status_17", "status_18", "status_9",
    "status_24", "status_15"
]

# 状态中文映射
STATUS_MAP = {
    "rejected": "已关闭",
    "planning": "规划中",
    "status_5": "需求评审",
    "status_6": "需求修改",
    "audited": "已评审",
    "status_19": "实现中",
    "status_4": "待开发",
    "developing": "开发中",
    "product_experience": "产品体验",
    "for_test": "待测试",
    "status_20": "测试中",
    "status_22": "验证中",
    "status_23": "待发布",
    "status_2": "已实现(原)",
    "status_16": "已关闭(原)",
    "status_10": "已完成",
    "status_21": "灰度中",
    "status_17": "已实现",
    "status_18": "未开始",
    "status_9": "挂起",
    "status_24": "全量发布",
    "status_15": "已拒绝",
}

# ==================== 全局变量 ====================
session = requests.Session()
api_user = ""
api_password = ""


def setup_auth():
    """设置 API 认证"""
    global api_user, api_password
    api_user = os.environ.get("TAPD_API_USER", "")
    api_password = os.environ.get("TAPD_API_PASSWORD", "")

    if not api_user or not api_password:
        api_user = input("API 账号 (api_user): ").strip()
        api_password = input("API 口令 (api_password): ").strip()

    if not api_user or not api_password:
        print("❌ API 凭据不能为空！")
        sys.exit(1)

    # 验证
    print("🔐 验证 API 凭据...")
    try:
        resp = session.get(
            f"{BASE_URL}/quickstart/testauth",
            auth=(api_user, api_password),
            timeout=10
        )
        if resp.status_code == 200:
            print("✅ API 认证成功！\n")
        else:
            print(f"❌ API 认证失败！状态码: {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        sys.exit(1)


def query_stories(page=1, limit=200, status=None, created=None, ids=None, parent_id=None, fields=None):
    """查询需求列表"""
    params = {
        "workspace_id": WORKSPACE_ID,
        "limit": limit,
        "page": page,
    }
    if status:
        params["status"] = status
    if created:
        params["created"] = created
    if ids:
        params["id"] = ids
    if parent_id:
        params["parent_id"] = parent_id
    if fields:
        params["fields"] = fields

    try:
        resp = session.get(
            f"{BASE_URL}/stories",
            params=params,
            auth=(api_user, api_password),
            timeout=30
        )
        data = resp.json()
        if data.get("status") == 1 and data.get("data"):
            stories = [item.get("Story", {}) for item in data["data"]]
            return stories, int(data.get("count", 0))
        return [], 0
    except Exception as e:
        print(f"  ⚠️ 查询失败 (page={page}): {e}")
        return [], 0


def get_status_name(status_code):
    """获取状态中文名"""
    return STATUS_MAP.get(status_code, status_code)


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║   查询"父需求已关闭但子需求未关闭"的情况                      ║
║   项目: 运营商合作部_技术研发中心 (ID: 20398362)              ║
║   范围: 2026年以前创建的需求                                  ║
╚══════════════════════════════════════════════════════════════╝
    """)

    setup_auth()

    # ============ Step 1: 收集所有非关闭状态的子需求 ============
    print("📋 Step 1: 查询所有2026年以前创建的、非关闭状态的需求...")

    all_non_closed = []
    status_str = "|".join(NON_CLOSED_STATUSES)
    page = 1

    # 先查第一页获取总数
    stories, total = query_stories(
        page=1, limit=BATCH_SIZE,
        status=status_str,
        created="<2026-01-01",
        fields="id,name,status,parent_id,created"
    )
    if total == 0:
        print("没有找到符合条件的需求")
        return

    print(f"  总共有 {total} 条非关闭状态的需求（2026年前创建）")
    all_non_closed.extend(stories)

    total_pages = (total + BATCH_SIZE - 1) // BATCH_SIZE
    for page in range(2, total_pages + 1):
        stories, _ = query_stories(
            page=page, limit=BATCH_SIZE,
            status=status_str,
            created="<2026-01-01",
            fields="id,name,status,parent_id,created"
        )
        all_non_closed.extend(stories)
        if page % 5 == 0:
            print(f"  已获取 {page}/{total_pages} 页...")
        time.sleep(REQUEST_DELAY)

    print(f"  ✅ 共获取 {len(all_non_closed)} 条非关闭需求\n")

    # ============ Step 2: 筛选有 parent_id 的子需求 ============
    print("📋 Step 2: 筛选有父需求的子需求...")
    children_with_parent = [
        s for s in all_non_closed
        if s.get("parent_id") and s["parent_id"] != "0" and s["parent_id"] != ""
    ]
    print(f"  ✅ 其中 {len(children_with_parent)} 条有父需求\n")

    if not children_with_parent:
        print("没有找到有父需求的子需求")
        return

    # ============ Step 3: 收集所有涉及的父需求 ID ============
    print("📋 Step 3: 查询这些子需求的父需求状态...")
    parent_ids = list(set(s["parent_id"] for s in children_with_parent))
    print(f"  涉及 {len(parent_ids)} 个不同的父需求")

    # 批量查询父需求状态（每次最多查 200 个 ID）
    parent_status_map = {}
    parent_name_map = {}
    batch_count = 0

    for i in range(0, len(parent_ids), 50):
        batch_ids = parent_ids[i:i + 50]
        ids_str = ",".join(batch_ids)
        batch_count += 1

        parents, _ = query_stories(
            page=1, limit=50,
            ids=ids_str,
            fields="id,name,status"
        )

        for p in parents:
            parent_status_map[p["id"]] = p.get("status", "unknown")
            parent_name_map[p["id"]] = p.get("name", "未知")

        if batch_count % 5 == 0:
            print(f"  已查询 {min(i + 50, len(parent_ids))}/{len(parent_ids)} 个父需求...")
        time.sleep(REQUEST_DELAY)

    print(f"  ✅ 查询完毕\n")

    # ============ Step 4: 找出父需求已关闭但子需求未关闭的情况 ============
    print("📋 Step 4: 筛选父需求已关闭但子需求未关闭的情况...\n")

    # 按父需求分组
    problematic = defaultdict(list)

    for child in children_with_parent:
        parent_id = child["parent_id"]
        parent_status = parent_status_map.get(parent_id, "unknown")

        if parent_status == "rejected":
            child_status = get_status_name(child.get("status", "unknown"))
            problematic[parent_id].append({
                "id": child["id"],
                "short_id": child["id"].replace("1020398362", ""),
                "name": child.get("name", "未知"),
                "status": child_status,
                "status_code": child.get("status", ""),
                "created": child.get("created", ""),
            })

    if not problematic:
        print("🎉 没有找到 父需求已关闭但子需求未关闭 的情况！")
        return

    # ============ 输出结果 ============
    print("=" * 80)
    print(f"⚠️  发现 {len(problematic)} 个父需求已关闭但仍有未关闭子需求")
    total_unclosed_children = sum(len(v) for v in problematic.values())
    print(f"   涉及 {total_unclosed_children} 个未关闭的子需求")
    print("=" * 80)

    # 按子需求数量排序
    sorted_parents = sorted(problematic.items(), key=lambda x: len(x[1]), reverse=True)

    results = []
    for idx, (parent_id, children) in enumerate(sorted_parents, 1):
        parent_name = parent_name_map.get(parent_id, "未知")
        parent_short_id = parent_id.replace("1020398362", "")

        print(f"\n{'─' * 70}")
        print(f"[{idx}] 父需求: {parent_name}")
        print(f"    ID: {parent_short_id} (已关闭)")
        print(f"    未关闭子需求 ({len(children)} 个):")

        parent_result = {
            "parent_id": parent_short_id,
            "parent_long_id": parent_id,
            "parent_name": parent_name,
            "unclosed_children": []
        }

        for child in children:
            print(f"      - [{child['short_id']}] {child['name']}")
            print(f"        状态: {child['status']} | 创建时间: {child['created']}")
            parent_result["unclosed_children"].append({
                "id": child["short_id"],
                "long_id": child["id"],
                "name": child["name"],
                "status": child["status"],
                "created": child["created"],
            })

        results.append(parent_result)

    # 保存结果到 JSON 文件
    output_file = "unclosed_children_report.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_parent_stories": len(problematic),
                "total_unclosed_children": total_unclosed_children,
            },
            "data": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n\n📊 详细结果已保存到: {output_file}")

    # 输出按状态的统计
    status_count = defaultdict(int)
    for children in problematic.values():
        for child in children:
            status_count[child["status"]] += 1

    print(f"\n{'=' * 50}")
    print("📈 未关闭子需求的状态分布:")
    print(f"{'=' * 50}")
    for status, count in sorted(status_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count} 个")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
