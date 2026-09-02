# Changelog

## 1.4.8 - 2026-09-02

- Corrigida a serialização do conteúdo do workspace durante a sincronização dos links.

## 1.4.7 - 2026-09-02

- Tratada a normalização de conteúdo inválido do workspace antes da sincronização dos links.

## 1.4.6 - 2026-09-02

- Normalizado o conteúdo do workspace antes de sincronizar links no Frappe v16.

## 1.4.5 - 2026-09-02

- Corrigidos os destinos dos links do workspace `DDS` no Frappe v16.
- Removidos links antigos sem destino durante a sincronização pós-migração.

## 1.4.4 - 2026-09-02

- Corrigidos os destinos dos links do workspace `DDS` para Frappe v16.

## 1.4.3 - 2026-09-02

- Criado o workspace `DDS` na rota `/desk/dds`.
- Adicionados atalhos para `DDS`, `DDS Tema`, `Employee DDS History` e `DDS Dashboard`.

## 1.4.2 - 2026-09-02

- Preparados metadados e documentação para publicação no Frappe Marketplace.
- Adicionado CI para validar metadados, Python, JSON e whitespace.
- Restringida a injeção do asset da página HRMS às rotas `/hrms` e `/hrms/home`.

## 1.4.1 - 2026-09-02

- Corrigido o acesso ao relatório `Employee DDS History` para `Employee Self Service`.
- Mantido o isolamento server-side por participante e responsável.

## 1.4.0 - 2026-09-02

- Criado o cadastro dinâmico `DDS Tema`.
- Convertido o campo `Tema` do DDS para um link com filtro de temas ativos.
- Adicionada carga inicial dos temas de SST.

## 1.3.8 - 2026-09-02

- Removido o campo duplicado `Cliente` do DDS.
- Cliente e empresa passam a ser derivados do `Project`.

## 1.3.7 - 2026-09-02

- Seção de correção exibida somente quando habilitada.
- Seção de cancelamento exibida somente no estado `Cancelado`.

## 1.3.0 - 2026-09-02

- Adicionadas regras de imutabilidade após envio.
- Criado o painel `DDS Dashboard` com indicadores e alerta de recência por projeto.
- Reduzida a exposição de metadados técnicos de assinatura no PDF operacional.

## 1.2.0 - 2026-09-02

- Adicionado o link de histórico de DDS à tela de autoatendimento `/hrms/home`.
- Integração com o formulário `Employee`.

## 1.0.0 - 2026-09-02

- Primeira versão funcional do app HRMS DDS BR.
