# export_mcfunction.py
import os
from . import global_storage


def export_mcfunction(output_dir, namespace):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            return False
    
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
        return True
    except Exception as e:
        print(f"导出命令文件失败: {e}")
        return False


def generate_auto_exec_file(output_dir, namespace):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(os.path.join(output_dir, 'auto_exec.mcfunction'), 'w', encoding='utf-8', newline='\n') as f:
            for tick in range(global_storage.MAX_TICK + 1):
                f.write(f"schedule function {namespace}:{tick + 1} {tick}t\n")
        return True
    except Exception as e:
        print(f"生成自动执行文件失败: {e}")
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
            
        return True, output_dir
    except Exception as e:
        print(f"生成数据包失败: {e}")
        return False, None










