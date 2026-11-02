"""Edit the manual in the browser: click any text, change it, Save.

Run: python3 edit.py   then open http://localhost:8790 (the light edition; ?v=dark for the dark one).

Save writes each change into the source (build.py, hilt.py), so it lasts through every rebuild and shows in
every edition, then rebuilds the three PDFs and copies the light ones into ../site. A change the source can't
place on its own (the text appears more than once, or the edit touches a page number filled in by the build)
goes to edits_pending.json for a manual fix. Publish uploads ../site to the live page.
"""
import html
import json
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
SOURCES = [HERE / "build.py", HERE / "hilt.py"]
PENDING = HERE / "edits_pending.json"
PORT = 8790

EDITOR = """
<style>
  .page [contenteditable] { outline: none; cursor: text }
  .page [contenteditable]:hover, .page svg text:hover { background: rgba(68,176,61,.12) }
  .page [contenteditable]:focus { background: rgba(68,176,61,.18) }
  .page svg text { cursor: pointer }
  .edited { box-shadow: inset 0 -2px #44B03D }
  #bar { position: fixed; top: 12px; right: 12px; z-index: 9; display: flex; gap: 8px; align-items: center;
         font: 500 14px Poppins, sans-serif; background: #fff; color: #111; padding: 8px; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,.25) }
  #bar button { font: inherit; min-height: 40px; padding: 0 16px; border-radius: 8px; border: 1.5px solid #111; background: #fff; color: #111; cursor: pointer }
  #bar button.go { background: #111; color: #fff }
  #bar button:disabled { opacity: .45; cursor: default }
  #msg { max-width: 360px }
  @media print { #bar { display: none } }
</style>
<div id="bar"><span id="msg">Click any text to change it</span>
  <button id="save" class="go" disabled>Save</button><button id="pub">Publish online</button></div>
<script>
addEventListener("load", () => setTimeout(() => {
  const orig = new Map(), msg = document.getElementById("msg"), save = document.getElementById("save");
  const skip = el => el.closest(".toc, .pn, #bar, script, style, defs, symbol");
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = walk.nextNode());) if (n.nodeValue.trim() && !skip(n.parentElement)) orig.set(n, n.nodeValue);
  const changed = () => [...orig].filter(([n, t]) => n.nodeValue !== t);
  const mark = () => { const c = changed().length; save.disabled = !c; msg.textContent = c ? `${c} unsaved change${c > 1 ? "s" : ""}` : "Click any text to change it" };
  // HTML text: edit in place. Every element that holds text directly (a bare description after a bold
  // name, a table cell, a heading), so any visible text can be clicked.
  new Set([...orig.keys()].map(n => n.parentElement)).forEach(el => { if (el.closest("svg")) return; el.contentEditable = "plaintext-only";
      el.addEventListener("keydown", e => { if (e.key === "Enter") e.preventDefault() });
      el.addEventListener("input", () => { el.classList.add("edited"); mark() }) });
  // Text inside drawings: click to edit in a box.
  document.querySelectorAll(".page svg text, .page svg tspan").forEach(el => el.addEventListener("click", e => {
    e.stopPropagation();
    const node = [...el.childNodes].find(n => n.nodeType === 3 && orig.has(n)); if (!node) return;
    const t = prompt("Change this label:", node.nodeValue); if (t === null) return;
    node.nodeValue = t; el.classList.add("edited"); mark() }));
  document.addEventListener("click", e => { const a = e.target.closest(".page a"); if (a) e.preventDefault() }, true);
  save.onclick = async () => {
    const edits = changed().map(([n, t]) => ({ old: t, new: n.nodeValue }));
    save.disabled = true; msg.textContent = "Saving and rebuilding the PDFs, about a minute…";
    const r = await (await fetch("/save", { method: "POST", body: JSON.stringify(edits) })).json();
    if (r.error) { msg.textContent = "Rebuild failed: " + r.error; return }
    msg.textContent = r.pending.length ? `Saved ${r.applied}. ${r.pending.length} need Claude (kept in edits_pending.json).` : `Saved ${r.applied}. Reloading…`;
    if (!r.pending.length) setTimeout(() => location.reload(), 800);
  };
  document.getElementById("pub").onclick = async () => {
    if (!confirm("Upload the current light PDFs to the live page?")) return;
    msg.textContent = "Publishing…";
    const r = await (await fetch("/publish", { method: "POST" })).json();
    msg.textContent = r.ok ? "Published to lightsaber-proffie-quinlan-vos-manual.pages.dev" : "Publish failed: " + r.error;
  };
}, 300));
</script>
"""


