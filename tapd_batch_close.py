#!/usr/bin/env python3
"""
TAPD 批量关闭需求和任务脚本
=========================
功能：
1. 查询所有非排除状态的需求（Story），排除「月迭代 26 年 3 月」的需求
2. 将这些需求状态改为「已关闭」(rejected)
3. 查询所有未完成的任务（Task），排除「月迭代 26 年 3 月」的任务
4. 将这些任务状态改为「已完成」(done)

使用方式：
    python3 tapd_batch_close.py

首次运行会要求输入 TAPD API 凭据。
"""

import requests
import time
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ==================== 配置区 ====================
WORKSPACE_ID = "20398362"
BASE_URL = "https://api.tapd.cn"

# 「月迭代 26 年 3 月」的迭代 ID —— 需要排除
EXCLUDE_ITERATION_ID = "1020398362002224029"

# 需求（Story）的排除状态（这些不需要处理）
STORY_EXCLUDE_STATUSES = {
    "rejected",      # 已关闭（目标状态）
    "status_17",     # 已实现
    "status_18",     # 未开始
    "status_9",      # 挂起
    "status_24",     # 全量发布
    "status_15",     # 已拒绝
}

# 需求（Story）中需要处理的状态列表
STORY_PROCESS_STATUSES = [
    "planning", "status_5", "status_6", "audited", "status_19",
    "status_4", "developing", "product_experience", "for_test",
    "status_20", "status_22", "status_23", "status_2", "status_16",
    "status_10", "status_21"
]

# 任务（Task）中需要处理的状态
TASK_PROCESS_STATUSES = ["open", "progressing"]

# 并发数（同时发出的请求数）
MAX_WORKERS = 10

# 每批处理数量
BATCH_SIZE = 200

# 请求间隔（秒），避免触发限流
REQUEST_DELAY = 0.05

# 日志文件
LOG_FILE = "tapd_batch_close.log"

# 进度文件（记录已处理的 ID，方便断点续传）
PROGRESS_FILE = "tapd_batch_close_progress.json"

# ==================== 全局变量 ====================
session = requests.Session()
api_user = ""
api_password = ""


