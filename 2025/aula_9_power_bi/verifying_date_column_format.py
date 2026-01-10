arquivo_grande_csv = './data/311_Service_Requests_from_2010_to_Present_20251115.csv'
numero_de_linhas_para_ler = 5

print(f"--- Exibindo as primeiras {numero_de_linhas_para_ler} linhas brutas do arquivo ---")

with open(arquivo_grande_csv, 'r', encoding='utf-8') as f:
    for i in range(numero_de_linhas_para_ler):
        linha = f.readline()
        if not linha:  # Para o loop se o arquivo tiver menos de 5 linhas
            break
        print(f"Linha {i}: {linha.strip()}") # .strip() remove o '\n' do final

print("--- Fim da leitura ---")