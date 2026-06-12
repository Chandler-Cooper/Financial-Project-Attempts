# 🚀 快速开始指南

欢迎使用 **A股量化与舆情智能分析系统**！本指南将帮您在 5 分钟内启动应用。

---

## 📋 前置要求

| 环节 | 版本要求 |
|------|---------|
| Python | 3.9+ （推荐 3.11） |
| pip | 最新版本 |
| Git | 可选 |

---

## 🔧 安装步骤

### 方式一：本地开发环境（推荐个人用户）

**第1步：克隆或下载项目**
```bash
git clone https://github.com/Chandler-Cooper/Financial-Project-Attempts.git
cd Financial-Project-Attempts
```

**第2步：创建虚拟环境**
```bash
# 使用 conda（推荐）
conda create -n fin-analysis python=3.11
conda activate fin-analysis

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows PowerShell
```

**第3步：安装依赖**
```bash
pip install -r requirements.txt
```

**第4步：配置环境变量（可选）**
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env，填入 DeepSeek API Key
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

**第5步：启动应用**
```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`

---

### 方式二：Docker 容器（推荐企业用户）

**前置条件：已安装 Docker 和 docker-compose**

**一键启动：**
```bash
# 启动应用
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问
# http://localhost:8501
```

**停止应用：**
```bash
docker-compose down
```

---

## 📊 首次使用

### 1️⃣ 输入股票代码
- 在左侧边栏输入 A 股股票代码（6 位数字，如 `688111`）
- 选择起始查询日期

### 2️⃣ 点击【开始智能分析】
系统将自动：
- ✅ 获取历史 K 线数据
- ✅ 计算技术指标（MA、MACD）
- ✅ 爬取最新新闻
- ✅ 进行情感分析

### 3️⃣ 查看实时监控看板
- 📊 **K 线图表**：技术走势分析
- 💭 **舆情指数**：市场情绪评估
- ☁️ **词云分析**：热点话题提取

### 4️⃣ 启用 AI 助手（可选）
- 获取 DeepSeek API Key：https://platform.deepseek.com
- 在左侧边栏输入 API Key
- 点击【一键注入数据】生成投研简报
- 进行多轮对话，进行沙盘推演

### 5️⃣ 查看策略回测
- 切换到【🧪 量化策略历史回测沙盒】
- 查看双因子策略的历史表现
- 对比基准（买入持有）

---

## 🆘 常见问题

### Q1: 提示"找不到模块"怎么办？

**解决方案：**
```bash
# 重新安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 或清空缓存重装
pip install -r requirements.txt --no-cache-dir --force-reinstall
```

---

### Q2: 词云显示为方块或无法渲染？

**问题原因：** 系统缺少中文字体

**解决方案：**

**Windows:**
```bash
# 将 simhei.ttf 复制到 C:\Windows\Fonts\
# 或使用 pip 安装中文字体包
pip install matplotlib-cjk-fonts
```

**Linux:**
```bash
sudo apt-get install fonts-noto-cjk
```

**macOS:**
```bash
brew install font-noto-cjk
```

---

### Q3: 没有 API Key 也能用吗？

**是的！** 系统分为两部分：
- ✅ **看板功能**（K线、舆情、回测）：无需 API Key
- ❌ **AI 助手功能**：需要 DeepSeek API Key

---

### Q4: 数据获取失败怎么办？

**常见原因：**
1. 网络连接问题
2. AKShare 接口暂时不可用
3. 股票代码错误

**解决方案：**
- 检查网络连接
- 确认股票代码格式（6位数字，如 `688111`）
- 等待 1 分钟后重试
- 查看日志：`logs/app.log`

---

### Q5: 如何修改策略参数？

**当前版本：** 参数已硬编码，需要手动修改源代码

**修改位置：** `data_engine.py` 第 33-35 行
```python
df['MA5'] = df['Close'].rolling(window=5).mean()    # 改这里
df['MA20'] = df['Close'].rolling(window=20).mean()  # 改这里
```

**未来版本：** 计划在 Streamlit 侧边栏添加滑块调参

---

## 📚 深入学习

### 项目结构
```
├── app.py                 # Streamlit 主程序
├── data_engine.py         # 数据与回测引擎
├── nlp_engine.py          # NLP 情感分析
├── llm_agent.py           # 大模型 AI 助手
├── config.py              # 配置管理
├── exceptions.py          # 自定义异常
├── requirements.txt       # 依赖清单
├── Dockerfile             # 容器镜像
├── docker-compose.yml     # 容器编排
├── .env.example           # 环境变量示例
└── logs/                  # 运行日志（自动生成）
```

### 查看完整文档

详见项目根目录的 [README.md](README.md)

---

## 🆘 获取帮助

| 问题类型 | 解决方案 |
|---------|---------|
| 🐛 **Bug 或异常** | [GitHub Issues](https://github.com/Chandler-Cooper/Financial-Project-Attempts/issues) |
| 💬 **功能建议** | [GitHub Discussions](https://github.com/Chandler-Cooper/Financial-Project-Attempts/discussions) |
| 📖 **使用文档** | [完整 README](README.md) |
| 🚀 **版本更新** | [CHANGELOG](CHANGELOG.md) |

---

## 🎓 推荐学习路径

1. **初级** → 查看 K 线图表和舆情指数
2. **中级** → 学习技术指标（MA、MACD）
3. **进阶** → 理解回测指标（夏普比率、最大回撤）
4. **专家** → 修改策略参数，研发新策略

---

**现在就开始吧！** 🚀 `streamlit run app.py`
