from typing import Dict, Any
import json


def generate_key_pair() -> None:
    """
    Generate a Diffie-Hellman key pair and save it to a JSON file.
    """
    from diffie_hellman import main_dh
    from RSA import main_rsa

    p, g, private_key, public_key = main_dh()
    n, e, d = main_rsa()
    print(f"Diffie-Hellman keys: {p}, {g}, {public_key}")
    print(f"RSA keys: {e}, {n}")
    with open("key_pair.json", "w") as file:
        json.dump(
            {"p": p, "g": g, "private_key": private_key, "public_key": public_key, "n": n, "e": e, "d": d}, file
        )


def load_keys(filename: str = "key_pair.json") -> Dict[str, Any]:
    """
    Load Diffie-Hellman keys from a JSON file.
    Args:
        filename: Path to the key file.
    Returns:
        Dictionary with keys 'p', 'g', 'private_key', 'public_key'.
    """
    with open(filename, "r") as file:
        return json.load(file)
