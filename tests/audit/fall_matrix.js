const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:900,height:900}});const err=[];p.on('pageerror',e=>err.push(String(e)));
const F=[['A Weiden 200k','92637','200000','',''],['B Metzingen 250k 100kW','72555','250000','100',''],['C Metzingen SLP 60k','72555','60000','',''],['D Weiden 3 Mio','92637','3000000','',''],['E Büro 150k Metzingen','72555','150000','','buero'],['F Meerane 120k','08393','120000','',''],['G Berlin 500k','10115','500000','','']];
const out=[];
for(const [name,plz,kwh,kw,br] of F){
 await p.goto('file://' + require('path').resolve(__dirname, '../../abschaetzung_testseite/netzentgelt_abschaetzung.html') + '');
 await p.fill('#plz',plz);await p.dispatchEvent('#plz','input');if(br)await p.selectOption('#branche',br);await p.fill('#kwh',kwh);if(kw)await p.fill('#kw',kw);await p.waitForTimeout(1500);
 const d=await p.evaluate(()=>{const t=document.getElementById('ergebnis').innerText;
  const rows=[...document.querySelectorAll('.sp-tab tbody tr')].map(r=>[r.cells[0].innerText.split('\n')[0].trim(),r.cells[1].innerText.trim(),r.cells[2].innerText.trim()]);
  const hz=[...document.querySelectorAll('#ergebnis table')].filter(x=>/Jahreszeit/.test(x.innerText)).map(x=>[...x.querySelectorAll('tbody tr')].map(r=>[r.cells[0].innerText.trim(),r.cells[1].innerText.trim()]))[0]||null;
  const hzHead=(document.querySelector('#ergebnis table th:nth-child(2)')||{}).innerText;
  return {titel:(t.match(/Ergebnis für ([^\n]+)/)||[])[1],gross:(t.match(/([\d.]+) €\n?\s*\/ Jahr/)||[])[1],ct:(t.match(/JE KILOWATTSTUNDE\s*\n?([\d,]+) ct/i)||[])[1],rows,hz,
   auto:document.getElementById('auto-box').innerText.replace(/\n+/g,' | '),kwFeld:document.getElementById('kw').value,preisFeld:document.getElementById('a-strom').value,ebene:document.getElementById('ebene').value,
   empf:(t.match(/Sie haben [^\n]*\n?[^\n]*/)||[''])[0],lp:(t.match(/Leistungspreis ([\d,]+) €\/kW/)||[])[1],apm:(t.match(/Arbeitspreis ([\d,]+) ct\/kWh/)||[])[1],tarif:(t.match(/\nTARIF\s*\n?([^\n]+)/i)||[])[1],
   zeitfenster:(t.match(/Hochlastzeitfenster von[^\n]*/i)||[''])[0],text:t.length};});
 d.name=name;d.plz=plz;d.kwh=kwh;out.push(d);}
fs.writeFileSync('audit.json',JSON.stringify(out,null,1));console.log('Fehler:',err,'Fälle:',out.length);await b.close()})();
