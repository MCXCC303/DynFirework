# Function 文件

## 什么是 function 文件

Minecraft Java Edition 1.13 起引入了 function 机制——将多条命令打包为单个可执行单元。`.mcfunction` 文件是纯文本命令列表，每行一条命令，执行时按顺序逐条执行。

```mcfunction
particle minecraft:flame ~ ~ ~ 0.1 0.1 0.1 0 10
particle minecraft:smoke ~ ~ ~ 0.5 0.5 0.5 0 20
playsound minecraft:entity.generic.explode master @a ~ ~ ~
```

执行 `/function namespace:path/to/function` 会一次性触发文件中所有命令。

## 在游戏中使用

function 文件需放在数据包的 `data/<命名空间>/function/` 目录下。执行语法为 `/function <命名空间>:<路径>`，其中的 `/` 对应目录层级，命名规则为 `[a-z0-9_/.-]+`。

有关数据包的完整结构，参考 "Minecraft 数据包"。

## 与 DynFirework 的关系

DynFirework 将烟花秀导出为一组 function 文件：每个 tick（或秒级时间点）对应一个 function，包含该时刻的所有粒子命令。在每个 function 的末尾调用 `schedule` 命令安排下一 tick 的 function 执行，以此实现连续播放。

## 参考链接

- [命令/function — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E5%91%BD%E4%BB%A4/function)
- [Function (Java Edition) — Minecraft Wiki](https://minecraft.wiki/Function_%28Java_Edition%29)
