# Linear Algebra Visual Lab

Gilbert Strang《Introduction to Linear Algebra》第 5 版的几何学习实验室。从一个具体问题出发，先观察向量和空间的关系，再连接数学表达。按学习需求逐个增加实验，不预建课程目录。

- **Static Visualization**：可编辑、可重新生成的 SVG 数学插图。
- **Interactive Visualization**：原生 HTML / CSS / JavaScript 实验，实时修改参数、观察几何结果。
- **本地优先**：无构建工具、运行时 CDN 或账号依赖。当前示例的整个目录复制后仍可离线打开。

## 开始使用

```bash
git clone https://github.com/Maverickhj/linear-algebra-visual-lab.git
cd linear-algebra-visual-lab
python scripts/lab.py serve
```

需要 Python 3.10+；浏览器访问 `http://127.0.0.1:8080/`。也可以直接用浏览器打开仓库根目录的 [index.html](index.html)。GitHub 文件页面展示源码，交互实验需在本地浏览器中打开。

服务启动前会校验所有 Unit 并更新索引。云环境中的 localhost 属于云主机，需要该环境的端口转发，或把仓库克隆到自己的电脑运行。

## 文件职责

```text
index.html                     自动生成的可浏览索引，提交到 Git
visualizations/<id>/           一个概念或一道习题的独立 Unit
  unit.json                    标题、维度、状态、可选教材定位
  README.md                    主题、几何直觉、图示、观察方法、验证
  figure.svg                   可选：静态插图
  interactive.html             可选：交互入口
  ...                          按需添加本 Unit 的模型、样式、生成脚本和测试
templates/unit/                新 Unit 的最小骨架
scripts/lab.py                 创建、校验、生成索引、静态服务
docs/conventions.md            命名、内容、数学绘图与交互约定
docs/verification.md           初始示例的验证结果与复现方法
tests/                        框架检查和可选浏览器检查
```

每个 Unit 至少有一种可视化，不要求同时存在 SVG 与 HTML，也不要求相同的文件数量。索引自动发现各目录的 `unit.json`，没有另一个手动维护的注册表。

## 新增可视化

```bash
python scripts/lab.py new my-concept --title '一个具体的几何问题' --kind both
# --kind 可选 static / interactive / both；--dimension 可选 2 / 3。
```

1. 编辑新目录的 `README.md`，写清问题、想建立的直觉、符号、观察方法和边界。
2. 实现 `figure.svg`、`interactive.html` 中需要的形式。模板只提供占位区域，不能当作已完成的数学实验。
3. 在 `unit.json` 中按需填写英文教材的章节、**印刷页码**、图号或习题号。标题和教材定位只在此维护；正文集中解释数学。
4. 对照可手算的例子与退化情形，实际检查浏览器交互后，把 `status` 从 `draft` 改为 `ready`，在 Unit README 的 Validation 中记录证据。
5. 校验并更新索引，然后提交新 Unit 和索引：

```bash
python scripts/lab.py check
python scripts/lab.py index
```

无需修改脚本、模板、根 README 或其他 Unit。具体约定见 [conventions.md](docs/conventions.md)。

## 最小示例与验证

当前仅包含“向量加法”一个二维示例。静态图与交互图调用同一份绘图函数；默认值是本项目自选的 $(2,1)$ 与 $(1,2)$，不是教材图中数值的复刻。

查看示例的 `README.md` 了解观察方法和文件分工。浏览器中可调整两个向量的四个分量，比较首尾相接路径与合向量；支持零向量、抵消和重置。

```bash
# Python 标准库：目录约定、脚手架和索引
python -m unittest discover -s tests -v

# Node 18+：仅供开发，重新生成静态图并验证模型
node visualizations/vector-addition/generate.cjs
node --test visualizations/vector-addition/model.test.cjs

# 可选浏览器回归；安装方法见 docs/verification.md
python tests/browser_check.py
```

阅读、操作实验不需要 Node、Playwright 或 Python 包。基础数学公式使用浏览器原生 MathML，Markdown 使用 LaTeX；复杂公式或三维问题出现时再按 Unit 记录和引入必要的本地依赖。

## 设计来源

参考 [ai-infra-visual-lab](https://github.com/Maverickhj/ai-infra-visual-lab) 的实际实现，保留本地优先、原生网页、Python 标准库工具和模型与界面分离的做法。针对当前规模，改用每个 Unit 的轻量元数据及自动发现索引。取舍和核对版本见 [约定文档](docs/conventions.md#设计依据)。
