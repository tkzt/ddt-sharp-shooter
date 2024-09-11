# DDT Sharp Shooter

<img src="assets/logo.ico" width="48"/>

这是一个 DDT 工具。基本原理在于，基于广为流传的力度表和简单运动模型[拟合](https://www.52pojie.cn/thread-1132459-1-1.html)出关键参数，得出由风力、角度、距离计算发射力度的一般函数，最后利用 [Pynput](https://github.com/moses-palmer/pynput) 自动发射。

其中，力度通过按压时长来体现，具体见[这里](https://github.com/boring-plans/ddt-sharp-shooter/tree/master)。

## 运行

[Releases](https://github.com/boring-plans/ddt-sharp-shooter/releases) 中提供了一些可执行文件，当然你也可以在 `Python3.6+` 环境中通过：

```shell
python main.py
```

直接执行脚本。

### 打包

PyInstaller 打包参考：

```
python -m PyInstaller main.py -F -w  -i "./assets/logo.icns" --name "dss"
```

## Getting Started

### 计算模式

拟合出的公式大致定义是 `力度=f(风速, x方向距离, y方向距离, 角度)`，故需要约定输入以获取必要参数值。

两次按下 `t` 键后，进入输入状态，而后输入形如 `x12,y1,w-2,d65` 的一段字符串按下回车后，会按照：

```
dx=12
dy=1
wind=-2
degree=65
```

的参数赋值计算出所需要的力度，然后发射。其中：

- 参数输入不要求顺序
- 参数默认皆为 0
- 参数的标记需按照约定（即 x, y, w, d）
- 输入过程中按下 `esc` 可退出输入模式（以便快速重新输入）

### 力度模式

另外，直接输入 `f + 数值`（e.g. f30），可以指定特定力度，而后直接发射。这个模式在 25 级前，有力度提示阶段，非常有用。

## 最后

本工具旨在娱乐，切勿走火入魔。
