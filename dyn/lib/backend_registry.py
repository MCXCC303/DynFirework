"""后端注册表 — 管理DynFirework的命令生成后端.

全局后端切换，支持不同Minecraft版本对应的命令格式.

Backend types:
    DFP         — DynFirework Particles Mod (/dfp 命令), MC 1.20.1
    PARTICLEEX  — ParticleEx / Colorblock Mod (/particleex 命令), MC 1.12.2/1.16.5
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import NamedTuple

log = logging.getLogger("dyn.lib.backend_registry")


class BackendType(Enum):
    """命令生成后端类型."""
    DFP = "dfp"
    PARTICLEEX = "particleex"


class _McVersionInfo(NamedTuple):
    backend: BackendType
    pack_format: int
    display_name: str


#: Minecraft 版本
# @TianKong-y: 如果你看到这里说明你该去更新适配你的 DynFireworkParticles 了
MC_VERSION_MAP: dict[str, _McVersionInfo] = {
    "1.12.2": _McVersionInfo(BackendType.PARTICLEEX, 4, "Minecraft 1.12.2 (ParticleEx)"),
    "1.16.5": _McVersionInfo(BackendType.PARTICLEEX, 6, "Minecraft 1.16.5 (ParticleEx)"),
    "1.20.1": _McVersionInfo(BackendType.DFP, 15, "Minecraft 1.20.1 (DynFirework Particles)"),
    "1.20.4": _McVersionInfo(BackendType.DFP, 18, "Minecraft 1.20.4 (DynFirework Particles)"),
    "1.21":   _McVersionInfo(BackendType.DFP, 48, "Minecraft 1.21 (DynFirework Particles)"),
}

#: 支持的MC版本列表（按发布顺序排列）
SUPPORTED_MC_VERSIONS: list[str] = [
    "1.12.2", "1.16.5", "1.20.1", "1.20.4", "1.21",
]

#: 默认后端
_current_backend: BackendType = BackendType.DFP


def set_backend(backend: BackendType) -> None:
    """切换当前活动的命令生成后端.

    Args:
        backend: 目标后端类型

    .. note::
       此操作影响全局状态。应在导出前调用，不应在导出过程中切换。
    """
    global _current_backend
    if _current_backend != backend:
        log.info(f"后端切换: {_current_backend.value} → {backend.value}")
    _current_backend = backend


def get_backend() -> BackendType:
    """返回当前活动的命令生成后端."""
    return _current_backend


def resolve_mc_version(mc_version: str) -> _McVersionInfo:
    """根据MC版本号解析对应的后端和pack_format.

    Args:
        mc_version: Minecraft 版本字符串 (e.g. "1.20.1")

    Returns:
        _McVersionInfo 包含后端类型和pack_format

    Raises:
        KeyError: 不支持的MC版本
    """
    try:
        return MC_VERSION_MAP[mc_version]
    except KeyError:
        log.warning(f"不支持的MC版本: {mc_version}, 可用版本: {SUPPORTED_MC_VERSIONS}")
        raise


def get_pack_format(mc_version: str) -> int:
    """获取指定MC版本对应的数据包格式号."""
    return MC_VERSION_MAP[mc_version].pack_format


def get_default_mc_version() -> str:
    """返回默认MC版本（最新支持的版本）."""
    return SUPPORTED_MC_VERSIONS[-1]
