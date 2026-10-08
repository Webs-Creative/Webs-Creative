// Graba escena.html fotograma a fotograma y lo convierte en vídeo.
//
//   node render.mjs                         → salida/video.mp4 (con salida/audio.wav si existe)
//   node render.mjs --fotos 1.5,9,40        → salida/foto-1.5.png … (para revisar escenas sueltas)
//
// Reparte los fotogramas entre varios Chromium a la vez; cada uno codifica su
// trozo con ffmpeg y al final se unen sin volver a codificar.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import os from "node:os";

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require("playwright"); }
catch { playwright = require(join(process.execPath, "..", "..", "lib", "node_modules", "playwright")); }

const AQUI = dirname(fileURLToPath(import.meta.url));
const SALIDA = join(AQUI, "salida");
mkdirSync(SALIDA, { recursive: true });

const tiempos = JSON.parse(readFileSync(join(AQUI, "tiempos.json"), "utf8"));
const { fps, ancho, alto } = tiempos;
const total = Math.ceil(tiempos.duracion * fps);
const pagina = pathToFileURL(join(AQUI, "escena.html")).href;

const args = process.argv.slice(2);
const fotos = args.includes("--fotos") ? args[args.indexOf("--fotos") + 1].split(",").map(Number) : null;
const trabajadores = Math.max(1, Math.min(4, os.cpus().length - 1));

async function abrir(navegador){
  const p = await navegador.newPage({ viewport: { width: ancho, height: alto }, deviceScaleFactor: 1 });
  await p.addInitScript(() => { window.__GRABANDO__ = true; });
  await p.goto(pagina);
  await p.evaluate(() => window.listo);
  return p;
}

function ffmpeg(argumentos){
  const proceso = spawn("ffmpeg", argumentos, { stdio: ["pipe", "ignore", "pipe"] });
  let errores = "";
  proceso.stderr.on("data", d => { errores = (errores + d).slice(-4000); });
  const fin = new Promise((ok, mal) => proceso.on("close", c => c === 0 ? ok() : mal(new Error(errores))));
  return { proceso, fin };
}

async function grabarTrozo(navegador, desde, hasta, archivo, avance){
  const p = await abrir(navegador);
  const { proceso, fin } = ffmpeg([
    "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", String(fps), archivo,
  ]);
  for (let f = desde; f < hasta; f++){
    await p.evaluate(t => window.pintar(t), f / fps);
    const jpg = await p.screenshot({ type: "jpeg", quality: 95 });
    if (!proceso.stdin.write(jpg)) await new Promise(r => proceso.stdin.once("drain", r));
    avance();
  }
  proceso.stdin.end();
  await fin;
  await p.close();
}

const navegador = await playwright.chromium.launch({ args: ["--force-color-profile=srgb", "--disable-lcd-text"] });
try {
  if (fotos){
    const p = await abrir(navegador);
    for (const t of fotos){
      await p.evaluate(x => window.pintar(x), t);
      await p.screenshot({ path: join(SALIDA, `foto-${t}.png`) });
      console.log(`salida/foto-${t}.png`);
    }
  } else {
    const trozos = [];
    const porTrozo = Math.ceil(total / trabajadores);
    let hechos = 0, aviso = 0;
    const avance = () => {
      hechos++;
      const pct = Math.floor(100 * hechos / total);
      if (pct >= aviso){ console.log(`  ${pct}% (${hechos}/${total} fotogramas)`); aviso = pct + 10; }
    };
    const inicio = Date.now();
    await Promise.all(Array.from({ length: trabajadores }, (_, k) => {
      const desde = k * porTrozo, hasta = Math.min(total, desde + porTrozo);
      const archivo = join(SALIDA, `trozo-${k}.mp4`);
      trozos.push(archivo);
      return grabarTrozo(navegador, desde, hasta, archivo, avance);
    }));
    const lista = join(SALIDA, "trozos.txt");
    writeFileSync(lista, trozos.map(t => `file '${t}'`).join("\n"));
    const audio = join(SALIDA, "audio.wav");
    const conAudio = existsSync(audio);
    const destino = join(SALIDA, conAudio ? "video.mp4" : "video-sin-audio.mp4");
    const { fin } = ffmpeg([
      "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
      ...(conAudio ? ["-i", audio, "-c:a", "aac", "-b:a", "256k", "-shortest"] : []),
      "-c:v", "copy", "-movflags", "+faststart", destino,
    ]);
    await fin;
    for (const t of trozos) rmSync(t);
    rmSync(lista);
    console.log(`${destino} (${total} fotogramas en ${Math.round((Date.now() - inicio) / 1000)} s)`);
  }
} finally {
  await navegador.close();
}
