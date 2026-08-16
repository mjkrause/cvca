# Carmel Views HOA Assistant

A local chatbot for answering homeowner questions about the Carmel Views CC&Rs, Bylaws, and the Davis-Stirling Act. Runs entirely on your computer — no accounts, no subscriptions, no data sent anywhere except the Anthropic API.

---

## Files

- `carmel-views-hoa-chatbot.html` — the chatbot application
- `proxy.js` — local proxy server (handles the API key and bypasses browser security restrictions)
- `README.md` — this file

---

## One-time setup

### 1. Get an Anthropic API key

Go to [console.anthropic.com](https://console.anthropic.com), create an account, and add a small amount of credit. Each question costs a fraction of a cent, so $5 will last a long time.

Your API key looks like: `sk-ant-api03-...`

### 2. Install nvm and Node.js

nvm lets you install and manage Node.js versions. Open Terminal and run:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

Close Terminal and reopen it, then install Node.js:

```bash
nvm install --lts
nvm use --lts
```

Verify both installed correctly:

```bash
node --version
npm --version
```

---

## Starting the app

Every time you want to use the chatbot, open Terminal and run:

```bash
cd /path/to/this/folder
node proxy.js sk-ant-your-key-here
```

Then open your browser and go to:

```
http://localhost:3000/carmel-views-hoa-chatbot.html
```

To stop the server when you're done, press `Ctrl+C` in Terminal.

---

## How it works

The proxy server does two things:

1. Serves the HTML chatbot to your browser at `localhost:3000`
2. Forwards your questions to the Anthropic API, adding your API key server-side

This means your API key is never exposed in the browser — it stays in the Terminal session only. The browser talks to `localhost`, not to Anthropic directly, which avoids the CORS security restrictions that browsers enforce on direct API calls.

---

## Documents covered

- **CC&Rs** — Second Restated Declaration of Covenants, Conditions and Restrictions for Carmel Views (December 2017)
- **Bylaws** — Bylaws of Carmel Views Community Association (includes changes dated January 6, 1982)
- **Davis-Stirling Act** — California Civil Code Part 5, Common Interest Developments (AB 805, operative January 1, 2014)

---

## Notes

- Answers are based solely on the documents above. The chatbot is not a substitute for legal advice — consult a licensed attorney for specific legal questions.
- The Davis-Stirling Act embedded in the app reflects the 2012 AB-805 recodification. California law may have been amended since; verify current Civil Code for anything high-stakes.
- Conversation history is maintained within a session, so you can ask follow-up questions. History resets when you reload the page.
