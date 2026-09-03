# Homologação

Roteiro para validar o aplicativo antes de publicar no Frappe Marketplace ou em produção.

## 1. Preparar bench limpo

Requisitos:

- Frappe `16.x`
- ERPNext `16.x`
- HRMS `16.x`
- Python `>=3.10,<3.15`
- Node/yarn para build

```bash
# apps já instalados: frappe, erpnext, hrms
cd <bench>
bench get-app https://github.com/glsoltec/hrms_dds_br.git --branch version-16
bench --site teste.local install-app hrms_dds_br
bench --site teste.local migrate
bench build --app hrms_dds_br
```

## 2. Executar testes

```bash
# testes de configuração (stdlib, sem Frappe)
python -m unittest discover -s tests -v

# testes Frappe (criam dados transacionais no site de teste)
bench --site teste.local run-tests --app hrms_dds_br
```

## 3. Cenários funcionais

1. Cadastrar temas em **DDS Tema** (somente System Manager cria).
2. Criar um **DDS** (Project com cliente, tema ativo, responsável, participantes).
3. Conferir participante presente **sem assinatura** (deve permitir envio).
4. Enviar pelo workflow (`Rascunho → Realizado/Enviado`).
5. Receber notificação no submit (participante com `Employee.user_id`).
6. Abrir o DDS e revisar presença.
7. Imprimir o PDF (responsável e participantes).
8. Cancelar:
   - System Manager/Administrator: sem motivo.
   - Safety Manager: com motivo (caixa de texto).
9. Confirmar que assinaturas/foto não são retornadas a usuários comuns via REST/Desk.
10. Dashboard **Segurança do Trabalho/SST DDS** e relatórios `Employee DDS History` e `DDS Dashboard`.
11. Link da tela HRMS `/hrms/home`.

## 4. Matriz de acesso

| Papel             | Criar |   Ler    | Enviar |  Cancelar  |      Excluir      |
| :---------------- | :---: | :------: | :----: | :--------: | :---------------: |
| System Manager    |  Sim  |   Sim    |  Sim   | Sem motivo | Após cancelamento |
| Administrator     |  Sim  |   Sim    |  Sim   | Sem motivo | Após cancelamento |
| Safety Manager    |  Sim  |   Sim    |  Sim   | Com motivo |        Não        |
| Safety Supervisor |  Sim  |   Sim    |  Sim   |    Não     |        Não        |
| Responsavel DDS   |  Sim  | Próprios |  Sim   |    Não     |        Não        |
| Employee/ESS      |  Não  | Próprios |  Não   |    Não     |        Não        |
| HR Manager        |  Não  |   Sim    |  Não   |    Não     |        Não        |

## 5. Decisões registradas (itens 5 e 6 da revisão)

- **Confirmação de presença:** a notificação do submit orienta a _revisar_ a presença. Não há endpoint de confirmação automática; qualquer confirmação deve usar o fluxo oficial de edição com autorização por participante.
- **Logs:** erros de notificação registram apenas o nome do DDS (`frappe.log_error(...)`), sem PII/assinatura. Revisar antes de alterar o texto.

## 6. Antes da submissão

- Screenshots do workspace, formulário, relatórios e dashboard.
- Rodar `bench run-tests --app hrms_dds_br` com sucesso.
- Revisar `SECURITY.md`, `CONTRIBUTING.md` e seção de privacidade do README.
