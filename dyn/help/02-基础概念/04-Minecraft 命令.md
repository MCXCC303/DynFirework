# Minecraft 命令

DynFirework 支持两种 Minecraft 粒子模组，对应不同的游戏版本和命令格式。在项目设置中选择目标 Minecraft 版本后，导出的命令自动适配。

## 命令格式对照

|        | DynFireworkMod | ColorBlock |
|--------|------------------------------|---------------------------|
| 模组   | DynFireworkMod | ColorBlock Mod |
| MC 版本 | 1.20.1 / 1.20.4 / 1.21 / 1.21.8 | 1.12.2 / 1.16.5 |
| 命令前缀 | `/dfp`（v1.x）/ `/df`（v2.0） | `/particleex` |
| 颜色支持 | 原生双色渐变 | rgbatickparameter 表达式 |
| 时间单位 | 秒（v2.0） / tick（v1.x） | tick |

各模组的详细命令格式和参数见后续章节。

## schedule 命令

`/schedule` 是 Minecraft 原生命令，用于在指定延迟后执行一个 function。DynFirework 利用此命令串联逐时间点的 function 执行链。

语法：

```mcfunction
schedule function <namespace>:<name> <time>
```

`time` 支持以下后缀：`t`（tick，默认）、`s`（秒）、`d`（游戏日）。1.20.2 起支持 `t` 后缀，之前版本仅接受纯数字（tick）。

示例：

```mcfunction
schedule function fireworks1:tick_0050 2s
schedule function fireworks1:tick_0100 100t
schedule function fireworks1:tick_0150 150
```

## 参考链接

- [命令/schedule — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E5%91%BD%E4%BB%A4/schedule)
- [命令 — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E5%91%BD%E4%BB%A4)
