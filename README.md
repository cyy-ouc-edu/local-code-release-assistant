# Local Code Release Assistant

一个本地优先的代码交付 Skill，把 Git 变更整理成可以直接使用的 PR 描述、发布说明、风险提示、测试建议和回滚方案。

源码仓库：[cyy-ouc-edu/local-code-release-assistant](https://github.com/cyy-ouc-edu/local-code-release-assistant)

## 解决什么问题

代码写完后，开发者仍需反复阅读 diff、归纳影响范围、补写 PR 描述并考虑测试和回滚。Local Code Release Assistant 将这部分重复工作变成一次本地命令，同时明确区分事实与待确认项。

## 核心能力

- 采集当前分支、Git 状态、变更文件、diff 统计、diff 内容和最近提交。
- 提供 `pr`、`release`、`review` 三种交付模式。
- 根据前端、API、配置、依赖和数据库文件给出针对性风险与测试建议。
- 支持只分析暂存变更，并限制超长 diff，避免大仓库输出失控。
- 只使用 Python 标准库与本地 Git，不依赖云端 API。

## 环境要求

- Python 3.9 或更高版本。
- Git 2.x。
- 一个需要分析的本地 Git 仓库。

确认环境：

```powershell
python --version
git --version
```

Windows 如果提示找不到 `python`，请先从 [Python 官网](https://www.python.org/downloads/windows/) 安装，并在安装界面勾选将 Python 加入 PATH。

## 快速开始

克隆项目：

```powershell
git clone https://github.com/cyy-ouc-edu/local-code-release-assistant.git
cd local-code-release-assistant
```

为另一个本地仓库生成 PR 报告：

```powershell
python scripts/generate_report.py --repo C:\path\to\your-repository --mode pr --output pr_report.md
```

只分析已暂存的改动：

```powershell
python scripts/generate_report.py --repo C:\path\to\your-repository --mode review --staged --output review_report.md
```

生成发布说明：

```powershell
python scripts/generate_report.py --repo C:\path\to\your-repository --mode release --output release_notes.md
```

仅查看结构化 Git 上下文：

```powershell
python scripts/collect_git_context.py --repo C:\path\to\your-repository
```

## 输出内容

报告包含：变更摘要、变更文件、行为影响、风险等级、测试建议、回滚方案、对应模式的交付文案，以及需要人工确认的问题。

查看已生成的公开样例：

- [前端交互报告](examples/frontend_report.md)
- [API 审查报告](examples/api_report.md)
- [配置发布报告](examples/config_report.md)

## 作为 Skill 使用

将整个目录放到支持 Agent Skills 标准的 Skills 目录中。之后可以直接对 Agent 说：

```text
请检查当前仓库的暂存改动，生成 PR 描述、风险点和测试建议。
```

Agent 会按照 `SKILL.md` 选择报告模式，并调用本地脚本。发布到 ModelScope 后也可通过 Skills Center 安装。

## 隐私设计

- 默认只读取本机 Git 元数据和 diff。
- 不读取环境变量，不连接外部模型或分析服务。
- 报告不包含仓库绝对路径。
- 自动分析只作为交付草稿，不声称测试已通过或部署已成功。

## 限制

- 基于文件路径和 Git 变更进行规则分析，不能替代人工代码审查。
- 无法仅凭 diff 确认真实业务意图、测试结果和部署状态。
- 二进制文件只能识别为变更，不能分析其内容。

## Roadmap

- 中英文报告切换。
- Conventional Commits 建议。
- 按模块汇总大型仓库变更。
- 可配置的项目风险规则。

## License

[MIT](LICENSE)
