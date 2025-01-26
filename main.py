# main.py
import os
import basic_fireworks
import export_mcfunction
import global_storage
import firework_trajectories


def schedule_next_tick(datapack_namespace):
    for tick in range(global_storage.MAX_TICK + 1):
        # 在每个 tick 对应的命令列表后面添加一个 schedule 指令
        if tick == global_storage.MAX_TICK:
            break
        global_storage.add_command(tick, f'schedule function {datapack_namespace}:{tick + 1} 1t')


if __name__ == '__main__':
    # Generate a datapack (1.16.5)
    datapack_namespace = 'fireworks1'
    datapack_name = 'Fireworks'
    datapack_description = 'Fireworks Test'
    output_dir = os.path.dirname(os.path.abspath(__file__)) + f"/{datapack_name}/data/{datapack_namespace}/functions/"
    datapack_dir = os.path.dirname(os.path.abspath(__file__)) + f"/{datapack_name}/"
    export_mcfunction.generate_data_pack(datapack_name, datapack_namespace, datapack_description)
    # =====这是一个示例=====
    firework_trajectories.expanding_trajectory_with_random_offset(
        end_tick=39,
        x0=0, y0=0, z0=0,
        x1=10, y1=100, z1=10,
        k=1.2,
        m0=2.0,
        duration=2.0,
        lifetime=1.0,
        interval_ticks=5,
        points_per_tick=5,
        range_x=0.15, range_y=0.15, range_z=0.15,
        particle_count=4,
        speed_factor=0.1
    )
    basic_fireworks.clustered_firework(
        tick=39,
        x=10.0, y=100.0, z=10.0,
        start_color=(255, 0, 0),
        end_color=(255, 255, 255),
        speed=25.0,
        horizontal_angle_step=45,
        vertical_angle_step=45,
        track_count=5,
        spread_angle=15,
        duration=3.5,
        lifetime=1.0
    )

    firework_trajectories.launch_spark_trajectory(
        end_tick=60,
        x0=30, y0=0, z0=30,
        x1=50, y1=100, z1=30,
        duration=2.0,
        k=1.2,
        m0=2.0,
        lifetime=0.5,
        particle_count=5
    )
    basic_fireworks.basic_single_layer_firework(
        tick=60,
        x=50.0, y=100.0, z=30.0,
        start_color=(255, 0, 0),
        end_color=(255, 255, 0),
        speed=30,
        horizontal_angle_step=30,
        vertical_angle_step=30,
        duration=2.0,
        lifetime=1.0
    )

    firework_trajectories.launch_spark_trajectory(
        end_tick=70,
        x0=10, y0=0, z0=10,
        x1=-10, y1=100, z1=-20,
        duration=2.0,
        k=1.2,
        m0=2.0,
        lifetime=0.5,
        particle_count=5
    )
    basic_fireworks.basic_single_layer_firework(
        tick=70,
        x=-10.0, y=100.0, z=-20.0,
        start_color=(255, 0, 0),
        end_color=(255, 255, 0),
        speed=30,
        horizontal_angle_step=30,
        vertical_angle_step=30,
        duration=2.0,
        lifetime=1.0
    )

    firework_trajectories.trajectory_with_random_offset(
        end_tick=90,
        x0=0, y0=0, z0=0,
        x1=30, y1=100, z1=20,
        k=1.2,
        m0=2.0,
        duration=2.0,
        lifetime=1.0,
        interval_ticks=5,
        points_per_tick=5,
    )
    basic_fireworks.basic_double_layer_firework(
        tick=90,
        x=30.0, y=100.0, z=20.0,
        inner_start_color=(255, 0, 0),
        inner_end_color=(255, 255, 0),
        outer_start_color=(255, 0, 0),
        outer_end_color=(255, 255, 255),
        inner_speed=15,
        outer_speed=25,
        outer_horizontal_angle_step=30,
        outer_vertical_angle_step=30,
        duration=2.0,
        lifetime=1.0,
    )

    firework_trajectories.launch_trajectory(
        end_tick=110,
        x0=0, y0=0, z0=0,
        x1=10, y1=100, z1=10,
        start_color=(255, 255, 0),
        end_color=(255, 255, 255),
        k=1.2,
        m0=2.0,
        duration=2.0,
        lifetime=1.0,
        rho=3
    )

    basic_fireworks.basic_single_layer_firework(
        tick=110,
        x=10.0, y=100.0, z=10.0,
        start_color=(255, 100, 0),
        end_color=(255, 100, 0),
        speed=35.0,
        horizontal_angle_step=20,
        vertical_angle_step=20,
        duration=4.0,
        lifetime=1.5
    )
    # =====这是一个示例=====
    print(f"max tick={global_storage.MAX_TICK}")
    # 调用 schedule_next_tick 来生成 schedule 指令
    schedule_next_tick(datapack_namespace)

    # 输出 mcfunction 文件
    export_mcfunction.export_mcfunction(output_dir)
    # Create auto exec function file
    # export_mcfunction.generate_auto_exec_file(output_dir, datapack_namespace)
