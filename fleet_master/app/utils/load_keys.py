from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

def load_private_key(path: str) -> str:
    return Path(path).read_text()

def load_public_key(node_name: str, base_path="config/fleet/public_keys") -> str:
    key_path = Path(base_path) / f"{node_name}.pem"
    
    # 如果公钥不存在，记录警告
    if not key_path.exists():
        logger.warning(f"节点 {node_name} 的公钥不存在，路径: {key_path}")
        raise FileNotFoundError(f"找不到公钥: {key_path}")
        
    return key_path.read_text()

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