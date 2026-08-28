# 【Intel AI PC】让本地 Git 变更自动变成可交付的审查报告：Local Code Release Assistant

## 一、为什么要做这个 Skill

一次代码提交的成本并不只在编码本身。开发者通常还需要重新阅读 Git diff、整理 PR 描述、判断接口或配置风险、补充测试范围，并准备发布后的回滚方案。这个过程重复且容易遗漏；对于私有代码，直接上传完整源码到外部服务也并不合适。

Local Code Release Assistant 将这段交付准备工作封装为一个本地优先的 Agent Skill。它只读取本地 Git 工作区的状态和 diff，生成结构化的 Markdown 报告，包括变更摘要、风险点、测试建议、PR/发布文案和回滚提示。

项目源码：[cyy-ouc-edu/local-code-release-assistant](https://github.com/cyy-ouc-edu/local-code-release-assistant)

## 二、能力与边界

Skill 提供三种模式：

- `pr`：生成 Pull Request 描述。
- `release`：生成发布说明与回滚提示。
- `review`：生成变更审查风险与测试建议。

当前实现使用 Python 标准库和本地 Git，不调用云端模型或外部分析 API。它不读取环境变量、凭据或私有配置；报告中也不输出仓库绝对路径。规则分析会区分“从 diff 直接观察到的事实”和“仍需人工确认的事项”，不会虚构测试通过、部署成功或回滚安全。

## 三、实现方式

核心流程如下：

```text
本地 Git 工作区
  -> 收集分支、status、changed files、diff 和近期提交
  -> 根据 API、前端、配置、依赖和数据库变更识别风险
  -> 输出 Markdown 交付报告
  -> 由 Agent 按用户意图提供 PR、发布或审查结果
```

项目的 `SKILL.md` 描述触发场景和约束；`scripts/collect_git_context.py` 负责采集 Git 上下文；`scripts/generate_report.py` 负责生成报告。超长 diff 会被截断保护，避免大仓库中的分析输出失控。

## 四、在 TRAE Work 中验证本地 Skill

我将打包后的 `local-code-release-assistant-0.1.0.zip` 上传到 TRAE Work 的“技能”页面，作为个人 Skill 启用。随后在 TRAE Work 中输入自然语言指令：仅分析演示仓库当前工作区改动，生成 review 报告，不修改源代码，并返回风险、测试和回滚建议。

TRAE Work 成功调用 Skill，生成 `demo-repository_review_report.md`。这说明 Skill 不只是独立脚本，也能被生产力 Agent 按任务意图加载和执行。

<!-- 插图 1：TRAE Work 技能列表中 local-code-release-assistant 已启用。 -->

<!-- 插图 2：TRAE Work 对话中调用 Skill 并生成 demo-repository_review_report.md。 -->

## 五、演示案例：API 参数校验改动

演示仓库中仅修改了 `src/routes/orders.py`：为 `list_orders(limit)` 新增 `1 <= limit <= 100` 的参数校验。Git 统计显示为 1 个文件、2 行新增；随后运行：

```powershell
python scripts/generate_report.py --repo demo-repository --mode review --output demo_report.md
```

生成的报告识别到这不是普通的代码整理，而是可能影响既有调用方的 API 行为变化。报告给出以下结论：

- 风险：`P1 - Compatibility`，非法参数从原本可直接返回变为抛出异常。
- 测试：覆盖 `limit=1`、`limit=100`、`limit=0`、`limit=101`，以及上层接口将异常转换为稳定客户端错误的场景。
- 回滚：保留可回退的 Git 提交；如发生回归，回退交付提交并重新部署已验证版本。
- 待确认：`1..100` 是否符合产品/API 文档，以及上层是否会捕获 `ValueError` 并返回 HTTP 400。

<!-- 插图 3：终端中同时展示 git diff --stat 与 Report written to demo_report.md。 -->

<!-- 插图 4：报告中展示 P1 - Compatibility、Test Suggestions 与 Rollback Plan。 -->

## 六、Hybrid AI 与本地生产力的思考

这个 Skill 将高频、隐私敏感、规则明确的工作放在端侧完成：Git diff 不离开本机，基础分析不依赖云端推理，也不需要把代码发送给第三方。Agent 的价值在于理解开发者的交付意图，选择 PR、发布或审查模式，并把结构化结果转成适合团队使用的表达。

这种“端侧规则分析 + Agent 工作流编排”的组合，适合日常开发中的高频交付环节：减少重复整理时间，同时保留人工审查对业务意图、测试结果和发布决策的最终判断。

## 七、复现步骤

```powershell
git clone https://github.com/cyy-ouc-edu/local-code-release-assistant.git
cd local-code-release-assistant
python scripts/create_demo_repo.py --output demo-repository
python scripts/generate_report.py --repo demo-repository --mode review --output demo_report.md
```

环境要求为 Python 3.9+ 与 Git 2.x。完整用法、示例和约束见仓库 README；Skill 文件可从 ModelScope Skills Center 安装。

## 八、后续方向

- 提供中英文报告切换。
- 支持 Conventional Commits 建议。
- 为大型仓库按模块汇总改动。
- 允许团队配置专属风险规则和测试清单。

Local Code Release Assistant 的目标不是替代代码审查，而是把“读 diff 到形成可交付初稿”的重复环节压缩为一次本地、可解释、可复现的 Agent 工作流。
