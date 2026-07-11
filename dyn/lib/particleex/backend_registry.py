"""后端注册表 - 管理 particleex 后端与 MC 版本映射."""
from __future__ import annotations

import logging
from typing import NamedTuple

log = logging.getLogger("dyn.lib.backend_registry")

class _McVersionInfo(NamedTuple):
	pack_format: int
	display_name: str

MC_VERSION_MAP: dict[str, _McVersionInfo] = {
	"1.12.2": _McVersionInfo(4, "Minecraft 1.12.2 (ParticleEx)"),
	"1.16.5": _McVersionInfo(6, "Minecraft 1.16.5 (ParticleEx)"),
}

SUPPORTED_MC_VERSIONS: list[str] = ["1.12.2", "1.16.5"]

def resolve_mc_version(mc_version: str) -> _McVersionInfo:
	try:
		return MC_VERSION_MAP[mc_version]
	except KeyError:
		log.warning(f"不支持的MC版本: {mc_version}, 可用版本: {SUPPORTED_MC_VERSIONS}")
		raise

def get_pack_format(mc_version: str) -> int:
	return MC_VERSION_MAP[mc_version].pack_format

def get_default_mc_version() -> str:
	return SUPPORTED_MC_VERSIONS[-1]
