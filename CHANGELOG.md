# Changelog

## 1.4.25 - 2026-09-02

- Alterado o nome comercial exibido para `Diálogo Diário de Segurança`.
- Mantido o identificador técnico `hrms_dds_br` para preservar compatibilidade.

## 1.4.24 - 2026-09-02

- System Manager e Administrator podem excluir DDS (inclusive enviado/cancelado) sem informar motivo.

## 1.4.23 - 2026-09-02

- Adicionada notificação aos participantes no envio do DDS.
- System Manager/Administrador podem cancelar o DDS sem informar motivo.
- Demais responsáveis cancelam informando motivo via caixa de texto.

## 1.4.22 - 2026-09-02

- Removida a obrigatoriedade de assinatura dos participantes no envio. A assinatura do responsável continua obrigatória.

## 1.4.21 - 2026-09-02

- Corrigido o erro de metadados da assinatura no envio: quando a assinatura não muda, os metadados são mantidos do banco (ignora reenvio do formulário).

## 1.4.20 - 2026-09-02

- Corrigida a validação dos metadados da assinatura do responsável no envio (primeiro registro).

## 1.4.19 - 2026-09-02

- Corrigida a permissão de criação para papéis privilegiados (o hook `has_permission` retornava `None`, que era tratado como bloqueio).

## 1.4.18 - 2026-09-02

- Removido o workspace `DDS`. O acesso ao DocType `DDS` é feito pela lista `/app/dds`.
- Rota do app screen atualizada para `Segurança do Trabalho`.

## 1.4.17 - 2026-09-02

- Corrigida a renderização dos gráficos/cards no workspace (blocos no content).
- `/desk/dds` redireciona para a lista do DocType DDS (`/app/dds`).

## 1.4.16 - 2026-09-02

- Corrigida a ordem de criação dos gráficos/cards antes da sincronização dos workspaces.

## 1.4.15 - 2026-09-02

- Ampliado o dashboard de DDS com gráficos por Tema, Projeto e Situação e card `DDS Rascunho`.

## 1.4.14 - 2026-09-02

- Preenchido o workspace `DDS` com atalhos, number cards e gráfico (não exibe mais "Bem-vindo").

## 1.4.13 - 2026-09-02

- Corrigido o intervalo de tempo do gráfico `DDS por Mês`.

## 1.4.12 - 2026-09-02

- Corrigido o tipo dos Number Cards para `Document Type`.

## 1.4.11 - 2026-09-02

- Adicionado o papel `Responsavel DDS` com permissão de criação no DocType `DDS`.
- Adicionados gráficos (Total DDS, DDS Enviados, DDS Cancelados e DDS por Mês) ao workspace `Segurança do Trabalho`.
- Ajustado `DDS Tema` para que apenas administradores criem temas; colaboradores têm leitura.

## 1.4.10 - 2026-09-02

- Corrigido o atalho `DDS` em branco no workspace `Segurança do Trabalho`.

## 1.4.9 - 2026-09-02

- Adicionados atalhos de `DDS`, `DDS Tema`, `Employee DDS History` e `DDS Dashboard` ao workspace e à sidebar `Segurança do Trabalho`.

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