def log(message, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


def load_progress():
    """加载进度文件"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"closed_stories": [], "closed_tasks": [], "last_run": None}


def save_progress(progress):
    """保存进度文件"""
    progress["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def setup_auth():
    """设置 API 认证"""
    global api_user, api_password

    # 先尝试从环境变量读取
    api_user = os.environ.get("TAPD_API_USER", "")
    api_password = os.environ.get("TAPD_API_PASSWORD", "")

    if not api_user or not api_password:
        print("\n" + "=" * 60)
        print("TAPD API 认证设置")
        print("=" * 60)
        print("请输入 TAPD API 凭据（可在公司管理 -> 开放平台查看）")
        print("或设置环境变量 TAPD_API_USER 和 TAPD_API_PASSWORD")
        print("=" * 60)
        api_user = input("API 账号 (api_user): ").strip()
        api_password = input("API 口令 (api_password): ").strip()

    if not api_user or not api_password:
        print("❌ API 凭据不能为空！")
        sys.exit(1)

    # 验证凭据
    print("\n🔐 验证 API 凭据...")
    try:
        resp = session.get(
            f"{BASE_URL}/quickstart/testauth",
            auth=(api_user, api_password),
            timeout=10
        )
        if resp.status_code == 200:
            print("✅ API 认证成功！")
            return True
        else:
            print(f"❌ API 认证失败！状态码: {resp.status_code}")
            print(f"   返回内容: {resp.text[:200]}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        sys.exit(1)


def query_stories(page=1, limit=200, created_range=None):
    """查询需求列表"""
    params = {
        "workspace_id": WORKSPACE_ID,
        "status": "|".join(STORY_PROCESS_STATUSES),
        "limit": limit,
        "page": page,
        "fields": "id,name,status,iteration_id,created"
    }
    if created_range:
        params["created"] = created_range

    try:
        resp = session.get(
            f"{BASE_URL}/stories",
            params=params,
            auth=(api_user, api_password),
            timeout=30
        )
        data = resp.json()
        if data.get("status") == 1 and data.get("data"):
            stories = []
            for item in data["data"]:
                story = item.get("Story", {})
                stories.append(story)
            return stories, int(data.get("count", 0))
        return [], 0
    except Exception as e:
        log(f"查询需求失败 (page={page}): {e}", "ERROR")
        return [], 0


def query_tasks(page=1, limit=200, created_range=None):
    """查询任务列表"""
    params = {
        "workspace_id": WORKSPACE_ID,
        "status": "|".join(TASK_PROCESS_STATUSES),
        "limit": limit,
        "page": page,
        "fields": "id,name,status,iteration_id,created"
    }
    if created_range:
        params["created"] = created_range

    try:
        resp = session.get(
            f"{BASE_URL}/tasks",
            params=params,
            auth=(api_user, api_password),
            timeout=30
        )
        data = resp.json()
        if data.get("status") == 1 and data.get("data"):
            tasks = []
            for item in data["data"]:
                task = item.get("Task", {})
                tasks.append(task)
            return tasks, int(data.get("count", 0))
        return [], 0
    except Exception as e:
        log(f"查询任务失败 (page={page}): {e}", "ERROR")
        return [], 0


def update_story_status(story_id, new_status="rejected"):
    """更新单条需求状态"""
    try:
        resp = session.post(
            f"{BASE_URL}/stories",
            data={
                "id": story_id,
                "workspace_id": WORKSPACE_ID,
                "status": new_status
            },
            auth=(api_user, api_password),
            timeout=15
        )
        data = resp.json()
        if data.get("status") == 1:
            return True, story_id
        else:
            return False, f"{story_id}: {data.get('info', '未知错误')}"
    except Exception as e:
        return False, f"{story_id}: {str(e)}"


def update_task_status(task_id, new_status="done"):
    """更新单条任务状态"""
    try:
        resp = session.post(
            f"{BASE_URL}/tasks",
            data={
                "id": task_id,
                "workspace_id": WORKSPACE_ID,
                "status": new_status
            },
            auth=(api_user, api_password),
            timeout=15
        )
        data = resp.json()
        if data.get("status") == 1:
            return True, task_id
        else:
            return False, f"{task_id}: {data.get('info', '未知错误')}"
    except Exception as e:
        return False, f"{task_id}: {str(e)}"


def collect_all_stories():
    """收集所有需要处理的需求 ID"""
    log("📋 开始收集需要关闭的需求...")
    all_stories = []
    page = 1

    # 先查第一页获取总数
    stories, total = query_stories(page=1, limit=BATCH_SIZE)
    if total == 0:
        log("没有需要处理的需求")
        return []

    log(f"总共有 {total} 条非排除状态的需求")

    # 过滤掉「月迭代 26 年 3 月」的需求
    for s in stories:
        if s.get("iteration_id") != EXCLUDE_ITERATION_ID:
            all_stories.append(s)

    # 继续查剩余页
    total_pages = (total + BATCH_SIZE - 1) // BATCH_SIZE
    for page in range(2, total_pages + 1):
        stories, _ = query_stories(page=page, limit=BATCH_SIZE)
        for s in stories:
            if s.get("iteration_id") != EXCLUDE_ITERATION_ID:
                all_stories.append(s)
        log(f"  已获取第 {page}/{total_pages} 页数据...")
        time.sleep(REQUEST_DELAY)

    log(f"✅ 收集完毕：{len(all_stories)} 条需求需要关闭（已排除月迭代26年3月的需求）")
    return all_stories


def collect_all_tasks():
    """收集所有需要处理的任务 ID"""
    log("📋 开始收集需要关闭的任务...")
    all_tasks = []
    page = 1

    tasks, total = query_tasks(page=1, limit=BATCH_SIZE)
    if total == 0:
        log("没有需要处理的任务")
        return []

    log(f"总共有 {total} 条非完成状态的任务")

    for t in tasks:
        if t.get("iteration_id") != EXCLUDE_ITERATION_ID:
            all_tasks.append(t)

    total_pages = (total + BATCH_SIZE - 1) // BATCH_SIZE
    for page in range(2, total_pages + 1):
        tasks, _ = query_tasks(page=page, limit=BATCH_SIZE)
        for t in tasks:
            if t.get("iteration_id") != EXCLUDE_ITERATION_ID:
                all_tasks.append(t)
        log(f"  已获取第 {page}/{total_pages} 页数据...")
        time.sleep(REQUEST_DELAY)

    log(f"✅ 收集完毕：{len(all_tasks)} 条任务需要关闭（已排除月迭代26年3月的任务）")
    return all_tasks


def batch_update_stories(stories, progress):
    """批量更新需求状态"""
    already_done = set(progress.get("closed_stories", []))
    to_process = [s for s in stories if s["id"] not in already_done]

    if not to_process:
        log("所有需求已处理完毕！")
        return

    log(f"🚀 开始批量关闭需求：共 {len(to_process)} 条待处理（跳过已处理 {len(already_done)} 条）")

    success_count = 0
    fail_count = 0
    batch_num = 0

    # 分批处理
    for i in range(0, len(to_process), MAX_WORKERS * 5):
        batch = to_process[i:i + MAX_WORKERS * 5]
        batch_num += 1

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {}
            for story in batch:
                future = executor.submit(update_story_status, story["id"], "rejected")
                futures[future] = story["id"]
                time.sleep(REQUEST_DELAY)  # 小延迟避免瞬间打满

            for future in as_completed(futures):
                success, result = future.result()
                if success:
                    success_count += 1
                    progress["closed_stories"].append(result)
                else:
                    fail_count += 1
                    log(f"  ❌ 失败: {result}", "ERROR")

        # 每批处理完保存进度
        save_progress(progress)
        processed = i + len(batch)
        log(f"  📊 进度: {processed}/{len(to_process)} | 成功: {success_count} | 失败: {fail_count}")

    log(f"✅ 需求关闭完毕！成功: {success_count} | 失败: {fail_count}")


def batch_update_tasks(tasks, progress):
    """批量更新任务状态"""
    already_done = set(progress.get("closed_tasks", []))
    to_process = [t for t in tasks if t["id"] not in already_done]

    if not to_process:
        log("所有任务已处理完毕！")
        return

    log(f"🚀 开始批量关闭任务：共 {len(to_process)} 条待处理（跳过已处理 {len(already_done)} 条）")

    success_count = 0
    fail_count = 0

    for i in range(0, len(to_process), MAX_WORKERS * 5):
        batch = to_process[i:i + MAX_WORKERS * 5]

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {}
            for task in batch:
                future = executor.submit(update_task_status, task["id"], "done")
                futures[future] = task["id"]
                time.sleep(REQUEST_DELAY)

            for future in as_completed(futures):
                success, result = future.result()
                if success:
                    success_count += 1
                    progress["closed_tasks"].append(result)
                else:
                    fail_count += 1
                    log(f"  ❌ 失败: {result}", "ERROR")

        save_progress(progress)
        processed = i + len(batch)
        log(f"  📊 进度: {processed}/{len(to_process)} | 成功: {success_count} | 失败: {fail_count}")

    log(f"✅ 任务关闭完毕！成功: {success_count} | 失败: {fail_count}")


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║          TAPD 批量关闭需求和任务脚本 v1.0               ║
╠══════════════════════════════════════════════════════════╣
║  项目: 运营商合作部_技术研发中心 (ID: 20398362)         ║
║  操作: 将历史需求关闭(rejected)，任务完成(done)         ║
║  排除: 「月迭代 26 年 3 月」迭代中的需求和任务          ║
║  排除状态: 已关闭/已实现/未开始/挂起/全量发布/已拒绝    ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 加载进度
    progress = load_progress()
    if progress.get("last_run"):
        print(f"📂 发现上次运行记录 ({progress['last_run']})")
        print(f"   已处理需求: {len(progress.get('closed_stories', []))} 条")
        print(f"   已处理任务: {len(progress.get('closed_tasks', []))} 条")
        resume = input("是否继续上次的进度？(Y/n): ").strip().lower()
        if resume == 'n':
            progress = {"closed_stories": [], "closed_tasks": [], "last_run": None}
            print("🔄 已重置进度\n")

    # 认证
    setup_auth()

    # 确认操作
    print("\n" + "=" * 60)
    print("⚠️  即将执行以下操作：")
    print("  1. 查询所有非排除状态的需求，排除「月迭代 26 年 3 月」")
    print("  2. 将这些需求状态改为「已关闭」(rejected)")
    print("  3. 查询所有未完成的任务，排除「月迭代 26 年 3 月」")
    print("  4. 将这些任务状态改为「已完成」(done)")
    print("=" * 60)
    confirm = input("\n确认执行？(y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消操作。")
        return

    start_time = time.time()
    log("=" * 60)
    log("开始执行批量关闭操作")
    log("=" * 60)

    # Step 1: 收集并关闭需求
    stories = collect_all_stories()
    if stories:
        batch_update_stories(stories, progress)

    # Step 2: 收集并关闭任务
    tasks = collect_all_tasks()
    if tasks:
        batch_update_tasks(tasks, progress)

    # 完成
    elapsed = time.time() - start_time
    log("=" * 60)
    log(f"🎉 全部完成！耗时: {elapsed:.1f} 秒")
    log(f"   需求关闭: {len(progress.get('closed_stories', []))} 条")
    log(f"   任务关闭: {len(progress.get('closed_tasks', []))} 条")
    log("=" * 60)


if __name__ == "__main__":
    main()
