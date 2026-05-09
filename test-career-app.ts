import { chromium } from 'playwright';

async function testCareerApp() {
  console.log('🚀 启动浏览器测试...\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  try {
    // 测试1: 访问首页
    console.log('📍 测试1: 访问首页');
    await page.goto('http://localhost:5173/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    const title = await page.title();
    console.log(`   ✅ 页面标题: ${title}`);

    // 检查首页内容
    const bodyText = await page.locator('body').innerText();
    const hasStartBtn = bodyText.includes('开始规划');
    console.log(`   ${hasStartBtn ? '✅' : '❌'} 首页包含开始按钮: ${hasStartBtn}`);

    // 测试2: 点击开始规划按钮
    console.log('\n📍 测试2: 跳转到表单页面');
    await page.click('button:has-text("开始规划")');
    await page.waitForURL('**/survey', { timeout: 10000 });
    console.log('   ✅ 成功跳转到 /survey');

    await page.waitForTimeout(1000);

    // 测试3: 填写表单
    console.log('\n📍 测试3: 填写表单');

    // 找到所有输入框
    const currentJobInput = page.locator('input[type="text"]').first();
    await currentJobInput.fill('前端工程师');
    console.log('   ✅ 填写当前职业: 前端工程师');

    // 填写技能
    const skillTextarea = page.locator('textarea').first();
    await skillTextarea.fill('JavaScript, React, TypeScript, Webpack, Vite, CI/CD');
    console.log('   ✅ 填写技能: JavaScript, React, TypeScript, Webpack, Vite, CI/CD');

    // 填写目标公司
    const inputs = page.locator('input[type="text"]');
    await inputs.nth(1).fill('字节跳动');
    console.log('   ✅ 填写目标公司: 字节跳动');

    // 填写目标岗位
    await inputs.nth(2).fill('前端开发工程师');
    console.log('   ✅ 填写目标岗位: 前端开发工程师');

    // 填写目标薪资
    await inputs.nth(3).fill('25K');
    console.log('   ✅ 填写目标薪资: 25K');

    // 测试4: 提交表单
    console.log('\n📍 测试4: 提交表单');
    const submitBtn = page.locator('button:has-text("开始分析")');
    await submitBtn.click();
    console.log('   ✅ 点击提交按钮');

    // 等待分析结果
    console.log('   ⏳ 等待分析结果（这可能需要几秒钟）...');
    await page.waitForURL('**/analysis', { timeout: 45000 });
    console.log('   ✅ 成功跳转到 /analysis');

    // 等待分析内容加载
    await page.waitForTimeout(3000);

    const analysisText = await page.locator('body').innerText();

    // 验证分析结果
    const hasJobType = analysisText.includes('前端族');
    const hasGap = analysisText.includes('差距') || analysisText.includes('技能');
    const hasAction = analysisText.includes('短期') || analysisText.includes('中期') || analysisText.includes('长期');

    console.log('\n📊 分析结果验证:');
    console.log(`   ${hasJobType ? '✅' : '❌'} 岗位族识别: ${hasJobType ? '前端族' : '未找到'}`);
    console.log(`   ${hasGap ? '✅' : '❌'} 差距分析: ${hasGap ? '包含技能分析' : '未找到'}`);
    console.log(`   ${hasAction ? '✅' : '❌'} 行动路径: ${hasAction ? '包含阶段计划' : '未找到'}`);

    // 输出控制台错误
    if (errors.length > 0) {
      console.log('\n⚠️ 控制台错误:');
      errors.slice(0, 5).forEach(err => console.log(`   - ${err.substring(0, 150)}`));
    } else {
      console.log('\n✅ 无控制台错误');
    }

    console.log('\n🎉 测试完成！');

  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);

    // 截图
    try {
      await page.screenshot({ path: '/workspace/error-screenshot.png', fullPage: true });
      console.log('📸 截图已保存到 /workspace/error-screenshot.png');
    } catch (e) {}

    // 输出错误日志
    if (errors.length > 0) {
      console.log('\n📋 控制台错误日志:');
      errors.forEach(err => console.log(`   ${err}`));
    }
  } finally {
    await browser.close();
  }
}

testCareerApp();
