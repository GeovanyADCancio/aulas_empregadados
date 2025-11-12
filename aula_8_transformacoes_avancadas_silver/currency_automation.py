from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import calendar

# ========== CONFIGURAÇÕES ==========
MAX_WAIT_CSV = 2        # tempo máximo para esperar botão CSV
MAX_WAIT_NOVA = 2       # tempo máximo para esperar botão "Nova consulta"
SLEEP_APOS_DOWNLOAD = 1 # tempo fixo após clicar no CSV
SLEEP_ENTRE_TENTATIVAS = 1  # tempo entre tentativas (dias anteriores)
SLEEP_ENTRE_MESES = 1       # tempo entre meses

# ========== FUNÇÕES AUXILIARES ==========
def gerar_datas_finais(inicio_ano=2022, inicio_mes=1, fim_ano=2025, fim_mes=9):
    """Gera uma lista com o último dia de cada mês entre duas datas."""
    datas = []
    ano, mes = inicio_ano, inicio_mes
    while (ano < fim_ano) or (ano == fim_ano and mes <= fim_mes):
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        datas.append(datetime(ano, mes, ultimo_dia))
        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1
    return datas


def tentar_data(driver, wait, data_base):
    """
    Tenta buscar a cotação a partir de uma data.
    Se não encontrar botão CSV, volta um dia e tenta novamente.
    """
    while data_base >= datetime(2022, 1, 1):
        data_str = data_base.strftime("%d%m%Y")
        print(f"Tentando data {data_str}...")

        campo_data_ini = wait.until(EC.presence_of_element_located((By.ID, "DATAINI")))
        campo_data_ini.clear()
        campo_data_ini.send_keys(data_str)

        # Campo final vazio
        try:
            campo_data_fim = driver.find_element(By.ID, "DATAFIM")
            campo_data_fim.clear()
            campo_data_fim.send_keys("")
        except:
            pass

        # Seleciona "REAL BRASIL"
        select_moeda = Select(wait.until(EC.presence_of_element_located((By.NAME, "ChkMoeda"))))
        select_moeda.select_by_visible_text("REAL BRASIL")

        # Clica em "Pesquisar"
        botao_pesquisar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Pesquisar']")))
        botao_pesquisar.click()

        try:
            # Espera botão CSV aparecer rapidamente (até MAX_WAIT_CSV segundos)
            botao_csv = WebDriverWait(driver, MAX_WAIT_CSV).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'CSV')]"))
            )
            botao_csv.click()
            print(f"✅ Download iniciado para {data_str}")
            
            # Em vez de esperar 5s fixos, aguarda o botão "Nova consulta"
            try:
                WebDriverWait(driver, MAX_WAIT_NOVA).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@value='Nova consulta']"))
                )
            except:
                time.sleep(SLEEP_APOS_DOWNLOAD)
            
            return True

        except:
            # Nenhum resultado -> tenta o dia anterior rapidamente
            print(f"❌ Nenhum resultado para {data_str}, tentando dia anterior...")
            data_base -= timedelta(days=1)
            time.sleep(SLEEP_ENTRE_TENTATIVAS)

            # Volta à tela anterior (nova consulta)
            try:
                botao_nova_consulta = WebDriverWait(driver, MAX_WAIT_NOVA).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@value='Nova consulta']"))
                )
                botao_nova_consulta.click()
            except:
                pass
            continue

    print("⚠️ Nenhuma data válida encontrada antes de 2022-01-01.")
    return False


# ========== SCRIPT PRINCIPAL ==========
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Edge(options=options)
wait = WebDriverWait(driver, 30)

try:
    driver.get("https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes")
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='ptax_internet']")))
    driver.switch_to.frame(iframe)

    # Seleciona a opção 2
    radio_opcao_2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='RadOpcao' and @value='2']")))
    radio_opcao_2.click()

    # Gera as datas alvo
    datas_alvo = gerar_datas_finais(2022, 1, 2025, 9)

    for data_final in datas_alvo:
        print("=" * 60)
        print(f"🔹 Processando {data_final.strftime('%B/%Y').capitalize()}...")
        sucesso = tentar_data(driver, wait, data_final)

        # Volta à tela inicial antes do próximo mês
        try:
            botao_nova_consulta = WebDriverWait(driver, MAX_WAIT_NOVA).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Nova consulta']"))
            )
            botao_nova_consulta.click()

            # Seleciona novamente a opção 2
            radio_opcao_2 = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@name='RadOpcao' and @value='2']"))
            )
            radio_opcao_2.click()
        except:
            driver.switch_to.default_content()
            driver.refresh()
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='ptax_internet']")))
            driver.switch_to.frame(iframe)
            radio_opcao_2 = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@name='RadOpcao' and @value='2']"))
            )
            radio_opcao_2.click()

        time.sleep(SLEEP_ENTRE_MESES)

finally:
    print("Finalizando o driver.")
    driver.quit() # Evita processos fantasmas consumindo recursos do computador
