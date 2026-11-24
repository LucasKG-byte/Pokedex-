
import requests

def trazer_imagem(nome):

    nome = nome.strip().lower().replace(" ", "-")

    url = f"https://pokeapi.co/api/v2/pokemon/{nome}"

    try:

        resposta = requests.get(url, timeout=10)

        if resposta.status_code != 200:
            print("Pokemon nao encontrado!")
            return None
        
        # Descobri que essa parte transforma o pokeAPI em tipo um codigo python @Lucas
        dados = resposta.json()

        sprites = dados.get("sprites", {})
        official = sprites.get("other", {}).get(
            "official-artwork", {}
        )

        imapoke_url = (
            official.get("front_default")
            or sprites.get("front_default")
        )

        if not imapoke_url:
            print("Imagem nao encontrada!")
            return None

        imapoke = requests.get(imapoke_url, timeout=15)

        imapoke.raise_for_status()

        print("Imagem encontrada e baixada!")

        return imapoke.content

    except requests.RequestException as erro:

        print("Erro ao buscar imagem:", erro)
        return None
