"""播放控制栏 — 音乐播放/暂停/停止和时间显示."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSlider,
)
from PySide6.QtCore import Qt, Slot

from dyn.service.playback_controller import PlaybackController


class TransportBar(QWidget):
    """播放传输控制条."""

    def __init__(
        self,
        controller: PlaybackController,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # 播放/暂停
        self._btn_play = QPushButton("▶")
        self._btn_play.setFixedSize(32, 32)
        self._btn_play.setToolTip("播放/暂停 (Space)")
        layout.addWidget(self._btn_play)

        # 停止
        self._btn_stop = QPushButton("■")
        self._btn_stop.setFixedSize(32, 32)
        self._btn_stop.setToolTip("停止")
        layout.addWidget(self._btn_stop)

        # 跳转到开头
        self._btn_start = QPushButton("⏮")
        self._btn_start.setFixedSize(32, 32)
        self._btn_start.setToolTip("跳转到开头")
        layout.addWidget(self._btn_start)

        layout.addSpacing(12)

        # 时间显示
        self._label_time = QLabel("00:00.000")
        self._label_time.setFixedWidth(100)
        self._label_time.setAlignment(Qt.AlignCenter)
        self._label_time.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(self._label_time)

        # Tick 显示
        self._label_tick = QLabel("Tick: 0")
        self._label_tick.setFixedWidth(80)
        self._label_tick.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label_tick)

        layout.addSpacing(12)

        # 音量滑块
        layout.addWidget(QLabel("音量"))
        self._slider_volume = QSlider(Qt.Horizontal)
        self._slider_volume.setRange(0, 100)
        self._slider_volume.setValue(80)
        self._slider_volume.setFixedWidth(100)
        layout.addWidget(self._slider_volume)

        layout.addStretch()

        # 音乐文件路径
        self._label_music = QLabel("")
        self._label_music.setToolTip("当前音乐文件路径")
        self._label_music.setStyleSheet("color: #888;")
        layout.addWidget(self._label_music)

        layout.addSpacing(8)

        # BPM 显示
        self._label_bpm = QLabel("BPM: 120")
        self._label_bpm.setToolTip("可在项目设置中修改 BPM")
        layout.addWidget(self._label_bpm)

    def set_music_path(self, path: str) -> None:
        self._label_music.setText(path if path else "")

    def _setup_connections(self) -> None:
        self._btn_play.clicked.connect(self._on_play_pause)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_start.clicked.connect(self._on_go_to_start)
        self._slider_volume.valueChanged.connect(self._on_volume_changed)
        self._controller.position_changed.connect(self._on_position_changed)
        self._controller.state_changed.connect(self._on_state_changed)

    @Slot()
    def _on_play_pause(self) -> None:
        self._controller.toggle_play_pause()

    @Slot()
    def _on_stop(self) -> None:
        self._controller.stop()

    @Slot()
    def _on_go_to_start(self) -> None:
        self._controller.seek_to_tick(0)

    @Slot(int)
    def _on_volume_changed(self, value: int) -> None:
        from PySide6.QtMultimedia import QAudioOutput
        audio = self._controller._player.audioOutput()
        if audio:
            audio.setVolume(value / 100.0)

    @Slot(int)
    def _on_position_changed(self, tick: int) -> None:
        seconds = tick / 20.0
        minutes = int(seconds // 60)
        secs = seconds % 60
        ms = int((secs - int(secs)) * 1000)
        self._label_time.setText(f"{minutes:02d}:{int(secs):02d}.{ms:03d}")
        self._label_tick.setText(f"Tick: {tick}")

    @Slot(str)
    def _on_state_changed(self, state: str) -> None:
        if state == "playing":
            self._btn_play.setText("⏸")
        else:
            self._btn_play.setText("▶")

    def set_bpm(self, bpm: float) -> None:
        self._label_bpm.setText(f"BPM: {bpm:.0f}")
