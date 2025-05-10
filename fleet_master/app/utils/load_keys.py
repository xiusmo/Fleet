from pathlib import Path

def load_private_key(path: str) -> str:
    return Path(path).read_text()

def load_public_key(node_name: str, base_path="config/fleet/public_keys") -> str:
    key_path = Path(base_path) / f"{node_name}.pem"
    return key_path.read_text()