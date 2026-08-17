// proxy.js — all deployment-specific settings come from environment variables,
// normally set via ~/.config/cvca-chatbot/env (see cvcachatbot.service):
//   ANTHROPIC_API_KEY   required, no default
//   PORT                default 3000
//   HOST                default 127.0.0.1
//   ALLOWED_ORIGINS     comma-separated; default derived from HOST/PORT
// Run with: systemctl --user start cvcachatbot
//       or: ANTHROPIC_API_KEY=sk-ant-... node proxy.js

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const API_KEY = process.env.ANTHROPIC_API_KEY;

if (!API_KEY || !API_KEY.startsWith('sk-ant-')) {
  console.error('ANTHROPIC_API_KEY is not set, or does not look like an Anthropic key.');
  console.error('Set it in ~/.config/cvca-chatbot/env, or export it before running.');
  process.exit(1);
}

const PORT = parseInt(process.env.PORT, 10) || 3000;
const HOST = process.env.HOST || '127.0.0.1';

const ALLOWED_ORIGINS = new Set(
  process.env.ALLOWED_ORIGINS
    ? process.env.ALLOWED_ORIGINS.split(',').map(o => o.trim()).filter(Boolean)
    : [`http://localhost:${PORT}`, `http://127.0.0.1:${PORT}`]
);

const MIME = {
  '.html': 'text/html',
  '.js':   'application/javascript',
  '.css':  'text/css',
};

const server = http.createServer((req, res) => {

  // Only the chatbot page may call this proxy from a browser. Requests with no
  // Origin (curl, same-origin navigation) are allowed; a cross-origin page always
  // sends one, so this is what keeps other sites from spending the API key.
  const origin = req.headers.origin;
  const originAllowed = !origin || ALLOWED_ORIGINS.has(origin);

  if (origin && originAllowed) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  }

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(originAllowed ? 204 : 403);
    res.end();
    return;
  }

  // Proxy POST /v1/messages → Anthropic API
  if (req.method === 'POST' && req.url === '/v1/messages') {
    // Enforced here too: withholding CORS headers stops the browser reading the
    // reply, but the request would still reach Anthropic and bill the account.
    if (!originAllowed) {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: { message: 'Origin not allowed' } }));
      return;
    }

    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const options = {
        hostname: 'api.anthropic.com',
        path: '/v1/messages',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': API_KEY,
          'anthropic-version': '2023-06-01',
          'Content-Length': Buffer.byteLength(body),
        },
      };

      const proxyReq = https.request(options, proxyRes => {
        res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json' });
        proxyRes.pipe(res);
      });

      proxyReq.on('error', err => {
        console.error('Proxy error:', err);
        res.writeHead(502);
        res.end(JSON.stringify({ error: { message: err.message } }));
      });

      proxyReq.write(body);
      proxyReq.end();
    });
    return;
  }

  // Serve static files (the HTML chatbot)
  let urlPath;
  try {
    urlPath = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  } catch {
    res.writeHead(400);
    res.end('Bad request');
    return;
  }

  const rel = urlPath === '/' ? '/carmel-views-hoa-chatbot.html' : urlPath;
  const filePath = path.resolve(__dirname, '.' + rel);

  // path.resolve collapses '..', so comparing the result against the project
  // directory rejects anything that climbed out of it.
  if (filePath !== __dirname && !filePath.startsWith(__dirname + path.sep)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'text/plain' });
    res.end(data);
  });
});

server.listen(PORT, HOST, () => {
  console.log('');
  console.log('  Carmel Views HOA Assistant is running.');
  console.log('');
  console.log('  Open this in your browser:');
  console.log('  http://localhost:' + PORT + '/carmel-views-hoa-chatbot.html');
  console.log('');
  console.log('  Press Ctrl+C to stop.');
  console.log('');
});
