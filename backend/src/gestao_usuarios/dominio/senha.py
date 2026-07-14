"""Hash e verificação de senhas (NF007).

Algoritmo: PBKDF2-HMAC-SHA256 (``hashlib``, biblioteca padrão), com salt
aleatório de 16 bytes e 600.000 iterações — parâmetros recomendados pelo
OWASP Password Storage Cheat Sheet. A senha em texto puro nunca é
armazenada: apenas o hash resultante, no formato

    pbkdf2_sha256$<iterações>$<salt_hex>$<hash_hex>

O número de iterações fica gravado dentro do próprio hash, então ele pode
ser aumentado no futuro sem invalidar as senhas já cadastradas.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000
_TAMANHO_SALT_BYTES = 16


def gerar_hash(senha: str) -> str:
    """Devolve o hash da senha, com salt aleatório embutido."""
    salt = secrets.token_bytes(_TAMANHO_SALT_BYTES)
    derivada = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, ITERACOES)
    return f"{ALGORITMO}${ITERACOES}${salt.hex()}${derivada.hex()}"


def verificar(senha: str, hash_armazenado: str) -> bool:
    """Confere a senha contra um hash gerado por ``gerar_hash``.

    Usa ``hmac.compare_digest`` (comparação em tempo constante) para não
    vazar informação por tempo de resposta. Devolve ``False`` para hashes
    em formato desconhecido em vez de lançar exceção — para o chamador,
    equivale a senha incorreta.
    """
    try:
        algoritmo, iteracoes, salt_hex, hash_hex = hash_armazenado.split("$")
        if algoritmo != ALGORITMO:
            return False
        derivada = hashlib.pbkdf2_hmac(
            "sha256", senha.encode(), bytes.fromhex(salt_hex), int(iteracoes)
        )
        return hmac.compare_digest(derivada.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False
