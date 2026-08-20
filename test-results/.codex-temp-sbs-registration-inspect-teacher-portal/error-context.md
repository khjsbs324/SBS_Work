# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: .codex-temp\sbs-registration.spec.js >> inspect teacher portal
- Location: .codex-temp\sbs-registration.spec.js:3:1

# Error details

```
Error: page.waitForFunction: Target page, context or browser has been closed
```

# Test source

```ts
  1  | const { test, chromium } = require('C:/Users/SBS/AppData/Local/npm-cache/_npx/420ff84f11983ee5/node_modules/@playwright/test');
  2  | 
  3  | test('inspect teacher portal', async () => {
  4  |   test.setTimeout(720000);
  5  |   const context = await chromium.launchPersistentContext(
  6  |     'C:/Users/SBS/Documents/GitHub/SBS_Work/.playwright-sbs-eval-profile',
  7  |     { channel: 'chrome', headless: false, viewport: { width: 1440, height: 1000 } }
  8  |   );
  9  |   const page = context.pages()[0] || await context.newPage();
  10 |   await page.goto('https://sbsartdj.maniaro.net/teacher/', { waitUntil: 'domcontentloaded' });
  11 |   await page.waitForTimeout(1000);
  12 |   if ((await page.locator('body').innerText()).includes('로그인')) {
  13 |     console.log('WAITING_FOR_LOGIN');
> 14 |     await page.waitForFunction(() => document.body.innerText.includes('로그아웃'), null, { timeout: 600000 });
     |                ^ Error: page.waitForFunction: Target page, context or browser has been closed
  15 |     await page.waitForLoadState('domcontentloaded');
  16 |     await page.waitForTimeout(1500);
  17 |   }
  18 |   await context.storageState({ path: 'C:/Users/SBS/Documents/GitHub/SBS_Work/.codex-temp/sbs-state.json' });
  19 |   const abilityMenu = page.getByText('능력단위평가', { exact: true }).first();
  20 |   if (await abilityMenu.count()) {
  21 |     await abilityMenu.click();
  22 |     await page.waitForLoadState('domcontentloaded');
  23 |     await page.waitForTimeout(1500);
  24 |   }
  25 |   console.log('URL', page.url());
  26 |   console.log('TITLE', await page.title());
  27 |   console.log('TEXT', (await page.locator('body').innerText()).slice(0, 6000));
  28 |   console.log('LINKS', await page.locator('a').evaluateAll((items) => items.map((a) => ({ text: (a.innerText || '').trim(), href: a.href })).filter((x) => x.text || x.href).slice(0, 200)));
  29 |   await page.screenshot({ path: 'C:/Users/SBS/AppData/Local/Temp/sbs-registration-inspect.png', fullPage: true });
  30 |   await context.close();
  31 | });
  32 | 
```