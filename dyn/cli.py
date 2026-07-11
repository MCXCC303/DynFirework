"""
用法::

    python -m dyn.cli <command> [options]

命令::

    info             显示项目信息
    export points    导出位置点到 JSON
    export datapack  导出 Minecraft 数据包
    export music     提取嵌入的音乐文件
    export table     导出元素表 (JSON / CSV)
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any

from dyn.lib import fireworks as fw
from dyn.lib import global_storage, export_mcfunction
from dyn.lib import trajectories as traj
from dyn.lib.backend_registry import set_backend, resolve_mc_version, BackendType, MC_VERSION_MAP
from dyn.lib.export_helpers import (
	TRAJ_FUNC_MAP, FW_FUNC_MAP, build_traj_kwargs, fill_fw_kwargs,
)
from dyn.models.elements import TrajectoryElement, FireworkElement
from dyn.models.timeline import Project

log = logging.getLogger("dyn.cli")

def _load_project(path: str):
	"""加载 .dyn 项目文件."""
	# 确保项目根目录在 sys.path 中
	project_root = Path(__file__).parent.parent
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))
	log.debug(f"CLI 加载项目: {path}")
	return Project.from_file(path)

# info

def cmd_info(args: argparse.Namespace) -> int:
	"""显示项目基本信息."""
	proj = _load_project(args.project)
	print(f"项目名称:   {proj.name}")
	print(f"BPM:        {proj.bpm:.0f}")
	print(f"MC 版本:    {proj.mc_version}")
	print(f"拍号:       {proj.time_signature[0]}/{proj.time_signature[1]}")
	print(f"Tick/拍:    {proj.ticks_per_beat}")
	print(f"总 Tick:    {proj.total_duration_ticks}")
	print(f"元素数量:   {len(proj.all_elements)}")
	print(f"  轨迹:     {len(proj.trajectories)}")
	print(f"  烟花:     {len(proj.fireworks)}")
	print(f"  轨迹烟花: {len(proj.traj_fireworks)}")
	print(f"保存位置:   {len(proj.saved_positions)}")
	print(f"音乐:       {proj.music_original_name if proj.has_music else '无'}")
	if proj.has_music:
		print(f"  大小:     {len(proj.music_data):,} 字节")
	return 0

# export points

def cmd_export_points(args: argparse.Namespace) -> int:
	"""导出位置点到 JSON 文件."""
	proj = _load_project(args.project)
	pts = proj.saved_positions
	if not pts:
		print("项目中没有保存的位置点。", file=sys.stderr)
		return 1

	output = args.output or "positions.json"
	data: dict[str, Any] = {
		"project": proj.name,
		"count": len(pts),
		"points": pts,
	}
	Path(output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
	print(f"已导出 {len(pts)} 个位置点到: {output}")
	return 0

# export music

def cmd_export_music(args: argparse.Namespace) -> int:
	"""提取嵌入的音乐文件."""
	proj = _load_project(args.project)
	if not proj.has_music:
		print("项目中没有嵌入的音乐。", file=sys.stderr)
		return 1

	suffix = Path(proj.music_original_name).suffix or ".mp3"
	output = args.output or f"{proj.name}_music{suffix}"
	Path(output).write_bytes(proj.music_data)
	print(f"已提取音乐到: {output} ({len(proj.music_data):,} 字节)")
	return 0

# export table

def cmd_export_table(args: argparse.Namespace) -> int:
	"""导出元素表."""
	proj = _load_project(args.project)
	elements = proj.all_elements
	if not elements:
		print("项目中没有元素。", file=sys.stderr)
		return 1

	fmt = args.format or "json"
	output = args.output or f"{proj.name}_elements.{fmt}"

	rows: list[dict[str, Any]] = []
	type_names = {"trajectory": "轨迹", "firework": "烟花", "traj_firework": "轨迹烟花"}
	for e in elements:
		etype = e.element_type.value if hasattr(e.element_type, "value") else str(e.element_type)
		rows.append({
			"id": e.id,
			"type": etype,
			"type_cn": type_names.get(etype, etype),
			"name": e.name,
			"start_tick": e.start_tick,
			"duration_ticks": e.duration_ticks,
			"enabled": e.enabled,
		})

	if fmt == "csv":
		fieldnames = ["id", "type", "type_cn", "name", "start_tick", "duration_ticks", "enabled"]
		with open(output, "w", newline="", encoding="utf-8") as f:
			w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
			w.writeheader()
			w.writerows(rows)
	else:
		data = {"project": proj.name, "count": len(rows), "elements": rows}
		Path(output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

	print(f"已导出 {len(rows)} 个元素到: {output}")
	return 0

# export datapack

def _do_sync_export(
		elements: list[Any],
		output_dir: str,
		namespace: str,
		datapack_name: str,
		description: str,
		pack_format: int,
		mc_version: str,
) -> tuple[bool, str]:
	"""同步导出数据包（无 Qt 依赖）."""
	try:
		info = resolve_mc_version(mc_version)
		set_backend(info.backend)
	except KeyError:
		log.warning(f"CLI 导出: 未知MC版本 {mc_version}, 使用默认DFP后端")
		set_backend(BackendType.DFP)

	global_storage.commands_by_tick.clear()
	global_storage.MAX_TICK = 0

	total = len(elements)
	for i, elem in enumerate(elements):
		if not elem.enabled:
			continue

		if isinstance(elem, TrajectoryElement):
			_export_traj_sync(elem, traj)
		elif isinstance(elem, FireworkElement):
			_export_fw_sync(elem, fw)
		elif hasattr(elem, "traj_type") and hasattr(elem, "fw_type"):
			_export_tf_sync(elem, traj, fw)

		if (i + 1) % 10 == 0:
			print(f"  进度: {i + 1}/{total}")

	pack_dir = Path(output_dir) / datapack_name
	func_dir = pack_dir / "data" / namespace / "functions"
	func_dir.mkdir(parents=True, exist_ok=True)

	mcmeta = {"pack": {"pack_format": pack_format, "description": description}}
	(pack_dir / "pack.mcmeta").write_text(
		json.dumps(mcmeta, ensure_ascii=False, indent=2), encoding="utf-8"
	)

	export_mcfunction.export_mcfunction(str(func_dir), namespace)
	export_mcfunction.generate_auto_exec_file(str(func_dir), namespace)

	return True, f"导出完成: {pack_dir}"

def _export_traj_sync(elem: Any, traj_mod: Any) -> None:
	func = getattr(traj_mod, TRAJ_FUNC_MAP.get(elem.traj_type, "launch_trajectory"), None)
	if func is None:
		log.warning(f"CLI 导出: 未知轨迹类型 {elem.traj_type}, 元素 id={elem.id}")
		return
	pos = elem.start_position
	end = elem.end_position
	kwargs = build_traj_kwargs(elem, pos.x, pos.y, pos.z,
	                           end.x, end.y, end.z,
	                           elem.duration_ticks)
	func(elem.start_tick, **kwargs)

def _export_fw_sync(elem: Any, fw_mod: Any) -> None:
	func = getattr(fw_mod, FW_FUNC_MAP.get(elem.fw_type, "basic_single_layer_firework"), None)
	if func is None:
		log.warning(f"CLI 导出: 未知烟花类型 {elem.fw_type}, 元素 id={elem.id}")
		return
	pos = elem.position
	kwargs: dict[str, Any] = {
		"tick": elem.start_tick,
		"x": pos.x, "y": pos.y, "z": pos.z,
		"duration": elem.duration_ticks / 20,
		"lifetime": elem.duration_ticks / 20,
	}
	fill_fw_kwargs(elem, kwargs)
	func(**kwargs)

def _export_tf_sync(elem: Any, traj_mod: Any, fw_mod: Any) -> None:
	"""导出 TrajFireworkElement."""
	pos = elem.start_position
	end = elem.mid_position or pos

	func = getattr(traj_mod, TRAJ_FUNC_MAP.get(elem.traj_type, "launch_trajectory"), None)
	if func:
		kwargs = build_traj_kwargs(elem, pos.x, pos.y, pos.z,
		                           end.x, end.y, end.z,
		                           elem.traj_duration_ticks)
		func(elem.start_tick, **kwargs)

	fw_func = getattr(fw_mod, FW_FUNC_MAP.get(elem.fw_type, "basic_single_layer_firework"), None)
	if fw_func:
		fw_kwargs: dict[str, Any] = {
			"tick": elem.fw_start_tick,
			"x": end.x, "y": end.y, "z": end.z,
			"duration": elem.fw_duration_ticks / 20,
			"lifetime": elem.fw_duration_ticks / 20,
		}
		fill_fw_kwargs(elem, fw_kwargs)
		fw_func(**fw_kwargs)

def cmd_export_datapack(args: argparse.Namespace) -> int:
	"""导出 Minecraft 数据包."""
	proj = _load_project(args.project)
	elements = proj.all_elements
	if not elements:
		print("项目中没有元素，无法导出数据包。", file=sys.stderr)
		return 1

	output_dir = args.output or "."
	namespace = args.namespace or "fireworks1"
	name = args.name or proj.name or "DynFirework"
	desc = args.description or "DynFirework generated datapack"

	# 从 MC 版本映射获取 pack_format
	mc_ver = args.mc_version or proj.mc_version
	info = MC_VERSION_MAP.get(mc_ver)
	if info:
		pack_format = args.pack_format or info.pack_format
	else:
		pack_format = args.pack_format or 15

	print(f"导出数据包: {name}")
	print(f"  输出目录:   {Path(output_dir).resolve()}")
	print(f"  命名空间:   {namespace}")
	print(f"  MC 版本:   {mc_ver} (pack_format={pack_format})")
	print(f"  元素数量:   {len(elements)}")

	ok, msg = _do_sync_export(
		elements, output_dir, namespace, name, desc, pack_format, mc_ver
	)
	print(msg)
	return 0 if ok else 1

# CLI 入口

def _add_common_args(sub: argparse.ArgumentParser) -> None:
	sub.add_argument("project", help=".dyn 项目文件路径")

def _add_output_arg(sub: argparse.ArgumentParser, default: str, help_text: str) -> None:
	sub.add_argument("-o", "--output", default=None, help=help_text)

def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="dyncli",
		description="DynFirework 命令行工具",
	)
	sub = parser.add_subparsers(dest="command", required=True)

	# info
	p = sub.add_parser("info", help="显示项目信息")
	_add_common_args(p)

	# export points
	p = sub.add_parser("points", help="导出位置点到 JSON")
	_add_common_args(p)
	_add_output_arg(p, "positions.json", "输出 JSON 文件路径")

	# export music
	p = sub.add_parser("music", help="提取嵌入的音乐文件")
	_add_common_args(p)
	_add_output_arg(p, None, "输出音频文件路径（默认: <项目名>_music.<ext>）")

	# export table
	p = sub.add_parser("table", help="导出元素表")
	_add_common_args(p)
	_add_output_arg(p, None, "输出文件路径")
	p.add_argument("-f", "--format", choices=["json", "csv"], default="json",
	               help="输出格式 (默认: json)")

	# export datapack
	p = sub.add_parser("datapack", help="导出 Minecraft 数据包")
	_add_common_args(p)
	_add_output_arg(p, ".", "输出目录路径")
	p.add_argument("--namespace", default=None, help="命名空间 (默认: fireworks1)")
	p.add_argument("--name", default=None, help="数据包名称 (默认: 项目名)")
	p.add_argument("--description", default=None, help="数据包描述")
	p.add_argument("--mc-version", default=None, help="MC 版本 (覆盖项目设置)")
	p.add_argument("--pack-format", type=int, default=None, help="pack_format (覆盖自动推导)")

	return parser

def main(argv: list[str] | None = None) -> int:
	parser = build_parser()
	args = parser.parse_args(argv)

	handlers = {
		"info": cmd_info,
		"points": cmd_export_points,
		"music": cmd_export_music,
		"table": cmd_export_table,
		"datapack": cmd_export_datapack,
	}
	handler = handlers.get(args.command)
	if handler is None:
		parser.print_help()
		return 1
	log.debug(f"CLI 命令: {args.command}, project={args.project}")
	return handler(args)

if __name__ == "__main__":
	sys.exit(main())
