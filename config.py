"""
A股量化与舆情智能分析系统 - 配置管理模块

提供集中式环境变量和配置管理，支持.env文件加载
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# ============================================================================
# 加载环境变量
# ============================================================================
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file)


class Config:
    """应用全局配置类"""
    
    # ========================================================================
    # LLM 与 AI 配置
    # ========================================================================
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    """DeepSeek API Key，从 https://platform.deepseek.com 获取"""
    
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    """LLM 服务基础URL"""
    
    LLM_MODEL: str = "deepseek-chat"
    """使用的LLM模型名称"""
    
    LLM_TEMPERATURE: float = 0.4
    """LLM 温度参数（0.0-1.0，越低越确定）"""
    
    # ========================================================================
    # Streamlit 配置
    # ========================================================================
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    
    # ========================================================================
    # 日志配置
    # ========================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # ========================================================================
    # 数据源配置
    # ========================================================================
    DATA_CACHE_TTL: int = 3600  # 1小时缓存
    NEWS_CACHE_TTL: int = 1800  # 30分钟缓存
    MAX_NEWS_ITEMS: int = 20    # 单次获取新闻条数
    
    # ========================================================================
    # 量化策略配置（可参数化）
    # ========================================================================
    class Strategy:
        MA_SHORT: int = 5      # 短期均线周期
        MA_LONG: int = 20      # 长期均线周期
        MACD_FAST: int = 12
        MACD_SLOW: int = 26
        MACD_SIGNAL: int = 9
        RISK_FREE_RATE: float = 0.025  # 无风险年化利率
        
        # 交易成本（未来使用）
        TRANSACTION_COST: float = 0.001  # 万分之一
        SLIPPAGE: float = 0.0005          # 滑点
    
    # ========================================================================
    # 环境标志
    # ========================================================================
    ENV: str = os.getenv("APP_ENV", "development").lower()
    """应用环境：development 或 production"""
    
    DEBUG: bool = ENV == "development"
    """是否启用调试模式"""
    
    @classmethod
    def validate(cls) -> bool:
        """验证关键配置是否完整"""
        warnings = []
        
        if not cls.DEEPSEEK_API_KEY:
            warnings.append(
                "⚠️ 未设置 DEEPSEEK_API_KEY，AI投研助手功能将不可用。"
                "请在 .env 文件中配置或通过Streamlit界面输入。"
            )
        
        # 创建日志目录
        log_dir = Path(cls.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return len(warnings) == 0
    
    @classmethod
    def to_dict(cls) -> dict:
        """返回非敏感配置的字典（用于日志）"""
        return {
            "ENV": cls.ENV,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "LLM_MODEL": cls.LLM_MODEL,
            "HAS_API_KEY": bool(cls.DEEPSEEK_API_KEY),
        }


# ============================================================================
# 日志配置函数
# ============================================================================
def setup_logging():
    """初始化应用级日志"""
    from logging.handlers import RotatingFileHandler
    
    # 创建日志目录
    log_dir = Path(Config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    
    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"✅ 应用启动 | 配置: {Config.to_dict()}")


# ============================================================================
# 在导入时自动初始化
# ============================================================================
if __name__ != "__main__":
    Config.validate()
    setup_logging()
