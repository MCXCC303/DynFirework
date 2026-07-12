# ColorBlock 命令

ColorBlock Mod 是适用于 Minecraft 1.12.2 / 1.16.5 的粒子模组，使用 `/particleex` 前缀的命令。

## 命令格式

需在命令中指定原版粒子类型并配置各轴的缩放参数：

```mcfunction
particleex normal <x> <y> <z> <dx> <dz> <dy> <speed> <count> <lifetime> <particle> <rgbatickparameter>
```

时间单位均为 tick。

## rgbatickparameter 子命令

支持逐 tick 颜色插值，格式为 `R1 G1 B1 A1 R2 G2 B2 A2 ...`，每 4 个数字对应一个时间点的 RGBA 颜色值（0-255 整数）。各时间点之间线性插值。

例如 `255 0 0 0 0 0 255 255` 表示从红色渐变到蓝色（透明度同速率变化）。

## 架构说明

ColorBlock Mod 的 `/particleex normal` 每 tick 在指定坐标生成指定数量的原版粒子，通过 rgbatickparameter 实现逐粒子颜色控制。与 DynFireworkMod 不同，所有粒子计算在服务端完成，没有客户端本地生成能力。

详细的子命令参数见 ColorBlock 元素与参数文档。

## 参考链接

- [命令/particle — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E5%91%BD%E4%BB%A4/particle)
- [粒子 — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E7%B2%92%E5%AD%90)
