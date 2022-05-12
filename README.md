# DDT Sharp Shooter


这是一个基于 [Pynputs](https://github.com/moses-palmer/pynput) 的 DDT 工具。基本原理在于，输入风力、角度、距离，根据力度表得出发射力度，而后发射。

其中，力度通过按压时常来体现，具体见[这里](https://github.com/boring-plans/ddt-sharp-shooter/tree/master)。

## Getting Started

众所周知，20度、30度、50度、65度（变角）为 DDT 常见打法，于是，顺风 1.2、距离 17，发射角度为 30 时，在开启 `Sharp Shooter` 情况下，我们可以暗自输入：

```bash
ttw1.2 d17 m30 ↩️
```

其中，`tt` 用于进入输入状态，`w` 表示风力（顺+、逆-），`d` 表示距离，`m` 表示 mode，可取值 20、30、50、65，而 `↩️`（回车）用于结束输入、开火🚀。

需要注意的是：

- 发射前，需要保证角度确切地处于 20、30、50、65 度
- 处于命令输入状态时，按下 `ESC` 即可退出
- 按下第一个 `t` 后，紧接着按下的键若非 `t`，则停止进入输入状态

## ..

就这。
