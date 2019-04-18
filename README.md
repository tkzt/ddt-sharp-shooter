---
title: 恶灵王v0.0.1诞生记
date: 2019/04/09 19:36
tags: 
    - 程序员物语
    - AI
---

## 晚霞

随着年纪的增长，我们对待某些事物的方式会发生变化。比如，今天的晚霞是那种贼好看的晚霞，我情不自禁地把它拍了下来。当然，到这里变化还没有发生，变化是随后我开始编辑这张照片：裁剪、调整局部饱和度、增加些许颗粒……如下：

<div style="text-align:center;font-size:12px;"><img src="/images/晚霞一瞬D.jpg">
<i>&copy;Qingqiu 2019-04-18 in Wuxi</i>
</div>

我以前是绝不会这么做的。像我们做完绝大多数事情一样，点击了保存以后，一切索然无味。大概这就是人生吧。

同样，当我 22 岁再打开[弹弹堂（全民弹弹堂）](https://qqgame.qq.com/app/gamedetail_10554.shtml)，熟悉的BGM响起，事情却不一样了起来。

## 恶灵王v0.0.1

### 这是一个合情合理的辅助

这次我不是孤身奋战~

我用 python 写了个脚本，通过识别距离（这版不知为何可以直接显示屏距了）、风力、角度，再结合各角度的力度表，最后实现自动开火，大概就像这样：

<div style="text-align:center;">
    <iframe 
    width="700" 
    height="450" 
    src="https://v.qq.com/x/page/b08621jlmfi.html"
    frameborder="0" 
    allowfullscreen>
    </iframe>
</div>

之所以叫「恶灵王」，是因为这版弹弹堂里出了个叫恶灵的武器，无视风力，简直牛批。

### 一些罗列

#### 键鼠事件

*  键鼠事件的监听（以及屏幕的截取）利用 PyHook3 ，以实现武器的切换（这版）、打法的切换
*  键鼠事件的模拟利用 pywin32 ，以实现调整角度、开火

#### 识别

我利用伟大的 [CSDN 上的一个 Digital Character 数据集](https://download.csdn.net/download/qq_34654240/10673771)（但事后发现了一个似乎更好的[数据集](https://download.csdn.net/download/pku_coder/10892198)）以及伟大的 TensorFlow，通过 BP 神经网络，训练出一个准确率 97%+ 的模型，用以识别风力、角度、距离。实践下来，效果海星。

#### 开炮

据多次测量（手动测量..）,满力度需用时（按满整个力度条）4.0s-4.3s，那么在网络延迟不高的情况下，力度与蓄力（按下空格）时长近似有如下关系：

> 蓄力时长（s） = 力度（单位1）/100*4.2

当然，被该死的「肉肉（某个宠物..）」的恍惚（能加速力度条移动）技能打了的话，自动开火什么的就 G 了。

## 最后

刚刚偶然间听到 wuli 智恩唱的《爱情》，顺手搬上来。

<div align=center><iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=700 height=86 src="//music.163.com/outchain/player?type=2&id=399552413&auto=1&height=66"></iframe></div>

有缘的话，以后想再整个半透明的 GUI，再整个抛物线绘制、直线绘制……收。

索然无味。