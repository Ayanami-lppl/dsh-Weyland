<div align="center">

# dsh-Weyland

**给 DeepSeek Harness 换上一段《异形》维兰德-汤谷风格的 CRT 开机动画**

![启动序列](assets/preview.gif)

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-3DA639?style=flat-square)
![Dependencies](https://img.shields.io/badge/dependency-无第三方包-4B8BBE?style=flat-square)

</div>

---

## 这是什么

一段 8 秒的 CRT 启动序列，致敬《异形》(1979) 与《异形 2》(1986) 里**维兰德-汤谷公司（Weyland-Yutani Corp.）**的复古终端界面：扫描线、荧光绿残影、信号锁定、逐字打印的启动日志。

**它提供两种形态，任选其一：**

| | **方式 A：应用内插件**（推荐） | **方式 B：独立启动器** |
|---|---|---|
| 播放位置 | DeepSeek Harness 窗口**内部**，像应用自己的启动画面 | 一个无边框窗口**盖住整个屏幕** |
| 观感 | 贴合应用 | 独立开机动画 |
| 右上角三个窗口按钮 | 盖不住，但会**跟着动画染成荧光绿** | **完全盖住** |
| 应用自己的加载画面 | 会先闪一下 | **完全盖住** |
| 需要什么 | Python + 安装脚本 | Python + `pywebview` |
| 改应用文件吗 | 只往 DSH 的 profile 目录加插件，不碰安装目录 | 完全不碰 |

两种形态**用的是同一套动画**（都在 `splash/` 里），视觉完全一致。

## 效果

一段 8 秒的连续演出：

| 时间 | 画面 |
| :--- | :--- |
| 0.0 – 0.7s | CRT 通电：亮线从屏幕中间扫开、过曝白闪、同步滚动、雪花噪点 |
| 1.0 – 2.9s | 双层圆环与四向刻度依次描边，W-Y 徽记成形，带红/青色彩分离残影 |
| 2.8 – 4.6s | `WEYLAND-YUTANI` 字距收拢落版，两侧亮线拉开，副标 `CORP. / BUILDING BETTER WORLDS` |
| 4.1 – 4.4s | 横向撕裂与 RGB 分离抖动 |
| 4.4 – 6.3s | 左下逐字打印启动日志，右下 SIGNAL 条爬升到 `LOCKED 100%` |
| 7.4 – 8.0s | CRT 关机：画面塌缩成一条亮线 → 残留光点 → 全黑 |

全程叠加 CRT 扫描线、滚动亮带、颗粒噪点、暗角与荧光呼吸。界面元素（`MU/TH/UR 6000`、`180924609`、启动日志）均为静态装饰，不涉及任何真实数据。

---

# 方式 A：应用内插件（推荐）

动画在 DeepSeek Harness 窗口内部播放，看起来像应用自带的开机画面。

## 环境要求

| 项目 | 要求 |
| :--- | :--- |
| 系统 | Windows 10 / 11 |
| Python | 3.8 或更高（只用来跑安装脚本） |
| 目标 | DeepSeek Harness 桌面版 |
| 依赖 | **无**，不需要 `pip install` 任何东西 |

## 安装

```bash
git clone https://github.com/Ayanami-lppl/dsh-Weyland.git
cd dsh-Weyland
python plugin/install.py
```

看到 `Done. Restart DeepSeek Harness to see it.` 之后**重启 DeepSeek Harness** 即可。

安装脚本做四件事，全部可逆：

1. 找到 dsh profile（默认 `~/.dsh/profiles/desktop`，可用 `--profile` 指定）
2. 从 `splash/` 生成插件代码（`plugin/build.py`）
3. 把插件复制到 `<profile>/node_modules/dsh-weyland-intro/`
4. 在 `<profile>/cordis.patch.yml` 里加两行注册——**改之前会先备份**，且只动它自己那一条

**不碰 DeepSeek Harness 的安装目录**，也不用管理员权限。

## 卸载

```bash
python plugin/install.py --uninstall
```

删掉插件目录并撤掉注册。重启应用即恢复原样。

## 几点要知道的

- **会先闪一下应用自己的加载画面**。动画必须在应用窗口出现之后才能挂载，所以它盖不住应用启动到渲染之间的那段空白。方式 B 可以避免这个问题。
- **右上角的三个窗口按钮盖不住，但会被染成动画的配色**。它们由 Windows 直接画在网页内容之上（Electron 的 Window Controls Overlay），任何网页内容都盖不住——这是刻意的设计，否则网页就能藏掉关闭按钮。
  不过应用有一条约定的配色通道：它自己的 preload 会监听页面里一个隐藏元素，把它的颜色转发给主进程的 `setTitleBarOverlay()`。播放动画期间改写那个元素，三个按钮就会跟着变成透明底 + 荧光绿，播完自动还原。想完全盖住它们只能用方式 B。
- **如果本机已经有另一个开场插件**（比如 `dsh-boot-intro`），安装脚本会检测到，并让两个动画**按时段轮流播放**，不会同时出现。没有对手插件时，本插件每次启动都播。
- **不可跳过**，完整播满 8 秒。想改成可点击跳过，见「自定义」。

---

# 方式 B：全屏独立启动器

在应用启动**之前**用一个无边框窗口盖住整个屏幕（连任务栏一起），播完再拉起 DeepSeek Harness。

## 环境要求

| 项目 | 要求 |
| :--- | :--- |
| 系统 | Windows 10 / 11 |
| Python | 3.8 或更高（需要 `pythonw.exe`） |
| 运行时 | Microsoft Edge WebView2 Runtime（装了 Edge 就有） |
| 依赖 | `pywebview >= 5.0` |

## 安装

```bash
git clone https://github.com/Ayanami-lppl/dsh-Weyland.git
cd dsh-Weyland
pip install -r requirements.txt
pythonw launch.pyw
```

> 用 `pythonw` 而不是 `python`，这样不会弹出黑色控制台窗口。

**通常在标准位置安装的 DeepSeek Harness 会被自动找到**。找不到的话，复制 `config.example.json` 成 `config.json`，把 `app` 填成可执行文件的完整路径。

## 做成桌面快捷方式

在项目目录下打开 PowerShell，粘贴：

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
$s.Save()
```

以后双击 `DeepSeek Harness` 就会先播动画。要还原，把 `.lnk.bak` 覆盖回去。

## 配置项

`config.json` 全部字段（**整个文件都可以不存在**，缺省即为下列默认值）：

| 字段 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `app` | string | `""` | 要启动的程序完整路径。支持 `~` 和 `%环境变量%`。留空或路径不存在时自动探测 |
| `duration_ms` | number | `8000` | 动画时长（毫秒）。**修改时必须与 `splash/splash.css` 的时间轴一致** |
| `warm_start_ms` | number \| null | `6900` | 在动画的第几毫秒**提前**把应用拉起来，这样动画结束时应用已经就绪。设为 `null` 则播完才启动 |

---

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

打开 `splash/index.html`，找到 `<div class="bootlog">`，直接改里面的文字。每行开头的 `--d:4350` 是这一行开始打印的时间（毫秒）。

### 改时长 / 让它可跳过

时间轴由 CSS 动画的 `animation-delay` / `animation-duration`（毫秒）写死，改时长要把 `splash/splash.css` 里各段的延迟按比例缩放。

**方式 A 的用户注意**：改完 `splash/` 里的任何东西，都要重新跑一次 `python plugin/install.py`，否则应用里播的还是旧的。想让它可点击跳过，在 `plugin/build.py` 生成的组件里加一个 `pointerdown` 监听调用 `setGone(true)` 即可。

### 给别的程序用（仅方式 B）

`config.json` 的 `app` 填任何 `.exe` 都能用。

## 常见问题

<details>
<summary><b>方式 A：重启后没有任何动画？</b></summary>

按顺序查：

1. 插件目录在不在：`~/.dsh/profiles/desktop/node_modules/dsh-weyland-intro/`（应有 `package.json` 和 `lib/`）
2. `~/.dsh/profiles/desktop/cordis.patch.yml` 末尾有没有这两行：
   ```yaml
   - insert:
       - id: weyland-intro
         name: dsh-weyland-intro
   ```
3. 本机如果还装了 `dsh-boot-intro` 之类的**另一个开场插件**，两个会轮流播——可能这次轮到对方了
4. 重新跑一次 `python plugin/install.py`

要彻底重来：`python plugin/install.py --uninstall` 再装一次。
</details>

<details>
<summary><b>方式 B：双击后没动画，直接进应用了？</b></summary>

这是**设计如此**的失败开放行为——启动器遇到任何异常都会跳过动画直接拉起应用，保证快捷方式不会变成死链。常见原因：

- `pywebview` 没装 → `pip install pywebview`
- Python 目录变了（升级了 Python，`pythonw.exe` 换了位置）→ 重建快捷方式
- 缺少 WebView2 运行时 → 装一下 Microsoft Edge WebView2 Runtime

想看到真正的报错，把快捷方式的目标从 `pythonw.exe` 临时改成 `python.exe`。
</details>

<details>
<summary><b>为什么右上角的三个按钮盖不住？</b></summary>

它们由 Windows 直接画在网页内容之上（Electron 的 Window Controls Overlay，应用里配置的是 `titleBarOverlay: { height: 40 }`）。这是刻意设计——否则网页就能藏掉关闭按钮。任何网页内容、任何 z-index 都盖不住。

**想要盖住它们，用方式 B。**
</details>

<details>
<summary><b>方式 B：动画播完，应用还要等一会儿才出来？</b></summary>

把 `config.json` 里的 `warm_start_ms` 调**小**（比如 `5000`），让应用更早开始启动。调太小的话，若应用启动很快，其窗口可能在动画末尾出现在上层——这时往回调一点即可。
</details>

<details>
<summary><b>动画一闪就结束了？</b></summary>

检查 Windows 的**"在 Windows 中显示动画"**开关（设置 → 辅助功能 → 视觉效果）。关闭的话系统会向网页报告 `prefers-reduced-motion: reduce`，本项目会跳过全部动效。
</details>

<details>
<summary><b>全屏播放时卡顿？</b></summary>

动画用了较多全屏叠加层（扫描线、噪点、发光）。老机器的集显可能吃力，可以注释掉 `splash/splash.css` 里 `.fx-grain`（颗粒噪点）和 `.fx-bloom`（辉光）两段。
</details>

<details>
<summary><b>怎么彻底卸载？</b></summary>

- **方式 A**：`python plugin/install.py --uninstall`（会删掉插件目录并撤掉注册）
- **方式 B**：把备份的 `DeepSeek Harness.lnk.bak` 覆盖回桌面，删掉项目文件夹，可选 `pip uninstall pywebview`

DeepSeek Harness 本身从未被修改过，不需要重装。
</details>

<details>
<summary><b>支持 macOS / Linux 吗？</b></summary>

**方式 B** 的代码只依赖 pywebview，理论上跨平台，但只在 Windows 10/11 上测试过；应用路径探测和 `creationflags` 是 Windows 专用的。

**方式 A** 依赖 DeepSeek Harness 的插件系统，与系统无关，但未经测试。
</details>

## 工作原理

```
方式 A —— 应用内插件
DeepSeek Harness 启动
      │ 读 ~/.dsh/profiles/desktop/cordis.patch.yml
      │ 加载 node_modules/dsh-weyland-intro
      ▼
插件的 apply() 往 shell.overlay 槽位注册一个全屏覆盖层
      │ React Portal 挂到 <body>（避开祖先的 transform 让 fixed 失效）
      │ Shadow DOM 隔离（动画 CSS 是页面级的，不能污染应用本身）
      │ 纯 CSS 播完 8 秒，然后卸载，把窗口交还给应用
      ▼
应用界面

方式 B —— 独立启动器
双击快捷方式 → pythonw launch.pyw
      │ 读 config.json（缺失/损坏则用默认值 + 自动探测应用路径）
      │ pywebview 开一个全屏无边框置顶窗口，加载 splash/index.html
      │ 纯 CSS 播完 8 秒
      │ Python 轮询页面上的完成标志（或超时兜底），关闭窗口
      │ 第 warm_start_ms 毫秒时已提前把应用拉起
      ▼
应用界面
```

几个值得一提的取舍：

- **徽记是矢量画出来的**：SVG 路径用 `pathLength="1"` + `stroke-dashoffset` 描边，无图片素材；字体只用系统自带的 Bahnschrift（字标）和 Consolas（终端文字）。
- **`?t=` 定格参数**：浏览器打开 `splash/index.html?t=4200` 可以定格到任意毫秒，方便调时间轴。
- **方式 A 用轮询标志而不是 `js_api` 回调**（方式 B）：`js_api` 桥接有注入时机问题，页面一旦抛异常就可能永远等不到回调、把启动卡死。
- **两个开场插件按时段轮流播出**：两边各自从系统时钟算同一个值（murmurhash3 混合后取奇偶），不需要任何共享状态文件。

## 目录结构

```
dsh-Weyland/
├─ plugin/                 # 方式 A：应用内插件
│  ├─ install.py           #   安装 / 卸载
│  ├─ build.py             #   从 ../splash/ 生成 lib/client.js
│  ├─ package.json
│  └─ lib/
│     ├─ index.js          #   宿主侧（空壳）
│     └─ client.js         #   生成物，不入库
├─ launch.pyw              # 方式 B：全屏独立启动器
├─ config.example.json
├─ requirements.txt        # 方式 B 的依赖（pywebview）
├─ splash/                 # 两种形态共用的动画本体
│  ├─ index.html           #   结构 + 内嵌 SVG 徽记
│  ├─ splash.css           #   全部视觉效果与 8 秒时间轴
│  └─ splash.js            #   时长解析、定格/seek、完成标志
└─ assets/
   ├─ preview.gif
   └─ preview.png
```

## 免责声明

- 本项目是**非官方的粉丝向作品**，与 DeepSeek 官方没有任何关系。
- 「Weyland-Yutani / 维兰德-汤谷」及相关名称、世界观出自《异形》系列电影，版权归 20th Century Studios / The Walt Disney Company 所有。本项目中的徽记是**按该风格手绘的 SVG 矢量图形**，未使用任何官方素材文件，仅作个人桌面美化与前端技术演示之用。
- 请勿将本项目用于任何商业用途。

## License

[MIT](LICENSE)
