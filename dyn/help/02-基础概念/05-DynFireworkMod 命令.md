# DynFireworkMod 命令

DynFireworkMod 是适用于 Minecraft 1.20.1+ 的高性能粒子模组。v2.0 起使用 `/df` 前缀的高层烟花命令，客户端本地计算全部粒子。

## 命令格式

v2.0 每个 `/df` 子命令描述一个完整烟花效果，按效果类型分为爆炸类、轨迹类、特殊效果类和组合类。时间参数单位为秒（浮点数）。

v1.x 命令格式（`/dfp`，向后兼容）：

```
/dfp <x> <y> <z> <r1> <g1> <b1> <r2> <g2> <b2> <vx> <vy> <vz> <lifetime>
```

每粒子一条命令，颜色 0-255，速度任意浮点，生命周期 1-1200 tick。位置支持 `~` 相对坐标。

## 架构原理

模组采用"服务端下发参数 → 客户端本地计算渲染"架构。服务端仅序列化烟花参数（约 75-150 字节），客户端运行生成算法（斐波那契球面、轨迹采样、噪声扰动）产生全部粒子。一个参数包可在客户端生成数千粒子，网络开销为零增量。

## 客户端配置

配置文件 `.minecraft/config/dynfirework-client.json`：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `particleSpacing` | 0.1 | 粒子间距（格），影响空间采样密度 |
| `maxParticles` | 65536 | 全局粒子上限 |

详细的子命令参数见 DynFireworkMod 元素与参数文档。

## 参考链接

- [粒子 — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E7%B2%92%E5%AD%90)
- [命令/particle — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E5%91%BD%E4%BB%A4/particle)
