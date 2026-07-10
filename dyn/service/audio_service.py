"""音频服务 — 波形加载."""

from __future__ import annotations

import logging

from dyn.logging_config import get_logger

log = get_logger(__name__)


def load_waveform(path: str) -> tuple[list[float] | None, int]:
    """从音频文件加载归一化振幅数据。返回 (samples, sample_rate)."""
    log.info(f"加载波形: {path}")
    try:
        import numpy as np
        data = None
        sr = 44100

        try:
            import soundfile as sf
            data, sr = sf.read(path, dtype='float32', always_2d=False)
            log.debug(f"soundfile 成功: sr={sr}, len={len(data)}")
        except Exception as e:
            log.warning(f"soundfile 失败: {e}")

        if data is None:
            try:
                from scipy.io import wavfile
                sr, data = wavfile.read(path)
                if data.ndim > 1:
                    data = data.mean(axis=1).astype(np.float32)
                data = data.astype(np.float32) / (np.abs(data).max() + 1e-6)
                log.debug(f"scipy wavfile 成功: sr={sr}")
            except Exception as e:
                log.warning(f"scipy wavfile 失败: {e}")

        if data is not None and len(data) > 0:
            if hasattr(data, 'ndim') and data.ndim > 1:
                data = data.mean(axis=1)
            data = np.abs(data.astype(np.float32))
            mx = data.max()
            if mx > 1e-6:
                data = data / mx
            samples = data.tolist()
            log.info(f"波形加载完成: {len(samples)} 采样点, sr={sr}")
            return samples, int(sr)
    except Exception:
        log.exception("波形加载致命错误")
    return None, 44100
