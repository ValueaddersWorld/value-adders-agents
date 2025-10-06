# PathLog Bridge Chrome Extension

This extension provides a lightweight bridge between AI chat surfaces and your local PathLog vault. Highlight any text in a browser tab (e.g., ChatGPT, Claude, Notion AI), right-click, and choose **"Send selection to PathLog."** The selected passage is POSTed to the PathLog `/capture` API with optional passphrase authentication.

## Project Structure

- `manifest.json` - Manifest V3 definition with context menu & background service worker
- `background.js` - Service worker creating context menu and forwarding selections to the PathLog API
- `options.html|css|js` - Simple settings page for configuring API base URL, user ID, passphrase, and tool alias
- `icons/` - Minimal branded icons for Chrome toolbar and web store listing

## Local Development

1. Ensure the PathLog FastAPI service is running locally (default `http://localhost:8002`).
2. In Chrome, open `chrome://extensions` and enable **Developer mode**.
3. Click **Load unpacked** and select the `pathlog/browser_extension` directory inside this repo.
4. Open the extension options (Details -> Extension options) and configure:
   - API Base URL (e.g., `http://localhost:8002`)
   - User ID (`/consent` response UUID)
   - Passphrase (only if your vault requires one)
   - Tool name (defaults to `browser_extension`)
5. Highlight text in a chat window, right-click, and choose **Send selection to PathLog**. You can also press **Alt+Shift+L** to send the current selection automatically. A notification confirms success or failure.

## Packaging for Chrome Web Store

1. Update `manifest.json` metadata (version, description, host permissions) as needed.
2. Run a production build (zip the folder):
   ```powershell
   Compress-Archive -Path pathlog\browser_extension\* -DestinationPath pathlog-bridge-extension.zip -Force
   ```
3. Provide 128x128 icon (already included) and any promotional imagery required by the store listing.
4. Submit the zipped package through the [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/developer/dashboard) with appropriate privacy disclosures (data is transmitted only to your configured PathLog endpoint).

## Security Notes

- The extension only sends the selected text, page URL, and title. No continuous monitoring or keylogging is implemented.
- Data is transmitted to the base URL you configure. For production, deploy the PathLog API behind HTTPS with valid certificates.
- Passphrases are stored using `chrome.storage.sync`; consider switching to `chrome.storage.local` for sensitive deployments or implementing session prompts.

## Roadmap Ideas

- Auto-detect agent prompts/responses from popular chat UIs for structured logging.
- Allow manual tagging before submission.
- Integrate with the PathLog timeline for quick previews after capture.


