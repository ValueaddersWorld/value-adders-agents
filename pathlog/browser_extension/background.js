const MENU_ID = "pathlog-send-selection";

const DEFAULT_SETTINGS = {
  baseUrl: "http://localhost:8002",
  userId: "",
  passphrase: "",
  toolName: "browser_extension",
};

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: MENU_ID,
    title: "Send selection to PathLog",
    contexts: ["selection"],
  });
});

async function loadSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(DEFAULT_SETTINGS, (items) => {
      resolve({ ...DEFAULT_SETTINGS, ...items });
    });
  });
}

async function showNotification(title, message) {
  try {
    await chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon128.png",
      title,
      message,
    });
  } catch (error) {
    console.warn("PathLog notification error", error);
  }
}

async function sendToPathLog(selectionText, pageUrl, pageTitle) {
  const settings = await loadSettings();
  if (!settings.userId) {
    await showNotification("PathLog Bridge", "Set your User ID in the options page before sending content.");
    return;
  }
  if (!selectionText) {
    return;
  }

  const payload = {
    user_id: settings.userId,
    tool_name: settings.toolName || "browser_extension",
    prompt: selectionText,
    response: "",
    metadata: {
      source_url: pageUrl || null,
      page_title: pageTitle || null,
      captured_at: new Date().toISOString(),
      agent: "chrome_selection",
    },
  };

  if (settings.passphrase) {
    payload.passphrase = settings.passphrase;
  }

  const endpoint = `${settings.baseUrl.replace(/\/$/, "")}/capture`;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `HTTP ${response.status}`);
    }

    await showNotification("PathLog", "Selection sent securely to your vault.");
  } catch (error) {
    console.error("PathLog send failed", error);
    await showNotification("PathLog Error", error.message || "Unable to reach PathLog bridge.");
  }
}

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId !== MENU_ID) {
    return;
  }
  const selection = (info.selectionText || "").trim();
  sendToPathLog(selection, info.pageUrl, tab?.title);
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "PATHLOG_SEND") {
    const { text, url, title } = message.payload || {};
    sendToPathLog(text, url, title);
    sendResponse({ status: "queued" });
    return true;
  }
  return false;
});
