# ChainVet Web

A static web UI for [ChainVet](https://github.com/chainvet/chainvet) that talks to
a running `chainvet-server` over its HTTP API (file browser + analyze + progress).

## Run

1. Start the API server from the ChainVet workspace (listens on `127.0.0.1:8080`):

   ```bash
   CHAINVET_SERVER_ROOT=/path/to/your/contracts chainvet-server
   ```

2. Serve this UI with any static file server, e.g.:

   ```bash
   cd assets && python3 -m http.server 5173
   ```

3. Open <http://127.0.0.1:5173>. By default the UI calls the API at
   `http://127.0.0.1:8080`.

## Configure the API endpoint

Set `window.CHAINVET_API_BASE` before `app.js` loads (for example in `index.html`):

```html
<script>window.CHAINVET_API_BASE = "http://my-host:8080";</script>
```
