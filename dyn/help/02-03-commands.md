# Minecraft 命令

DynFirework 支持两种 Minecraft 粒子模组，对应不同的游戏版本和命令格式。在项目设置中选择目标 Minecraft 版本后，导出的命令会自动适配。

---

## 命令格式对照

|        | dfp（DynFirework Particles） | particleex（Colorblock） |
|--------|------------------------------|---------------------------|
| 模组   | DynFirework Particles Mod    | Colorblock Mod |
| MC 版本 | 1.20.1 / 1.20.4 / 1.21 | 1.12.2 / 1.16.5 |
| 命令前缀 | `/dfp` | `/particleex` |
| 颜色支持 | 原生双色渐变 | rgbatickparameter 表达式 |
| 粒子类型 | 模组内置 | `minecraft:end_rod` |

---

## schedule 命令

`schedule` 命令用于在指定的延迟后执行一个 function。两种后端通用。

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

---

## dfp 命令（DynFirework Particles Mod）

`dfp` 是 DynFirework Particles Mod 提供的自定义粒子命令。支持颜色渐变、精确的速度控制和独立的粒子生命周期。

**适用版本：Minecraft 1.20.1 / 1.20.4 / 1.21**

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

### dfp 子命令说明

DynFirework 内部使用三种 dfp 调用模式：

| 模式 | 速度 | 用途 |
|------|------|------|
| 静态粒子 | `0 0 0` | 烟花爆炸效果 — 粒子在计算位置静态显示 |
| 火花粒子 | 真实速度 | 轨迹尾迹 — 暖白→金色渐变，速度向后散射 |
| 速度粒子 | 真实速度 | 膨胀球体、特殊效果 — 粒子由模组物理引擎驱动 |

---

## particleex 命令（Colorblock Mod）

`particleex` 是 Colorblock Mod 提供的粒子命令扩展。通过 `rgbatickparameter` 子命令实现基于粒子生命周期的颜色渐变，或通过 `normal` 子命令发射带速度的粒子。

**适用版本：Minecraft 1.12.2 / 1.16.5**

### rgbatickparameter 子命令

用于颜色随时间渐变的静态粒子（烟花爆炸效果）。

语法：

```
particleex rgbatickparameter minecraft:end_rod <x> <y> <z> <dx> <dy> <dz> <speed> <count> "<color_expr>" <size> <count> <lifetime>
```

参数说明：

| 参数 | 说明 |
|------|------|
| `x y z` | 粒子生成位置 |
| `dx dy dz` | 扩散范围，烟花使用 `0.0 0.0 0.0` |
| `speed` | 粒子速度，烟花使用 `0.0` |
| `count` | 每 tick 生成数量，固定 `1.0` |
| `color_expr` | 颜色表达式（见下方说明） |
| `size` | 粒子大小，固定 `0.1` |
| `particle_count` | 粒子数量，固定 `1` |
| `lifetime` | 存活时间（tick） |

颜色表达式 `color_expr` 格式：

```
x=0;y=0;z=0;cr=(R1+(R2-R1)*(t/lifetime))/255.0;cg=(G1+(G2-G1)*(t/lifetime))/255.0;cb=(B1+(B2-B1)*(t/lifetime))/255.0
```

其中 `t` 是粒子的当前存活时间，模组在渲染每帧时自动计算，实现平滑的颜色渐变。

### normal 子命令

用于带速度的粒子（轨迹火花、膨胀特效等）。使用固定白色，由速度驱动运动。

语法：

```
particleex normal minecraft:end_rod <x> <y> <z> <r> <g> <b> <a> <vx> <vy> <vz> <rx> <ry> <rz> <count> <lifetime>
```

参数说明：

| 参数 | 说明 |
|------|------|
| `x y z` | 粒子生成位置 |
| `r g b a` | 颜色和透明度（0.0-1.0），火花使用 `1.0 1.0 1.0 1.0` |
| `vx vy vz` | 初速度矢量 |
| `rx ry rz` | 随机扩散范围，固定 `0 0 0` |
| `count` | 粒子数量，固定 `1` |
| `lifetime` | 存活时间（tick） |

**注意：** normal 子命令不支持颜色渐变。对于膨胀球体和特殊效果（双螺旋、旋转环等），DynFirework 使用起点和终点的中点颜色作为单一颜色。

---

## 两种后端的区别总结

| 特性 | dfp | particleex |
|------|-----|------------|
| 颜色渐变方式 | 原生 RGB 起止色 | rgbatickparameter 数学表达式 |
| 速度粒子颜色 | 支持渐变 | 固定单色（取中点） |
| 粗火花实现 | 逐粒子循环生成 | 一条命令含范围参数 |
| 依赖模组 | DynFirework Particles | Colorblock |
