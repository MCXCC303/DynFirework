""".dyn 项目文件格式 tar.gz 归档读写、格式检测与元数据校验.
project.dyn  (gzip-compressed tar)
├── manifest.json          # 项目元数据 + 文件清单 + 校验和
├── elements/
│   ├── <uuid>.json        # 每个元素一个 JSON 文件
│   └── ...
├── positions.json         # 保存的位置坐标
├── timeline_state.json    # 时间线 UI 状态
└── assets/
    └── music.dat          # 嵌入的音乐文件
"""
from __future__ import annotations

import hmac
import io
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dyn.logging_config import get_logger

log = get_logger(__name__)

from .integrity import bytes_sha256

# 常量

FORMAT_VERSION = "1.0"
"""当前文件格式版本号."""

GZIP_MAGIC = b"\x1f\x8b"
"""gzip 文件魔术字节，用于格式检测."""

_MANIFEST_MEMBER = "manifest.json"
_ELEMENTS_DIR = "elements"
_POSITIONS_MEMBER = "positions.json"
_TIMELINE_STATE_MEMBER = "timeline_state.json"
_ASSETS_DIR = "assets"
_MUSIC_MEMBER = "assets/music.dat"

# 写入

def write_project_archive(
		filepath: str | Path,
		backend: str,
		manifest_data: dict[str, Any],
		elements: list[dict[str, Any]],
		positions: list[dict[str, Any]],
		timeline_state: dict[str, Any],
		music_data: bytes | None = None,
		music_original_name: str = "",
) -> None:
	"""将项目数据写入 .dyn tar.gz 归档.

	Args:
		filepath: 输出文件路径
		backend: 模组后端标识 ("cb" 或 "df")
		manifest_data: 项目元数据（project 子对象的内容）
		elements: 元素序列，每个元素为 (type, id, json_data) 的映射
		positions: 保存的位置列表
		timeline_state: 时间线状态字典
		music_data: 音乐文件的原始字节，None 表示无音乐
		music_original_name: 音乐文件的原始名称（用于记录）
	"""
	filepath = Path(filepath)
	now = datetime.now(timezone.utc).isoformat()

	try:
		# 构建元素清单
		element_manifest: list[dict[str, str]] = []
		member_files: dict[str, bytes] = {}

		# 按类型统计元素
		type_counts: dict[str, int] = {}
		for elem in elements:
			etype = elem["type"]
			type_counts[etype] = type_counts.get(etype, 0) + 1
		log.debug(f"写入 {len(elements)} 条元素 ({', '.join(f'{k}={v}' for k, v in type_counts.items())})")
		for elem in elements:
			etype = elem["type"]
			eid = elem["id"]
			filename = f"{_ELEMENTS_DIR}/{eid}.json"
			element_manifest.append({"type": etype, "id": eid, "file": filename})
			member_files[filename] = json.dumps(
				elem["data"], ensure_ascii=False, indent=2
			).encode("utf-8")

		# 位置的 JSON
		pos_bytes = json.dumps(positions, ensure_ascii=False, indent=2).encode("utf-8")
		member_files[_POSITIONS_MEMBER] = pos_bytes

		# 时间线状态的 JSON
		ts_bytes = json.dumps(timeline_state, ensure_ascii=False, indent=2).encode("utf-8")
		member_files[_TIMELINE_STATE_MEMBER] = ts_bytes

		# 音乐资源
		music_info: dict[str, Any] | None = None
		if music_data is not None:
			member_files[_MUSIC_MEMBER] = music_data
			music_info = {
				"original_name": music_original_name,
				"size": len(music_data),
			}

		# 计算所有成员文件的校验和
		file_checksums: dict[str, str] = {}
		for name in sorted(member_files):
			file_checksums[name] = bytes_sha256(member_files[name])

		# 构建 manifest（不含 checksums 键）
		manifest_body: dict[str, Any] = {
			"format_version": FORMAT_VERSION,
			"backend": backend,
			"project": manifest_data,
			"music": music_info,
			"elements": element_manifest,
			"created_at": now,
			"updated_at": now,
		}

		# 计算 manifest 主体自身的校验和
		manifest_body_bytes = json.dumps(
			manifest_body, ensure_ascii=False, indent=2
		).encode("utf-8")
		manifest_hash = bytes_sha256(manifest_body_bytes)

		# 组装完整 manifest
		manifest: dict[str, Any] = {**manifest_body}
		manifest["checksums"] = {
			"algorithm": "sha256",
			"manifest_body": manifest_hash,
			"files": file_checksums,
		}

		manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")

		# 写入 tar.gz
		with tarfile.open(filepath, mode="w:gz") as tar:
			# manifest.json 必须第一个写入
			info = tarfile.TarInfo(name=_MANIFEST_MEMBER)
			info.size = len(manifest_bytes)
			tar.addfile(info, io.BytesIO(manifest_bytes))

			for name in sorted(member_files):
				data = member_files[name]
				info = tarfile.TarInfo(name=name)
				info.size = len(data)
				tar.addfile(info, io.BytesIO(data))

		log.debug(f"写入项目归档: {filepath} ({len(member_files)} 个成员文件)")

	except Exception as e:
		log.error(f"写入归档失败 {filepath}: {e}", exc_info=True)
		raise

