import requests
from bs4 import BeautifulSoup

def get_exchange_rate_google(currency1: str, currency2: str):
    try:
        # URL de busca no Google
        url = f"https://www.google.com/search?q={currency1}+to+{currency2}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        
        # Usar BeautifulSoup para extrair o valor
        soup = BeautifulSoup(response.text, "html.parser")
        rate = soup.find("span", {"class": "DFlfde", "data-precision": "2"}).text
        
        return f"{currency1} para {currency2}: {rate}"
    except Exception as e:
        return f"Erro ao obter cotação do Google: {e}"


# Testes
if __name__ == "__main__":
    moeda_entrada = "USD"
    moeda_saida = "EUR"
    print(get_exchange_rate_google(moeda_entrada, moeda_saida))
