#!/usr/bin/env node
/**
 * Export the animated loaders to GIF and animated WebP.
 *
 * Requires Node 22+, Chrome/Chromium and FFmpeg. Frames are captured from the
 * CSS animations through the Chrome DevTools Protocol, so the exporter never
 * reimplements the motion. Run `node scripts/loaders_animated.mjs --only=NAME`
 * to regenerate a single loader.
 */

import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = process.env.CHROME || 'google-chrome';
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const CONFIG = JSON.parse(readFileSync(path.join(ROOT, 'scripts', 'loaders.json'), 'utf8'));
const FPS = CONFIG.fps;
const LOADERS = CONFIG.loaders;
const FORMATS = ['gif', 'webp'];

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class Cdp {
  constructor(url) {
    this.url = url;
    this.nextId = 0;
    this.pending = new Map();
    this.ws = null;
  }

  async connect() {
    this.ws = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      this.ws.addEventListener('open', resolve, { once: true });
      this.ws.addEventListener('error', reject, { once: true });
    });
    this.ws.addEventListener('message', (event) => {
      const text = typeof event.data === 'string' ? event.data : Buffer.from(event.data).toString('utf8');
      const message = JSON.parse(text);
      if (!message.id) return;
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) {
        pending.reject(new Error(`${message.error.message} (${message.error.code})`));
      } else {
        pending.resolve(message.result);
      }
    });
  }

  send(method, params = {}) {
    const id = ++this.nextId;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  close() {
    try {
      this.ws.close();
    } catch {
      // already closed
    }
  }
}

async function evaluate(cdp, expression, { awaitPromise = false } = {}) {
  const result = await cdp.send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    const description = result.exceptionDetails.exception?.description;
    throw new Error(description || result.exceptionDetails.text || 'Runtime.evaluate failed');
  }
  return result.result.value;
}

async function launchChrome() {
  const profile = mkdtempSync(path.join(tmpdir(), 'easysql-chrome-'));
  let stderr = '';
  const chrome = spawn(
    CHROME,
    [
      '--headless=new',
      '--no-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--hide-scrollbars',
      '--mute-audio',
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-background-networking',
      '--disable-extensions',
      '--disable-sync',
      '--force-device-scale-factor=1',
      `--user-data-dir=${profile}`,
      '--remote-debugging-port=0',
      'about:blank',
    ],
    { detached: true, stdio: ['ignore', 'ignore', 'pipe'] },
  );
  chrome.stderr.on('data', (chunk) => {
    stderr += chunk.toString();
  });
  chrome.on('error', (error) => {
    stderr += error.message;
  });

  const portFile = path.join(profile, 'DevToolsActivePort');
  let port = '';
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (existsSync(portFile)) {
      port = readFileSync(portFile, 'utf8').split('\n')[0].trim();
      break;
    }
    if (chrome.exitCode !== null) break;
    await sleep(50);
  }
  if (!port) {
    try {
      process.kill(-chrome.pid, 'SIGKILL');
    } catch {
      // already stopped
    }
    rmSync(profile, { recursive: true, force: true });
    throw new Error(`Chrome did not start.\n${stderr}`);
  }

  let target;
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/list`);
      const targets = await response.json();
      target = targets.find((item) => item.type === 'page' && item.webSocketDebuggerUrl);
      if (target) break;
    } catch {
      // Chrome is still starting
    }
    await sleep(50);
  }
  if (!target) {
    try {
      process.kill(-chrome.pid, 'SIGKILL');
    } catch {
      // already stopped
    }
    rmSync(profile, { recursive: true, force: true });
    throw new Error('Chrome did not expose a page target.');
  }

  const cdp = new Cdp(target.webSocketDebuggerUrl);
  await cdp.connect();
  return { chrome, profile, cdp };
}

async function stopChrome(chrome, profile, cdp) {
  cdp.close();
  try {
    process.kill(-chrome.pid, 'SIGTERM');
  } catch {
    // already stopped
  }
  await new Promise((resolve) => {
    if (chrome.exitCode !== null) {
      resolve();
      return;
    }
    chrome.once('exit', resolve);
    setTimeout(resolve, 2000);
  });
  try {
    process.kill(-chrome.pid, 'SIGKILL');
  } catch {
    // already stopped
  }
  rmSync(profile, { recursive: true, force: true });
}

async function waitForLoad(cdp) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    try {
      if ((await evaluate(cdp, 'document.readyState')) === 'complete') return;
    } catch {
      // navigation replaced the execution context
    }
    await sleep(25);
  }
  throw new Error('Page did not finish loading.');
}

async function waitForAnimations(cdp) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    try {
      const count = await evaluate(cdp, 'document.getAnimations().length');
      if (count > 0) return count;
    } catch {
      // navigation replaced the execution context
    }
    await sleep(25);
  }
  throw new Error('No CSS animations found in the SVG.');
}

async function captureLoader(cdp, loader, frameDir) {
  const svg = path.join(ROOT, 'loaders', `${loader.name}.svg`);
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width: loader.width,
    height: loader.height,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await cdp.send('Page.navigate', { url: pathToFileURL(svg).href });
  await waitForLoad(cdp);
  const animationCount = await waitForAnimations(cdp);
  await cdp.send('Emulation.setDefaultBackgroundColorOverride', {
    color: { r: 0, g: 0, b: 0, a: 0 },
  });

  const box = await evaluate(
    cdp,
    `(() => {
      const root = document.documentElement;
      root.setAttribute('width', '${loader.width}');
      root.setAttribute('height', '${loader.height}');
      root.style.width = '${loader.width}px';
      root.style.height = '${loader.height}px';
      const rect = root.getBoundingClientRect();
      return [rect.width, rect.height];
    })()`,
  );
  if (box[0] !== loader.width || box[1] !== loader.height) {
    throw new Error(`${loader.name}: expected ${loader.width}x${loader.height}, got ${box.join('x')}`);
  }

  const frames = Math.round(loader.duration * FPS);
  for (let index = 0; index < frames; index += 1) {
    const time = (loader.loopStart + (index * loader.duration) / frames) * 1000;
    await evaluate(
      cdp,
      `(() => {
        const time = ${time};
        for (const animation of document.getAnimations()) {
          animation.pause();
          animation.currentTime = time;
        }
      })()`,
    );
    await evaluate(
      cdp,
      'new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))',
      { awaitPromise: true },
    );
    const { data } = await cdp.send('Page.captureScreenshot', {
      format: 'png',
      fromSurface: true,
      captureBeyondViewport: false,
    });
    writeFileSync(
      path.join(frameDir, `frame-${String(index).padStart(3, '0')}.png`),
      Buffer.from(data, 'base64'),
    );
  }
  return { frames, animationCount };
}

function run(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: ['ignore', 'ignore', 'pipe'] });
    let stderr = '';
    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });
    child.on('error', reject);
    child.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${command} exited with ${code}\n${stderr}`));
    });
  });
}

