
import pandas as pd
import google.generativeai as genai
import time
import json
import logging
import re
import sys

# === CONFIGURAÇÕES ===
API_KEY = ""  # será definida dinamicamente via interface
CSV_INPUT = "produtos.csv"
CSV_OUTPUT = "produtos_saida.csv"
LOG_FILE = "processo.log"
MODELO = "gemini-2.5-pro"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def configurar_api_key(api_key):
    global API_KEY
    API_KEY = api_key
    genai.configure(api_key=API_KEY)

def criar_prompt(linha):
    return (
        f"Você é um especialista em cadastro de produtos. Analise os dados abaixo "
        f"e gere um JSON com os campos: nome_ml, descricao, descricao_resumida.\n\n"
        f"Marca + Código de Fabricante + Produto: {linha['nome']}\n"
        f"EAN: {linha['ean']}\n"
        "{\n"
        '  "nome_ml": "nome organizado do produto",\n'
        '  "descricao": "Texto descritivo do produto",\n'
        '  "descricao_resumida": "descricao resumida em 3 linhas"\n'
        "}"
    )

def processar_produtos(api_key):
    configurar_api_key(api_key)
    logging.info("===== INÍCIO DO PROCESSO =====")
    logging.info(f"Arquivo de entrada: {CSV_INPUT}")

    try:
        df = pd.read_csv(CSV_INPUT, dtype=str)
    except FileNotFoundError:
        logging.error("Arquivo base não encontrado.")
        sys.exit("Arquivo base não encontrado.")

    model = genai.GenerativeModel(MODELO)

    for col in ["nome_ml", "descricao", "descricao_resumida"]:
        if col not in df.columns:
            df[col] = ""

    for i, row in df.iterrows():
        sku = row.get('sku', f'linha_{i}')
        prompt = criar_prompt(row)
        logging.info(f"Processando linha {i+1}/{len(df)} | SKU: {sku}")

        try:
            response = model.generate_content(prompt)
            texto = response.text.strip()

            match = re.search(r'\{[\s\S]*\}', texto)
            if not match:
                raise ValueError("Nenhum JSON válido encontrado na resposta.")

            dados = json.loads(match.group(0))
            df.loc[i, "nome_ml"] = dados.get("nome_ml", "").strip()
            df.loc[i, "descricao"] = dados.get("descricao", "").strip()
            df.loc[i, "descricao_resumida"] = dados.get("descricao_resumida", "").strip()

        except Exception as e:
            logging.error(f"Erro ao processar SKU {sku}: {e}")
            df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
            logging.info("Processo interrompido devido a erro. Progresso salvo.")
            return

        df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
        time.sleep(1)

    logging.info(f"Processo concluído! Resultados salvos em {CSV_OUTPUT}")
    logging.info("===== FIM DO PROCESSO =====")

if __name__ == "__main__":
    processar_produtos(API_KEY)
