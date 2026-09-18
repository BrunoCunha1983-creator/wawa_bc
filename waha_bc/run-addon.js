const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const OPTIONS_FILE = "/data/options.json";
const INTEGRATION_SOURCE = "/opt/wawa_bc/integration/wawa_bc";
const HA_CUSTOM_COMPONENTS = "/homeassistant/custom_components";
const INTEGRATION_TARGET = path.join(HA_CUSTOM_COMPONENTS, "wawa_bc");
const DEFAULT_HA_WEBHOOK =
  "http://homeassistant:8123/api/webhook/wawa_bc";

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

function installHomeAssistantIntegration(options) {
  if (options.install_integration === false) {
    console.log("[WAHA BC] Instalação automática da integração HA desativada");
    return;
  }

  try {
    if (!fs.existsSync("/homeassistant")) {
      console.warn(
        "[WAHA BC] /homeassistant não está montado. " +
          "A integração nativa não foi instalada."
      );
      return;
    }

    fs.mkdirSync(HA_CUSTOM_COMPONENTS, { recursive: true });
    fs.rmSync(INTEGRATION_TARGET, { recursive: true, force: true });
    fs.cpSync(INTEGRATION_SOURCE, INTEGRATION_TARGET, { recursive: true });

    console.log(
      "[WAHA BC] Integração Home Assistant 0.2.0 instalada/atualizada em " +
        INTEGRATION_TARGET
    );
    console.log(
      "[WAHA BC] Reinicia o Home Assistant para carregar/atualizar a integração."
    );
  } catch (error) {
    console.error(
      "[WAHA BC] Falha ao instalar a integração Home Assistant:",
      error.message
    );
  }
}

function sharpDiagnostics() {
  try {
    const pkg = JSON.parse(
      fs.readFileSync("/app/node_modules/sharp/package.json", "utf8")
    );
    console.log(`[WAHA BC] sharp principal: ${pkg.version}`);
  } catch (error) {
    console.warn(
      "[WAHA BC] Não foi possível obter a versão do sharp principal:",
      error.message
    );
  }

  const nested =
    "/app/node_modules/@wppconnect-team/wppconnect/node_modules/sharp";

  try {
    const stat = fs.lstatSync(nested);
    if (stat.isSymbolicLink()) {
      console.log(`[WAHA BC] sharp WPPConnect -> ${fs.readlinkSync(nested)}`);
    } else {
      console.warn(
        "[WAHA BC] sharp WPPConnect continua como diretório próprio"
      );
    }
  } catch (error) {
    console.warn(
      "[WAHA BC] sharp WPPConnect não encontrado:",
      error.message
    );
  }
}

const options = readOptions();

installHomeAssistantIntegration(options);

requireSecret(options.api_key, "CHANGE_ME_API_KEY", "api_key");
requireSecret(options.password, "CHANGE_ME_PASSWORD", "password");

ensurePersistentLink("/app/.sessions", "/data/sessions");
ensurePersistentLink("/app/.media", "/data/media");

const apiHash = crypto
  .createHash("sha512")
  .update(options.api_key)
  .digest("hex");

const webhookSecret = crypto
  .createHash("sha256")
  .update(options.api_key)
  .digest("hex");

process.env.WAHA_API_KEY = `sha512:${apiHash}`;
process.env.WAHA_API_KEY_PLAIN = options.api_key;
process.env.WAHA_DASHBOARD_USERNAME = options.username || "admin";
process.env.WAHA_DASHBOARD_PASSWORD = options.password;
process.env.WHATSAPP_SWAGGER_USERNAME = options.username || "admin";
process.env.WHATSAPP_SWAGGER_PASSWORD = options.password;
process.env.WAHA_DASHBOARD_ENABLED = "True";
process.env.WHATSAPP_SWAGGER_ENABLED = "True";
process.env.WHATSAPP_DEFAULT_ENGINE = "GOWS";
process.env.WAHA_NAMESPACE = "all";
process.env.WAHA_CLIENT_DEVICE_NAME =
  options.client_device_name || "Home Assistant WAHA BC";
process.env.TZ = options.timezone || "Europe/Lisbon";
process.env.WAHA_MEDIA_STORAGE = "LOCAL";

if (options.auto_start_session && options.session) {
  process.env.WHATSAPP_START_SESSION = options.session;
}

const webhookUrl = options.webhook_url || DEFAULT_HA_WEBHOOK;
process.env.WHATSAPP_HOOK_URL = webhookUrl;
process.env.WHATSAPP_HOOK_EVENTS =
  options.webhook_events ||
  "session.status,message,message.reaction";
process.env.WHATSAPP_HOOK_CUSTOM_HEADERS =
  `X-WAHA-BC-Webhook:${webhookSecret}`;

console.log("[WAHA BC] A iniciar WAHA BC 0.2.0");
console.log("[WAHA BC] Engine: GOWS (imagem dedicada)");
console.log(`[WAHA BC] Sessão persistente: ${options.session || "default"}`);
console.log("[WAHA BC] Dashboard: porta 3000 /dashboard");
console.log("[WAHA BC] API protegida por X-Api-Key");
console.log("[WAHA BC] Webhook: " + webhookUrl);
console.log(
  "[WAHA BC] Webhook protegido por hash SHA-256 derivado da API key"
);
sharpDiagnostics();

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
