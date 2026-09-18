# Changelog

## 0.1.2

- Mantém a opção `engine: GOWS` para compatibilidade com instalações 0.1.0.
- A engine continua fixa em GOWS.
- Evita falhas de validação do Supervisor durante o upgrade.

## 0.1.1

- Corrige crash no arranque em `sharp` / WPPConnect.
- Troca as imagens genéricas pelas imagens GOWS dedicadas.
- Usa WAHA 2026.8.2 fixo para evitar regressões provocadas por `latest`.
- amd64 usa `gows-2026.8.2`.
- aarch64 usa `gows-arm-2026.8.2`.
- Remove execução de engines incompatíveis com a imagem do add-on.

## 0.1.0

- Primeira versão.
- WAHA como add-on do Home Assistant.
- Suporte amd64 e aarch64.
- Persistência de sessões e media em `/data`.
- Configuração de API key, Dashboard, engine, sessão e webhooks.
- API key armazenada no processo WAHA em formato SHA-512.
