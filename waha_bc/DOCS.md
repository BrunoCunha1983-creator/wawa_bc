# WAHA BC 0.2.0

WAHA BC executa o WAHA dentro do Home Assistant e, a partir da versão 0.2.0, instala também uma integração nativa em `custom_components/wawa_bc`.

## 1. Atualizar o add-on

Atualiza o **WAHA BC** pela Loja de Apps e inicia a versão **0.2.0**.

A opção:

```yaml
install_integration: true
```

faz o add-on instalar/atualizar automaticamente a integração em:

```text
/config/custom_components/wawa_bc
```

(O caminho dentro do contentor do add-on é `/homeassistant/custom_components/wawa_bc`.)

Depois de atualizar/iniciar o add-on, **reinicia o Home Assistant** para carregar a integração.

## 2. Adicionar a integração pela interface

Vai a:

**Definições → Dispositivos e Serviços → Adicionar integração → WAHA BC**

Preenche:

- **URL do WAHA**: normalmente `http://IP_DO_HOME_ASSISTANT:3000`
- **Chave da API**: a mesma `api_key` configurada no add-on
- **Sessão**: normalmente `default`
- **Destinatário padrão**: número internacional, por exemplo `351912345678`
- **Verificar SSL**: desligado para HTTP local

A integração testa imediatamente a ligação e confirma se a sessão existe.

## 3. Entidades criadas

A integração cria:

- `notify.whatsapp_bc`
- sensor de estado da sessão
- botão **Start session**
- botão **Restart session**
- botão **Stop session**

O sensor é atualizado por polling e também imediatamente quando chega um webhook `session.status`.

## 4. Enviar mensagens

### Compatibilidade simples

```yaml
action: notify.whatsapp_bc
data:
  message: "🚨 Porta da entrada aberta"
```

Usa o destinatário padrão configurado.

Também podes indicar outro número:

```yaml
action: notify.whatsapp_bc
data:
  target:
    - "351912345678"
  message: "Teste WAHA BC"
```

### Serviço nativo WAHA BC

```yaml
action: wawa_bc.send_message
data:
  target: "351912345678"
  title: "Home Assistant"
  message: "Internet recuperada."
```

Também podes usar a entidade de notificação moderna através de `notify.send_message`.

## 5. Grupos

Para enviar para um grupo, usa diretamente o chat ID WAHA:

```text
1203630XXXXXXXX@g.us
```

Números normais podem ser escritos apenas com algarismos; a integração acrescenta automaticamente `@c.us`.

## 6. Receber mensagens no Home Assistant

Se `webhook_url` ficar vazio no add-on, a versão 0.2.0 usa automaticamente:

```text
http://homeassistant:8123/api/webhook/wawa_bc
```

O webhook é protegido por um segredo SHA-256 derivado da tua API key e enviado no cabeçalho `X-WAHA-BC-Webhook`.

Eventos criados no Home Assistant:

- `wawa_bc_message_received`
- `wawa_bc_session_status`
- `wawa_bc_reaction_received`
- `wawa_bc_message_sent`

Exemplo de automação para uma mensagem recebida:

```yaml
alias: WhatsApp - receber comando
triggers:
  - trigger: event
    event_type: wawa_bc_message_received

conditions:
  - condition: template
    value_template: >
      {{ trigger.event.data.body | lower == 'estado casa' }}

actions:
  - action: notify.whatsapp_bc
    data:
      target:
        - "{{ trigger.event.data.from }}"
      message: >
        🏠 Home Assistant está online.
```

## 7. Segurança

- Não abras a porta 3000 no router para a Internet.
- Usa uma API key longa.
- Usa uma palavra-passe forte.
- O webhook interno não envia a API key em claro; usa um hash SHA-256 derivado dela.
- Para acesso remoto, prefere VPN/Tailscale.

## 8. Engine

A versão 0.2.0 mantém **GOWS** e as imagens WAHA dedicadas 2026.8.2:

- amd64: `devlikeapro/waha:gows-2026.8.2`
- aarch64: `devlikeapro/waha:gows-arm-2026.8.2`

Mantém também o workaround do `sharp` que resolveu o arranque no teu Home Assistant.
