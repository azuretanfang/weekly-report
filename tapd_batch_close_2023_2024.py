#!/usr/bin/env python3
"""
TAPD 批量关闭需求脚本（2023-2024年）
通过 TAPD API 批量更新需求状态为 rejected（已关闭）
"""

import json
import time
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('tapd_batch_close_2023_2024.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

WORKSPACE_ID = "20398362"

# 2023年需求ID（47条）
# 规划中 31条
IDS_2023_PLANNING = [
    "1020398362115689163","1020398362115610113","1020398362115276139","1020398362114778260",
    "1020398362887090349","1020398362886854547","1020398362886589163","1020398362886582965",
    "1020398362886404703","1020398362886401473","1020398362886334261","1020398362886243933",
    "1020398362886103401","1020398362885601981","1020398362885600359","1020398362884576531",
    "1020398362884371413","1020398362884371353","1020398362884131789","1020398362883602169",
    "1020398362883601453","1020398362883601215","1020398362883067563","1020398362882751879",
    "1020398362882716349","1020398362882708397","1020398362882489317","1020398362882418697",
    "1020398362881814521","1020398362881267367","1020398362881256863",
]

# 实现中 2条
IDS_2023_IN_PROGRESS = [
    "1020398362000004161","1020398362887562903",
]

# 未开始 11条
IDS_2023_NOT_STARTED = [
    "1020398362887592229","1020398362885996039","1020398362885942337","1020398362885794059",
    "1020398362885793549","1020398362884529855","1020398362884524853","1020398362884524705",
    "1020398362882570407","1020398362882570387","1020398362882113021",
]

# 待开发 3条
IDS_2023_TO_DEVELOP = [
    "1020398362886474393","1020398362886100051","1020398362882418347",
]

# 2024年需求ID（104条）
# 规划中 63条
IDS_2024_PLANNING = [
    "1020398362121466945","1020398362121466902","1020398362121466893","1020398362121466854",
    "1020398362121466844","1020398362121466838","1020398362121466835","1020398362121466805",
    "1020398362121466776","1020398362121442539","1020398362121426675","1020398362121135063",
    "1020398362121116958","1020398362120978599","1020398362120977629","1020398362120914714",
    "1020398362120482606","1020398362120261757","1020398362119936099","1020398362119917456",
    "1020398362119367511","1020398362119367477","1020398362119161353","1020398362119159428",
    "1020398362119126409","1020398362119107972","1020398362119069843","1020398362118630077",
    "1020398362118602090","1020398362118346180","1020398362117645296","1020398362117182139",
    "1020398362116887064","1020398362116808134","1020398362116808121","1020398362116808109",
    "1020398362116808050","1020398362116808025","1020398362116808020","1020398362116807693",
    "1020398362116807685","1020398362116788139","1020398362116787890","1020398362116787828",
    "1020398362116671641","1020398362116671640","1020398362116671636","1020398362116580197",
    "1020398362116494358","1020398362116277693","1020398362116277682","1020398362116235517",
    "1020398362116169729","1020398362116120646","1020398362115945457","1020398362115921921",
    "1020398362115906098","1020398362115906054","1020398362115905982","1020398362115885636",
    "1020398362115885422","1020398362115885402","1020398362115850209",
]

# 实现中 11条
IDS_2024_IN_PROGRESS = [
    "1020398362121470317","1020398362121466149","1020398362121382236","1020398362121326571",
    "1020398362121106316","1020398362121105108","1020398362121053787","1020398362120988211",
    "1020398362120979515","1020398362119602326","1020398362119462607",
]

# 未开始 28条
IDS_2024_NOT_STARTED = [
    "1020398362121215670","1020398362121215566","1020398362121211593","1020398362121206606",
    "1020398362121115821","1020398362121107330","1020398362121107303","1020398362121106596",
    "1020398362121106504","1020398362120728022","1020398362120728012","1020398362120261861",
    "1020398362120261790","1020398362119319813","1020398362119005436","1020398362118865433",
    "1020398362118865430","1020398362118015500","1020398362118015432","1020398362117881490",
    "1020398362117805947","1020398362117537676","1020398362117537308","1020398362117424443",
    "1020398362117324064","1020398362117221439","1020398362116981348","1020398362116424104",
]

# 待开发 2条
IDS_2024_TO_DEVELOP = [
    "1020398362121351955","1020398362120607524",
]

# 合并所有ID
ALL_IDS = (
    IDS_2023_PLANNING + IDS_2023_IN_PROGRESS + IDS_2023_NOT_STARTED + IDS_2023_TO_DEVELOP +
    IDS_2024_PLANNING + IDS_2024_IN_PROGRESS + IDS_2024_NOT_STARTED + IDS_2024_TO_DEVELOP
)

# 进度文件
PROGRESS_FILE = "tapd_batch_close_2023_2024_progress.json"

def load_progress():
    """加载处理进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "failed": []}

def save_progress(progress):
    """保存处理进度"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def update_story_via_api(story_id, auth):
    """通过 TAPD API 更新需求状态"""
    import requests
    url = "https://api.tapd.cn/stories"
    data = {
        "workspace_id": WORKSPACE_ID,
        "id": story_id,
        "status": "rejected"
    }
    try:
        resp = requests.post(url, data=data, auth=auth, timeout=15)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("status") == 1:
                return True, "success"
            else:
                return False, f"API error: {result}"
        else:
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return False, str(e)

def main():
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # 尝试从环境变量获取凭据
    api_user = os.environ.get("TAPD_API_USER", "")
    api_password = os.environ.get("TAPD_API_PASSWORD", "")
    
    if not api_user or not api_password:
        api_user = input("请输入 TAPD API User: ").strip()
        api_password = input("请输入 TAPD API Password: ").strip()
    
    auth = (api_user, api_password)
    
    # 先验证凭据
    logger.info("验证 API 凭据...")
    test_resp = requests.get(
        "https://api.tapd.cn/stories",
        params={"workspace_id": WORKSPACE_ID, "limit": 1, "fields": "id"},
        auth=auth, timeout=10
    )
    if test_resp.status_code != 200:
        logger.error(f"API 凭据验证失败！Status: {test_resp.status_code}")
        logger.error("请确保 API 账号有项目 20398362 的读写权限")
        return
    
    logger.info("✅ API 凭据验证成功！")
    
    # 加载进度
    progress = load_progress()
    completed_set = set(progress["completed"])
    
    # 过滤已完成的
    pending_ids = [sid for sid in ALL_IDS if sid not in completed_set]
    
    total = len(ALL_IDS)
    done = len(completed_set)
    logger.info(f"总计 {total} 条需求，已完成 {done} 条，待处理 {len(pending_ids)} 条")
    logger.info(f"  - 2023年: {len(IDS_2023_PLANNING) + len(IDS_2023_IN_PROGRESS) + len(IDS_2023_NOT_STARTED) + len(IDS_2023_TO_DEVELOP)} 条")
    logger.info(f"  - 2024年: {len(IDS_2024_PLANNING) + len(IDS_2024_IN_PROGRESS) + len(IDS_2024_NOT_STARTED) + len(IDS_2024_TO_DEVELOP)} 条")
    
    if not pending_ids:
        logger.info("🎉 所有需求已处理完毕！")
        return
    
    # 确认操作
    confirm = input(f"\n即将关闭 {len(pending_ids)} 条需求（2023-2024年），确认执行？(y/n): ").strip().lower()
    if confirm != 'y':
        logger.info("操作已取消")
        return
    
    # 并发处理
    BATCH_SIZE = 20
    MAX_WORKERS = 10
    success_count = 0
    fail_count = 0
    
    for i in range(0, len(pending_ids), BATCH_SIZE):
        batch = pending_ids[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(pending_ids) + BATCH_SIZE - 1) // BATCH_SIZE
        
        logger.info(f"\n--- 批次 {batch_num}/{total_batches} ({len(batch)}条) ---")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(update_story_via_api, sid, auth): sid 
                for sid in batch
            }
            for future in as_completed(futures):
                sid = futures[future]
                try:
                    ok, msg = future.result()
                    if ok:
                        success_count += 1
                        progress["completed"].append(sid)
                    else:
                        fail_count += 1
                        progress["failed"].append({"id": sid, "error": msg})
                        logger.warning(f"❌ {sid}: {msg}")
                except Exception as e:
                    fail_count += 1
                    progress["failed"].append({"id": sid, "error": str(e)})
                    logger.error(f"❌ {sid}: {e}")
        
        # 每批次保存进度
        save_progress(progress)
        logger.info(f"进度: {done + success_count + fail_count}/{total} (成功:{done + success_count}, 失败:{fail_count})")
        
        # 避免频率限制
        time.sleep(0.5)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"✅ 处理完成！成功: {success_count}, 失败: {fail_count}")
    logger.info(f"总进度: {done + success_count}/{total}")
    if fail_count > 0:
        logger.info(f"失败的ID保存在 {PROGRESS_FILE}")

if __name__ == "__main__":
    main()
