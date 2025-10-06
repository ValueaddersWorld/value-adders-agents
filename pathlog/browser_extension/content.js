const HOTKEY = {
  alt: true,
  shift: true,
  code: "KeyL",
};

function matchesHotkey(event) {
  return event.altKey === HOTKEY.alt && event.shiftKey === HOTKEY.shift && event.code === HOTKEY.code;
}

document.addEventListener("keydown", (event) => {
  if (!matchesHotkey(event)) {
    return;
  }
  const selection = window.getSelection()?.toString().trim();
  if (!selection) {
    return;
  }
  chrome.runtime.sendMessage({
    type: "PATHLOG_SEND",
    payload: {
      text: selection,
      url: window.location.href,
      title: document.title,
    },
  });
});
