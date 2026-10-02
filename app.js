const make = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

async function searchPage() {
  const form = document.querySelector("#search-form");
  if (!form) return;
  const results = document.querySelector("#search-results");
  const count = document.querySelector("#search-count");
  try {
    const response = await fetch("/content/search.json");
    if (!response.ok) throw new Error("index");
    const index = await response.json();
    const query = document.querySelector("#query");
    const scope = document.querySelector("#scope");
    const params = new URLSearchParams(location.search);
    query.value = params.get("q") || "";
    if (params.get("scope") === "all") scope.value = "all";
    const render = () => {
      const terms = query.value.trim().toLocaleLowerCase().split(/\s+/u).filter(Boolean);
      const found = index.filter(item =>
        (scope.value === "all" || item.site === scope.value || item.site === "shared") &&
        terms.every(term => [item.title, item.original, item.summary, ...item.tags].join(" ").toLocaleLowerCase().includes(term))
      );
      results.replaceChildren();
      count.textContent = found.length ? `找到 ${found.length} 条记录 · 基础条目跳转目录，详情样板跳转独立档案。` : "没有找到对应记录。可以换一个集名或主题，或选择两个专题。";
      for (const item of found) {
        const card = make("a", undefined, "route-card");
        card.href = item.url;
        card.append(make("p", `${item.site.toUpperCase()} / ${item.status}`, "label"), make("h3", item.title), make("p", item.original), make("p", item.summary));
        results.append(card);
      }
    };
    form.addEventListener("submit", event => {
      event.preventDefault();
      const params = new URLSearchParams({q: query.value.trim(), scope: scope.value});
      history.replaceState(null, "", `?${params}`);
      render();
    });
    scope.addEventListener("change", render);
    render();
  } catch {
    count.textContent = "搜索目录读取失败，请刷新后重试。";
  }
}

async function editorPage() {
  const form = document.querySelector("#editor-form");
  if (!form) return;
  const status = document.querySelector("#editor-status");
  const entrySelect = document.querySelector("#entry");
  const fieldSelect = document.querySelector("#field");
  const text = document.querySelector("#text");
  const preview = document.querySelector("#text-preview");
  const link = document.querySelector("#preview-link");
  let payload, original = "", dirty = false;
  const selectedEntry = () => payload.entries[Number(entrySelect.value)];
  const selectedField = () => selectedEntry().fields[Number(fieldSelect.value)];
  const readValue = path => path.reduce((current, part) => current[part], payload.content);
  const displayText = () => {
    preview.textContent = text.value;
    dirty = text.value !== original;
  };
  const loadField = () => {
    original = readValue(selectedField().path);
    text.value = original;
    displayText();
  };
  const loadEntry = () => {
    fieldSelect.replaceChildren();
    selectedEntry().fields.forEach((field, i) => {
      const option = make("option", field.label);
      option.value = String(i);
      fieldSelect.append(option);
    });
    link.href = selectedEntry().url;
    loadField();
  };
  const refresh = async () => {
    const response = await fetch("/api/editor", {cache:"no-store"});
    if (!response.ok) throw new Error("editor");
    payload = await response.json();
  };
  try {
    await refresh();
    payload.entries.forEach((entry, i) => {
      const option = make("option", entry.label);
      option.value = String(i);
      entrySelect.append(option);
    });
    loadEntry();
    status.textContent = "本地编辑已就绪。保存后重新打开页面即可看到持久化结果。";
    let selectedEntryValue = entrySelect.value, selectedFieldValue = fieldSelect.value;
    entrySelect.addEventListener("change", () => {
      if (dirty && !window.confirm("当前文字尚未保存。放弃修改并切换条目？")) {
        entrySelect.value = selectedEntryValue;
        return;
      }
      selectedEntryValue = entrySelect.value;
      loadEntry();
      selectedFieldValue = fieldSelect.value;
    });
    fieldSelect.addEventListener("change", () => {
      if (dirty && !window.confirm("当前文字尚未保存。放弃修改并切换字段？")) {
        fieldSelect.value = selectedFieldValue;
        return;
      }
      selectedFieldValue = fieldSelect.value;
      loadField();
    });
    text.addEventListener("input", displayText);
    document.querySelector("#reset-text").addEventListener("click", loadField);
    window.addEventListener("beforeunload", event => {if (dirty) {event.preventDefault(); event.returnValue = "";}});
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      status.textContent = "正在保存并更新页面…";
      try {
        const response = await fetch("/api/editor", {
          method:"POST", headers:{"Content-Type":"application/json","X-Editor-Token":payload.token},
          body:JSON.stringify({version:payload.version, path:selectedField().path, value:text.value})
        });
        const saved = await response.json();
        if (!response.ok) throw new Error(saved.error || "保存失败");
        await refresh();
        loadField();
        status.textContent = `已保存。自动备份：${saved.backup}。页面文案已更新，样式保持独立。`;
      } catch(error) {
        status.textContent = error.message;
      } finally {button.disabled = false;}
    });
  } catch {
    form.hidden = true;
    status.textContent = "文案编辑需要本地编辑服务；静态预览仍可阅读，不能在这里保存。";
  }
}

searchPage();
editorPage();
if (["localhost", "127.0.0.1"].includes(location.hostname)) {
  fetch("/api/editor", {cache:"no-store"}).then(response => {
    if (response.ok) document.querySelectorAll("[data-local-edit]").forEach(link => {link.hidden = false;});
  }).catch(() => {});
}

// The start screen is a real link: it also works without JavaScript.
const start = document.querySelector('.press-start');
if (start) document.addEventListener('keydown', event => {
  if (event.key === 'Enter' && event.target === document.body) start.click();
});
const tiles = [...document.querySelectorAll('.menu-tile')];
if (tiles.length) {
  const select = tile => {
    tiles.forEach(item => item.classList.toggle('selected', item === tile));
    document.querySelector('#menu-title').textContent = tile.dataset.title;
    document.querySelector('#menu-description').textContent = tile.dataset.description;
  };
  select(tiles[0]);
  tiles.forEach(tile => {
    tile.addEventListener('mouseenter', () => select(tile));
    tile.addEventListener('focus', () => select(tile));
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') { location.href = '/arkham/'; return; }
    const columns = matchMedia('(max-width:640px)').matches ? 2 : 3;
    const delta = {ArrowRight:1, ArrowLeft:-1, ArrowDown:columns, ArrowUp:-columns}[event.key];
    if (delta !== undefined) {
      event.preventDefault();
      const current = Math.max(0, tiles.findIndex(tile => tile.classList.contains('selected')));
      tiles[(current + delta + tiles.length) % tiles.length].focus();
    } else if (event.key === 'Enter' && event.target === document.body) {
      tiles.find(tile => tile.classList.contains('selected')).click();
    }
  });
}