async function encodeLoader(loader, frameDir, outRoot) {
  const input = path.join(frameDir, 'frame-%03d.png');
  const base = ['-y', '-framerate', String(FPS), '-i', input];
  const bitexact = ['-fflags', '+bitexact', '-flags', '+bitexact', '-map_metadata', '-1'];

  await run(FFMPEG, [
    ...base,
    '-filter_complex',
    '[0:v]split[a][b];[a]palettegen=reserve_transparent=1:stats_mode=full[p];[b][p]paletteuse=alpha_threshold=128:diff_mode=rectangle',
    '-loop',
    '0',
    ...bitexact,
    path.join(outRoot, 'gif', `${loader.name}.gif`),
  ]);

  await run(FFMPEG, [
    ...base,
    '-c:v',
    'libwebp_anim',
    '-lossless',
    '0',
    '-q:v',
    '80',
    '-loop',
    '0',
    '-an',
    ...bitexact,
    path.join(outRoot, 'webp', `${loader.name}.webp`),
  ]);
}

async function main() {
  const only = process.argv.find((argument) => argument.startsWith('--only='))?.split('=')[1];
  const keepFrames = process.argv.includes('--keep-frames');
  const loaders = only ? LOADERS.filter((loader) => loader.name === only) : LOADERS;
  if (loaders.length === 0) {
    throw new Error(`Unknown loader: ${only}`);
  }

  const outRoot = path.join(ROOT, 'loaders', 'exports');
  for (const format of FORMATS) {
    mkdirSync(path.join(outRoot, format), { recursive: true });
  }

  const { chrome, profile, cdp } = await launchChrome();
  try {
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Emulation.setDefaultBackgroundColorOverride', {
      color: { r: 0, g: 0, b: 0, a: 0 },
    });
    await cdp.send('Emulation.setEmulatedMedia', {
      features: [{ name: 'prefers-reduced-motion', value: 'no-preference' }],
    });

    for (const loader of loaders) {
      const frameDir = mkdtempSync(path.join(tmpdir(), `easysql-${loader.name}-`));
      try {
        const result = await captureLoader(cdp, loader, frameDir);
        await encodeLoader(loader, frameDir, outRoot);
        console.log(`${loader.name}: ${result.frames} frames, ${result.animationCount} animations`);
        if (keepFrames) console.log(`frames: ${frameDir}`);
      } finally {
        if (!keepFrames) rmSync(frameDir, { recursive: true, force: true });
      }
    }
  } finally {
    await stopChrome(chrome, profile, cdp);
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});