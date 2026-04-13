#!/usr/bin/env python3
"""
排期表「交付状态」字段补丁脚本
功能：
1. index.html - 新增交付状态筛选下拉框 + 表头列
2. app-views.js - 新增交付状态渲染、编辑弹窗、筛选逻辑、变更日志联动
3. styles.css - 新增交付状态相关样式
"""

import re
import os
import shutil
from datetime import datetime

BASE_DIR = '/data/meeting-system'

def backup_file(filepath):
    """备份文件"""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = f"{filepath}.bak.delivery_{ts}"
    shutil.copy2(filepath, bak)
    print(f"[BACKUP] {filepath} -> {bak}")
    return bak

def patch_index_html():
    """在 index.html 中新增交付状态筛选框和表头列"""
    filepath = os.path.join(BASE_DIR, 'index.html')
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # === 1. 在筛选栏中新增「交付状态」筛选器 ===
    # 找到最后一个 filter-multi-select (dev) 的结束标签后插入
    old_dev_filter = '''<div class="filter-multi-select" id="filterMulti_dev" onclick="toggleFilterDropdown('dev')">
            <div class="filter-multi-display"><span class="filter-multi-placeholder">全部开发人员</span><span class="filter-multi-arrow">▾</span></div>
            <div class="filter-multi-dropdown" id="filterDropdown_dev" onclick="event.stopPropagation()"></div>
          </div>'''
    
    new_dev_filter = '''<div class="filter-multi-select" id="filterMulti_dev" onclick="toggleFilterDropdown('dev')">
            <div class="filter-multi-display"><span class="filter-multi-placeholder">全部开发人员</span><span class="filter-multi-arrow">▾</span></div>
            <div class="filter-multi-dropdown" id="filterDropdown_dev" onclick="event.stopPropagation()"></div>
          </div>
          <div class="filter-multi-select" id="filterMulti_delivery" onclick="toggleFilterDropdown('delivery')">
            <div class="filter-multi-display"><span class="filter-multi-placeholder">全部交付状态</span><span class="filter-multi-arrow">▾</span></div>
            <div class="filter-multi-dropdown" id="filterDropdown_delivery" onclick="event.stopPropagation()"></div>
          </div>'''
    
    content = content.replace(old_dev_filter, new_dev_filter)
    
    # === 2. 在表头中新增「交付状态」列（风险/备注之后，预计排期之前）===
    old_thead = '''<th style="min-width:100px;">风险/备注</th>
              <th style="min-width:140px;white-space:nowrap;cursor:pointer;" onclick="sortSchedule('planSchedule')">预计排期 ↕</th>'''
    
    new_thead = '''<th style="min-width:100px;">风险/备注</th>
              <th style="min-width:90px;white-space:nowrap;cursor:pointer;" onclick="sortSchedule('deliveryStatus')">交付状态 ↕</th>
              <th style="min-width:140px;white-space:nowrap;cursor:pointer;" onclick="sortSchedule('planSchedule')">预计排期 ↕</th>'''
    
    content = content.replace(old_thead, new_thead)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[PATCH] index.html - 已新增交付状态筛选框和表头列 ✅")

