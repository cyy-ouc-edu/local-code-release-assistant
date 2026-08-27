# ModelScope 提交清单

## Skill 创建页

| 字段 | 填写内容 |
| --- | --- |
| 英文名称 | `local-code-release-assistant` |
| 展示名称 | `Local Code Release Assistant / 本地代码交付助手` |
| 来源地址 | `https://github.com/cyy-ouc-edu/local-code-release-assistant` |
| 所有者 | 选择当前账号 `OUCShip` |
| License | `MIT License` |
| 是否公开 | `公开` |
| Skill 类型 | 优先选择 `Developer Tools / 开发者工具`；没有该项时选择 `Code Quality & Testing / 代码质量与测试` |
| 自定义标签 | `git`、`code-review`、`release-notes`、`local-first` |
| Skill 文件 | `dist/local-code-release-assistant-0.1.0.zip` |
| 图标 | 非必填；时间紧时沿用平台默认图标 |

## 简短描述

Local Code Release Assistant 是一个本地优先的代码交付 Skill。它读取 Git 变更，自动生成 PR 描述、发布说明、风险点、测试建议和回滚提示。无需云端 API，源码默认不离开本机。

## 完整项目介绍

开发者完成编码后，仍需反复阅读 diff、归纳影响范围、补写 PR 描述，并思考测试与回滚方案。这个过程重复、容易遗漏，私有代码也不适合上传到外部分析服务。

Local Code Release Assistant 在本地采集当前分支、工作区状态、变更文件、diff 统计和最近提交，通过可解释规则生成结构化交付报告。它提供 PR、发布和审查三种模式，可识别前端交互、API、配置、依赖和数据库相关风险，并给出针对性测试建议与回滚提示。自动分析不会声称测试已经通过，也会把无法从 diff 确定的业务信息保留为待确认项。

项目仅依赖 Python 标准库与 Git，不连接外部模型或分析 API。仓库提供三组公开合成样例、验收清单和可一键创建的演示仓库，方便评委复现完整流程。

## 核心亮点

- 本地优先：默认不上传代码，不读取环境变量或凭据。
- 一次生成：把零散 Git diff 整理为可直接使用的交付 Markdown。
- 三种模式：覆盖 PR 描述、发布说明和变更审查。
- 风险可解释：根据变更类型给出 P0/P1/P2 提示与对应测试建议。
- 零云端依赖：仅需 Python 3.9+ 与 Git。
- 可复现：自带前端、API、配置样例和 60-90 秒演示流程。

## 使用方式

```powershell
python scripts/generate_report.py --repo C:\path\to\repository --mode pr --output pr_report.md
```

只检查暂存改动：

```powershell
python scripts/generate_report.py --repo C:\path\to\repository --mode review --staged --output review_report.md
```

## Demo 描述

演示从一个包含 API 参数校验改动的本地 Git 仓库开始。执行一条命令后，Skill 生成结构化审查报告，自动指出 API 兼容性风险、成功与失败路径测试、鉴权与向后兼容检查，以及回滚和待确认事项。整个过程不上传源码。

## 提交前核对

- [ ] GitHub 仓库可公开访问，README 与目录完整。
- [ ] ZIP 根目录正好包含一个 `SKILL.md`。
- [ ] ZIP 小于 5 MB。
- [ ] 来源地址填写 GitHub 仓库链接。
- [ ] License 选择 MIT。
- [ ] Skill 设置为公开。
- [ ] 演示视频或两张关键截图已准备。
- [ ] 创建后打开 Skill 详情页，确认安装说明和文件列表可见。
- [ ] 保存创建成功页面和比赛作品提交状态截图。
