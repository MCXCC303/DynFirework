"""播放控制器 — 封装 QMediaPlayer 用于音乐回放."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from dyn.logging_config import get_logger

log = get_logger(__name__)


class PlaybackController(QObject):
    """控制音频播放并与时间线同步."""

    position_changed = Signal(int)  # tick
    state_changed = Signal(str)  # "playing", "paused", "stopped"
    duration_changed = Signal(int)  # total ticks

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._player = QMediaPlayer()
        self._audio = QAudioOutput()
        self._player.setAudioOutput(self._audio)

        self._bpm: float = 120.0
        self._ticks_per_beat: int = 20
        self._total_ticks: int = 0

        # 同步定时器 — 每 50ms 更新一次位置
        self._sync_timer = QTimer()
        self._sync_timer.setInterval(50)
        self._sync_timer.timeout.connect(self._sync_position)

        self._player.positionChanged.connect(self._on_media_position_changed)
        self._player.playbackStateChanged.connect(self._on_state_changed)

    @property
    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    @property
    def is_paused(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PausedState

    @property
    def is_stopped(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.StoppedState

    def set_bpm(self, bpm: float) -> None:
        self._bpm = bpm

    def set_ticks_per_beat(self, tpb: int) -> None:
        self._ticks_per_beat = tpb

    def load_music(self, path: str | Path) -> bool:
        from PySide6.QtCore import QUrl
        path = Path(path)
        if not path.exists():
            log.warning(f"音乐文件不存在: {path}")
            return False
        url = QUrl.fromLocalFile(str(path.resolve()))
        self._player.setSource(url)
        log.info(f"加载音乐: {path}")
        self._player.mediaStatusChanged.connect(self._on_media_loaded)
        return True

    def _on_media_loaded(self, status) -> None:
        from PySide6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            duration_ms = self._player.duration()
            self._total_ticks = self._ms_to_ticks(duration_ms)
            self.duration_changed.emit(self._total_ticks)

    def play(self) -> None:
        log.debug("播放")
        self._player.play()
        self._sync_timer.start()

    def pause(self) -> None:
        log.debug("暂停")
        self._player.pause()
        self._sync_timer.stop()

    def stop(self) -> None:
        log.debug("停止")
        self._player.stop()
        self._sync_timer.stop()
        self.position_changed.emit(0)

    def toggle_play_pause(self) -> None:
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def seek_to_tick(self, tick: int) -> None:
        ms = self._ticks_to_ms(tick)
        self._player.setPosition(ms)

    def current_tick(self) -> int:
        return self._ms_to_ticks(self._player.position())

    def _sync_position(self) -> None:
        tick = self.current_tick()
        self.position_changed.emit(tick)

    def _on_media_position_changed(self, position_ms: int) -> None:
        pass  # _sync_timer 处理周期性更新

    def _on_state_changed(self, state) -> None:
        state_map = {
            QMediaPlayer.PlaybackState.PlayingState: "playing",
            QMediaPlayer.PlaybackState.PausedState: "paused",
            QMediaPlayer.PlaybackState.StoppedState: "stopped",
        }
        self.state_changed.emit(state_map.get(state, "stopped"))

    # ── 内部转换 ─────────────────────────────────────

    def _ticks_to_ms(self, ticks: int) -> int:
        beats = ticks / self._ticks_per_beat
        seconds = beats * 60.0 / self._bpm
        return int(seconds * 1000)

    def _ms_to_ticks(self, ms: int) -> int:
        seconds = ms / 1000.0
        beats = seconds * self._bpm / 60.0
        return int(beats * self._ticks_per_beat)