def patch_app_views_js():
    """在 app-views.js 中新增交付状态的渲染、编辑、筛选逻辑"""
    filepath = os.path.join(BASE_DIR, 'app-views.js')
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # === 1. 在 FILTER_STATE 中新增 delivery 数组 ===
    old_filter_state = """const FILTER_STATE = {
  source: [],   // 选中的来源值
  status: [],   // 选中的状态分组值
  dev: []       // 选中的开发人员
};"""
    
    new_filter_state = """const FILTER_STATE = {
  source: [],     // 选中的来源值
  status: [],     // 选中的状态分组值
  dev: [],        // 选中的开发人员
  delivery: []    // 选中的交付状态
};"""
    
    content = content.replace(old_filter_state, new_filter_state)
    
    # === 2. 新增交付状态筛选选项定义（在 FILTER_STATUS_OPTIONS 之后）===
    old_status_options_end = """const FILTER_STATUS_OPTIONS = [
  { value: 'dev', label: '开发中', color: '#ecc94b', icon: '💻' },
  { value: 'testing', label: '测试/验收', color: '#4299e1', icon: '🧪' },
  { value: 'waiting', label: '待开发/已评审', color: '#667eea', icon: '📝' },
  { value: 'planning', label: '规划中/未开始', color: '#a0aec0', icon: '📐' },
  { value: 'done', label: '已完成/已关闭', color: '#48bb78', icon: '✅' },
  { value: 'blocked', label: '挂起', color: '#e53e3e', icon: '⏸️' }
];"""
    
    new_status_options_end = """const FILTER_STATUS_OPTIONS = [
  { value: 'dev', label: '开发中', color: '#ecc94b', icon: '💻' },
  { value: 'testing', label: '测试/验收', color: '#4299e1', icon: '🧪' },
  { value: 'waiting', label: '待开发/已评审', color: '#667eea', icon: '📝' },
  { value: 'planning', label: '规划中/未开始', color: '#a0aec0', icon: '📐' },
  { value: 'done', label: '已完成/已关闭', color: '#48bb78', icon: '✅' },
  { value: 'blocked', label: '挂起', color: '#e53e3e', icon: '⏸️' }
];

// 交付状态筛选选项
const FILTER_DELIVERY_OPTIONS = [
  { value: 'delayed', label: '🔴 已延期', color: '#e53e3e' },
  { value: 'rescheduled', label: '🟡 排期调整', color: '#d69e2e' },
  { value: 'on_time', label: '✅ 按时交付', color: '#48bb78' },
  { value: 'none', label: '⬜ 未标记', color: '#a0aec0' }
];

// 交付状态配置映射
const DELIVERY_STATUS_CONFIG = {
  'delayed':     { label: '已延期', emoji: '🔴', color: '#e53e3e', bgColor: '#e53e3e15', borderColor: '#e53e3e30' },
  'rescheduled': { label: '排期调整', emoji: '🟡', color: '#d69e2e', bgColor: '#d69e2e15', borderColor: '#d69e2e30' },
  'on_time':     { label: '按时交付', emoji: '✅', color: '#48bb78', bgColor: '#48bb7815', borderColor: '#48bb7830' }
};"""
    
    content = content.replace(old_status_options_end, new_status_options_end)
    
    # === 3. 在 initScheduleFilters 中新增 delivery 初始化 ===
    old_init_filters = """function initScheduleFilters() {
  renderFilterDropdownOptions('source');
  renderFilterDropdownOptions('status');
  initScheduleDevFilter();
}"""
    
    new_init_filters = """function initScheduleFilters() {
  renderFilterDropdownOptions('source');
  renderFilterDropdownOptions('status');
  renderFilterDropdownOptions('delivery');
  initScheduleDevFilter();
}"""
    
    content = content.replace(old_init_filters, new_init_filters)
    
    # === 4. 在 renderFilterDropdownOptions 中支持 delivery 类型 ===
    old_render_filter = """  let options = [];
  if (type === 'source') options = FILTER_SOURCE_OPTIONS;
  else if (type === 'status') options = FILTER_STATUS_OPTIONS;"""
    
    new_render_filter = """  let options = [];
  if (type === 'source') options = FILTER_SOURCE_OPTIONS;
  else if (type === 'status') options = FILTER_STATUS_OPTIONS;
  else if (type === 'delivery') options = FILTER_DELIVERY_OPTIONS;"""
    
    content = content.replace(old_render_filter, new_render_filter)
    
    # === 5. 在 removeFilterTag 中支持 delivery 类型重新渲染 ===
    old_remove_tag = """  // 重新渲染选项区域以同步checkbox
  if (type === 'source' || type === 'status') renderFilterDropdownOptions(type);
  else initScheduleDevFilter();"""
    
    new_remove_tag = """  // 重新渲染选项区域以同步checkbox
  if (type === 'source' || type === 'status' || type === 'delivery') renderFilterDropdownOptions(type);
  else initScheduleDevFilter();"""
    
    content = content.replace(old_remove_tag, new_remove_tag)
    
    # === 6. 在 refreshFilterDisplay 中支持 delivery 类型 ===
    old_placeholder_map = "  const placeholderMap = { source: '全部来源', status: '全部状态', dev: '全部开发人员' };"
    new_placeholder_map = "  const placeholderMap = { source: '全部来源', status: '全部状态', dev: '全部开发人员', delivery: '全部交付状态' };"
    content = content.replace(old_placeholder_map, new_placeholder_map)
    
    # === 7. 在 refreshFilterDisplay 中支持 delivery 选项颜色查找 ===
    old_filter_display_color = """      if (type === 'source') {
        const opt = FILTER_SOURCE_OPTIONS.find(o => o.value === val);
        if (opt) { label = opt.label; color = opt.color; }
      } else if (type === 'status') {
        const opt = FILTER_STATUS_OPTIONS.find(o => o.value === val);
        if (opt) { label = (opt.icon || '') + ' ' + opt.label; color = opt.color; }
      } else {
        color = '#2b6cb0';
      }"""
    
    new_filter_display_color = """      if (type === 'source') {
        const opt = FILTER_SOURCE_OPTIONS.find(o => o.value === val);
        if (opt) { label = opt.label; color = opt.color; }
      } else if (type === 'status') {
        const opt = FILTER_STATUS_OPTIONS.find(o => o.value === val);
        if (opt) { label = (opt.icon || '') + ' ' + opt.label; color = opt.color; }
      } else if (type === 'delivery') {
        const opt = FILTER_DELIVERY_OPTIONS.find(o => o.value === val);
        if (opt) { label = opt.label; color = opt.color; }
      } else {
        color = '#2b6cb0';
      }"""
    
    content = content.replace(old_filter_display_color, new_filter_display_color)
    
    # === 8. 在 getFilteredScheduleData 中新增 delivery 筛选逻辑 ===
    old_get_filtered = """  const sourceFilters = FILTER_STATE.source;
  const statusFilters = FILTER_STATE.status;
  const devFilters = FILTER_STATE.dev;"""
    
    new_get_filtered = """  const sourceFilters = FILTER_STATE.source;
  const statusFilters = FILTER_STATE.status;
  const devFilters = FILTER_STATE.dev;
  const deliveryFilters = FILTER_STATE.delivery;"""
    
    content = content.replace(old_get_filtered, new_get_filtered)
    
    # 在 devFilters 筛选逻辑之后插入 delivery 筛选
    old_dev_filter_check = """    if (devFilters.length > 0) {
      const allDevs = [item.backendDev, item.frontendDev, item.dataDev, item.developer].filter(Boolean).join(',');
      if (!devFilters.some(dev => allDevs.includes(dev))) return false;
    }
    return true;"""
    
    new_dev_filter_check = """    if (devFilters.length > 0) {
      const allDevs = [item.backendDev, item.frontendDev, item.dataDev, item.developer].filter(Boolean).join(',');
      if (!devFilters.some(dev => allDevs.includes(dev))) return false;
    }
    // 交付状态筛选
    if (deliveryFilters.length > 0) {
      const ds = item.deliveryStatus || 'none';
      if (!deliveryFilters.includes(ds)) return false;
    }
    return true;"""
    
    content = content.replace(old_dev_filter_check, new_dev_filter_check)
    
    # === 9. 修改 colspan 从 15 到 17（新增了交付状态列）===
    content = content.replace(
        '''tbody.innerHTML = '<tr><td colspan="15"''',
        '''tbody.innerHTML = '<tr><td colspan="17"'''
    )
    
    # === 10. 在表格行渲染中添加交付状态列（风险/备注 td 之后，预计排期之前）===
    # 找到风险备注 td 和预计排期 td 之间
    old_risknote_to_plan = """      <td>\${renderPlanScheduleCell(item, canEdit)}</td>"""
    
    new_risknote_to_plan = """      <td>\${renderDeliveryStatusCell(item, canEdit)}</td>
      <td>\${renderPlanScheduleCell(item, canEdit)}</td>"""
    
    content = content.replace(old_risknote_to_plan, new_risknote_to_plan)
    
    # === 11. 在排序逻辑中支持 deliveryStatus 字段排序 ===
    old_sort_else = """  } else {
    data.sort((a, b) => {
      let va = (a[scheduleSortField] || '').toString().toLowerCase();
      let vb = (b[scheduleSortField] || '').toString().toLowerCase();
      if (va < vb) return scheduleSortAsc ? -1 : 1;
      if (va > vb) return scheduleSortAsc ? 1 : -1;
      return 0;
    });
  }"""
    
    new_sort_else = """  } else if (scheduleSortField === 'deliveryStatus') {
    // 交付状态排序：延期>排期调整>按时>未标记
    const dsOrder = { delayed: 0, rescheduled: 1, on_time: 2 };
    data.sort((a, b) => {
      const va = a.deliveryStatus ? (dsOrder[a.deliveryStatus] ?? 3) : 3;
      const vb = b.deliveryStatus ? (dsOrder[b.deliveryStatus] ?? 3) : 3;
      if (va !== vb) return scheduleSortAsc ? va - vb : vb - va;
      return 0;
    });
  } else {
    data.sort((a, b) => {
      let va = (a[scheduleSortField] || '').toString().toLowerCase();
      let vb = (b[scheduleSortField] || '').toString().toLowerCase();
      if (va < vb) return scheduleSortAsc ? -1 : 1;
      if (va > vb) return scheduleSortAsc ? 1 : -1;
      return 0;
    });
  }"""
    
    content = content.replace(old_sort_else, new_sort_else)
    
    # === 12. 在文件末尾（onScheduleSourceChange 之后）添加新函数 ===
    # 找到 onScheduleSourceChange 函数结尾后插入
    old_source_change_end = """async function onScheduleSourceChange(tapdId, newVal) {
  await addOrUpdateScheduleItem({ tapdId, source: newVal });
  renderScheduleTable();
  showToast('需求来源已更新 ✅', 'success');
}"""
    
    new_functions = """async function onScheduleSourceChange(tapdId, newVal) {
  await addOrUpdateScheduleItem({ tapdId, source: newVal });
  renderScheduleTable();
  showToast('需求来源已更新 ✅', 'success');
}

// ============================================
// 交付状态功能
// ============================================

/** 渲染交付状态单元格 */
function renderDeliveryStatusCell(item, canEdit) {
  const ds = item.deliveryStatus;
  const note = item.deliveryNote || '';
  
  if (!ds) {
    // 未标记状态
    if (canEdit) {
      return `<span class="delivery-status-empty" onclick="openDeliveryStatusDialog('${item.tapdId}')" title="点击标记交付状态">—</span>`;
    }
    return '<span style="color:#cbd5e0;">—</span>';
  }
  
  const config = DELIVERY_STATUS_CONFIG[ds];
  if (!config) return '<span style="color:#cbd5e0;">—</span>';
  
  const tooltipText = note ? `${config.emoji} ${config.label}\\n原因：${note}` : `${config.emoji} ${config.label}`;
  
  if (canEdit) {
    return `<span class="delivery-status-tag delivery-${ds}" onclick="openDeliveryStatusDialog('${item.tapdId}')" title="${tooltipText.replace(/"/g, '&quot;')}" style="cursor:pointer;">${config.emoji} ${config.label}</span>`;
  }
  return `<span class="delivery-status-tag delivery-${ds}" title="${tooltipText.replace(/"/g, '&quot;')}">${config.emoji} ${config.label}</span>`;
}

/** 打开交付状态标记弹窗 */
function openDeliveryStatusDialog(tapdId) {
  const item = findScheduleItem(tapdId);
  if (!item) return;
  
  const currentStatus = item.deliveryStatus || '';
  const currentNote = item.deliveryNote || '';
  
  const dialogHtml = `
    <div class="delivery-dialog-overlay" id="deliveryDialogOverlay" onclick="closeDeliveryStatusDialog()">
      <div class="delivery-dialog" onclick="event.stopPropagation()">
        <div class="delivery-dialog-header">
          <h3>📋 标记交付状态</h3>
          <button class="delivery-dialog-close" onclick="closeDeliveryStatusDialog()">✕</button>
        </div>
        <div class="delivery-dialog-body">
          <div class="delivery-dialog-info">
            <span class="delivery-dialog-tapd">TAPD ${item.tapdId}</span>
            <span class="delivery-dialog-name" title="${item.name}">${item.name}</span>
          </div>
          <div class="delivery-radio-group">
            <label class="delivery-radio-item ${currentStatus === '' ? 'active' : ''}">
              <input type="radio" name="deliveryStatus" value="" ${currentStatus === '' ? 'checked' : ''} onchange="onDeliveryRadioChange()">
              <span class="delivery-radio-label" style="color:#a0aec0;">⬜ 未标记</span>
            </label>
            <label class="delivery-radio-item ${currentStatus === 'delayed' ? 'active' : ''}">
              <input type="radio" name="deliveryStatus" value="delayed" ${currentStatus === 'delayed' ? 'checked' : ''} onchange="onDeliveryRadioChange()">
              <span class="delivery-radio-label" style="color:#e53e3e;">🔴 已延期</span>
            </label>
            <label class="delivery-radio-item ${currentStatus === 'rescheduled' ? 'active' : ''}">
              <input type="radio" name="deliveryStatus" value="rescheduled" ${currentStatus === 'rescheduled' ? 'checked' : ''} onchange="onDeliveryRadioChange()">
              <span class="delivery-radio-label" style="color:#d69e2e;">🟡 排期调整</span>
            </label>
            <label class="delivery-radio-item ${currentStatus === 'on_time' ? 'active' : ''}">
              <input type="radio" name="deliveryStatus" value="on_time" ${currentStatus === 'on_time' ? 'checked' : ''} onchange="onDeliveryRadioChange()">
              <span class="delivery-radio-label" style="color:#48bb78;">✅ 按时交付</span>
            </label>
          </div>
          <div class="delivery-note-section" id="deliveryNoteSection" style="display:${currentStatus === 'delayed' || currentStatus === 'rescheduled' ? 'block' : 'none'};">
            <label class="delivery-note-label">延期/调整原因 <span style="color:#e53e3e;">*</span></label>
            <textarea class="delivery-note-textarea" id="deliveryNoteInput" placeholder="请输入延期或排期调整的原因...">${currentNote}</textarea>
          </div>
        </div>
        <div class="delivery-dialog-footer">
          <button class="btn btn-sm btn-outline" onclick="closeDeliveryStatusDialog()">取消</button>
          <button class="btn btn-sm btn-primary" onclick="saveDeliveryStatus('${tapdId}')" style="background:linear-gradient(135deg,#667eea,#764ba2);">保存</button>
        </div>
      </div>
    </div>
  `;
  
  // 移除已有弹窗（如果存在）
  const existing = document.getElementById('deliveryDialogOverlay');
  if (existing) existing.remove();
  
  document.body.insertAdjacentHTML('beforeend', dialogHtml);
  
  // 添加入场动画
  requestAnimationFrame(() => {
    document.getElementById('deliveryDialogOverlay').classList.add('show');
  });
}

/** 关闭交付状态弹窗 */
function closeDeliveryStatusDialog() {
  const overlay = document.getElementById('deliveryDialogOverlay');
  if (overlay) {
    overlay.classList.remove('show');
    setTimeout(() => overlay.remove(), 200);
  }
}

/** radio 切换时控制原因输入框的显隐 */
function onDeliveryRadioChange() {
  const selected = document.querySelector('input[name="deliveryStatus"]:checked')?.value || '';
  const noteSection = document.getElementById('deliveryNoteSection');
  if (noteSection) {
    noteSection.style.display = (selected === 'delayed' || selected === 'rescheduled') ? 'block' : 'none';
  }
  // 更新 radio-item 的 active 样式
  document.querySelectorAll('.delivery-radio-item').forEach(el => {
    el.classList.toggle('active', el.querySelector('input').checked);
  });
}

/** 保存交付状态 */
async function saveDeliveryStatus(tapdId) {
  const selected = document.querySelector('input[name="deliveryStatus"]:checked')?.value || '';
  const noteInput = document.getElementById('deliveryNoteInput');
  const note = noteInput ? noteInput.value.trim() : '';
  
  // 校验：已延期/排期调整 必须填写原因
  if ((selected === 'delayed' || selected === 'rescheduled') && !note) {
    showToast('⚠️ 请填写延期/调整原因', 'error');
    if (noteInput) noteInput.focus();
    return;
  }
  
  const item = findScheduleItem(tapdId);
  if (!item) return;
  
  const oldStatus = item.deliveryStatus || null;
  const newStatus = selected || null;
  
  // 更新排期数据
  const updateData = {
    tapdId,
    deliveryStatus: newStatus,
    deliveryNote: note || null,
    deliveryTaggedAt: newStatus ? new Date().toISOString() : null
  };
  
  await addOrUpdateScheduleItem(updateData);
  
  // 自动写入排期变更日志
  if (newStatus && newStatus !== oldStatus) {
    await writeDeliveryChangeLog(tapdId, item, oldStatus, newStatus, note);
  }
  
  closeDeliveryStatusDialog();
  renderScheduleTable();
  
  const statusLabels = { delayed: '🔴 已延期', rescheduled: '🟡 排期调整', on_time: '✅ 按时交付' };
  const label = statusLabels[newStatus] || '未标记';
  showToast(`交付状态已更新为：${label}`, 'success');
}

/** 将交付状态变更写入排期变更日志 */
async function writeDeliveryChangeLog(tapdId, item, oldStatus, newStatus, note) {
  try {
    // 获取当前月份的会议数据
    const monthData = getMonthData(currentMonth);
    if (!monthData.scheduleChanges) {
      monthData.scheduleChanges = [];
    }
    
    const changeTypeMap = {
      delayed: '延期',
      rescheduled: '排期调整',
      on_time: '按时交付'
    };
    
    const oldLabel = oldStatus ? (changeTypeMap[oldStatus] || oldStatus) : '未标记';
    const newLabel = changeTypeMap[newStatus] || newStatus;
    
    const logEntry = {
      meetingId: 'delivery_tag_' + Date.now(),
      meetingDate: new Date().toISOString().split('T')[0],
      changeType: newStatus === 'delayed' ? '延期' : (newStatus === 'rescheduled' ? '排期调整' : '按时'),
      tapdId: tapdId,
      originalDate: '',
      newDate: '',
      reason: note || `交付状态标记：${oldLabel} → ${newLabel}`,
      decider: '',
      affected: item.name || '',
      impact: `交付状态：${newLabel}`
    };
    
    monthData.scheduleChanges.push(logEntry);
    
    // 保存月度数据
    await saveMonthData(currentMonth, monthData);
    console.log(`[交付状态] 已写入排期变更日志: ${tapdId} -> ${newLabel}`);
  } catch (e) {
    console.error('[交付状态] 写入变更日志失败:', e);
    // 不阻塞主流程，只打印错误
  }
}"""
    
    content = content.replace(old_source_change_end, new_functions)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[PATCH] app-views.js - 已新增交付状态完整功能 ✅")

