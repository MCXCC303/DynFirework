# Function 文件

## 什么是 function 文件

在 Minecraft Java Edition 1.13 及更高版本中，function 是一种将多条命令打包为一个可执行单元的方式。一个 `.mcfunction` 文件是纯文本的命令列表，每行一条命令。在游戏中执行 function 时，文件中的所有命令按顺序被逐条执行。

```mcfunction
particle minecraft:flame ~ ~ ~ 0.1 0.1 0.1 0 10
particle minecraft:smoke ~ ~ ~ 0.5 0.5 0.5 0 20
playsound minecraft:entity.generic.explode master @a ~ ~ ~
```

执行 `/function namespace:explosion` 会一次性触发以上所有效果。

## 在游戏中使用

function 文件需要放在数据包的 `functions` 目录下。执行语法为 `/function <命名空间>:<function名称>`。

有关数据包的更多信息，参考第2.2章：Minecraft 数据包。

## 与 DynFirework 的关系

DynFirework 将烟花秀导出为一组 function 文件。每个 tick 对应一个 function 文件，包含该时刻的所有粒子命令。这些 function 通过 `schedule` 命令串联，执行入口 function 后按 tick 顺序自动播放。
