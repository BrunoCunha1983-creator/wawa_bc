"""Constants for WAHA BC."""

DOMAIN = "wawa_bc"

CONF_API_KEY = "api_key"
CONF_SESSION = "session"
CONF_RECIPIENT = "recipient"
CONF_VERIFY_SSL = "verify_ssl"

DEFAULT_SESSION = "default"
DEFAULT_VERIFY_SSL = False
DEFAULT_PORT = 3000
DEFAULT_WEBHOOK_ID = "wawa_bc"

SERVICE_SEND_MESSAGE = "send_message"
NOTIFY_SERVICE = "whatsapp_bc"

EVENT_MESSAGE_RECEIVED = "wawa_bc_message_received"
EVENT_SESSION_STATUS = "wawa_bc_session_status"
EVENT_REACTION_RECEIVED = "wawa_bc_reaction_received"
EVENT_MESSAGE_SENT = "wawa_bc_message_sent"

WEBHOOK_HEADER = "X-WAHA-BC-Webhook"
