const { chromium } = require('playwright'); const path = require('path');
require('fs').mkdirSync(require('path').join(__dirname, '..', 'shots'), { recursive: true });
(async () => {
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const fehler = []; page.on('pageerror', e => fehler.push(e.message)); page.on('console', m => m.type() === 'error' && fehler.push(m.text()));
  await page.goto('file://' + path.resolve(__dirname, '..', 'index.html')); await page.waitForTimeout(1200);
  const k = async (c, ms = 80) => { await page.keyboard.down(c); await page.waitForTimeout(ms); await page.keyboard.up(c); await page.waitForTimeout(60); console.log(c, '->', await page.evaluate(() => { const s = window.__tuk.szene; return s.constructor.name + (s.titel ? ':' + s.titel + ':' + s.wahl : '') + (s.c ? ':' + JSON.stringify(s.c) : ''); })); };
  await k('Enter'); await k('ArrowDown'); await k('ArrowDown'); await k('Enter');           // 2 Spieler
  await k('KeyD'); await k('KeyF');                                                        // P1: Riff
  await k('ArrowLeft'); await k('ArrowDown'); await k('KeyJ');                             // P2: Rex Aloha
  await page.waitForTimeout(900); await k('Enter');                                        // Arena
  await page.waitForTimeout(400); await k('Enter'); await page.waitForTimeout(2200);                                       // Steuerung weg, Intro
  console.log('Szene:', await page.evaluate(() => { const s = window.__tuk.szene; return s.constructor.name + ' ' + s.k.map(x => x.def.id).join(' vs ') + ' phase=' + s.phase; }));
  // Beide gleichzeitig: P1 läuft nach rechts, P2 nach links
  await page.keyboard.down('KeyD'); await page.keyboard.down('ArrowLeft'); await page.waitForTimeout(500);
  const pos = await page.evaluate(() => window.__tuk.szene.k.map(x => x.zustand + '@' + Math.round(x.x)));
  await page.keyboard.up('KeyD'); await page.keyboard.up('ArrowLeft');
  // gleichzeitig angreifen: P1 F, P2 J (Laptop) bzw. Numpad2
  await page.keyboard.down('KeyF'); await page.keyboard.down('Numpad2'); await page.waitForTimeout(50);
  const st = await page.evaluate(() => window.__tuk.szene.k.map(x => x.zustand + (x.angriff ? ':' + x.angriff.m.name : '')));
  await page.keyboard.up('KeyF'); await page.keyboard.up('Numpad2');
  console.log('Laufen:', pos, 'Angriff:', st);
  await page.screenshot({ path: require('path').join(__dirname, '..', 'shots', '50_2p.png') });
  console.log('FEHLER:', fehler.length ? fehler : 'keine'); await b.close();
})();
