# WAHA BC

WAHA BC executa o WAHA dentro do Home Assistant e disponibiliza o WhatsApp através de uma API REST local.

## 1. Configuração inicial

Antes de iniciar o add-on, altera obrigatoriamente:

- `api_key`: chave longa e aleatória usada pelo Home Assistant para aceder à API.
- `password`: palavra-passe do Dashboard e Swagger.
- `username`: por omissão é `admin`.

O add-on recusa arrancar enquanto os valores `CHANGE_ME_...` estiverem definidos.

### Engine

- `GOWS`: predefinido, leve e recomendado para começar.
- `NOWEB`: sem Chromium.
- `WEBJS`: usa Chromium e consome mais memória.

## 2. Associar o WhatsApp

1. Inicia o add-on.
2. Abre **Interface Web**.
3. Entra com o utilizador e palavra-passe configurados.
4. Introduz a `api_key` quando o Dashboard a pedir.
5. Cria/inicia a sessão `default`.
6. Abre o QR Code.
7. No telemóvel: **WhatsApp → Dispositivos associados → Associar dispositivo**.
8. Lê o QR Code.

As credenciais de sessão ficam guardadas em `/data/sessions` e sobrevivem a reinícios/updates do add-on.

Depois da primeira associação podes ativar `auto_start_session: true`.

## 3. Enviar mensagens a partir do Home Assistant

O endpoint WAHA é:

`POST http://IP_DO_HOME_ASSISTANT:3000/api/sendText`

Cabeçalho obrigatório:

`X-Api-Key: A_TUA_API_KEY`

Exemplo de `rest_command` no Home Assistant:

```yaml
rest_command:
  whatsapp_send:
    url: "http://IP_DO_HOME_ASSISTANT:3000/api/sendText"
    method: POST
    headers:
      X-Api-Key: !secret waha_api_key
      Content-Type: "application/json"
    payload: >-
      {
        "session": "default",
        "chatId": "{{ phone }}@c.us",
        "text": {{ message | to_json }}
      }
```

No `secrets.yaml`:

```yaml
waha_api_key: "A_MESMA_CHAVE_DO_ADDON"
```

Exemplo de utilização:

```yaml
action: rest_command.whatsapp_send
data:
  phone: "351912345678"
  message: "Teste enviado diretamente pelo Home Assistant."
```

## 4. Webhooks / mensagens recebidas

Para receber eventos do WhatsApp podes preencher:

- `webhook_url`
- `webhook_events`

O valor inicial de eventos é:

`session.status,message,message.reaction`

Numa próxima versão podemos ligar isto diretamente a um webhook do Home Assistant e criar comandos bidirecionais.

## Segurança

- Não abras a porta 3000 no router para a Internet.
- Usa uma API key longa.
- Usa uma palavra-passe forte.
- Para acesso remoto, prefere VPN/Tailscale.
