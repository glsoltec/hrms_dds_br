# Segurança

Obrigado por contribuir com a segurança do **Diálogo Diário de Segurança** (`hrms_dds_br`).

## Como reportar

NÃO abra issue pública com detalhes de vulnerabilidade explorável. Envie para:

```text
dev@glsoltec.com.br
```

Informe:

- versão do app;
- versões de Frappe/ERPNext/HRMS/Python;
- descrição e impacto;
- passo a passo de reprodução (sem dados reais);
- evidência mínima (sem payloads completos).

## Compromisso

- Confidencialidade até a correção/publicação.
- Reconhecimento do relator, se desejado.
- Correção priorizada conforme severidade.

## Limitações conhecidas

- A assinatura registrada não é assinatura digital (ICP-Brasil); é evidência de coleta com hash SHA-256.
- Assinaturas/foto de terceiros são protegidas por `permlevel` para usuários comuns; a impressão/PDF usa o documento autorizado.
- A integração `/hrms/home` depende de seletores do frontend HRMS e deve ser validada após upgrades do HRMS.
