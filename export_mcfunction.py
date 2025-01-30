# export_mcfunction.py
import os
import global_storage


def export_mcfunction(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for tick in range(global_storage.MAX_TICK + 1):
        filename = os.path.join(output_dir, f'{tick}.mcfunction')
        f = open(filename, 'w')
        for cmd in global_storage.commands_by_tick[tick]:
            f.write(f'{cmd}\n')


def generate_auto_exec_file(output_dir, namespace):
    with open(os.path.join(output_dir, 'auto_exec.mcfunction'), 'w') as f:
        for tick in range(global_storage.MAX_TICK + 1):
            f.write(f"schedule function {namespace}:{tick + 1} {tick}t\n")


def generate_data_pack(datapack_name, datapack_namespace, datapack_desc):
    output_dir = os.path.dirname(os.path.abspath(__file__)) + f"/{datapack_name}/data/{datapack_namespace}/functions/"
    datapack_dir = os.path.dirname(os.path.abspath(__file__)) + f"/{datapack_name}/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(datapack_dir, 'pack.mcmeta'), 'w') as f:
        f.writelines(f'{{"pack":{{"pack_format": 6,\"description\":\"{datapack_desc}\"}}}}')
