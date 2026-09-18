# WAHA BC - Home Assistant Add-on Repository

Repositório de add-ons para Home Assistant.

## WAHA BC

WAHA BC empacota o [WAHA - WhatsApp HTTP API](https://github.com/devlikeapro/waha) como add-on do Home Assistant.

### Instalação

1. No Home Assistant abre **Definições → Apps → Loja de Apps**.
2. Abre o menu de repositórios.
3. Adiciona:
   `https://github.com/BrunoCunha1983-creator/wawa_bc`
4. Atualiza a loja.
5. Instala **WAHA BC**.
6. Antes de iniciar, define uma API key e uma palavra-passe fortes na configuração do add-on.
7. Abre a interface Web do add-on, cria/inicia a sessão `default` e lê o QR Code com **WhatsApp → Dispositivos associados**.

## Segurança

Não exponhas a porta 3000 diretamente à Internet. Usa a API key e mantém o acesso limitado à LAN/VPN.

## Plataformas

- amd64
- aarch64

O add-on seleciona automaticamente a imagem WAHA adequada à arquitetura do Home Assistant.
