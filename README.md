# DDT Sharp Shooter

<img src="assets/logo.ico" width="48"/>

这是一个 DDT 工具。基本原理在于，基于广为流传的力度表和简单运动模型[拟合](https://www.52pojie.cn/thread-1132459-1-1.html)出关键参数，得出由风力、角度、距离计算发射力度的一般函数，最后利用 [Pynput](https://github.com/moses-palmer/pynput) 自动发射。

其中，力度通过按压时长来体现，具体见[这里](https://github.com/boring-plans/ddt-sharp-shooter/tree/master)。

## 运行

~~[Releases](https://github.com/boring-plans/ddt-sharp-shooter/releases) 中提供了一些可执行文件，当然你也~~可以在具备 `[uv](https://docs.astral.sh/uv/)` 的环境中，依次执行：

```shell
uv sync
uv run ./main.py
```

来启动。

### 打包

当然，项目根目录提供了一个可用于 `PyInstaller` 打包的 `dss.spec` 文件，为了维护宇宙和平，暂不直接提供可执行文件。

## Getting Started

### 手动档

拟合出的公式大致定义是 `力度=f(风速, x方向距离, y方向距离, 角度)`，故需要约定输入以获取必要参数值。

两次按下 `t` 键后，进入输入状态，而后输入形如 `x12,y1,w-2,d65` 的一段字符串再次按下 `t` 后，会按照：

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
- 输入过程中按下 `esc` 可退出输入模式（以便快速重新输入以及新的对局清理数据）

### 自动档

除了直接接收一系列数值，程序也基于 `[ddddocr](https://github.com/sml2h3/ddddocr)` 等库简单实现了自动识别风力、角度、十屏像素值功能。在进入输入状态后，将鼠标**先后**放在小地图敌我位置上，并分别按下 `y` 即可记录敌我坐标情况，再按下 `t` 即可触发自动识别、计算、开火。

此功能依赖于一系列游戏内元素相对于游戏左上坐标的位置情况，所以在使用前需要通过类似于标记敌我位置的操作，分别标记游戏区域左上、右下的位置，同样需要在输入状态下进行，对应的标记按键是 `r`。

### 力度模式

另外，直接输入 `l + 数值`（e.g. l30），可以指定特定力度，而后直接发射。这个模式在 25 级前，有力度提示阶段，非常有用。

## 最后

本工具旨在娱乐，切勿走火入魔。
