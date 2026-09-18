# Changelog

## 0.1.4

- Mantém `WAHA_API_KEY` em SHA-512.
- Disponibiliza também `WAHA_API_KEY_PLAIN` apenas dentro do contentor para componentes internos do WAHA.
- Facilita a autenticação do Dashboard/Apps sem expor a chave no log.
- Mantém toda a configuração existente do utilizador.

## 0.1.3

- Corrige o crash que continuava a ocorrer em `@wppconnect-team/wppconnect/node_modules/sharp`.
- Remove a cópia aninhada de `sharp` do WPPConnect durante o build.
- Faz o WPPConnect reutilizar o `sharp` principal do WAHA.
- Mantém GOWS como única engine do add-on.
- Adiciona diagnóstico da versão/resolução de `sharp` ao log de arranque.

## 0.1.2

- Mantém a opção `engine: GOWS` para compatibilidade com instalações 0.1.0.
- A engine continua fixa em GOWS.
- Evita falhas de validação do Supervisor durante o upgrade.

## 0.1.1

- Troca as imagens genéricas pelas imagens GOWS dedicadas.
- Usa WAHA 2026.8.2 fixo para evitar regressões provocadas por `latest`.
- amd64 usa `gows-2026.8.2`.
- aarch64 usa `gows-arm-2026.8.2`.

## 0.1.0

- Primeira versão.
- WAHA como add-on do Home Assistant.
- Suporte amd64 e aarch64.
- Persistência de sessões e media em `/data`.
- Configuração de API key, Dashboard, engine, sessão e webhooks.
- API key armazenada no processo WAHA em formato SHA-512.
