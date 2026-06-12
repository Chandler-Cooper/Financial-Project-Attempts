from openai import OpenAI
import logging

class FinancialAgent:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        
        # 定义全局人设
        self.system_prompt = """
        你是一位拥有15年A股实战经验的顶尖百亿私募量化基金经理。
        擅长结合“结构化技术面”与“非结构化舆情面”进行深度多维共振分析。
        面对用户的提问，你的回答要专业、犀利、逻辑严密，多用金融术语。
        如果用户提出假设，你需要进行沙盘推演。
        """

    def generate_initial_prompt(self, stock_code: str, price: float, ma_status: str, macd_status: str, news_list: list) -> str:
        """生成首轮背景注入的 Prompt"""
        news_text = "\n".join([f"{i+1}. {news}" for i, news in enumerate(news_list[:10])])
        return f"""
        请基于以下关于股票【{stock_code}】的最新多模态数据，生成今日盘后投研简报：
        [结构化技术面] 收盘价：{price:.2f}，均线：{ma_status}，MACD：{macd_status}
        [消息面舆情] {news_text}
        【格式要求】：
        🎯 **核心结论**：（定性当前盘面）
        💡 **多空逻辑**：（结合数据交叉验证）
        ⚠️ **风险防范**：（潜在雷点或支撑位）
        """

    def stream_chat(self, messages: list):
        """
        [硬核升级] 支持上下文记忆的流式对话引擎 (Streaming Generator)
        """
        try:
            # 强制把系统人设插在对话最前面
            full_messages = [{"role": "system", "content": self.system_prompt}] + messages
            
            # 开启 stream=True 进行打字机输出
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=full_messages,
                temperature=0.4,
                stream=True  # 流式输出，大幅提升高级感
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logging.error(f"大模型对话异常: {e}")
            yield f"\n\n❌ 抱歉，Agent 连接出现异常：{str(e)}"