"""项目管理器 — .dyn 文件读写和项目生命周期管理."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from dyn.logging_config import get_logger
from dyn.models.timeline import Project

log = get_logger(__name__)


class ProjectManager(QObject):
    """管理项目的新建、打开、保存和关闭."""

    project_opened = Signal(Project)
    project_saved = Signal(str)  # file_path
    project_modified = Signal()
    project_closed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._project: Project = Project()
        self._file_path: str = ""
        self._is_modified: bool = False

    @property
    def project(self) -> Project:
        return self._project

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @property
    def has_file(self) -> bool:
        return bool(self._file_path)

    def mark_modified(self) -> None:
        self._is_modified = True
        self.project_modified.emit()

    def new_project(self) -> Project:
        log.info("创建新项目")
        self._project = Project()
        self._file_path = ""
        self._is_modified = False
        self.project_opened.emit(self._project)
        return self._project

    def open_project(self, path: str | Path) -> Project:
        log.info(f"打开项目: {path}")
        self._project = Project.from_file(path)
        self._file_path = str(path)
        self._is_modified = False
        if self._project.music_path and not Path(self._project.music_path).exists():
            log.warning(f"音乐文件不存在: {self._project.music_path}")
            self._project.music_path = ""
        self.project_opened.emit(self._project)
        return self._project

    def save_project(self, path: str | Path | None = None) -> bool:
        if path is not None:
            self._file_path = str(path)
        if not self._file_path:
            log.warning("保存失败: 无文件路径")
            return False
        log.info(f"保存项目: {self._file_path}")
        self._project.to_file(self._file_path)
        self._is_modified = False
        self.project_saved.emit(self._file_path)
        return True

    def set_music_path(self, path: str) -> None:
        log.debug(f"设置音乐路径: {path}")
        self._project.music_path = path
        self.mark_modified()

    def close_project(self) -> None:
        log.info("关闭项目")
        self._project = Project()
        self._file_path = ""
        self._is_modified = False
        self.project_closed.emit()
