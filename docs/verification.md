# 初始化验证记录

日期：2026-10-27。实际环境：Python 3.12.14、Node 24.19.0、Playwright 1.62.0、Chromium 154.0.8037.57（Linux）。Python 工具的语法与依赖按 3.10+ 编写，未逐一运行所有较早版本。

## 已执行

| 检查 | 结果与范围 |
| --- | --- |
| `python -m unittest discover -s tests -v` | 6 项通过：三种输出形式、自动发现索引、草稿、3D 元数据、拒绝覆盖与路径穿越、文本转义、无效目录及元数据 |
| `node --test visualizations/vector-addition/model.test.cjs` | 6 项通过：手算结果、负值和边界、交换顺序、零向量、不合法输入、等比例坐标、静态图与交互图一致 |
| `python scripts/lab.py check` | 通过；仓库中仅有一个实际 Unit |
| 真实 CLI `new` → `check` | 在临时目录分别创建 static / interactive / both，三种情况均可自动入索引；不在项目中留下额外主题 |
| `python tests/browser_check.py` | 本地 HTTP 索引、实验、独立 SVG 均可打开；键盘、数字输入、参数同步、错误输入、恢复默认、抵消与零向量通过；无 JS 或资源错误 |
| 1280px / 390px 浏览器检查 | 绘图、控件、原生 MathML 和展开公式可见，无页面横向溢出；已人工查看示例截图，截图不提交 |
| 独立目录运行 | 只复制一个 Unit 到临时目录并静态服务，不访问仓库其他资源；仍可交互。拦截非本地请求，实际没有外部请求 |

教材定位已对照本地英文第 5 版原文：§1.1、印刷 p.3、Figure 1.1，图注描述平行四边形对角线，附近正文解释 head-to-tail。项目默认数值是自选例子，不是书中原图的数值。

## 复现

在仓库根目录运行：

```bash
python scripts/lab.py check
python -m unittest discover -s tests -v
node visualizations/vector-addition/generate.cjs
node --test visualizations/vector-addition/model.test.cjs
python scripts/lab.py index
```

可选浏览器工具应独立安装；不是页面运行依赖：

```bash
python -m venv .venv
# Linux/macOS；Windows 使用 .venv\Scripts\activate
source .venv/bin/activate
python -m pip install -r tests/requirements-browser.txt
python -m playwright install chromium
python tests/browser_check.py
```

如果已经安装系统 Chromium，脚本会优先使用 `chromium`；也可通过 `CHROMIUM_PATH` 指定可执行文件，不必再次下载。设置 `LAB_SCREENSHOTS` 为仓库外的目录可保留验收截图。检查脚本只启动临时的 loopback HTTP 服务，结束后关闭。

手动验证：`python scripts/lab.py serve`，打开索引进入示例，先改一个分量，再试抵消、零向量和重置；Tab 聚焦滑块，用方向键调整；在手机宽度检查图、读数与控件。

## 实际限制

- 该云环境的浏览器管理策略拒绝 `file://`，报 `ERR_BLOCKED_BY_ADMINISTRATOR`。脚本对这一具体情况打印 **SKIP**，不会将它报告为通过；其他错误仍失败。没有关闭或绕过浏览器策略。
- “无外网运行依赖”已通过只允许本地 HTTP 请求的浏览器检查；**浏览器 offline 模式下的 file 打开尚未在本环境验证**。可在允许本地文件导航的电脑重跑同一脚本。
- 未测试 Firefox、Safari、真实触屏设备或三维交互。本阶段只提供一个二维示例和三维 Unit 的组织与操作约定，没有实现三维渲染引擎。
- `check` 和元数据 `ready` 均不能代替数学 review；验证范围在各 Unit 的 Validation 中明确记录。
