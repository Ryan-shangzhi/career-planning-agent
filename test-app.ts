import { chromium } from 'playwright';

async function testApp() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  console.log('正在启动浏览器...');

  try {
    console.log('正在访问前端页面 http://localhost:5173/...');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle', timeout: 30000 });

    const title = await page.title();
    console.log(`页面标题: ${title}`);

    const bodyText = await page.locator('body').innerText();
    console.log(`页面内容预览: ${bodyText.substring(0, 200)}...`);

    console.log('正在测试表单填写...');
    await page.fill('input[placeholder*="当前职业"]', '前端工程师');
    await page.fill('input[placeholder*="JavaScript"]', 'JavaScript, React, TypeScript, Webpack');
    await page.fill('input[placeholder*="目标公司"]', '字节跳动');
    await page.fill('input[placeholder*="目标岗位"]', '前端开发工程师');
    await page.fill('input[placeholder*="目标薪资"]', '25K');

    console.log('正在提交表单...');
    await page.click('button:has-text("开始分析")');

    console.log('等待分析结果...');
    await page.waitForURL('**/analysis', { timeout: 30000 });

    console.log('分析页面加载成功！');
    const analysisContent = await page.locator('body').innerText();
    console.log(`分析页面内容预览: ${analysisContent.substring(0, 300)}...`);

    console.log('\n✅ 测试成功！应用正常工作');

  } catch (error) {
    console.error('❌ 测试失败:', error.message);

    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    console.log('正在截图...');
    await page.screenshot({ path: '/workspace/error-screenshot.png' });
    console.log('截图已保存到 /workspace/error-screenshot.png');
  } finally {
    await browser.close();
  }
}

testApp();