# 读取

class ArchiveReadResult:
	"""归档读取结果."""

	def __init__(
			self,
			manifest: dict[str, Any],
			elements: list[dict[str, Any]],
			positions: list[dict[str, Any]],
			timeline_state: dict[str, Any],
			music_data: bytes | None,
			errors: list[str],
	) -> None:
		self.manifest = manifest
		self.elements = elements
		self.positions = positions
		self.timeline_state = timeline_state
		self.music_data = music_data
		self.errors = errors

	@property
	def is_valid(self) -> bool:
		return len(self.errors) == 0

def read_project_archive(filepath: str | Path) -> ArchiveReadResult:
	"""从 .dyn tar.gz 归档读取项目数据.

	Args:
		filepath: 输入文件路径

	Returns:
		ArchiveReadResult 包含解析后的数据和验证错误列表

	Raises:
		ValueError: 文件格式无法识别
	"""
	filepath = Path(filepath)
	try:
		with open(filepath, "rb") as f:
			header = f.read(2)
	except (FileNotFoundError, PermissionError) as e:
		log.error(f"无法打开项目文件 {filepath}: {e}")
		raise
	if header != GZIP_MAGIC:
		raise ValueError(f"无法识别的文件格式: {filepath}")
	return _read_tar_gz(filepath)

# 内部：读取 tar.gz

