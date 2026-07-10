<h1 align="center">DynFirework</h1>

<p align="center">
  <b>更真实自然的烟花！</b>
</p>
<p align="center">
    <img src="https://img.shields.io/badge/Minecraft-1.12.2 1.16.5-green?style=for-the-badge">
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/License-GPL--3.0-important?style=for-the-badge">
    </a>
    <a href="https://qm.qq.com/q/m6XfOuCtVe">
        <img src="https://img.shields.io/badge/QQ-技术交流/反馈群-blue?style=for-the-badge">
    </a>
    <a href="https://space.bilibili.com/288309681">
        <img src="https://img.shields.io/badge/bilibili-TianKong_y-pink?style=for-the-badge">
    </a>
</p>

## > 公告

[*DynFirework Mod v2.0*](https://github.com/TianKong-y/DynFireworkMod)已开源，内置多种烟花样式，可直接通过调整指令参数实现基于客户端的烟花召唤，可用于服务器场景，发包数量极少，网络占用小。

## > 简介

*DynFirework*是使用Python (基于**PyQt5**框架) 编写的*Minecraft*粒子烟花生成器，提供了图形化界面和核心库函数，用以生成包含复杂烟花效果的数据包文件(.mcfunction)。

**[介绍视频](https://www.bilibili.com/video/BV1xYxxeqEMf/)**

## > 前置Mod及版本兼容性

*DynFirework*的输出指令基于[Colorblock](https://www.bilibili.com/read/cv32079719/)的`rgbatickparameter`和`normal`子指令，以实现渐变颜色粒子。

由于*Colorblock*仅支持1.12.2和1.16.5版本，当前版本的*DynFirework v1.1*生成的指令也只在上述2个版本有效。

理论上可以通过修改输出指令部分的代码并移除渐变色功能，使用原版particle指令以兼容全部版本，这是之后的更新内容之一。

## > 依赖

在源码所在根目录打开PowerShell，执行如下指令以下载依赖
```bash
pip install -r requirements.txt
```

## > 使用方法

### 方法1.图形化编辑

*DynFirework* 提供基于 **PyQt5** 编写的图形化界面，方便用户配置和生成烟花。

使用方法为，下载源代码后，执行 `python main.py` 启动图形界面，在界面中选择并配置所需的轨迹和烟花类型。

生成器会在根目录下创建一个与GUI界面设置中命名相同的子文件夹（数据包名称），该文件夹即为创建的数据包，可直接复制到存档中的`datapacks`目录下进行使用。

执行时，根据你在图形界面中设置的**命名空间(namespace)**，在游戏内执行`/function <你的命名空间>:0`。 命名空间的命名规范请参考[Minecraft Wiki](https://zh.minecraft.wiki/w/%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4ID?variant=zh-cn#%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4)。

### 方法2.核心库调用

对于需要更高自由度或希望将烟花生成集成到其他Python脚本的用户，可以直接调用 `gui/lib/` 目录下的核心库函数 (如 `basic_fireworks.py`, `firework_trajectories.py`) 来手动调用生成轨迹、烟花的函数。具体用法请参考[templates.md](templates.md)。

生成器会在代码目录下创建一个functions子文件夹，一个tick对应该文件夹下的一个.mcfuntion文件。

如果你不了解.mcfuntion，可以参考[BV1aP41167ef](https://www.bilibili.com/video/BV1aP41167ef)

执行时，根据对namespace的命名，在游戏内执行`/function namespace:0`。 namespace的命名规范请参考[Minecraft Wiki](https://zh.minecraft.wiki/w/%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4ID?variant=zh-cn#%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4)


## > 效果展示

<div align=center>  <img src="https://s2.loli.net/2024/09/30/15STOnguXb2vINA.png" height="300" width="300">  </div>
<p align="center"><b>双层烟花</b></p>
<div align=center>  <img src="https://s2.loli.net/2024/09/30/jOSAcTvmf4d7PCg.png" height="300" width="300">  </div>
<p align="center"><b>双层渐变烟花</b></p>
<div align=center>  <img src="https://s2.loli.net/2024/09/30/JuYBx7DfncHASQj.png" height="300" width="300">  </div>  
<p align="center"><b>单层渐变烟花</b></p>

## > 更新日志

- v1.0 2024.9.30 初始版本，提供多种烟花轨迹模板和烟花模板
- v1.1 2025.1.26 更新图形化界面 (基于 Tkinter)
- v1.2 2025.4.30 将 GUI 框架迁移至 PyQt5，重构项目结构。

## > 作者&技术交流/反馈群

- bilibili：[TianKong_y](https://space.bilibili.com/288309681)
- QQ：[技术交流/反馈群](https://qm.qq.com/q/m6XfOuCtVe)

## > 鸣谢

- MCXCC303 编写v1.1图形化界面

## > 项目统计

<div align="center">

![Repobeats analytics image](https://repobeats.axiom.co/api/embed/c15d66d9db4d74fe612ab88ffb75fd3231bd278d.svg "Repobeats analytics image")

</div>

