# export_mcfunction.py
import os
from gui.lib import global_storage


def schedule_next_tick(datapack_namespace):
    try:
        for tick in range(global_storage.MAX_TICK + 1):
            # 在每个 tick 对应的命令列表后面添加一个 schedule 指令
            if tick == global_storage.MAX_TICK:
                break
            global_storage.add_command(tick, f'schedule function {datapack_namespace}:{tick + 1} 1t')
        return True
    except Exception as e:
        print(f"添加命令调度失败: {e}")
        return False


def export_mcfunction(output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            return False
    
    # 导出每个 tick 的命令
    try:
        for tick in range(global_storage.MAX_TICK + 1):
            filename = os.path.join(output_dir, f'{tick}.mcfunction')
            with open(filename, 'w') as f:
                for cmd in global_storage.commands_by_tick[tick]:
                    f.write(f'{cmd}\n')
        return True
    except Exception as e:
        print(f"导出命令文件失败: {e}")
        return False


def generate_auto_exec_file(output_dir, namespace):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(os.path.join(output_dir, 'auto_exec.mcfunction'), 'w') as f:
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
        with open(os.path.join(datapack_dir, 'pack.mcmeta'), 'w') as f:
            f.writelines(f'{{"pack":{{"pack_format": 6,\"description\":\"{datapack_desc}\"}}}}')
            
        return True, output_dir
    except Exception as e:
        print(f"生成数据包失败: {e}")
        return False, None
