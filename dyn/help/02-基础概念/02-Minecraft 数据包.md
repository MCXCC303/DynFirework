# Minecraft 数据包

数据包是 Minecraft Java Edition 1.13 引入的内容分发格式，允许玩家通过 JSON 和 function 文件自定义游戏内容。

## 结构

```
datapack-name/
  pack.mcmeta
  pack.png（可选）
  data/
    <命名空间>/
      function/
        tick_0000.mcfunction
        tick_0001.mcfunction
        ...
        auto_exec.mcfunction
```

- `pack.mcmeta`：声明数据包元数据的 JSON 文件
- 命名空间：区分不同来源的内容，防止名称冲突
- `function/`：存放 `.mcfunction` 文件的目录

## 安装

1. 将数据包文件夹放入存档的 `datapacks/` 目录
2. 在游戏中执行 `/reload`
3. 执行 `/function <命名空间>:<function名称>`

## pack_format 版本对照

`pack_format` 用于声明数据包兼容的 Minecraft 版本。1.21.4 起引入 `min_format`/`max_format` 替代单一 `pack_format`，支持声明兼容的版本范围。

| Minecraft 版本 | pack_format |
|---------------|-------------|
| 1.13 至 1.14.4 | 4 |
| 1.15 至 1.16.1 | 5 |
| 1.16.2 至 1.16.5 | 6 |
| 1.17 至 1.17.1 | 7 |
| 1.18 至 1.18.2 | 9 |
| 1.19 至 1.19.2 | 10 |
| 1.19.3 | 12 |
| 1.19.4 | 13 |
| 1.20 至 1.20.1 | 15 |
| 1.20.2 | 18 |
| 1.20.3 至 1.20.4 | 22 |
| 1.20.5 至 1.20.6 | 41 |
| 1.21 | 48 |
| 1.21.2 至 1.21.3 | 57 |
| 1.21.4 | 61 |

DynFirework 导出时根据项目设置的 Minecraft 版本自动填入正确的 pack_format。

## 参考链接

- [数据包 — 中文 Minecraft Wiki](https://zh.minecraft.wiki/%E6%95%B0%E6%8D%AE%E5%8C%85)
- [Data pack — Minecraft Wiki](https://minecraft.wiki/Data_pack)
