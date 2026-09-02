### HRMS DDS BR

Formulário de Aplicação de DDS Diária para Obras e Projetos - Brasil, integrado ao **HRMS** do ERPNext/Frappe.

Versão atual: `1.3.3`.

### Recursos

- DocType submetível `DDS`, com numeração `DDS-AAAA-00001` e workflow `Rascunho > Realizado/Enviado > Cancelado`.
- Tabela filha `DDS Participante` com presença e assinatura.
- Função do colaborador preenchida a partir de `Employee.designation`.
- Cliente e empresa derivados do projeto, com validação de coerência.
- Somente empregados ativos e da mesma empresa podem participar.
- Coletor, data/hora e hash SHA-256 registrados para cada assinatura, com proteção contra adulteração dos metadados.
- Validação no servidor de presença, assinatura dos presentes e confirmação/assinatura do responsável.
- **Integração HRMS:** botão _Histórico de DDS_ no formulário do `Employee`.
- **Relatório `Employee DDS History`**: histórico de participação por empregado, com isolamento de acesso por participante/responsável no servidor.
- Link **Histórico de DDS** exibido também na tela de autoatendimento HRMS `/hrms/home`, junto aos atalhos rápidos.
- **Painel `DDS Dashboard`**: indicadores, gráfico mensal e alerta de projetos sem DDS recente.
- **Configuração via `site_config.json`**: chaves `dds_retroactive_days`, `dds_future_days` e `dds_no_dds_alert_days` (padrões 1, 0 e 3).
- Regras de negócio: cancelamento exige motivo registrado, DDS enviado/cancelado não pode ser excluído fisicamente, correção formal vinculada ao DDS original e aviso sobre a validade da assinatura no formulário.
- Papéis `Safety Manager` e `Safety Supervisor`.
- Workspace _Segurança do Trabalho_ e formato de impressão `DDS`.

### Dependências

O app requer o **HRMS** (e o ERPNext, base do HRMS) instalados no site antes do `hrms_dds_br`:

```bash
bench --site seu-site install-app hrms
bench --site seu-site install-app hrms_dds_br
```

### Instalação

No servidor Bench, a partir da pasta do bench:

```bash
bench get-app git@github.com:glsoltec/hrms_dds_br.git --branch version-16
bench --site seu-site install-app hrms_dds_br
bench --site seu-site migrate
bench --site seu-site clear-cache
```

### Regras de acesso

- `System Manager`: administração completa.
- `Safety Manager`: criar, editar, enviar, cancelar, excluir e imprimir.
- `Safety Supervisor`: criar, editar, enviar e imprimir; não cancela nem exclui.
- `HR Manager`: leitura e impressão para conferência funcional; não altera nem cancela DDS.
- `Employee`: leitura e impressão somente dos DDS em que aparece como responsável ou participante, usando o vínculo `Employee.user_id`.

Após o envio, o DDS é imutável. Para corrigir um registro, cancele-o com a justificativa operacional definida pela organização e registre um novo DDS. A permissão de edição exibida no workflow não substitui essa regra server-side.

As assinaturas usam o campo nativo `Signature`. O sistema registra quem coletou, quando ocorreu a coleta e o hash do desenho. Isso melhora a rastreabilidade, mas não prova que o usuário autenticado é o próprio participante e não equivale a assinatura digital ICP-Brasil.

### Homologação

```bash
bench --site seu-site migrate
bench --site seu-site run-tests --app hrms_dds_br
```

Homologue criação, envio, cancelamento, impressão/PDF, controle de acesso da foto, alteração de assinatura, empregado inativo, divergência de empresa, isolamento do relatório (participante, responsável, não participante e gestor), o botão _Histórico de DDS_ no `Employee` e o link na tela HRMS `/hrms/home`.

### Retenção e privacidade

A organização deve definir e documentar o prazo de retenção dos DDS, fotos, assinaturas, logs e backups, além do processo de exportação, correção e eliminação conforme a legislação aplicável. O app não presume base legal nem prazo de retenção. O PDF operacional não exibe hash, coletor ou data/hora técnica da assinatura; esses dados permanecem no registro para auditoria interna.

### License

mit
