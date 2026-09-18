# WAHA BC - Home Assistant App + Integration

Repositório do **WAHA BC**, uma ligação local entre Home Assistant e WhatsApp através do WAHA, sem Twilio.

## Instalação

Adiciona este repositório à Loja de Apps do Home Assistant:

```text
https://github.com/BrunoCunha1983-creator/wawa_bc
```

Instala **WAHA BC**, configura a API key/password e associa o WhatsApp por QR Code.

A partir da versão **0.2.0**, o próprio add-on instala também uma integração nativa do Home Assistant em `custom_components/wawa_bc`.

Depois de iniciar/atualizar o add-on:

1. Reinicia o Home Assistant.
2. Abre **Definições → Dispositivos e Serviços**.
3. Adiciona **WAHA BC**.
4. Usa a mesma API key do add-on.
5. Seleciona a sessão `default` e define o número WhatsApp padrão.

## Funcionalidades 0.2.0

- WAHA local / QR Code
- GOWS
- amd64 + aarch64
- sessões persistentes
- `notify.whatsapp_bc`
- `wawa_bc.send_message`
- sensor de estado da sessão
- Start / Restart / Stop
- mensagens recebidas por webhook
- eventos Home Assistant para automações
- suporte a números e grupos

## Segurança

Não exponhas a porta 3000 diretamente à Internet. O webhook automático entre WAHA e Home Assistant é protegido por um segredo derivado da API key.
