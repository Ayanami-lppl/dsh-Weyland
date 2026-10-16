<div align="center">

# dsh-Weyland

**给 DeepSeek Harness 换上一段《异形》维兰德-汤谷风格的 CRT 开机动画**

双击图标 → 全屏播放 8 秒启动序列 → 自动拉起 DeepSeek Harness

![启动序列](assets/preview.gif)

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-3DA639?style=flat-square)
![Dependencies](https://img.shields.io/badge/dependency-pywebview%20only-4B8BBE?style=flat-square)

</div>

---

## 这是什么

`dsh-Weyland` 是给 **DeepSeek Harness 桌面端**做的一个**开机动画启动器**。

它**不修改 DeepSeek Harness 的任何文件**，而是一个独立的小程序：你双击图标 → 它全屏播放一段 8 秒的 CRT 启动序列 → 序列结束的同时把 DeepSeek Harness 拉起来。

视觉上致敬《异形》(1979) 与《异形 2》(1986) 里**维兰德-汤谷公司（Weyland-Yutani Corp.）**的复古终端界面：扫描线、荧光绿残影、信号锁定、逐字打印的启动日志。

> 为什么不做成"改官方应用"？因为 DeepSeek Harness 是带数字签名、走 nightly 自动更新的官方 Electron 应用，直接改 `app.asar` 每次更新都会被覆盖掉。独立启动器则一劳永逸，而且随时可以一键还原。

## 效果

一段 8 秒的连续演出，时间轴如下：

| 时间 | 画面 |
| :--- | :--- |
| 0.0 – 0.7s | CRT 通电：亮线从屏幕中间扫开、过曝白闪、同步滚动、雪花噪点 |
| 1.0 – 2.9s | 双层圆环与四向刻度依次描边，W-Y 徽记成形，带红/青色彩分离残影 |
| 2.8 – 4.6s | `WEYLAND-YUTANI` 字距收拢落版，两侧亮线拉开，副标 `CORP. / BUILDING BETTER WORLDS` |
| 4.1 – 4.4s | 横向撕裂与 RGB 分离抖动 |
| 4.4 – 6.3s | 左下逐字打印启动日志，右下 SIGNAL 条爬升到 `LOCKED 100%` |
| 7.4 – 8.0s | CRT 关机：画面塌缩成一条亮线 → 残留光点 → 全黑，随后 DeepSeek Harness 已经就绪 |

全程叠加 CRT 扫描线、滚动亮带、颗粒噪点、暗角与荧光呼吸。界面元素（`MU/TH/UR 6000`、`180924609`、启动日志）均为静态装饰，不涉及任何真实数据。

## 特性

- **零侵入** —— 不碰官方应用的任何文件，卸载 = 删掉一个文件夹
- **失败开放** —— WebView2 缺失、配置写错、页面报错……任何异常都直接拉起应用，快捷方式绝不会变成死链
- **预热启动** —— 动画快结束时就开始启动应用，动画一黑屏应用基本已经就绪，不会干等
- **自动探测路径** —— 首次运行会自动在常见安装位置找 DeepSeek Harness，通常不用改任何配置
- **纯 HTML/CSS 绘制** —— 徽记是矢量路径描边动画，无图片素材、无外部字体、无网络请求
- **可自定义** —— 荧光色、时长、启动日志文案都在文件里几行就能改
- **只有一个依赖** —— `pywebview`，渲染直接用系统上的 Edge WebView2

## 环境要求

| 项目 | 要求 |
| :--- | :--- |
| 系统 | Windows 10 / 11 |
| Python | 3.8 或更高（需要带 `pythonw.exe`） |
| 运行时 | Microsoft Edge WebView2 Runtime（Win10/11 装了 Edge 就有，通常无需单独安装） |
| 依赖 | `pywebview >= 5.0` |
| 目标程序 | DeepSeek Harness 桌面版（其它程序也能用，见「自定义」） |

## 快速开始

### 1. 下载

```bash
git clone https://github.com/Ayanami-lppl/dsh-Weyland.git
cd dsh-Weyland
```

或者点仓库右上角 **Code → Download ZIP** 解压。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置（可选）

先直接试着运行一次——**大概率不需要配置**。程序会自动在下列位置寻找 DeepSeek Harness：

```
C:\deepseek harness\DeepSeek Harness.exe
%LOCALAPPDATA%\Programs\DeepSeek Harness\DeepSeek Harness.exe
%ProgramFiles%\DeepSeek Harness\DeepSeek Harness.exe
%ProgramFiles(x86)%\DeepSeek Harness\DeepSeek Harness.exe
...
```

如果自动探测失败（或者你想让它启动别的程序），复制一份配置模板：

```bash
copy config.example.json config.json
```

然后编辑 `config.json` 里的 `app` 字段，填可执行文件的完整路径。

### 4. 运行

```bash
pythonw launch.pyw
```

> 用 `pythonw` 而不是 `python`，这样不会弹出黑色控制台窗口。

### 5. 做成桌面快捷方式

把原来的快捷方式指向启动器即可。在项目目录下打开 PowerShell，粘贴：

```powershell
$here = (Resolve-Path .).Path
$py   = (Get-Command pythonw).Source
$lnk  = "$([Environment]::GetFolderPath('Desktop'))\DeepSeek Harness.lnk"

Copy-Item $lnk "$lnk.bak" -ErrorAction SilentlyContinue   # 备份原快捷方式
$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$s.TargetPath       = $py
$s.Arguments        = "`"$here\launch.pyw`""
$s.WorkingDirectory = $here
$s.Description      = 'DeepSeek Harness'
# 可选：用目标程序自己的图标，保持视觉一致
# $s.IconLocation   = 'C:\deepseek harness\DeepSeek Harness.exe,0'
$s.Save()
```

搞定。以后双击 `DeepSeek Harness` 就会先播动画。

## 配置项

`config.json` 全部字段（**整个文件都可以不存在**，缺省即为下列默认值）：

| 字段 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `app` | string | `""` | 要启动的程序完整路径。支持 `~` 和 `%环境变量%`。留空或路径不存在时自动探测 |
| `duration_ms` | number | `8000` | 动画时长（毫秒）。**修改时必须与 `splash/splash.css` 中的时间轴一致**，详见下节 |
| `warm_start_ms` | number \| null | `6900` | 在动画的第几毫秒**提前**把应用拉起来，这样动画结束时应用已经就绪。设为 `null` 则等动画播完才启动 |

## 自定义

### 换荧光色

打开 `splash/splash.css`，改最上面的几个变量：

```css
:root {
  --ph:      #7dffb4;   /* 荧光绿主色，改成 #ffb454 就是琥珀色 CRT */
  --ph-hi:   #d6ffe9;   /* 过曝高光 */
  --ph-dim:  #2c8a5c;   /* 暗部文字 */
  --ph-ghost:#0d3a26;  /* 描边、边框 */
  --bg:      #020503;   /* 底色 */
}
```

### 改启动日志文案

打开 `splash/index.html`，找到 `<div class="bootlog">`，直接改里面的文字。每行开头的 `--d:4350` 是这一行开始打印的时间（毫秒），按需调整即可。

### 改时长

时间轴由 CSS 动画的 `animation-delay` / `animation-duration`（毫秒）直接写死，所以改时长要把 `splash/splash.css` 里各段的延迟按比例缩放，并同步更新 `config.json` 的 `duration_ms`，否则动画还没播完应用就弹出来了（或反之）。

如果只是想**快一点**，把 `duration_ms` 改小即可强制中断——但画面会被硬切。

### 给别的程序用

`config.json` 的 `app` 填任何 `.exe` 都能用。比如 `"app": "C:\\Program Files\\Mozilla Firefox\\firefox.exe"`。

## 常见问题

<details>
<summary><b>双击后没动画，直接进应用了？</b></summary>

这是**设计如此**的失败开放行为。启动器遇到任何异常都会跳过动画直接拉起应用，保证快捷方式不会变成死链。常见原因：

- `pywebview` 没装 → `pip install pywebview`
- Python 目录变了（比如升级了 Python，`pythonw.exe` 换了位置）→ 重新执行第 5 步重建快捷方式
- 缺少 WebView2 运行时 → 装一下 Microsoft Edge WebView2 Runtime

想看到真正的报错信息，把快捷方式的目标从 `pythonw.exe` 临时改成 `python.exe`，就能看到控制台输出。
</details>

<details>
<summary><b>动画播完，应用还要等一会儿才出来？</b></summary>

把 `config.json` 里的 `warm_start_ms` 调**小**（比如 `5000`），让应用更早开始启动。调太小的话，若应用启动很快，其窗口有可能在动画最后阶段出现在上层——这时往回调一点即可。
</details>

<details>
<summary><b>动画一闪就结束了？</b></summary>

检查 Windows 的**"在 Windows 中显示动画"**开关（设置 → 辅助功能 → 视觉效果）。如果关闭了，系统会向网页报告 `prefers-reduced-motion: reduce`，本项目的 CSS 会跳过全部动效、1.2 秒后直接交接。
</details>

<details>
<summary><b>全屏播放时卡顿？</b></summary>

动画用了较多全屏叠加层（扫描线、噪点、发光）。老机器的集显可能吃力，可以打开 `splash/splash.css` 注释掉 `.fx-grain`（颗粒噪点）和 `.fx-bloom`（辉光）两段，效果影响不大但省不少性能。
</details>

<details>
<summary><b>怎么彻底卸载？</b></summary>

1. 把之前备份的 `DeepSeek Harness.lnk.bak` 覆盖回桌面快捷方式（或者手动把快捷方式指回 `DeepSeek Harness.exe`）
2. 删掉本项目文件夹
3. 可选：`pip uninstall pywebview`

DeepSeek Harness 本身从未被修改过，不需要重装。
</details>

<details>
<summary><b>支持 macOS / Linux 吗？</b></summary>

代码本身只依赖 pywebview，理论上跨平台，但**只在 Windows 10/11 上测试过**。`launch.pyw` 里的应用路径探测和 `creationflags` 参数是 Windows 专用的，移植需要改这两处。
</details>

## 工作原理

```
双击快捷方式
      │
      ▼
pythonw launch.pyw
      │
      ├─ 读 config.json（缺失/损坏则用默认值 + 自动探测应用路径）
      ├─ pywebview 创建一个全屏无边框、置顶的窗口，加载 splash/index.html
      │
      ├─ 页面用纯 CSS 动画播完 8 秒序列
      │   （用 document.getAnimations() 做绝对时间轴，可用 ?t=毫秒 定格任意一帧）
      │
      ├─ 第 warm_start_ms 毫秒：Python 侧提前 Popen 拉起应用（以 DETACHED 方式，脱离本进程）
      ├─ 页面播完后设置 window.__splashFinished = true
      ├─ Python 轮询到该标志（或超时兜底），关闭窗口 → 动画消失时应用已就绪
      │
      ▼
DeepSeek Harness 正常显示
```

几个值得一提的取舍：

- **用轮询标志而不是 `js_api` 回调**：`js_api` 桥接有注入时机问题，页面一旦抛异常就可能永远等不到回调、把启动卡死。轮询一个布尔标志没有这个问题，而且带超时兜底。
- **`gif` 之外没有素材**：徽记是 SVG 矢量路径用 `pathLength="1"` + `stroke-dashoffset` 描边画出来的，字体只用系统自带的 Bahnschrift（字标）和 Consolas（终端文字）。
- **`?t=` 定格参数**：页面支持 `splash/index.html?t=4200` 在浏览器里定格到任意毫秒，方便调时间轴。

## 目录结构

```
dsh-Weyland/
├─ launch.pyw              # 入口：全屏播放动画，然后拉起应用
├─ config.example.json     # 配置模板（复制成 config.json 后修改）
├─ requirements.txt
├─ splash/
│  ├─ index.html           # 结构 + 内嵌 SVG 徽记
│  ├─ splash.css           # 全部视觉效果与 8 秒时间轴
│  └─ splash.js            # 时长解析、定格/seek、完成标志
└─ assets/
   ├─ preview.gif          # README 里的演示
   └─ preview.png          # 全屏静态截图
```

## 免责声明

- 本项目是**非官方的粉丝向作品**，与 DeepSeek 官方没有任何关系。
- 「Weyland-Yutani / 维兰德-汤谷」及相关名称、世界观出自《异形》系列电影，版权归 20th Century Studios / The Walt Disney Company 所有。本项目中的徽记是**按该风格手绘的 SVG 矢量图形**，未使用任何官方素材文件，仅作个人桌面美化与前端技术演示之用。
- 请勿将本项目用于任何商业用途。

## License

[MIT](LICENSE)
