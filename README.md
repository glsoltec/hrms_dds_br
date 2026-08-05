# SST DDS BR — Diálogo Diário de Segurança

App simples para registrar Diálogo Diário de Segurança (DDS), participantes e assinaturas usando recursos nativos do Frappe.

Desenvolvido por **GL SOLTEC** — dev@glsoltec.com.br.

## Recursos

- DocType submetível `DDS`, com numeração `DDS-AAAA-00001`.
- Tabela filha `DDS Participante`.
- Função do colaborador preenchida a partir de `Employee.designation`.
- Cliente e empresa derivados do projeto, com validação de coerência.
- Somente empregados ativos e da mesma empresa podem participar.
- Coletor, data/hora e hash SHA-256 registrados para cada assinatura.
- Validação no servidor de presença, assinatura dos presentes e confirmação/assinatura do responsável.
- Workflow `Rascunho > Realizado/Enviado`.
- Papéis `Safety Manager` e `Safety Supervisor`.
- Workspace `Segurança do Trabalho` e formato de impressão `DDS`.

## Instalação

No servidor Bench, a partir da pasta do bench:

```bash
bench get-app /caminho/para/este/repositorio
bench --site seu-site install-app sst_dds_br
bench --site seu-site migrate
bench --site seu-site clear-cache
```

O site precisa ter `erpnext` e `hrms` v16 instalados antes do `sst_dds_br`.

Em produção, reinicie os serviços conforme o método nativo do seu ambiente (`sudo supervisorctl restart all` em instalações Supervisor ou `sudo systemctl restart ...` quando gerenciadas por systemd).

Depois da migração:

1. confirme que ERPNext e HRMS estão instalados e atualizados na versão 16;
2. atribua `Safety Manager` aos responsáveis por administrar DDS;
3. atribua `Safety Supervisor` aos líderes que criam e enviam DDS;
4. confirme que os colaboradores possuem `User ID`, `Designation`, empresa e situação ativa no HRMS;
5. abra **Segurança do Trabalho > DDS** e faça um teste completo, incluindo impressão e isolamento por participante.

## Regras de acesso

- `System Manager`: administração completa.
- `Safety Manager`: criar, editar, enviar, cancelar, excluir e imprimir.
- `Safety Supervisor`: criar, editar, enviar e imprimir; não cancela nem exclui.
- `HR Manager`: leitura e impressão para conferência funcional; não altera nem cancela DDS.
- `Employee`: leitura e impressão somente dos DDS em que aparece como participante, usando o vínculo `Employee.user_id`. Sem esse vínculo, o empregado não visualiza registros.

As assinaturas usam o campo nativo `Signature`. O sistema registra quem coletou, quando ocorreu a coleta e o hash do desenho. Isso melhora a rastreabilidade, mas não prova que o usuário autenticado é o próprio participante e não equivale a assinatura digital ICP-Brasil.

## Homologação

Em um site de teste v16:

```bash
bench --site seu-site migrate
bench --site seu-site run-tests --app sst_dds_br
```

Homologue criação, envio, cancelamento, impressão/PDF, controle de acesso da foto, alteração de assinatura, empregado inativo, divergência de empresa e acesso de um Employee participante e não participante.

## Atualização

Após atualizar os arquivos do app:

```bash
bench --site seu-site migrate
bench --site seu-site clear-cache
```

## Distribuição

O identificador técnico do app é `sst_dds_br` e o título público é **SST DDS BR**. Consulte [MARKETPLACE.md](MARKETPLACE.md), [PRIVACY.md](PRIVACY.md) e [SUPPORT.md](SUPPORT.md) antes de publicar uma versão.
