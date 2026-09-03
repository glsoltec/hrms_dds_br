# Contribuindo

Contribuições são bem-vindas. Mantenha o padrão do projeto.

## Ambiente

- Frappe/ERPNext/HRMS `16.x`; Python `>=3.10,<3.15`.
- Branch ativa: `version-16`.

## Convenções

- Não renomear o identificador técnico `hrms_dds_br` (pacote, DocTypes, módulo).
- Usar os nomes exibidos já padronizados (`Diálogo Diário de Segurança`, rótulo `DDS`).
- `ruff` com a configuração do `pyproject.toml` (tabs, linha 110).
- Código novo abaixo de ~300 linhas por arquivo; dividir módulos quando necessário.

## Antes de enviar um PR

1. `python -m compileall hrms_dds_br`
2. `python -m json.tool` nos JSON alterados
3. `python -m unittest discover -s tests`
4. `git diff --check`
5. Se aplicável, `bench run-tests --app hrms_dds_br`

## Fluxo

1. Abra uma issue descrevendo a mudança.
2. Envie PR para `version-16`.
3. CI deve passar.
4. Para mudanças em regras de negócio, inclua/atualize testes e atualize o `CHANGELOG.md`.
