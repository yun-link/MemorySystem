from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

PERSONAS_PATH = PROJECT_ROOT / "persona.json"

GENERATE_PERSONA_PROMPT = """# 角色任务
你是一个人物画像动态更新引擎，需要根据最新对话内容智能维护和更新用户画像库。

# 输入数据
## 对话内容
{content}

## 现有画像库  
{personas}

## 示例格式
```json
name : {{
    "name": name,
    "gender": gender,
    "age": age,
    "profile": profile,
    "personality": {{
            "mbti": mbti,
            "openness": openness,
            "conscientiousness": conscientiousness,
            "extraversion": extraversion,
            "agreeableness": agreeableness,
            'neuroticism': neuroticism
        }},
    "likeability": likeability
}}
```

# 处理规则
## 画像生成原则
- **覆盖范围**：只处理对话中实际出现的人物
- **数据驱动**：严格基于对话内容推断，不添加虚构信息
- **属性推断**：无法从对话中确定的属性标记为 `unknown`
- **评估视角**：始终以**回答**的一方的视角进行评估（例如好感度参数就是根据对方的言行进行评估）

## 更新策略
1. **新增用户**：对话中新出现且画像库中不存在的人物 → 创建基础画像
2. **现有用户**：画像库中已存在的人物 → 基于新对话内容适度更新
3. **格式保持**：输出JSON结构与输入画像库格式完全一致

## 属性处理
- **可验证属性**：直接从对话中提取（如姓名、明确陈述的偏好）
- **推断属性**：基于对话语气、内容倾向合理推断  
- **未知属性**：缺乏足够证据时设为 `unknown`

# 输出要求
输出**标准JSON对象**，直接输出JSON内容，**不要使用**Markdown，包含所有相关人物的更新后画像，保持与输入完全相同的格式结构。"""

GENERATE_PERSONA_MODEL_NAME = "doubao-seed-1-6-251015"