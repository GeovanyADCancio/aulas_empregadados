#### Criação de Job (Pipeline) no Databricks

Clica em Jobs & Pipelines no menu esquerdo:

Task Name: Pipeline_Saude_Synthea.

Type: Notebook.

Source: Selecione este notebook que criamos.

Cluster: Use o cluster disponível (Community) ou crie um Job Cluster (Standard).

Schedule: Defina para rodar "Every Day" às 08:00 AM.

CRON

  ┌───────────── Minuto (0 - 59)
  │ ┌───────────── Hora (0 - 23)
  │ │ ┌───────────── Dia do Mês (1 - 31)
  │ │ │ ┌───────────── Mês (1 - 12)
  │ │ │ │ ┌───────────── Dia da Semana (0 - 6) (Domingo=0 até Sábado=6)
  │ │ │ │ │
  * * * * *

Cron: 0 6 * * * (Tradução: Minuto 0, Hora 6, Qualquer dia, Qualquer mês, Qualquer dia da semana)
Cron: 30 7 * * 1 (Tradução: Às 07:30 da manhã, apenas se for Segunda-feira (1))
Cron: 0 8 * * 1-5 (Tradução: Às 08:00, de Segunda a Sexta-feira)
Cron: */15 * * * * (Tradução: A cada passo de 15 minutos, todas as horas, todos os dias)

Os Símbolos Mágicos:

* (Asterisco): Significa "qualquer" ou "todo". (Ex: * na hora = "toda hora").

, (Vírgula): Lista valores específicos. (Ex: 1,15 no dia = "dia 1 e dia 15").

- (Hífen): Define um intervalo. (Ex: 1-5 no dia da semana = "Segunda a Sexta").

/ (Barra): Define repetição/passo. (Ex: */5 no minuto = "a cada 5 minutos").