def patch_styles_css():
    """在 styles.css 末尾追加交付状态相关样式"""
    filepath = os.path.join(BASE_DIR, 'styles.css')
    backup_file(filepath)
    
    delivery_styles = """

/* ============================================
   交付状态功能样式
   ============================================ */

/* 交付状态标签 */
.delivery-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s;
}

.delivery-status-tag.delivery-delayed {
  background: #e53e3e15;
  color: #e53e3e;
  border: 1px solid #e53e3e30;
}

.delivery-status-tag.delivery-rescheduled {
  background: #d69e2e15;
  color: #d69e2e;
  border: 1px solid #d69e2e30;
}

.delivery-status-tag.delivery-on_time {
  background: #48bb7815;
  color: #48bb78;
  border: 1px solid #48bb7830;
}

.delivery-status-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.delivery-status-empty {
  display: inline-block;
  color: #cbd5e0;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.delivery-status-empty:hover {
  background: #edf2f7;
  color: #4a5568;
}

/* 交付状态弹窗 */
.delivery-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  opacity: 0;
  transition: opacity 0.2s;
}

.delivery-dialog-overlay.show {
  opacity: 1;
}

.delivery-dialog {
  background: #fff;
  border-radius: 16px;
  width: 480px;
  max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  transform: scale(0.95) translateY(10px);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.delivery-dialog-overlay.show .delivery-dialog {
  transform: scale(1) translateY(0);
}

.delivery-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 12px;
  border-bottom: 1px solid #edf2f7;
}

.delivery-dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #2d3748;
}

.delivery-dialog-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #a0aec0;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.15s;
}

.delivery-dialog-close:hover {
  background: #f7fafc;
  color: #4a5568;
}

.delivery-dialog-body {
  padding: 16px 24px;
}

.delivery-dialog-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f7fafc;
  border-radius: 10px;
  margin-bottom: 16px;
}

.delivery-dialog-tapd {
  font-size: 11px;
  font-weight: 600;
  color: #667eea;
  background: #667eea15;
  padding: 2px 8px;
  border-radius: 6px;
  white-space: nowrap;
}

.delivery-dialog-name {
  font-size: 13px;
  color: #4a5568;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Radio 选项组 */
.delivery-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.delivery-radio-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}

.delivery-radio-item:hover {
  background: #f7fafc;
}

.delivery-radio-item.active {
  background: #ebf8ff;
  border-color: #bee3f8;
}

.delivery-radio-item input[type="radio"] {
  margin: 0;
  accent-color: #667eea;
}

.delivery-radio-label {
  font-size: 14px;
  font-weight: 500;
}

/* 原因输入区 */
.delivery-note-section {
  margin-top: 4px;
}

.delivery-note-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 6px;
}

.delivery-note-textarea {
  width: 100%;
  min-height: 80px;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  color: #2d3748;
  resize: vertical;
  transition: border-color 0.15s;
  box-sizing: border-box;
  font-family: inherit;
}

.delivery-note-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px #667eea20;
}

.delivery-note-textarea::placeholder {
  color: #a0aec0;
}

.delivery-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 24px 20px;
}
"""
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(delivery_styles)
    
    print("[PATCH] styles.css - 已追加交付状态样式 ✅")

