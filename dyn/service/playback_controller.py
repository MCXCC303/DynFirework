"""播放控制器 封装 QMediaPlayer 用于音乐回放 df 适配秒单位."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from dyn.logging_config import get_logger

log = get_logger(__name__)

class PlaybackController(QObject):
	"""控制音频播放并与时间线同步 同时提供 tick 和 second 两种位置信号."""

	position_changed = Signal(int)  # tick (保留向后兼容)
	position_sec_changed = Signal(float)  # seconds
	state_changed = Signal(str)  # "playing", "paused", "stopped"
	duration_changed = Signal(int)  # total ticks

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self.player = QMediaPlayer()
		self._audio = QAudioOutput()
		self.player.setAudioOutput(self._audio)

		self._bpm: float = 120.0
		self._ticks_per_beat: int = 20
		self._total_ticks: int = 0

		self._sync_timer = QTimer()
		self._sync_timer.setInterval(50)
		self._sync_timer.timeout.connect(self._sync_position)

		self.player.positionChanged.connect(self._on_media_position_changed)
		self.player.playbackStateChanged.connect(self._on_state_changed)

	@property
	def is_playing(self) -> bool:
		return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

	@property
	def is_paused(self) -> bool:
		return self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState

	@property
	def is_stopped(self) -> bool:
		return self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState

	def set_bpm(self, bpm: float) -> None:
		log.debug(f"设置 BPM: {bpm}")
		self._bpm = bpm

	def set_ticks_per_beat(self, tpb: int) -> None:
		log.debug(f"设置 TPB: {tpb}")
		self._ticks_per_beat = tpb

	def load_music(self, path: str | Path) -> bool:
		path = Path(path)
		if not path.exists():
			log.warning(f"音乐文件不存在: {path}")
			return False
		url = QUrl.fromLocalFile(str(path.resolve()))
		self.player.setSource(url)
		log.debug(f"加载音乐: {path}")
		self.player.mediaStatusChanged.connect(self._on_media_loaded)
		return True

	def load_music_from_temp(self, temp_path: str) -> bool:
		log.debug(f"从临时文件加载音乐: {temp_path}")
		return self.load_music(temp_path)

	def _on_media_loaded(self, status) -> None:
		if status == QMediaPlayer.MediaStatus.LoadedMedia:
			duration_ms = self.player.duration()
			self._total_ticks = self._ms_to_ticks(duration_ms)
			log.debug(f"媒体加载完成: duration={duration_ms}ms, total_ticks={self._total_ticks}")
			self.duration_changed.emit(self._total_ticks)

	def play(self) -> None:
		log.debug(f"播放 (tick={self.current_tick()})")
		self.player.play()
		self._sync_timer.start()

	def pause(self) -> None:
		log.debug(f"暂停 (tick={self.current_tick()})")
		self.player.pause()
		self._sync_timer.stop()

	def stop(self) -> None:
		log.debug(f"停止 (tick={self.current_tick()})")
		self.player.stop()
		self._sync_timer.stop()
		self.position_changed.emit(0)
		self.position_sec_changed.emit(0.0)

	def toggle_play_pause(self) -> None:
		current_state = "playing" if self.is_playing else "paused" if self.is_paused else "stopped"
		log.debug(f"切换播放/暂停: 当前={current_state}")
		if self.is_playing:
			self.pause()
		else:
			self.play()

	def seek_to_tick(self, tick: int) -> None:
		log.debug(f"跳转到 tick: {tick}")
		ms = self._ticks_to_ms(tick)
		self.player.setPosition(ms)

	def seek_to_sec(self, sec: float) -> None:
		log.debug(f"跳转到 秒: {sec}")
		self.seek_to_tick(int(sec * 20))

	def current_tick(self) -> int:
		return self._ms_to_ticks(self.player.position())

	def current_sec(self) -> float:
		return self.current_tick() / 20.0

	def _sync_position(self) -> None:
		tick = self.current_tick()
		self.position_changed.emit(tick)
		self.position_sec_changed.emit(tick / 20.0)

	def _on_media_position_changed(self, position_ms: int) -> None:
		pass

	def _on_state_changed(self, state) -> None:
		log.debug(f"播放状态变更: {state}")
		state_map = {
			QMediaPlayer.PlaybackState.PlayingState: "playing",
			QMediaPlayer.PlaybackState.PausedState: "paused",
			QMediaPlayer.PlaybackState.StoppedState: "stopped",
		}
		self.state_changed.emit(state_map.get(state, "stopped"))

	def _ticks_to_ms(self, ticks: int) -> int:
		return int(ticks * 1000 / 20)

	def _ms_to_ticks(self, ms: int) -> int:
		return int(ms * 20 / 1000)
