/**
 * 修复脚本：手动将需求池中的 TAPD ID 132796150 同步到排期表
 * 
 * Bug描述：
 * - TAPD ID 132796150 在需求池中状态为 "scheduled"（已排期）
 * - 但在排期表中找不到该需求
 * - 原因：排期时 syncDemandToSchedule 函数可能执行失败或数据丢失
 * 
 * 修复方案：
 * - 从需求池读取该需求的信息
 * - 按照 syncDemandToSchedule 的逻辑构建排期表数据
 * - 添加到排期表并保存
 */

const API_BASE = 'https://fangtan-any3.devcloud.woa.com';
const TARGET_TAPD_ID = '132796150';

async function fixMissingSchedule() {
  try {
    console.log(`🔍 开始修复 TAPD ID ${TARGET_TAPD_ID} 的排期表同步问题...`);

    // 1. 从需求池获取该需求信息
    console.log('📥 正在从需求池获取需求信息...');
    const demandsResp = await fetch(`${API_BASE}/api/demands`);
    if (!demandsResp.ok) {
      throw new Error(`获取需求池数据失败: ${demandsResp.status}`);
    }
    const demands = await demandsResp.json();
    const demand = demands.find(d => d.tapdId === TARGET_TAPD_ID);
    
    if (!demand) {
      console.error(`❌ 在需求池中找不到 TAPD ID ${TARGET_TAPD_ID}`);
      return false;
    }

    console.log('✅ 找到需求：', {
      name: demand.name,
      status: demand.status,
      statusLabel: demand.statusLabel,
      scheduleMonth: demand.scheduleMonth,
      scheduleWeek: demand.scheduleWeek,
      backendDev: demand.backendDev
    });

    // 2. 检查排期表中是否已存在
    console.log('🔍 检查排期表中是否已存在...');
    const scheduleResp = await fetch(`${API_BASE}/api/schedule`);
    if (!scheduleResp.ok) {
      throw new Error(`获取排期表数据失败: ${scheduleResp.status}`);
    }
    const scheduleData = await scheduleResp.json();
    const existing = scheduleData.find(item => item.tapdId === TARGET_TAPD_ID);

    if (existing) {
      console.log('⚠️ 该需求已在排期表中，无需修复');
      return true;
    }

    // 3. 构建排期表数据（按照 syncDemandToSchedule 的逻辑）
    console.log('🔨 构建排期表数据...');
    
    // 计算迭代描述
    let iterationDesc = null;
    if (demand.scheduleMonth) {
      const [y, m] = demand.scheduleMonth.split('-');
      iterationDesc = `月迭代 ${y.slice(2)} 年 ${parseInt(m)} 月`;
    }

    // 拼接 developer 字段
    const devParts = [demand.backendDev, demand.frontendDev, demand.dataDev].filter(Boolean);
    const developer = devParts.length ? devParts.join(', ') : null;

    const scheduleItem = {
      tapdId: demand.tapdId,
      name: demand.name,
      status: '待开发',  // 刚排期的需求默认为"待开发"状态
      developer: developer,
      tapdLink: demand.tapdUrl || `https://tapd.woa.com/tapd_fe/20398362/story/detail/1020398362${demand.tapdId}`,
      iteration: iterationDesc,
      source: demand.source || '',
      backendDev: demand.backendDev || null,
      frontendDev: demand.frontendDev || null,
      dataDev: demand.dataDev || null,
      riskNote: null,
      // 来源标记
      importedAt: new Date().toISOString(),
      importSource: 'demand_pool_manual_fix',
      demandPoolId: demand.id,
      scheduleMonth: demand.scheduleMonth,
      scheduleWeek: demand.scheduleWeek
    };

    console.log('📋 待添加的排期表数据：', scheduleItem);

    // 4. 添加到排期表
    console.log('💾 正在添加到排期表...');
    scheduleData.push(scheduleItem);

    const saveResp = await fetch(`${API_BASE}/api/schedule`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scheduleData)
    });

    if (!saveResp.ok) {
      const errorResult = await saveResp.json().catch(() => ({}));
      throw new Error(`保存排期表失败: ${errorResult.error || saveResp.status}`);
    }

    console.log('✅ 排期表保存成功');

    // 5. 验证保存结果
    console.log('🔍 验证保存结果...');
    const verifyResp = await fetch(`${API_BASE}/api/schedule`);
    if (verifyResp.ok) {
      const verifyData = await verifyResp.json();
      const verified = verifyData.find(item => item.tapdId === TARGET_TAPD_ID);
      if (verified) {
        console.log('✅ 验证通过！需求已成功添加到排期表');
        return true;
      } else {
        console.error('❌ 验证失败：保存后在排期表中仍然找不到该需求');
        return false;
      }
    }

    return true;
  } catch (error) {
    console.error('❌ 修复过程中发生错误：', error);
    return false;
  }
}

// 执行修复
fixMissingSchedule().then(success => {
  if (success) {
    console.log('\n🎉 修复完成！请刷新页面查看排期表。');
  } else {
    console.log('\n❌ 修复失败，请检查错误日志。');
  }
});
