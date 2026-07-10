# Minecraft 命令

## schedule 命令

`schedule` 命令用于在指定的延迟后执行一个 function。

语法：

```mcfunction
schedule function <namespace>:<name> <time>
```

其中 `namespace:name` 是要执行的 function 标识符，`time` 是延迟时间，默认单位为 game tick（1/20 秒），也可以使用 `s`（秒）或 `d`（游戏日）作为后缀。

示例：

```mcfunction
schedule function fireworks1:50 100t    # 100 tick 后执行 function 50
schedule function fireworks1:10 1s      # 1 秒后执行
```

## dfp 命令（DynFirework Particle）

`dfp` 是 DynFirework Mod 提供的自定义粒子命令。与原版 `particle` 命令相比增加了颜色渐变、精确的速度控制和独立的粒子生命周期。

语法：

```
dfp <x> <y> <z> <r1> <g1> <b1> <r2> <g2> <b2> <vx> <vy> <vz> <lifetime>
```

参数说明：

| 参数 | 说明 |
|------|------|
| `x y z` | 粒子生成位置坐标 |
| `r1 g1 b1` | 起始颜色，RGB 三个通道，0 至 255 |
| `r2 g2 b2` | 结束颜色，粒子在生命周期内从起始色渐变到结束色 |
| `vx vy vz` | 初速度矢量。`0 0 0` 时粒子静止 |
| `lifetime` | 存活时间（tick），超时后消失 |

示例：

```
dfp 10.5 64.0 -5.2 255 100 0 255 50 0 0 0 0 15
```

在 (10.5, 64, -5.2) 处生成粒子，颜色从橙色 (255,100,0) 渐变到暗橙色 (255,50,0)，静止，存活 15 tick。