def place(old, new, files):
    """Write one text change into the source. The changed span grows by context until it occurs exactly once
    in the sources, raw or HTML-escaped. Returns the file it went into, or None."""
    p = 0
    while p < min(len(old), len(new)) and old[p] == new[p]:
        p += 1
    s = 0
    while s < min(len(old), len(new)) - p and old[-1 - s] == new[-1 - s]:
        s += 1
    a, b = p, len(old) - s  # changed span in old
    na, nb = p, len(new) - s
    if a == b and a > 0:  # pure insertion: anchor on a character before it
        a, na = a - 1, na - 1
    if a == b:
        b, nb = b + 1, nb + 1
    # context grows on each side separately (up to 60 characters), smallest total first: the build adds text the
    # source doesn't have (a closing period, a page number), so one side may have to stay short
    for g in range(0, 121):
        for left in range(max(0, g - 60), min(g, 60) + 1):
            lo, hi = a - left, b + g - left
            if lo < 0 or hi > len(old):
                continue
            window, repl = old[lo:hi], new[na - left:len(new) - (len(old) - hi)]
            tries = [(window, repl), (html.escape(window, quote=False), html.escape(repl, quote=False))]
            if lo == 0 and hi == len(old):  # the whole text of an element: its tags make a short label unique
                tries.append((f">{window}<", f">{repl}<"))
            for w, r in tries:
                hits = [(f, t.count(w)) for f, t in files.items() if w in t]
                if sum(c for _, c in hits) == 1:
                    f = hits[0][0]
                    files[f] = files[f].replace(w, r, 1)
                    return f
    return None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def log_message(self, *a):
        pass

    def reply(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/":
            page = "manual.html" if "v=dark" in self.path else "manual_light.html"
            text = (HERE / page).read_text().replace("</body>", EDITOR + "</body>")
            body = text.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/publish":
            r = subprocess.run(["npx", "--yes", "wrangler", "pages", "deploy", "site", "--project-name", "lightsaber-proffie-quinlan-vos-manual",
                                "--branch", "main", "--commit-message", "Quinlan Vos manual", "--commit-dirty=true"],
                               cwd=HERE.parent, capture_output=True, text=True)
            return self.reply({"ok": r.returncode == 0, "error": r.stderr[-400:]})
        edits = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        files = {f: f.read_text() for f in SOURCES}
        pending = [e for e in edits if not place(e["old"], e["new"], files)]
        for f, t in files.items():
            if t != f.read_text():
                f.write_text(t)
        if pending:
            PENDING.write_text(json.dumps(json.loads(PENDING.read_text()) + pending if PENDING.exists() else pending, indent=1, ensure_ascii=False))
        r = subprocess.run([sys.executable, "build.py"], cwd=HERE, capture_output=True, text=True)
        if r.returncode:
            return self.reply({"error": r.stderr[-400:]})
        site = HERE.parent / "site"
        (site / "quinlan-vos-manual-a5.pdf").write_bytes((HERE / "Quinlan_Vos_Proffie_Manual_Light_A5.pdf").read_bytes())
        (site / "quinlan-vos-manual-booklet-a4.pdf").write_bytes((HERE / "Quinlan_Vos_Proffie_Manual_Light_A4_Booklet.pdf").read_bytes())
        self.reply({"applied": len(edits) - len(pending), "pending": pending})


if __name__ == "__main__":
    print(f"Editor at http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