def _read_tar_gz(filepath: Path) -> ArchiveReadResult:
	errors: list[str] = []
	manifest: dict[str, Any] = {}
	elements: list[dict[str, Any]] = []
	positions: list[dict[str, Any]] = []
	timeline_state: dict[str, Any] = {}
	music_data: bytes | None = None

	member_bytes: dict[str, bytes] = {}

	try:
		with tarfile.open(filepath, mode="r:gz") as tar:
			for member in tar.getmembers():
				if not member.isfile():
					continue
				f = tar.extractfile(member)
				if f is None:
					continue
				data = f.read()
				member_bytes[member.name] = data
	except (tarfile.TarError, OSError) as e:
		errors.append(f"归档读取失败: {e}")
		log.error(f"归档文件损坏 {filepath}: {e}", exc_info=True)
		return ArchiveReadResult({}, [], [], {}, None, errors)

	# 验证 manifest 是否存在
	if _MANIFEST_MEMBER not in member_bytes:
		errors.append(f"缺少 {_MANIFEST_MEMBER} ，归档已损坏")
		log.warning(f"缺少 {_MANIFEST_MEMBER} ，归档已损坏")
		return ArchiveReadResult({}, [], [], {}, None, errors)

	# 解析 manifest
	try:
		manifest = json.loads(member_bytes[_MANIFEST_MEMBER].decode("utf-8"))
	except (json.JSONDecodeError, UnicodeDecodeError) as e:
		errors.append(f"manifest.json 解析失败: {e}")
		log.warning(f"manifest.json 解析失败: {e}")
		return ArchiveReadResult({}, [], [], {}, None, errors)

	# 验证格式版本
	format_ver = manifest.get("format_version", "1.0")
	log.debug(f"项目文件格式版本: {format_ver}")

	# 校验 manifest 自身完整性
	checksums = manifest.get("checksums", {})
	if checksums:
		errors.extend(_validate_manifest_integrity(manifest, checksums))

	# 加载元素
	element_manifest = manifest.get("elements", [])
	for entry in element_manifest:
		filename = entry["file"]
		if filename not in member_bytes:
			errors.append(f"缺少文件: {filename}")
			continue

		# 校验元素文件
		file_checksums = checksums.get("files", {})
		if filename in file_checksums:
			expected = file_checksums[filename]
			actual = bytes_sha256(member_bytes[filename])
			if not _timing_safe_eq(expected, actual):
				errors.append(f"文件校验失败: {filename}")

		try:
			data = json.loads(member_bytes[filename].decode("utf-8"))
		except (json.JSONDecodeError, UnicodeDecodeError) as e:
			errors.append(f"{filename} JSON 解析失败: {e}")
			continue

		elements.append({
			"type": entry["type"],
			"id": entry["id"],
			"file": filename,
			"data": data,
		})

	# 加载位置
	if _POSITIONS_MEMBER in member_bytes:
		try:
			positions = json.loads(member_bytes[_POSITIONS_MEMBER].decode("utf-8"))
		except (json.JSONDecodeError, UnicodeDecodeError) as e:
			errors.append(f"positions.json 解析失败: {e}")
			positions = []

	# 加载时间线状态
	if _TIMELINE_STATE_MEMBER in member_bytes:
		try:
			timeline_state = json.loads(
				member_bytes[_TIMELINE_STATE_MEMBER].decode("utf-8")
			)
		except (json.JSONDecodeError, UnicodeDecodeError) as e:
			errors.append(f"timeline_state.json 解析失败: {e}")
			timeline_state = {}

	# 加载音乐
	if _MUSIC_MEMBER in member_bytes:
		music_entry = manifest.get("music") or {}
		expected_size = music_entry.get("size", 0)
		actual_size = len(member_bytes[_MUSIC_MEMBER])
		if expected_size and expected_size != actual_size:
			errors.append(
				f"Music size mismatch: expect {expected_size}, read {actual_size}"
			)
			log.warning(f"音乐文件大小不匹配: expected={expected_size}, actual={actual_size}")
		music_data = member_bytes[_MUSIC_MEMBER]

	if errors:
		log.warning(f"项目文件存在 {len(errors)} 个校验问题: {errors}")

	return ArchiveReadResult(
		manifest=manifest,
		elements=elements,
		positions=positions,
		timeline_state=timeline_state,
		music_data=music_data,
		errors=errors,
	)

# 校验

def _validate_manifest_integrity(
		manifest: dict[str, Any], checksums: dict[str, Any]
) -> list[str]:
	"""验证 manifest 的完整性.

	计算 manifest 主体（不含 checksums 键）的 SHA-256，
	与存储的 manifest_body 校验和比对.
	"""
	errors: list[str] = []

	# 重建 manifest_body（去除 checksums 键）
	manifest_body = {k: v for k, v in manifest.items() if k != "checksums"}
	body_bytes = json.dumps(manifest_body, ensure_ascii=False, indent=2).encode("utf-8")
	actual_hash = bytes_sha256(body_bytes)
	expected_hash = checksums.get("manifest_body", "")

	if expected_hash:
		if not _timing_safe_eq(expected_hash, actual_hash):
			log.warning(f"manifest 校验和不匹配: expected={expected_hash[:16]}..., actual={actual_hash[:16]}...")
			errors.append("manifest 完整性校验失败")
	else:
		errors.append("缺少 manifest_body 校验和")

	return errors

def _timing_safe_eq(a: str, b: str) -> bool:
	"""Constant-time 字符串比较."""
	return hmac.compare_digest(a, b)

# 便捷函数

def get_music_original_name(manifest: dict[str, Any]) -> str:
	"""从 manifest 中获取音乐原始文件名."""
	music = manifest.get("music")
	if music:
		return music.get("original_name", "")
	return ""

def get_format_version(manifest: dict[str, Any]) -> str:
	"""获取 manifest 中的格式版本."""
	return manifest.get("format_version", FORMAT_VERSION)
