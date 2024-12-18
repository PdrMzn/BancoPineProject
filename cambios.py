import requests
from bs4 import BeautifulSoup

def get_exchange_rate_google(currency1: str, currency2: str) -> str:
    try:
        # URL para busca no Google
        url = f"https://www.google.com/search?q={currency1}+to+{currency2}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        
        # Fazer a requisição HTTP
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Garante que a resposta foi bem-sucedida
        
        # Verifica o conteúdo da resposta para bloqueios
        if "captcha" in response.text.lower():
            return "Erro: Bloqueio por CAPTCHA ao acessar o Google. Por favor tente novamente."
        
        # Usar BeautifulSoup para extrair a taxa de câmbio
        soup = BeautifulSoup(response.text, "html.parser")
        rate_element = soup.find("span", {"class": "DFlfde", "data-precision": "2"})
        
        if rate_element:
            rate = rate_element.text.strip()
            return f"A cotação de {currency1} para {currency2} é {rate}."
        else:
            return "Erro: Não foi possível encontrar a cotação no Google. Por favor tente novamente."
    except requests.exceptions.RequestException as req_err:
        return f"Erro de conexão: {req_err}"
    except Exception as e:
        return f"Erro ao obter cotação do Google: {e}. Por favor tente novamente."

# Testes
if __name__ == "__main__":
    moeda_entrada = "USD"
    moeda_saida = "BRL"
    print(get_exchange_rate_google("USD", "EUR"))
    print(get_exchange_rate_google("GBP", "JPY"))


