"""文件完整性校验工具 SHA-256 哈希计算与验证."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

log = logging.getLogger("dyn.lib.integrity")

def bytes_sha256(data: bytes) -> str:
	"""计算字节数据的 SHA-256 哈希（hex 字符串）."""
	return hashlib.sha256(data).hexdigest()

def file_sha256(filepath: Path) -> str:
	"""计算文件的 SHA-256 哈希."""
	log.debug(f"计算文件哈希: {filepath}")
	sha = hashlib.sha256()
	with open(filepath, "rb") as f:
		for chunk in iter(lambda: f.read(65536), b""):
			sha.update(chunk)
	return sha.hexdigest()

def verify_checksum(expected: str, actual: str) -> bool:
	"""对比校验和（constant-time 比较）."""
	result = hashlib.compare_digest(expected, actual)
	if not result:
		log.warning(f"校验和不匹配: expected={expected[:16]}..., actual={actual[:16]}...")
	else:
		log.debug(f"校验通过: {expected[:16]}...")
	return result
