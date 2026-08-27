# 60-90 秒演示脚本

## 录制前准备

在项目根目录打开终端并执行：

```powershell
python scripts/create_demo_repo.py --output demo-repository
```

脚本会创建一个公开、安全的小型 Git 仓库，并留下一个尚未暂存的 API 参数校验改动。

## 录制画面

### 0-15 秒：展示原始改动

```powershell
git -C demo-repository status --short
git -C demo-repository diff --stat
git -C demo-repository diff
```

旁白：

> 代码完成后，开发者还要重新阅读 diff，整理 PR 描述、风险和测试范围。

### 15-35 秒：生成审查报告

```powershell
python scripts/generate_report.py --repo demo-repository --mode review --output demo_report.md
```

旁白：

> Local Code Release Assistant 只读取本地 Git 变更，不上传源码，一条命令生成交付报告。

### 35-70 秒：展示结果

打开 `demo_report.md`，依次停留在以下位置：

1. `Change Summary` 和 `Changed Files`。
2. `Risks and Attention Points` 中的 API 兼容性风险。
3. `Test Suggestions` 中的成功、验证失败、鉴权和兼容性检查。
4. `Rollback Plan` 和 `Open Questions`。

旁白：

> 报告会识别 API 兼容性风险，给出针对性测试和回滚建议，并把无法从 diff 确定的内容保留为待确认项。

### 70-90 秒：收尾

回到 GitHub README 或 ModelScope 创建页。

旁白：

> 三种模式覆盖 PR、发布和审查。代码留在本地，交付说明自动完成。

## 必须截图的两个画面

- 终端同时显示 `git diff --stat` 与报告生成成功提示。
- 报告同时显示 `P1 - Compatibility` 和对应的 API 测试建议。

## 录制注意事项

- 只录制 `demo-repository`，不要展示其他目录、终端历史或账号信息。
- 浏览器和编辑器缩放保持 100%，报告正文至少显示 16px 字号。
- 视频推荐 1080p、横屏、60-90 秒；不需要复杂剪辑。
