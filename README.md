# HRMS DDS BR

Aplicativo Frappe/ERPNext para registro, assinatura e acompanhamento de Diálogos Diários de Segurança (DDS), integrado ao HRMS.

## Visão geral

O HRMS DDS BR registra a realização do DDS, os riscos abordados, as medidas preventivas, os participantes, a presença e as assinaturas coletadas. A solução foi desenhada para uso em obras, projetos e operações com empregados cadastrados no HRMS.

Versão atual: `1.4.18`.

## Compatibilidade

| Componente       | Versão             |
| :--------------- | :----------------- |
| Frappe Framework | `>=16.0.0,<17.0.0` |
| ERPNext          | `>=16.0.0,<17.0.0` |
| HRMS             | `>=16.0.0,<17.0.0` |
| Python           | `>=3.10,<3.15`     |

O app requer ERPNext e HRMS instalados no site antes da instalação do HRMS DDS BR.

## Recursos

- DocType submetível `DDS`, com numeração `DDS-AAAA-00001`.
- Workflow `Rascunho > Realizado/Enviado > Cancelado`.
- Cadastro dinâmico `DDS Tema`, com ativação e ordenação sem alteração de código.
- Tabela `DDS Participante` com presença, observação e assinatura.
- Cliente e empresa derivados do `Project`; não há campo duplicado de cliente no DDS.
- Validação de projeto, empresa, empregados ativos e participantes duplicados.
- Validação server-side de assinaturas, confirmação do responsável e participação.
- Proteção contra adulteração dos metadados de assinatura.
- DDS enviado ou cancelado não pode ser excluído fisicamente.
- Cancelamento com motivo, usuário e data/hora.
- Correção formal vinculada ao DDS original.
- Relatório `Employee DDS History` com isolamento por participante ou responsável.
- Painel `DDS Dashboard` com indicadores, gráfico mensal e alerta de projetos sem DDS recente.
- Link de acesso na tela HRMS `/hrms/home`.
- Botão de histórico no formulário `Employee`.
- Workspaces `DDS` e `Segurança do Trabalho`, com atalhos para cadastro, temas e relatórios.
- Print Format `DDS`.

## Instalação pelo Bench

```bash
bench get-app https://github.com/glsoltec/hrms_dds_br.git --branch version-16
bench --site seu-site install-app hrms_dds_br
bench --site seu-site migrate
bench --site seu-site clear-cache
bench build --app hrms_dds_br
```

Para repositório privado, configure uma deploy key de leitura no repositório e use a URL SSH:

```bash
bench get-app git@github.com:glsoltec/hrms_dds_br.git --branch version-16
```

## Configuração

Os limites de data e alerta podem ser definidos no `site_config.json`:

```json
{
  "dds_retroactive_days": 1,
  "dds_future_days": 0,
  "dds_no_dds_alert_days": 3
}
```

Padrões:

- `dds_retroactive_days`: 1 dia.
- `dds_future_days`: 0 dias.
- `dds_no_dds_alert_days`: 3 dias sem DDS para alerta por projeto.

Após alterar o `site_config.json`, execute:

```bash
bench --site seu-site clear-cache
```

## Uso

1. Cadastre ou revise os temas em **DDS Tema**.
2. Abra **DDS** e selecione um projeto.
3. Escolha um tema ativo.
4. Informe o responsável, conteúdo, riscos e medidas preventivas.
5. Adicione os participantes e registre presença/assinaturas.
6. Use a ação **Enviar** para concluir o DDS.
7. Acesse o histórico pela tela HRMS `/hrms/home` ou pelo formulário `Employee`.

Para cancelar, utilize a ação **Cancelar DDS**, informe a justificativa e confirme. Para corrigir um registro cancelado, use **Criar Correção**.

## Regras de acesso

- `System Manager`: administração completa.
- `Safety Manager`: criação, edição em rascunho, envio, cancelamento e impressão.
- `Safety Supervisor`: criação, edição em rascunho, envio e impressão.
- `HR Manager`: leitura, relatório e impressão.
- `Employee`: relatório, leitura e impressão somente de DDS em que participa ou é responsável.
- `Employee Self Service`: acesso ao histórico próprio na tela HRMS, limitado server-side a DDS em que participa ou é responsável.

Permissões não são controladas apenas pela interface. O app aplica `permission_query_conditions` e `has_permission` no servidor.

## Assinaturas e privacidade

As assinaturas usam o campo nativo `Signature`. O sistema registra coletor, data/hora e hash para rastreabilidade interna. O hash não comprova sozinho a identidade do signatário e não equivale a assinatura digital qualificada.

Para empregados comuns, assinaturas de terceiros são ocultadas na leitura do documento. O PDF operacional não exibe hash, coletor ou data/hora técnica da assinatura.

O app processa dados de empregados, presença, assinaturas e imagens. A organização responsável pelo site deve definir finalidade, base legal, retenção, acesso, eliminação, exportação e tratamento de backups conforme a legislação aplicável.

## Atualização

Faça backup antes de atualizar:

```bash
bench --site seu-site backup
bench --site seu-site migrate
bench --site seu-site clear-cache
bench build --app hrms_dds_br
```

Releases são identificadas por tags, por exemplo `v1.4.1`.

## Desinstalação

Faça backup e avalie a retenção dos dados antes de desinstalar:

```bash
bench --site seu-site backup
bench --site seu-site uninstall-app hrms_dds_br
```

A desinstalação pode remover DocTypes e dados associados. Não execute em produção sem validar a política de retenção e um plano de restauração.

## Desenvolvimento e validação

```bash
python -m compileall hrms_dds_br
python -m json.tool caminho/para/arquivo.json
bench --site seu-site run-tests --app hrms_dds_br
```

O teste completo requer um bench Frappe v16 com ERPNext e HRMS instalados. Não execute testes destrutivos em produção.

## Suporte

Abra uma issue em:

<https://github.com/glsoltec/hrms_dds_br/issues>

Inclua a versão do app, Frappe, ERPNext e HRMS, passos para reprodução e logs redigidos. Não envie senhas, tokens, dados pessoais completos ou anexos de empregados.

## Licença

MIT. Consulte `license.txt`.