def verify_patch():
    """验证补丁是否正确应用"""
    issues = []
    
    # 检查 index.html
    with open(os.path.join(BASE_DIR, 'index.html'), 'r', encoding='utf-8') as f:
        html = f.read()
    if 'filterMulti_delivery' not in html:
        issues.append("index.html: 缺少交付状态筛选框")
    if '交付状态 ↕' not in html:
        issues.append("index.html: 缺少交付状态表头列")
    
    # 检查 app-views.js
    with open(os.path.join(BASE_DIR, 'app-views.js'), 'r', encoding='utf-8') as f:
        js = f.read()
    checks = [
        ('FILTER_DELIVERY_OPTIONS', 'app-views.js: 缺少交付状态筛选选项定义'),
        ('DELIVERY_STATUS_CONFIG', 'app-views.js: 缺少交付状态配置映射'),
        ('renderDeliveryStatusCell', 'app-views.js: 缺少交付状态单元格渲染函数'),
        ('openDeliveryStatusDialog', 'app-views.js: 缺少交付状态弹窗函数'),
        ('saveDeliveryStatus', 'app-views.js: 缺少保存交付状态函数'),
        ('writeDeliveryChangeLog', 'app-views.js: 缺少变更日志写入函数'),
        ("delivery: []", 'app-views.js: FILTER_STATE 缺少 delivery 数组'),
    ]
    for keyword, msg in checks:
        if keyword not in js:
            issues.append(msg)
    
    # 检查 styles.css
    with open(os.path.join(BASE_DIR, 'styles.css'), 'r', encoding='utf-8') as f:
        css = f.read()
    if 'delivery-status-tag' not in css:
        issues.append("styles.css: 缺少交付状态标签样式")
    if 'delivery-dialog' not in css:
        issues.append("styles.css: 缺少交付状态弹窗样式")
    
    return issues

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 开始应用排期表「交付状态」补丁")
    print("=" * 50)
    
    try:
        patch_index_html()
        patch_app_views_js()
        patch_styles_css()
        
        print("\n" + "=" * 50)
        print("🔍 验证补丁...")
        issues = verify_patch()
        if issues:
            print("⚠️ 发现以下问题：")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 所有补丁验证通过！")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 补丁应用失败: {e}")
        import traceback
        traceback.print_exc()
