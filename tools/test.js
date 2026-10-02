// Automatischer Test: Konsole, Szenen-Screenshots, Kampf-Simulation
const { chromium } = require('playwright');
const path = require('path');
require('fs').mkdirSync(require('path').join(__dirname, '..', 'shots'), { recursive: true });
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const fehler = [];
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') fehler.push(m.type() + ': ' + m.text()); });
  page.on('pageerror', e => fehler.push('pageerror: ' + e.message));
  page.on('requestfailed', r => fehler.push('Ladefehler: ' + r.url().slice(0, 80)));
  await page.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  await page.waitForTimeout(1500);
  const fehlend = await page.evaluate(() => Object.entries(window.__tuk.BILDER).filter(([, b]) => !b).map(([n]) => n));
  if (fehlend.length) fehler.push('Fehlende Bilder: ' + fehlend.join(', '));
  const shot = async n => page.screenshot({ path: `${require('path').join(__dirname, '..', 'shots')}/${n}.png` });
  await shot('01_titel');
  await page.keyboard.press('Enter'); await page.waitForTimeout(300); await shot('02_menue');
  await page.keyboard.press('Enter'); await page.waitForTimeout(300); // Arcade -> Auswahl
  await page.keyboard.press('ArrowRight'); await page.waitForTimeout(200); await shot('03_auswahl');
  await page.keyboard.press('Escape'); await page.waitForTimeout(200);
  // Menü -> Duell gegen CPU
  await page.keyboard.press('ArrowDown'); await page.waitForTimeout(100); await page.keyboard.press('Enter'); await page.waitForTimeout(200);
  await page.keyboard.press('KeyF'); await page.waitForTimeout(200);
  await page.keyboard.press('ArrowRight'); await page.keyboard.press('ArrowDown'); await page.waitForTimeout(100);
  await shot('04_auswahl_cpu');
  await page.keyboard.press('KeyF'); await page.waitForTimeout(1000); await shot('05_arena');
  await page.keyboard.press('Enter'); await page.waitForTimeout(400); await shot('06_steuerung');
  await page.keyboard.press('Enter'); await page.waitForTimeout(800); await shot('07_intro');
  await page.waitForTimeout(1500);
  // Spieler 1 greift an
  const druck = async (k, ms = 60) => { await page.keyboard.down(k); await page.waitForTimeout(ms); await page.keyboard.up(k); };
  await page.keyboard.down('KeyD'); await page.waitForTimeout(700); await page.keyboard.up('KeyD');
  for (let i = 0; i < 3; i++) { await druck('KeyF'); await page.waitForTimeout(150); }
  await shot('08_kampf');
  await druck('KeyR'); await page.waitForTimeout(250); await shot('09_spezial');
  // Energie auffüllen und Super
  await page.evaluate(() => { const s = window.__tuk.szene; s.k[0].energie = 100; });
  await druck('KeyT'); await page.waitForTimeout(400); await shot('10_cutin');
  await page.waitForTimeout(900); await shot('11_super');
  await page.keyboard.press('Escape'); await page.waitForTimeout(200); await shot('12_pause');
  await page.keyboard.press('Escape'); await page.waitForTimeout(200);
  // Alle Paarungen und Arenen als KI-gegen-KI kurz simulieren (beschleunigt)
  const ids = ['basso', 'coolcat', 'riff', 'rex', 'bear', 'glut'], arenen = ['neon', 'spielhalle', 'retro', 'gamingzimmer'];
  const ergebnisse = [];
  for (let i = 0; i < ids.length; i++) {
    const a = ids[i], b = ids[(i + 1) % ids.length], ar = arenen[i % 4];
    const r = await page.evaluate(({ a, b, ar }) => {
      const T = window.__tuk; T.starteKampf({ modus: 'demo', d1: T.CHAR[a], d2: T.CHAR[b], arena: ar });
      const s = T.szene; let supers = 0, frames = 0; const haltungen = [new Set(), new Set()];
      for (const k of s.k) k.energie = 100;
      while (frames < 60 * 60 && T.szene === s) { s.aktualisiere(); if (s.cutin && s.cutin.t === 1) supers++; frames++; if (s.k) s.k.forEach((k, i) => haltungen[i].add(k.haltung)); if (frames % 600 === 0) for (const k of s.k) k.energie = 100; }
      return { a, b, ar, frames, lp: s.k ? s.k.map(k => Math.round(k.lp)) : null, siege: s.k.map(k => k.siege), runde: s.runde, supers, szene: T.szene.constructor.name, haltungen: haltungen.map(h => [...h].sort().join('')) };
    }, { a, b, ar });
    ergebnisse.push(r);
    await page.waitForTimeout(100);
    await shot('20_arena_' + ar + '_' + a);
  }
  console.log(JSON.stringify(ergebnisse, null, 1));
  // Mitten im Kampf-Screenshots je Arena
  for (const ar of arenen) {
    await page.evaluate(({ ar }) => { const T = window.__tuk; T.starteKampf({ modus: 'demo', d1: T.CHAR.glut, d2: T.CHAR.coolcat, arena: ar }); const s = T.szene; for (let i = 0; i < 420; i++) s.aktualisiere(); }, { ar });
    await page.waitForTimeout(80); await shot('30_' + ar);
  }
  // Ergebnis-Szene
  await page.evaluate(() => { const T = window.__tuk; T.starteKampf({ modus: 'cpu', d1: T.CHAR.bear, d2: T.CHAR.glut, arena: 'neon' }); const s = T.szene; s.k[0].siege = 1; s.matchEnde(s.k[0]); });
  await page.waitForTimeout(900); await shot('40_ergebnis');
  console.log('FEHLER:', fehler.length ? fehler.join('\n') : 'keine');
  await browser.close();
})();
