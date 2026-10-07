// Renderiza video/video.html fotograma a fotograma.
//   node render-video.js previa  <salida-dir> t1 t2 ...   → PNG de esos instantes (segundos)
//   node render-video.js completo <salida.mp4>            → H.264 sin audio, 1920x1080 a los fps de escenas.json
const { chromium } = require('playwright-core');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const V = path.join(__dirname, '..', 'video');

(async () => {
  const [modo, salida, ...resto] = process.argv.slice(2);
  const datos = JSON.parse(fs.readFileSync(path.join(V, process.env.ESCENAS || 'escenas.json'), 'utf8'));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  p.on('pageerror', (e) => console.error('ERR', e.message));
  await p.goto('file://' + path.join(V, 'video.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(async () => { await Promise.all([...document.images].map((i) => i.complete ? 1 : new Promise((r) => { i.onload = i.onerror = r; }))); });
  const total = await p.evaluate((d) => window.__preparar(d), datos);
  const stage = await p.$('#stage');
  if (modo === 'previa') {
    fs.mkdirSync(salida, { recursive: true });
    for (const t of resto.map(Number)) {
      await p.evaluate((t) => window.__render(t), t);
      await stage.screenshot({ path: path.join(salida, `t${t.toFixed(2).padStart(6, '0')}.png`) });
    }
    console.log('previa lista; duración total', total.toFixed(2), 's');
  } else {
    const fps = datos.fps, n = Math.round(total * fps);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', salida], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      await p.evaluate((t) => window.__render(t), i / fps);
      const buf = await stage.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`  fotograma ${i}/${n} · ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
    console.log('vídeo listo:', salida, n, 'fotogramas,', total.toFixed(2), 's');
  }
  await b.close();
})().catch((e) => { console.error('FALLO', e); process.exit(1); });
