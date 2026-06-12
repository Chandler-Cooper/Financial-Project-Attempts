"""
A股量化与舆情智能分析系统 - 自定义异常类

统一的异常处理机制，便于错误追踪和降级处理
"""


class FinancialAnalysisException(Exception):
    """基础异常类 - 所有业务异常的父类"""
    pass


# ============================================================================
# 数据相关异常
# ============================================================================
class DataFetchError(FinancialAnalysisException):
    """数据获取失败异常"""
    pass


class InvalidStockCode(FinancialAnalysisException):
    """无效的股票代码异常"""
    pass


class DataValidationError(FinancialAnalysisException):
    """数据验证失败异常"""
    pass


class InsufficientDataError(FinancialAnalysisException):
    """数据不足异常（如计算MA需要足够的历史数据）"""
    pass


# ============================================================================
# NLP 与情感分析异常
# ============================================================================
class NLPProcessingError(FinancialAnalysisException):
    """NLP处理异常"""
    pass


class SentimentAnalysisError(FinancialAnalysisException):
    """情感分析异常"""
    pass


class WordCloudGenerationError(FinancialAnalysisException):
    """词云生成异常"""
    pass


# ============================================================================
# LLM 与 AI 相关异常
# ============================================================================
class LLMConnectionError(FinancialAnalysisException):
    """LLM连接异常"""
    pass


class LLMAPIError(FinancialAnalysisException):
    """LLM API调用异常"""
    pass


class InvalidAPIKeyError(FinancialAnalysisException):
    """无效的API Key异常"""
    pass


class LLMTimeoutError(FinancialAnalysisException):
    """LLM请求超时异常"""
    pass


# ============================================================================
# 量化分析异常
# ============================================================================
class BacktestError(FinancialAnalysisException):
    """回测异常"""
    pass


class StrategyConfigError(FinancialAnalysisException):
    """策略配置错误异常"""
    pass


# ============================================================================
# 配置与系统异常
# ============================================================================
class ConfigError(FinancialAnalysisException):
    """配置错误异常"""
    pass


class SystemError(FinancialAnalysisException):
    """系统级异常"""
    pass
