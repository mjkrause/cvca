# Carmel Views HOA Assistant

A local chatbot for answering homeowner questions about the Carmel Views CC&Rs, Bylaws, and the Davis-Stirling Act. Runs entirely on your computer — no accounts, no subscriptions, no data sent anywhere except the Anthropic API.

Works the same way on macOS and Linux (Windows isn't covered here).

---

## Files

- `carmel-views-hoa-chatbot.html` — the chatbot application
- `proxy.js` — local proxy server (handles the API key and bypasses browser security restrictions)
- `env.example` — template for your own config file (API key, paths, port)
- `README.md` — this file

---

## One-time setup

### 1. Get an Anthropic API key

Go to [console.anthropic.com](https://console.anthropic.com), create an account, and add a small amount of credit. Each question costs a fraction of a cent, so $5 will last a long time.

Your API key looks like: `sk-ant-api03-...`

### 2. Install nvm and Node.js

nvm lets you install and manage Node.js versions. This step is identical on macOS and Linux. Open Terminal and run:

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

### 3. Create your config file

The chatbot reads its API key from a config file rather than a typed command, so the key never ends up in your shell history. Create it once:

```bash
cd /path/to/this/folder
mkdir -p ~/.config/cvca-chatbot
chmod 700 ~/.config/cvca-chatbot
cp env.example ~/.config/cvca-chatbot/env
chmod 600 ~/.config/cvca-chatbot/env
```

Open `~/.config/cvca-chatbot/env` in a text editor and fill in `ANTHROPIC_API_KEY` with your real key. Leave `NODE_BIN` and `PROJECT_DIR` for now — those are only needed if you set up the automatic background service below; `PORT`, `HOST`, and `ALLOWED_ORIGINS` already have sensible defaults.

---

## Starting the app

Every time you want to use the chatbot, open Terminal and run:

```bash
cd /path/to/this/folder
set -a; source ~/.config/cvca-chatbot/env; set +a
node proxy.js
```

Then open your browser and go to:

```
http://localhost:3000/carmel-views-hoa-chatbot.html
```

To stop the server when you're done, press `Ctrl+C` in Terminal.

(`set -a` / `set +a` works the same way in bash and zsh, so this is identical on Linux and macOS.)

---

## Running automatically (optional)

If you'd rather not start the server by hand every time, you can register it as a background service that starts at login. This reuses the config file created above — open `~/.config/cvca-chatbot/env` again and fill in the two fields you skipped earlier:

- `NODE_BIN` — the absolute path to `node`, found with `command -v node` (nvm-installed node has no fixed location, so this can't be looked up automatically)
- `PROJECT_DIR` — the absolute path to this folder

### Linux (systemd)

Create `~/.config/systemd/user/cvcachatbot.service`:

```ini
[Unit]
Description=Chatbot proxy

[Service]
EnvironmentFile=%h/.config/cvca-chatbot/env
ExecStart=/bin/sh -c '"$NODE_BIN" "$PROJECT_DIR/proxy.js"'
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

Then:

```bash
systemctl --user daemon-reload
systemctl --user enable --now cvcachatbot
systemctl --user status cvcachatbot --no-pager
```

Logs: `journalctl --user -u cvcachatbot -f`

### macOS (launchd)

Create `~/Library/LaunchAgents/com.cvca.chatbot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cvca.chatbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>-c</string>
        <string>set -a; . "$HOME/.config/cvca-chatbot/env"; set +a; exec "$NODE_BIN" "$PROJECT_DIR/proxy.js"</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/cvcachatbot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/cvcachatbot.log</string>
</dict>
</plist>
```

launchd has no equivalent of systemd's `EnvironmentFile=`, so the plist sources the same config file itself (`set -a` exports every variable it sets before running node).

Then:

```bash
launchctl load ~/Library/LaunchAgents/com.cvca.chatbot.plist
```

Logs: `cat /tmp/cvcachatbot.log`

To apply changes after editing the plist:

```bash
launchctl unload ~/Library/LaunchAgents/com.cvca.chatbot.plist
launchctl load ~/Library/LaunchAgents/com.cvca.chatbot.plist
```

---

## How it works

The proxy server does two things:

1. Serves the HTML chatbot to your browser at `localhost:3000`
2. Forwards your questions to the Anthropic API, adding your API key server-side

This means your API key is never exposed in the browser — it stays server-side, read from an environment variable rather than passed on the command line. The browser talks to `localhost`, not to Anthropic directly, which avoids the CORS security restrictions that browsers enforce on direct API calls. The proxy also only accepts cross-origin requests from the chatbot page itself, and only serves files from within this folder.

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
