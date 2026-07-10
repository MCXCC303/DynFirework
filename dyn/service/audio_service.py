"""音频服务 — 波形加载."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from dyn.logging_config import get_logger

log = get_logger(__name__)

#: 仅 scipy 支持的扩展名（scipy.io.wavfile 只能处理 WAV 容器）
_SCIPY_EXTENSIONS = frozenset({".wav"})


def load_waveform(path: str) -> tuple[list[float] | None, int]:
    """从音频文件加载归一化振幅数据。返回 (samples, sample_rate)."""
    log.debug(f"加载波形: {path}")
    return _read_waveform(path)


def load_waveform_from_bytes(data: bytes, suffix: str = ".mp3") -> tuple[list[float] | None, int]:
    """从内存中的音频数据加载波形.

    Args:
        data: 音频文件字节数据
        suffix: 文件扩展名（用于 soundfile 推断格式）

    Returns:
        (samples, sample_rate) 元组
    """
    log.debug(f"从内存加载波形: {len(data)} 字节, suffix={suffix}")
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, prefix="dyn_wf_")
    try:
        tmp.write(data)
        tmp.flush()
        tmp.close()
        return _read_waveform(tmp.name)
    finally:
        try:
            Path(tmp.name).unlink()
        except OSError:
            pass


def _read_waveform(path: str) -> tuple[list[float] | None, int]:
    """内部: 从路径读取波形，优先 soundfile，仅对 .wav 回退至 scipy."""
    try:
        import numpy as np
    except ImportError:
        log.error("numpy 未安装，无法加载波形")
        return None, 44100

    data: np.ndarray | None = None
    sr: int = 44100

    # 优先使用 soundfile（支持 MP3/WAV/OGG/FLAC 等）
    try:
        import soundfile as sf
        data, sr = sf.read(path, dtype="float32", always_2d=False)
        log.debug(f"soundfile 成功: sr={sr}, len={len(data)}")
    except Exception:
        log.debug("soundfile 不可用或读取失败，尝试其他方式")

    # soundfile 失败且是 WAV 文件时，回退到 scipy
    if data is None and Path(path).suffix.lower() in _SCIPY_EXTENSIONS:
        try:
            from scipy.io import wavfile
            sr, raw = wavfile.read(path)
            if raw.ndim > 1:
                raw = raw.mean(axis=1)
            data = raw.astype(np.float32) / (np.abs(raw).max() + 1e-6)
            log.debug(f"scipy wavfile 成功: sr={sr}")
        except Exception:
            log.debug("scipy wavfile 读取失败")

    if data is None:
        log.warning(f"无法读取音频文件: {path} (请确认已安装 soundfile 或文件格式为 WAV)")
        return None, 44100

    if data.ndim > 1:
        data = data.mean(axis=1)
    data = np.abs(data.astype(np.float32))
    mx = data.max()
    if mx > 1e-6:
        data = data / mx
    samples = data.tolist()
    log.debug(f"波形加载完成: {len(samples)} 采样点, sr={sr}")
    return samples, int(sr)
