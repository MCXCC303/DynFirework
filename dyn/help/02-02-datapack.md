# Minecraft 数据包

数据包是 Minecraft Java Edition 1.13 引入的内容分发格式。

## 结构

```
MyFireworkPack/
├── pack.mcmeta
└── data/
    └── <命名空间>/
        └── functions/
            ├── 0.mcfunction
            ├── 1.mcfunction
            ├── ...
            └── auto_exec.mcfunction
```

其中，`pack.mcmeta` 是声明格式版本和描述信息的 JSON 文件；命名空间用于区分不同数据包的内容，防止名称冲突；`functions/` 目录存放所有 `.mcfunction` 文件。

## 安装

1. 将数据包文件夹复制到存档的 `datapacks/` 目录下。
2. 在游戏中执行 `/reload`。
3. 执行 `/function <命名空间>:<function名称>`。

## pack_format 版本对照

| Minecraft 版本 | pack_format |
|---------------|-------------|
| 1.16.2 至 1.16.5 | 6 |
| 1.17 至 1.17.1   | 7 |
| 1.18 至 1.18.2   | 8 |
| 1.19 至 1.19.2   | 9 |
| 1.19.3        | 12 |
| 1.20 至 1.20.1   | 15 |
