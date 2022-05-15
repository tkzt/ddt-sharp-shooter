# DDT Sharp Shooter

<img src="assets/logo.ico" width="48"/>

这是一个基于 [Pynput](https://github.com/moses-palmer/pynput) 的 DDT 工具。基本原理在于，输入风力、角度、距离，根据力度表得出发射力度，而后发射。

其中，力度通过按压时长来体现，具体见[这里](https://github.com/boring-plans/ddt-sharp-shooter/tree/master)。

## Build

受 OS 所限，[Releases](https://github.com/boring-plans/ddt-sharp-shooter/releases) 仅提供了 MacOS 上的可执行文件。

可通过：

```shell
python setup.py py2app
```

自行构建 App。

## Getting Started

### 角度模式

众所周知，20度、30度、50度、65度（变角）为 DDT 常见打法，于是，顺风 1.2、距离 17，发射角度为 30 时，在开启 `Sharp Shooter` 情况下，我们可以暗自输入：

```bash
ttw1.2 ds17 dg30 ↩️
```

其中，`tt` 用于进入输入状态，`w` 表示风力（顺+、逆-），`ds` 表示距离，`dg` 表示 mode，可取值 20、30、50、65，而 `↩️`（回车）用于结束输入、开火🚀。

若不想自行推算屏距，可在进入输入状态后，依次在小地图点击 `当前位置`、`敌人位置`（更准确的说是，当前位置水平线与打击抛物线最终相交点）、`屏距测量框左侧边任意点`、`屏距测量框右侧边任意点`，而后 DSS 会在回车结束输入、开火时自动推算屏距。

在同时指定 `ds` 和提供位置点信息的情况下，后者生效。

需要注意的是：

- 发射前，需要保证角度确切地处于 20、30、50、65 度
- 处于命令输入状态时，按下 `ESC` 即可退出
- 按下第一个 `t` 后，紧接着按下的键若非 `t`，则停止进入输入状态

### 力度模式

另外，可以直接：

```bash
ttf35 ↩️
```

来指定特定力度，而后直接发射。这个模式在 25 级前，有力度提示阶段，非常有用。

## 最后

本工具旨在娱乐，切勿走火入魔。
