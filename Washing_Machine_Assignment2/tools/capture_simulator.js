// Captures the actual local browser simulation, with assertions on its controls.
const path = require('path');
const fs = require('fs');
const {pathToFileURL} = require('url');
const pkg = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const {chromium} = pkg ? require(path.join(pkg,'playwright')) : require('playwright');
const root = path.resolve(__dirname,'..');

(async()=>{
  const browser = await chromium.launch({headless:true,
    ...(process.env.ASSIGNMENT2_HEADLESS_SINGLE ? {args:['--single-process','--no-zygote','--disable-gpu']} : {}),
    ...(process.env.ASSIGNMENT2_BROWSER ? {executablePath:process.env.ASSIGNMENT2_BROWSER} : {})});
  try {
    const page = await browser.newPage({viewport:{width:1180,height:880},deviceScaleFactor:1.5});
    const errors=[]; page.on('pageerror',err=>errors.push(err.message));
    await page.goto(pathToFileURL(path.join(root,'simulator/index.html')).href);
    const evidence=path.join(root,'evidence');
    const figures=path.join(root,'report/figures');
    async function expect(fields) {
      const s=await page.evaluate(()=>window.demo.snapshot());
      for(const [k,v] of Object.entries(fields)) if(s[k]!==v) throw new Error(k+': '+s[k]+' != '+v);
    }
    async function shot(name) {
      await page.screenshot({path:path.join(evidence,name+'.png'),fullPage:true});
      await page.locator('.grid').screenshot({path:path.join(figures,name+'_panel.png')});
    }
    await expect({state:'STANDBY',credit:0,wash:false}); await shot('01_standby');
    await page.locator('[data-action="RUN"]').click(); await expect({state:'STANDBY'});
    await page.locator('[data-coin="20"]').click(); await page.locator('[data-coin="50"]').click();
    await expect({state:'READY',credit:70,blue:true}); await shot('02_ready');
    await page.locator('[data-action="RUN"]').click();
    await expect({state:'RUNNING',credit:0,remaining:1800000,wash:true}); await shot('03_running');
    await page.evaluate(()=>window.demo.advance(480000));
    await page.locator('[data-action="PAUSE"]').click();
    await expect({state:'PAUSED',remaining:1320000,wash:false}); await shot('04_paused');
    await page.evaluate(()=>window.demo.advance(480000));
    await page.locator('[data-action="RUN"]').click();
    await expect({state:'RUNNING',remaining:840000,wash:true}); await shot('05_resumed');
    await page.evaluate(()=>window.demo.advance(840000));
    await expect({state:'STANDBY',credit:0,wash:false}); await shot('06_timeout');
    fs.writeFileSync(path.join(evidence,'browser_cycle_log.json'),JSON.stringify(await page.evaluate(()=>window.demo.log()),null,2));
    await page.locator('#reset').click(); await page.locator('[data-coin="50"]').click(); await page.locator('[data-action="RUN"]').click();
    await page.locator('[data-action="STOP"]').click();
    await expect({state:'RUNNING',stops:1,wash:true}); await shot('07_first_stop');
    await page.locator('[data-action="STOP"]').click();
    await expect({state:'STANDBY',stops:0,wash:false}); await shot('08_force_stop');
    await page.locator('[data-coin="50"]').click(); await page.locator('[data-action="RUN"]').click();
    await page.locator('#fault').click(); await expect({state:'ERROR',wash:false,blue:false}); await shot('09_error');
    await page.locator('[data-action="RUN"]').click(); await expect({state:'ERROR'});
    await page.locator('#reset').click(); await expect({state:'STANDBY',credit:0});
    await page.locator('#speed').selectOption('60');
    await page.waitForFunction(()=>document.querySelector('#clock').textContent!=='00:00',null,{timeout:2000});
    await page.locator('#speed').selectOption('0');
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:path.join(evidence,'10_mobile_view.png'),fullPage:true});
    if(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth)) throw new Error('Mobile horizontal overflow');
    await page.goto(pathToFileURL(path.join(root,'output/Washing_Machine_Simulator.html')).href);
    await expect({state:'STANDBY',credit:0});
    await page.locator('[data-coin="50"]').click();
    await page.locator('[data-action="RUN"]').click();
    await expect({state:'RUNNING',credit:0,remaining:1800000});
    await page.locator('[data-action="PAUSE"]').click();
    await expect({state:'PAUSED',wash:false});
    if(errors.length) throw new Error(errors.join('\n'));
    const result={status:'PASS',screenshots:10,standalone_html:'PASS',controls:'Coins, RUN, PAUSE, STOP, fault, reset, auto clock',scope:'Real local browser interactions; no physical board.'};
    fs.writeFileSync(path.join(evidence,'browser_test_summary.json'),JSON.stringify(result,null,2));
    console.log('PASS: browser controls, 30 min timeout, STOP, fault, auto clock and mobile layout. 10 screenshots.');
  } finally { await browser.close(); }
})().catch(err=>{console.error(err);process.exit(1)});
