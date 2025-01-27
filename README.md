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

## > 简介

*DynFirework*是使用Python编写的*Minecraft*粒子烟花生成器**代码模板**，提供了若干模板函数以便生成一定样式的烟花数据包文件(
.mcfunction)。

**[介绍视频](https://www.bilibili.com/video/BV1xYxxeqEMf/)**

## > 前置Mod及版本兼容性

*DynFirework*的输出指令基于[Colorblock](https://www.bilibili.com/read/cv32079719/)的`rgbatickparameter`和`normal`子指令，以实现渐变颜色粒子。

由于*Colorblock*仅支持1.12.2和1.16.5版本，当前版本的*DynFirework v1.1*生成的指令也只在上述2个版本有效。

理论上可以通过修改输出指令部分的代码并移除渐变色功能，使用原版particle指令以兼容全部版本，这是之后的更新内容之一。

## > 使用方法

### 1.图形化编辑

*DynFirework v1.1*使用tkinter编写图形化界面

使用方法为，下载源代码后，运行gui.py，在界面中选择需生成的轨迹、烟花类型（暂时可以通过设置相同的起始点和终止点来实现无轨迹）。

生成器会在根目录下创建一个与GUI界面设置中命名相同的子文件夹，该文件夹即为创建的数据包，可直接复制到存档中的datapacks目录下进行使用。

执行时，根据Datapack Generator内对namespace的命名，在游戏内执行`/function namespace:0`。 namespace的命名规范请参考[Minecraft Wiki](https://zh.minecraft.wiki/w/%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4ID?variant=zh-cn#%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4)

### 2.代码编辑

编写main.py，调用[template.md](templates.md)提供的**函数模板介绍**部分进行**自由度更大**的烟花设计。

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
- v1.1 2025.1.26 更新图形化界面

## > 作者&技术交流/反馈群

- bilibili：[TianKong_y](https://space.bilibili.com/288309681)
- QQ：[技术交流/反馈群](https://qm.qq.com/q/m6XfOuCtVe)

## > 鸣谢

- MCXCC303 编写图形化界面

