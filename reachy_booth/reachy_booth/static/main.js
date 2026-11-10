// Status page for Reachy Booth. The web server starts before the app's routes
// are registered, so requests made right after loading may 404: just retry.

const healthEl = document.getElementById("health");
const daemonEl = document.getElementById("daemon");
const moveResult = document.getElementById("move-result");
const preview = document.getElementById("preview");
const previewBtn = document.getElementById("preview-btn");

async function refreshHealth() {
    try {
        const resp = await fetch("/health");
        if (!resp.ok) {
            healthEl.textContent = `Not ready yet (HTTP ${resp.status})`;
            return;
        }
        const health = await resp.json();
        healthEl.textContent = JSON.stringify(health, null, 2);
        daemonEl.textContent = health.daemon.connected
            ? "Daemon: connected"
            : `Daemon: NOT connected (${health.daemon.error})`;
    } catch (err) {
        healthEl.textContent = `Unreachable: ${err}`;
    }
}

document.querySelectorAll("button[data-move]").forEach((btn) => {
    btn.addEventListener("click", async () => {
        const move = btn.dataset.move;
        moveResult.textContent = `${move}…`;
        try {
            const resp = await fetch(`/${move}`, { method: "POST" });
            const body = await resp.json();
            moveResult.textContent = resp.ok ? `${move}: done` : `${move}: ${body.detail}`;
        } catch (err) {
            moveResult.textContent = `${move}: ${err}`;
        }
    });
});

previewBtn.addEventListener("click", () => {
    if (preview.hidden) {
        preview.src = "/camera/stream?width=640&height=360&fps=10&quality=60";
        preview.hidden = false;
        previewBtn.textContent = "Hide preview";
    } else {
        preview.removeAttribute("src"); // closes the stream
        preview.hidden = true;
        previewBtn.textContent = "Show preview";
    }
});

refreshHealth();
setInterval(refreshHealth, 2000);

document.getElementById("reconnect-btn").addEventListener("click", async () => {
    await fetch("/reconnect", { method: "POST" });
    setTimeout(refreshHealth, 1500);
});
