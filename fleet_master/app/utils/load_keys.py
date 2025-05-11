from pathlib import Path
import logging
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)

def load_private_key(path: str) -> str:
    key_path = Path(path)
    if not key_path.exists():
        # 如果私钥不存在，自动生成密钥对
        logger.info(f"私钥 {path} 不存在，自动生成密钥对")
        node_name = Path(path).parent.name
        private_pem, public_pem = generate_rsa_key_pair(node_name)
        
        # 确保目录存在
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存私钥
        key_path.write_text(private_pem)
        
        # 保存公钥
        public_path = key_path.parent / "public.pem"
        public_path.write_text(public_pem)
        
        # 同时保存到公钥目录
        public_keys_dir = key_path.parent / "public_keys"
        public_keys_dir.mkdir(parents=True, exist_ok=True)
        (public_keys_dir / f"{node_name}.pem").write_text(public_pem)
        
        logger.info(f"已生成并保存节点 {node_name} 的密钥对")
        return private_pem
    return key_path.read_text()

def load_public_key(node_name: str, base_path="config/fleet/public_keys") -> str:
    key_path = Path(base_path) / f"{node_name}.pem"
    
    # 如果公钥不存在，记录警告
    if not key_path.exists():
        logger.warning(f"节点 {node_name} 的公钥不存在，路径: {key_path}")
        raise FileNotFoundError(f"找不到公钥: {key_path}")
        
    return key_path.read_text()

def generate_rsa_key_pair(node_name: str) -> tuple:
    """生成 RSA 密钥对，返回 (private_key_pem, public_key_pem)"""
    logger.info(f"为节点 {node_name} 生成新的 RSA 密钥对")
    
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # 序列化私钥为 PEM 格式
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # 序列化公钥为 PEM 格式
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem

def save_node_public_key(node_name: str, public_key: str, base_path="config/fleet/public_keys") -> bool:
    """保存节点公钥到文件系统
    
    Args:
        node_name: 节点名称
        public_key: PEM格式的公钥内容
        base_path: 公钥存储的基础路径
        
    Returns:
        保存是否成功
    """
    try:
        # 确保目录存在
        key_dir = Path(base_path)
        key_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存公钥
        key_path = key_dir / f"{node_name}.pem"
        key_path.write_text(public_key)
        
        logger.info(f"已保存节点 {node_name} 的公钥到 {key_path}")
        return True
    except Exception as e:
        logger.error(f"保存节点 {node_name} 公钥失败: {e}")
        return False