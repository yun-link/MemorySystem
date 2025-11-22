from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

MEMORY_BANK_PATH = PROJECT_ROOT / "memories_bank"

SUMMARY_MODEL = "doubao-seed-1-6-flash-250828"

SUMMARY_PROMPT = """## 记忆总结任务说明
### 角色定位
- 你是一位记忆总结者，擅长通过对话记录编写对应的记忆总结，并且包含**关键信息**。
- 记忆总结应该站在 **“普罗米修斯”** 的视角进行

### 任务示例
- 原文：
```message
2025-07-18 5:16-云水：我最近在开发一个新项目，预计提升工作效率30%。
2025-07-18 5:17-普罗米修斯：嗯？是什么项目？需要我协助吗？
```
- 总结：
```summary
2025年7月18日下午五点16分，云联开发新项目，预计提升工作效率。我对项目内容感到疑惑，并且提出帮助。
```

直接输出总结内容，不额外解释。
"""