# export_mcfunction.py
import logging
import os

from . import global_storage

log = logging.getLogger("dyn.lib.export_mcfunction")

def export_mcfunction(output_dir, namespace):
	# 确保输出目录存在
	if not os.path.exists(output_dir):
		try:
			os.makedirs(output_dir)
			log.debug(f"创建输出目录: {output_dir}")
		except Exception as e:
			log.error(f"创建输出目录失败: {e}")
			return False

	total_commands = 0
	total_files = 0
	# 导出每个 tick 的命令，如果 tick 不存在则创建空文件
	try:
		for tick in range(global_storage.MAX_TICK + 1):
			filename = os.path.join(output_dir, f'{tick}.mcfunction')
			commands = global_storage.commands_by_tick.get(tick, [])

			# Add schedule command for the next tick
			if tick < global_storage.MAX_TICK:
				commands.append(f'schedule function {namespace}:{tick + 1} 1t')

			# 写入文件，每行都加换行符（Minecraft要求）
			with open(filename, 'w', encoding='utf-8', newline='\n') as f:
				for cmd in commands:
					f.write(f'{cmd}\n')
			total_commands += len(commands)
			total_files += 1
		log.debug(f"导出完成: {total_files} 个 .mcfunction 文件, {total_commands} 条命令 -> {output_dir}")
		return True
	except Exception as e:
		log.error(f"导出命令文件失败: {e}", exc_info=True)
		return False

def generate_auto_exec_file(output_dir, namespace):
	try:
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		auto_exec_path = os.path.join(output_dir, 'auto_exec.mcfunction')
		with open(auto_exec_path, 'w', encoding='utf-8', newline='\n') as f:
			for tick in range(global_storage.MAX_TICK + 1):
				f.write(f"schedule function {namespace}:{tick + 1} {tick}t\n")
		log.debug(f"生成 auto_exec.mcfunction: {global_storage.MAX_TICK + 1} 条 schedule 命令")
		return True
	except Exception as e:
		log.error(f"生成自动执行文件失败: {e}", exc_info=True)
		return False

def generate_data_pack(datapack_name, datapack_namespace, datapack_desc):
	try:
		output_dir = global_storage.project_dir + f"/{datapack_name}/data/{datapack_namespace}/functions/"
		datapack_dir = global_storage.project_dir + f"/{datapack_name}/"

		# 确保目录存在
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		# 创建pack.mcmeta文件
		with open(os.path.join(datapack_dir, 'pack.mcmeta'), 'w', encoding='utf-8', newline='\n') as f:
			f.writelines(f'{{"pack":{{"pack_format": 6,\"description\":\"{datapack_desc}\"}}}}')

		log.debug(f"创建数据包结构: {datapack_dir}")
		return True, output_dir
	except Exception as e:
		log.error(f"生成数据包失败: {e}", exc_info=True)
		return False, None
