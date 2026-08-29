const gridEl = document.getElementById("grid");
const statusLine = document.getElementById("status-line");
const connDot = document.getElementById("conn-dot");
const connStatus = document.getElementById("conn-status");
const portSelect = document.getElementById("port-select");
const shaderList = document.getElementById("shader-list");
const fpsSlider = document.getElementById("fps-slider");
const fpsValue = document.getElementById("fps-value");

let width = 5;
let height = 7;
let cells = [];
let activeShader = null;

function buildGrid(w, h) {
  width = w;
  height = h;
  gridEl.innerHTML = "";
  gridEl.style.setProperty("--cols", w);
  gridEl.style.setProperty("--rows", h);
  cells = [];
  for (let y = 0; y < h; y++) {
    const row = [];
    for (let x = 0; x < w; x++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      const cx = x, cy = y;
      cell.onclick = () => {
        cell.classList.toggle("on");
        fetch("/api/toggle", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ x: cx, y: cy }),
        });
      };
      gridEl.appendChild(cell);
      row.push(cell);
    }
    cells.push(row);
  }
}

function renderGrid(grid) {
  for (let y = 0; y < grid.length; y++) {
    for (let x = 0; x < grid[y].length; x++) {
      cells[y][x].classList.toggle("on", !!grid[y][x]);
    }
  }
}

async function pollState() {
  try {
    const res = await fetch("/api/state");
    const data = await res.json();
    if (cells.length !== data.height || cells[0]?.length !== data.width) {
      buildGrid(data.width, data.height);
    }
    renderGrid(data.grid);
    connDot.classList.toggle("on", data.connected);
    connStatus.textContent = data.connected ? `${data.port} — ${data.last_status}` : "disconnected";

    const pb = data.playback;
    statusLine.textContent =
      pb.mode === "shader" ? `playing shader: ${pb.shader} @ ${pb.fps}fps`
      : pb.mode === "media" ? `playing media: ${pb.media} @ ${pb.fps}fps`
      : "idle";

    document.querySelectorAll("#shader-list button").forEach((btn) => {
      btn.classList.toggle("active", pb.mode === "shader" && btn.dataset.key === pb.shader);
    });
  } catch (err) {
    connStatus.textContent = "server unreachable";
  }
}

async function loadShaders() {
  const res = await fetch("/api/shaders");
  const list = await res.json();
  shaderList.innerHTML = "";
  for (const s of list) {
    const btn = document.createElement("button");
    btn.textContent = s.name;
    btn.dataset.key = s.key;
    btn.onclick = () => {
      fetch("/api/shader", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: s.key, fps: Number(fpsSlider.value) }),
      });
    };
    shaderList.appendChild(btn);
  }
}

async function loadPorts() {
  const res = await fetch("/api/ports");
  const list = await res.json();
  portSelect.innerHTML = "";
  for (const p of list) {
    const opt = document.createElement("option");
    opt.value = p.device;
    opt.textContent = `${p.device} — ${p.description}`;
    portSelect.appendChild(opt);
  }
}

document.getElementById("refresh-ports").onclick = loadPorts;

document.getElementById("connect-btn").onclick = async () => {
  const port = portSelect.value;
  if (!port) return;
  await fetch("/api/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ port, baud: 115200 }),
  });
};

document.getElementById("stop-btn").onclick = () => fetch("/api/stop", { method: "POST" });

function fill(value) {
  fetch("/api/fill", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
}
document.getElementById("fill-white").onclick = () => fill(true);
document.getElementById("fill-black").onclick = () => fill(false);

fpsSlider.oninput = () => {
  fpsValue.textContent = fpsSlider.value;
  fetch("/api/fps", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fps: Number(fpsSlider.value) }),
  });
};

document.getElementById("file-input").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const uploadStatus = document.getElementById("upload-status");
  uploadStatus.textContent = "converting...";
  const form = new FormData();
  form.append("file", file);
  try {
    const res = await fetch("/api/upload", { method: "POST", body: form });
    const data = await res.json();
    uploadStatus.textContent = data.ok
      ? `playing ${data.frames} frame(s) @ ${data.fps}fps`
      : `error: ${data.error}`;
  } catch (err) {
    uploadStatus.textContent = "upload failed";
  }
};

buildGrid(width, height);
loadShaders();
loadPorts();
setInterval(pollState, 200);
pollState();
