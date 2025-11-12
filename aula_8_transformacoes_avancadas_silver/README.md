# 📘 Desafio: Coletar Cotações PTAX (Selenium → API Oficial)

Este desafio apresenta o que o script atual faz com **Selenium** e qual é o objetivo ao migrar para as **APIs oficiais do Banco Central (PTAX)** usando `requests`.

---

## ✅ O que o script com Selenium está fazendo

O script automatiza o site do Banco Central entrando no iframe do PTAX e executando este fluxo:

1. Seleciona a opção de consulta **"Cotação por período"**.  
2. Preenche a **data inicial** com o último dia do mês.  
3. Deixa a **data final vazia** para consultar apenas aquele dia.  
4. Escolhe a moeda **"REAL BRASIL"**.  
5. Clica em **Pesquisar**.  
6. Se houver cotação, o site mostra um botão **CSV** e o script baixa o arquivo.  
7. Se não houver cotação (ex.: feriado, final de semana), o script **tenta o dia anterior**.  
8. Repete tudo isso para todos os meses, de 2022 a 2025.

✅ Em resumo:  
O Selenium está baixando as **cotações PTAX do último dia útil de cada mês**, para o par **BRL ↔ outras moedas**, seguindo a mesma lógica que um usuário humano faria no site.

---

## ✅ O objetivo do desafio usando a API oficial PTAX

A API pública do Banco Central entrega os **mesmos dados do PTAX** em **JSON**, sem Selenium, sem iframe e sem interações na página.

A tarefa será:

1. Identificar o endpoint correto da **API PTAX** que retorna cotações diárias.  
2. Gerar a lista de **últimos dias de cada mês** (2022 → 2025).  
3. Para cada data, fazer uma consulta via `requests`.  
4. Tratar datas sem cotação, tentando o **dia útil anterior**.  
5. Coletar as moedas desejadas (USD, EUR, GBP, etc.) sempre em relação ao **REAL (BRL)**.  
6. Salvar o resultado em **CSV**, simulando o mesmo efeito do Selenium.  
7. Consolidar tudo em um único DataFrame final (opcional).

---

## ✅ Resumo final

- O Selenium baixa a cotação PTAX para o **último dia útil de cada mês**, interagindo com o site.  
- A API PTAX permite obter os **mesmos dados**, só que muito mais rápido e estável, usando HTTP + JSON.  
- Sua missão é **refazer o processo inteiro usando a API oficial**, sem Selenium e sem automação de navegador.
