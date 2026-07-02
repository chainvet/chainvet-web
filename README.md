# Chainvet Web

A static web UI for [Chainvet](https://github.com/chainvet/chainvet) that talks to
a running `chainvet-server` over its HTTP API (file browser + analyze + progress).

## Run

One command — starts the API server, serves the UI, waits until it's healthy, and
opens your browser (Ctrl-C stops both):

```bash
python3 serve.py --root /path/to/your/contracts
```

Needs `chainvet-server` on your `PATH` (install via
<https://install.chainvet.dev> with `CHAINVET_BINS=chainvet-server`, or pass
`--server-bin /path/to/chainvet-server`). Other flags: `--api-port`, `--ui-port`,
`--no-browser`.

<details>
<summary>Or run the two pieces by hand</summary>

1. Start the API server (listens on `127.0.0.1:8080`):

   ```bash
   CHAINVET_SERVER_ROOT=/path/to/your/contracts chainvet-server
   ```

2. Serve this UI with any static file server:

   ```bash
   cd assets && python3 -m http.server 5173
   ```

3. Open <http://127.0.0.1:5173>. By default the UI calls the API at
   `http://127.0.0.1:8080`.
</details>

## Configure the API endpoint

The launcher injects this automatically. For the manual path, set
`window.CHAINVET_API_BASE` before `app.js` loads (for example in `index.html`):

Set `window.CHAINVET_API_BASE` before `app.js` loads (for example in `index.html`):

```html
<script>window.CHAINVET_API_BASE = "http://my-host:8080";</script>
```
