from openai import OpenAI
import logging
from typing import List, Dict, Generator, Optional
from config import Config
from exceptions import InvalidAPIKeyError, LLMConnectionError, LLMAPIError, LLMTimeoutError

logger = logging.getLogger(__name__)


class FinancialAgent:
    """
    大模型驱动的量化投研智能助手
    
    支持流式对话、上下文记忆、沙盘推演
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化FinancialAgent
        
        Args:
            api_key: DeepSeek API Key，若为None则从环境变量读取
            base_url: LLM服务基础URL，若为None则使用配置默认值
            
        Raises:
            InvalidAPIKeyError: 如果未提供API Key且环境变量未配置
        """
        # 优先级：入参 > 环境变量 > 配置
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        
        if not self.api_key:
            logger.error("❌ 未配置 DEEPSEEK_API_KEY")
            raise InvalidAPIKeyError(
                "DeepSeek API Key 未配置。请在 .env 文件中设置 DEEPSEEK_API_KEY 或通过参数传入。"
            )
        
        self.base_url = base_url or Config.LLM_BASE_URL
        
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.info(f"✅ LLM 客户端初始化成功 | 地址: {self.base_url}")
        except Exception as e:
            logger.error(f"❌ LLM 客户端初始化失败: {e}")
            raise LLMConnectionError(f"无法连接到 LLM 服务: {str(e)}")
        
        # 定义全局人设
        self.system_prompt = """
        你是一位拥有15年A股实战经验的顶尖百亿私募量化基金经理。
        擅长结合“结构化技术面”与“非结构化舆情面”进行深度多维共振分析。
        面对用户的提问，你的回答要专业、犀利、逻辑严密，多用金融术语。
        如果用户提出假设，你需要进行沙盘推演。
        
        重要提示：
        - 始终基于提供的数据进行分析
        - 清晰标注风险和不确定性
        - 避免绝对化判断
        """

    def generate_initial_prompt(
        self,
        stock_code: str,
        price: float,
        ma_status: str,
        macd_status: str,
        news_list: List[str]
    ) -> str:
        """
        生成首轮背景注入的 Prompt
        
        Args:
            stock_code: 股票代码
            price: 收盘价
            ma_status: 均线状态描述
            macd_status: MACD状态描述
            news_list: 新闻标题列表
            
        Returns:
            格式化的prompt字符串
        """
        news_text = "\n".join([f"{i+1}. {news}" for i, news in enumerate(news_list[:10])])
        return f"""
        请基于以下关于股票【{stock_code}】的最新多模态数据，生成今日盘后投研简报：
        
        【结构化技术面】
        - 收盘价：{price:.2f}
        - 均线：{ma_status}
        - MACD：{macd_status}
        
        【消息面舆情】
        {news_text}
        
        【分析要求】：
        🎯 **核心结论**：定性当前盘面（明确看多/看空/中性）
        💡 **多空逻辑**：结合技术面+舆情面的交叉验证
        ⚠️ **风险防范**：列举潜在雷点、支撑位、阻力位
        """

    def stream_chat(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        支持上下文记忆的流式对话引擎
        
        Args:
            messages: 对话历史列表，格式为
                [{"role": "user/assistant", "content": "..."}]
                
        Yields:
            流式文本片段
            
        Raises:
            InvalidAPIKeyError: API Key无效
            LLMConnectionError: 连接失败
            LLMTimeoutError: 请求超时
            LLMAPIError: API返回错误
        """
        try:
            # 强制把系统人设插在对话最前面
            full_messages = [{"role": "system", "content": self.system_prompt}] + messages
            
            # 开启 stream=True 进行打字机输出
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=full_messages,
                temperature=Config.LLM_TEMPERATURE,
                stream=True  # 流式输出
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
            logger.info(f"✅ LLM对话完成 | 轮次: {len([m for m in messages if m['role']=='user'])}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ LLM对话异常: {error_msg}")
            
            # 异常分类
            if "401" in error_msg or "Unauthorized" in error_msg:
                raise InvalidAPIKeyError("API Key 无效或已过期")
            elif "timeout" in error_msg.lower():
                raise LLMTimeoutError("LLM请求超时，请重试")
            elif "connection" in error_msg.lower():
                raise LLMConnectionError("无法连接到LLM服务")
            else:
                raise LLMAPIError(f"LLM API 返回错误: {error_msg}")
            
            yield f"\n\n❌ 抱歉，Agent 连接出现异常：{error_msg}"