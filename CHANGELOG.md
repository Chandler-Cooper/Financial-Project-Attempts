# 📝 更新日志 (CHANGELOG)

所有项目的重大改动都会记录在此文档中。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，使用 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## 未发布版本

### 规划中的功能
- [ ] 参数优化界面（Streamlit 滑块调参）
- [ ] FinBERT 金融 NLP 模型升级
- [ ] Redis 缓存加速
- [ ] 蒙特卡洛预测可视化
- [ ] 多策略对比框架
- [ ] 用户认证系统

---

## [v1.1.0] - 工程规范化版 (2024-06-12)

### 🎉 新增

#### 工程化基础设施
- ✅ 添加 `requirements.txt` 依赖清单（Pin 版本号）
- ✅ 编写 `Dockerfile` 支持容器化部署
- ✅ 创建 `.gitignore` 防止敏感信息泄露
- ✅ 编写 `LICENSE` MIT 许可证
- ✅ 创建 `.env.example` 环境变量模板

#### 配置管理与异常处理
- ✅ 新增 `config.py` 集中式配置管理
- ✅ 新增 `exceptions.py` 自定义异常体系
- ✅ 支持 `.env` 文件加载环境变量
- ✅ 集成 `python-dotenv` 用于本地开发

#### 日志与监控
- ✅ 升级日志系统，使用 RotatingFileHandler
- ✅ 自动创建 `logs/` 目录
- ✅ 支持日志文件轮转（10MB 单个文件，保留 5 个备份）

#### 代码质量
- ✅ 添加类型注解（Type Hints）到核心模块
- ✅ 增强异常处理（try-catch + 分类异常）
- ✅ 改进函数文档字符串（Docstrings）
- ✅ 支持异常链（异常类继承体系）

#### 文档
- ✅ 创建 `QUICKSTART.md` 快速入门指南
- ✅ 创建 `CHANGELOG.md` 版本更新记录
- ✅ 增强 API 文档和使用示例

### 🔧 改进

#### app.py (Streamlit 主程序)
- 优化 API Key 管理（优先级：环保境变量 > 用户输入）
- 增强异常捕获，显示友好的错误消息
- 改进类型注解
- 添加详细的日志记录

#### data_engine.py (数据引擎)
- 添加 `_validate_stock_code()` 股票代码验证
- 增强 `fetch_history_prices()` 异常处理
- 新增 `_get_fallback_news()` 离线降级方案
- 改进 `run_strategy_backtest()` 异常捕获
- 所有方法添加详细的 Docstrings 和类型注解

#### nlp_engine.py (NLP 引擎)
- 改进 `analyze_sentence_score()` 异常处理
- 增强 `batch_sentiment_pipeline()` 的鲁棒性
- 优化 `generate_wordcloud()` 的错误处理
- 添加类型注解和 Docstrings

#### llm_agent.py (LLM Agent)
- 使用 `Config` 读取配置而非硬编码
- 增强 API Key 验证逻辑
- 改进异常分类和错误消息
- 添加详细的 Docstrings 和流式输出日志
- 修复 system_prompt 的格式

### 🐛 修复
- 修复潜在的 API Key 泄露风险
- 修复数据不足时的 IndexError
- 修复网络故障时的应用崩溃
- 改进词云字体适配（防止显示为方块）

### ⚡ 性能
- 优化日志写入性能（使用缓冲）
- 改进异常捕获效率

### 📚 文档
- 补充 API 文档的返回值说明
- 添加错误处理的最佳实践
- 增加故障排查指南

### ⚠️ 破坏性变更
- 无

### 🔐 安全性
- ✅ API Key 不再硬编码在代码中
- ✅ 敏感文件在 `.gitignore` 中
- ✅ 支持环保境变量隔离敏感配置

---

## [v1.0.0] - 初始版本 (2024-06-10)

### 🎉 新增

#### 核心功能
- ✅ 实时行情与舆情监控看板
- ✅ 大模型 AI 投研助手（DeepSeek 集成）
- ✅ 量化策略回测沙盒
- ✅ 技术指标计算（MA5/MA20/MACD）
- ✅ 情感分析与词云生成
- ✅ 流式对话支持

#### 数据与分析
- ✅ AKShare 接口集成
- ✅ 双因子共振策略
- ✅ 风险指标计算（夏普比率、最大回撤、年化波动率）
- ✅ SnowNLP 情感分析
- ✅ Jieba 分词与词云渲染

#### 前端与 UI
- ✅ Streamlit 交互式界面
- ✅ Plotly 动态图表
- ✅ K 线+均线+MACD 多层可视化
- ✅ 响应式布局

#### 部署与运维
- ✅ Docker Compose 配置
- ✅ 基础日志系统
- ✅ 缓存加速（Streamlit 内置）

---

## 注意事项

### 版本更新频率
- 每月一次 major/minor 更新
- 紧急 bug 修复随时发布

### 反馈与建议
欢迎通过以下途径参与项目：
- 📝 [GitHub Issues](https://github.com/Chandler-Cooper/Financial-Project-Attempts/issues) - 报告 Bug 或建议功能
- 💬 [GitHub Discussions](https://github.com/Chandler-Cooper/Financial-Project-Attempts/discussions) - 讨论与分享

### 兼容性
| 版本 | Python | Streamlit | 状态 |
|-----|--------|-----------|------|
| v1.1.0 | 3.9+ | 1.28+ | ✅ 当前 |
| v1.0.0 | 3.9+ | 1.28+ | ✅ 维护 |

---

**保持关注更新！** 📢
