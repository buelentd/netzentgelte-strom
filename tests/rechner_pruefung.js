// Rechenproben für die Testseite im Browser (Playwright). Aufruf: node tests/rechner_pruefung.js  -> Exit 1 bei Fehler.
const {chromium} = require('playwright');
const path = require('path');
const zahl = s => parseFloat(String(s).replace(/\./g, '').replace(',', '.'));
(async () => {
  const b = await chromium.launch(), p = await b.newPage(), fehler = [], ok = (c, t) => { if (!c) fehler.push(t); };
  p.on('pageerror', e => fehler.push('JS-Fehler: ' + e));
  await p.goto('file://' + path.resolve(__dirname, '../abschaetzung_testseite/netzentgelt_abschaetzung.html'));
  // 1. Keine versteckten Vorbelegungen
  ok(await p.inputValue('#plz') === '', 'PLZ ist vorbelegt');
  ok(await p.inputValue('#branche') === '', 'Branche ist vorbelegt');
  ok(await p.inputValue('#anlagen') === '', 'Anlagen sind vorbelegt');
  ok(await p.inputValue('#kwh') === '', 'Verbrauch ist vorbelegt');
  // 2. Furo-Vergleichsfall: Metzingen, 250.000 kWh, 100 kW (Leistungspreis MS/NS ab 2.500 h laut Preisblatt: 189,86)
  await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
  await p.fill('#plz', '72555'); await p.dispatchEvent('#plz', 'input'); await p.selectOption('#branche', 'sonstiges');
  await p.fill('#kwh', '250000'); await p.fill('#kw', '100'); await p.waitForTimeout(1200);
  await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
  ok(await p.inputValue('#ebene') === 'msns', 'Ebene bei 250.000 kWh nicht MS/NS');
  const t = await p.evaluate(() => document.getElementById('ergebnis').innerText);
  ok(/Leistungspreis 189,86 €\/kW/.test(t), 'Leistungspreis MS/NS Metzingen nicht 189,86');
  const k = t.match(/Zielspitze ([\d.,]+) statt ([\d.,]+) kW[^:]*: ([\d.,]+) € Netzentgelt/);
  ok(!!k, 'Kappungszeile fehlt');
  if (k) ok(Math.abs((zahl(k[2]) - zahl(k[1])) * 189.86 - zahl(k[3])) < 2, `Ersparnis ${k[3]} ≠ gekappte kW × Leistungspreis`);
  const kap = t.match(/NÖTIGE KAPAZITÄT\s*ca\. ([\d.,]+) kWh/i), form = t.match(/Kapazität = ([\d.,]+) kW × ([\d.,]+) h/);
  if (kap && form) ok(Math.abs(Math.ceil(zahl(form[1]) * zahl(form[2]) / 0.8) - zahl(kap[1])) <= 1, 'Nötige Kapazität passt nicht zur Formel');
  ok(/Hochlastzeitfenster von Stadtwerke Metzingen/i.test(t) && /13:15-14:15, 17:15-20:15/.test(t), 'Hochlastzeitfenster von Metzingen werden nicht ausgegeben');
  // Ergebnis ist ohne Aufklappen sichtbar (Netzentgelt, Strompreis-Tabelle, Empfehlung, Tageskurve)
  await p.reload(); await p.fill('#plz', '72555'); await p.dispatchEvent('#plz', 'input'); await p.fill('#kwh', '250000'); await p.waitForTimeout(1300);
  const sichtbar = await p.evaluate(() => document.getElementById('ergebnis').innerText);
  ok(/€ \/ Jahr/.test(sichtbar), 'Netzentgelt ist ohne Aufklappen nicht sichtbar');
  ok(/Ihr Strompreis/i.test(sichtbar), 'Strompreis-Tabelle ist ohne Aufklappen nicht sichtbar');
  ok(/Dann ist ein Speicher mit/.test(sichtbar), 'Empfehlung fehlt');
  ok(/Tageskurve und Hochlastzeitfenster/i.test(sichtbar), 'Tageskurve fehlt');
  await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
  await p.fill('#kw', '100'); await p.waitForTimeout(1000); await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
  // 3. Strompreis-Tabelle: Summen stimmen, Umsatzsteuer 19 %
  const z = await p.evaluate(() => [...document.querySelectorAll('.sp-tab tbody tr')].map(r => [r.cells[0].innerText.split('\n')[0], r.cells[1].innerText.trim()]));
  const wert = n => { const r = z.find(x => x[0].startsWith(n)); return r && r[1] ? zahl(r[1]) : 0; };
  const posten = z.filter(x => !/^(Summe|Umsatzsteuer)/.test(x[0])).reduce((a, x) => a + (x[1] ? zahl(x[1]) : 0), 0);
  ok(Math.abs(posten - wert('Summe der ausgewiesenen')) <= 2, 'Summe netto ≠ Summe der Posten');
  ok(Math.abs(wert('Umsatzsteuer') - 0.19 * wert('Summe der ausgewiesenen')) <= 2, 'Umsatzsteuer ≠ 19 %');
  ok(Math.abs(wert('Summe brutto') - wert('Summe der ausgewiesenen') - wert('Umsatzsteuer')) <= 2, 'brutto ≠ netto + Umsatzsteuer');
  ok(Math.abs(wert('KWKG') - 250000 * 0.00446) < 1, 'KWKG ≠ kWh × 0,446 ct');
  // 4. Strompreis-Eingabe: gesamter Arbeitspreis minus Netz-Arbeitspreis
  await p.fill('#a-strom', '25'); await p.waitForTimeout(900);
  await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
  const t2 = await p.evaluate(() => document.getElementById('ergebnis').innerText);
  const ap = t2.match(/Arbeitspreis ([\d,]+) ct\/kWh/), an = t2.match(/Strompreis angesetzt: ([\d,]+) ct/);
  if (ap && an) ok(Math.abs(25 - zahl(ap[1]) - zahl(an[1])) < 0.1, 'Strompreis ohne Netzentgelt ≠ Gesamtpreis − Netz-Arbeitspreis');
  // 5. Speicher, unabhängig nachgerechnet (tests/audit/speicher_nachrechnung.py): Metzingen, 250.000 kWh, 100 kW, Speicher 100 kWh
  await p.reload(); await p.fill('#plz', '72555'); await p.dispatchEvent('#plz', 'input'); await p.fill('#kwh', '250000'); await p.fill('#kw', '100'); await p.waitForTimeout(1200);
  ok(await p.inputValue('#a-steuern') === '5.11', 'Steuern und Umlagen ohne Entlastung nicht 5,11 ct (Tabelle: 0,11 + 0,446 + 0,941 + 1,559 + 2,05)');
  await p.evaluate(() => { const e = document.getElementById('speicher-kwh'); e.value = '100'; e.dispatchEvent(new Event('input', {bubbles: true})); });
  await p.waitForTimeout(1200); await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
  const t5 = await p.evaluate(() => document.getElementById('ergebnis').innerText);
  const bw = t5.match(/Barwert über 10 Jahre bei 6,0 % Zins: \+ ([\d.]+) €/), be = t5.match(/Speicherpreis von etwa ([\d.]+) €\/kWh/), su = t5.match(/Summe\s*\n[^\n]*Amortisation[^\n]*\n\+ ([\d.]+) €/);
  ok(!!bw && Math.abs(zahl(bw[1]) - 32362) <= 3, 'Speicher 100 kWh: Barwert nicht 32.362 € (Nachrechnung)');
  ok(!!be && Math.abs(zahl(be[1]) - 741) <= 1, 'Speicher 100 kWh: Preisgrenze nicht 741 €/kWh (Nachrechnung)');
  ok(!!su && Math.abs(zahl(su[1]) - 12394) <= 3, 'Speicher 100 kWh: Summe nicht 12.394 € (Nachrechnung)');
  await p.evaluate(() => document.getElementById('steuer-entl').click()); await p.waitForTimeout(900);
  ok(await p.inputValue('#a-steuern') === '3.11', 'Steuern und Umlagen mit Entlastung nicht 3,11 ct');
  await b.close();
  if (fehler.length) { console.log('FEHLER:\n- ' + fehler.join('\n- ')); process.exit(1); }
  console.log('Rechenproben ok');
})();
