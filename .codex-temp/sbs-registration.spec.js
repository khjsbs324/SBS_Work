const { test, chromium } = require('C:/Users/SBS/AppData/Local/npm-cache/_npx/420ff84f11983ee5/node_modules/@playwright/test');

test('inspect teacher portal', async () => {
  test.setTimeout(720000);
  const context = await chromium.launchPersistentContext(
    'C:/Users/SBS/Documents/GitHub/SBS_Work/.playwright-sbs-eval-profile',
    { channel: 'chrome', headless: false, viewport: { width: 1440, height: 1000 } }
  );
  const page = context.pages()[0] || await context.newPage();
  await page.goto('https://sbsartdj.maniaro.net/teacher/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);
  if ((await page.locator('body').innerText()).includes('로그인')) {
    console.log('WAITING_FOR_LOGIN');
    await page.waitForFunction(() => document.body.innerText.includes('로그아웃'), null, { timeout: 600000 });
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1500);
  }
  await context.storageState({ path: 'C:/Users/SBS/Documents/GitHub/SBS_Work/.codex-temp/sbs-state.json' });
  const abilityMenu = page.getByText('능력단위평가', { exact: true }).first();
  if (await abilityMenu.count()) {
    await abilityMenu.click();
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1500);
  }
  console.log('URL', page.url());
  console.log('TITLE', await page.title());
  console.log('TEXT', (await page.locator('body').innerText()).slice(0, 6000));
  console.log('LINKS', await page.locator('a').evaluateAll((items) => items.map((a) => ({ text: (a.innerText || '').trim(), href: a.href })).filter((x) => x.text || x.href).slice(0, 200)));
  await page.screenshot({ path: 'C:/Users/SBS/AppData/Local/Temp/sbs-registration-inspect.png', fullPage: true });
  await context.close();
});
