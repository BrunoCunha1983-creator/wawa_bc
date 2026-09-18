const crypto = require("crypto");
const fs = require("fs");
const { spawn } = require("child_process");

const OPTIONS_FILE = "/data/options.json";

function readOptions() {
  try {
    return JSON.parse(fs.readFileSync(OPTIONS_FILE, "utf8"));
  } catch (error) {
    console.error("[WAHA BC] Não foi possível ler /data/options.json:", error.message);
    process.exit(78);
  }
}

function requireSecret(value, placeholder, name) {
  if (!value || value === placeholder || value.startsWith("CHANGE_ME")) {
    console.error(`[WAHA BC] Configura "${name}" com um valor forte antes de iniciar o add-on.`);
    process.exit(78);
  }
}

function ensurePersistentLink(linkPath, targetPath) {
  fs.mkdirSync(targetPath, { recursive: true });

  try {
    const stat = fs.lstatSync(linkPath);
    if (stat.isSymbolicLink() && fs.readlinkSync(linkPath) === targetPath) {
      return;
    }
    fs.rmSync(linkPath, { recursive: true, force: true });
  } catch (error) {
    if (error.code !== "ENOENT") {
      throw error;
    }
  }

  fs.symlinkSync(targetPath, linkPath, "dir");
}

const options = readOptions();

requireSecret(options.api_key, "CHANGE_ME_API_KEY", "api_key");
requireSecret(options.password, "CHANGE_ME_PASSWORD", "password");

ensurePersistentLink("/app/.sessions", "/data/sessions");
ensurePersistentLink("/app/.media", "/data/media");

const apiHash = crypto.createHash("sha512").update(options.api_key).digest("hex");

process.env.WAHA_API_KEY = `sha512:${apiHash}`;
process.env.WAHA_DASHBOARD_USERNAME = options.username || "admin";
process.env.WAHA_DASHBOARD_PASSWORD = options.password;
process.env.WHATSAPP_SWAGGER_USERNAME = options.username || "admin";
process.env.WHATSAPP_SWAGGER_PASSWORD = options.password;
process.env.WAHA_DASHBOARD_ENABLED = "True";
process.env.WHATSAPP_SWAGGER_ENABLED = "True";
process.env.WHATSAPP_DEFAULT_ENGINE = options.engine || "GOWS";
process.env.WAHA_NAMESPACE = "all";
process.env.WAHA_CLIENT_DEVICE_NAME = options.client_device_name || "Home Assistant WAHA BC";
process.env.TZ = options.timezone || "Europe/Lisbon";
process.env.WAHA_MEDIA_STORAGE = "LOCAL";

if (options.auto_start_session && options.session) {
  process.env.WHATSAPP_START_SESSION = options.session;
}

if (options.webhook_url) {
  process.env.WHATSAPP_HOOK_URL = options.webhook_url;
  process.env.WHATSAPP_HOOK_EVENTS =
    options.webhook_events || "session.status,message,message.reaction";
}

console.log("[WAHA BC] A iniciar WAHA");
console.log(`[WAHA BC] Engine: ${process.env.WHATSAPP_DEFAULT_ENGINE}`);
console.log(`[WAHA BC] Sessão persistente: ${options.session || "default"}`);
console.log("[WAHA BC] Dashboard: porta 3000 /dashboard");
console.log("[WAHA BC] API protegida por X-Api-Key");

const child = spawn("/entrypoint.sh", [], {
  stdio: "inherit",
  env: process.env,
});

for (const signal of ["SIGTERM", "SIGINT"]) {
  process.on(signal, () => {
    if (!child.killed) {
      child.kill(signal);
    }
  });
}

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});
