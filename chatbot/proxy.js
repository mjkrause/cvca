// proxy.js — run with: node proxy.js YOUR_API_KEY
// Then open: http://localhost:3000/carmel-views-hoa-chatbot.html

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const API_KEY = process.argv[2];

if (!API_KEY || !API_KEY.startsWith('sk-ant-')) {
  console.error('Usage: node proxy.js YOUR_API_KEY');
  console.error('Example: node proxy.js sk-ant-api03-...');
  process.exit(1);
}

const PORT = 3000;

const MIME = {
  '.html': 'text/html',
  '.js':   'application/javascript',
  '.css':  'text/css',
};

const server = http.createServer((req, res) => {

  // CORS headers for all responses
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // Proxy POST /v1/messages → Anthropic API
  if (req.method === 'POST' && req.url === '/v1/messages') {
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
  let filePath = req.url === '/' ? '/carmel-views-hoa-chatbot.html' : req.url;
  filePath = path.join(__dirname, filePath);

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

server.listen(PORT, () => {
  console.log('');
  console.log('  Carmel Views HOA Assistant is running.');
  console.log('');
  console.log('  Open this in your browser:');
  console.log('  http://localhost:' + PORT + '/carmel-views-hoa-chatbot.html');
  console.log('');
  console.log('  Press Ctrl+C to stop.');
  console.log('');
});
