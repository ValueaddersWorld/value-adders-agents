const DEFAULT_SETTINGS = {
  baseUrl: "http://localhost:8002",
  userId: "",
  passphrase: "",
  toolName: "browser_extension",
};

const form = document.getElementById("settings-form");
const statusNode = document.getElementById("status");
const elements = {
  baseUrl: document.getElementById("baseUrl"),
  userId: document.getElementById("userId"),
  passphrase: document.getElementById("passphrase"),
  toolName: document.getElementById("toolName"),
};

function load() {
  chrome.storage.sync.get(DEFAULT_SETTINGS, (items) => {
    Object.entries({ ...DEFAULT_SETTINGS, ...items }).forEach(([key, value]) => {
      if (elements[key]) {
        elements[key].value = value || "";
      }
    });
  });
}

function save(event) {
  event.preventDefault();
  const payload = {
    baseUrl: elements.baseUrl.value.trim() || DEFAULT_SETTINGS.baseUrl,
    userId: elements.userId.value.trim(),
    passphrase: elements.passphrase.value.trim(),
    toolName: elements.toolName.value.trim() || DEFAULT_SETTINGS.toolName,
  };
  chrome.storage.sync.set(payload, () => {
    statusNode.textContent = "Settings saved.";
    setTimeout(() => (statusNode.textContent = ""), 2000);
  });
}

function reset() {
  chrome.storage.sync.set(DEFAULT_SETTINGS, () => {
    load();
    statusNode.textContent = "Defaults restored.";
    setTimeout(() => (statusNode.textContent = ""), 2000);
  });
}

form.addEventListener("submit", save);
document.getElementById("resetButton").addEventListener("click", reset);

load();
