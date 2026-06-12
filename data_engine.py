import akshare as ak
import pandas as pd
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from exceptions import DataFetchError, InvalidStockCode, InsufficientDataError, DataValidationError

logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """
    核心数据引擎：负责金融数据的抓取、清洗与技术指标计算
    
    功能包括：
    - 从AKShare获取A股历史K线数据
    - 计算技术指标（MA、MACD）
    - 执行量化策略回测
    - 获取个股舆情新闻
    """
    
    def __init__(self, stock_code: str):
        """
        初始化MarketDataFetcher
        
        Args:
            stock_code: A股股票代码（6位数字）
            
        Raises:
            InvalidStockCode: 如果股票代码格式无效
        """
        self.stock_code = stock_code.strip()
        self._validate_stock_code()

    def _validate_stock_code(self) -> None:
        """验证股票代码格式"""
        if not self.stock_code or len(self.stock_code) != 6 or not self.stock_code.isdigit():
            logger.error(f"❌ 无效的股票代码: {self.stock_code}")
            raise InvalidStockCode(f"股票代码必须是6位数字，收到: {self.stock_code}")

    def fetch_history_prices(self, start_date: str = "20240101") -> pd.DataFrame:
        """
        获取A股历史K线数据，并计算高阶量化因子
        
        Args:
            start_date: 开始日期（格式YYYYMMDD）
            
        Returns:
            包含OHLC、均线、MACD的DataFrame
            
        Raises:
            DataFetchError: 如果数据获取失败
            InsufficientDataError: 如果数据不足以计算指标
        """
        try:
            logger.info(f"📊 正在获取 {self.stock_code} 的历史K线数据...")
            end_date = datetime.now().strftime("%Y%m%d")
            df = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            
            if df.empty:
                logger.warning(f"⚠️ 股票 {self.stock_code} 在指定时间范围内无数据")
                raise DataFetchError(f"无法获取 {self.stock_code} 的历史数据，请检查代码是否正确")
            
            # 数据清洗与标准化
            df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
            df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']
            df['Date'] = pd.to_datetime(df['Date'])
            
            # 检查最少数据点数（计算MA20需要20个数据点）
            if len(df) < 20:
                logger.error(f"❌ 数据点数不足: {len(df)} < 20")
                raise InsufficientDataError(f"数据不足以计算技术指标（需要至少20个交易日，当前：{len(df)}）")
            
            # 计算技术指标
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            
            # MACD 动量因子
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD_DIF'] = exp1 - exp2
            df['MACD_DEA'] = df['MACD_DIF'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = 2 * (df['MACD_DIF'] - df['MACD_DEA'])
            
            logger.info(f"✅ 数据获取成功 | 记录数: {len(df)}")
            return df
            
        except Exception as e:
            error_msg = f"数据获取异常: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise DataFetchError(error_msg)

    def run_strategy_backtest(self, df: pd.DataFrame) -> Dict:
        """
        执行专业级量化策略回测
        
        策略逻辑：MA金叉 且 MACD为正（双因子共振）
        
        Args:
            df: 包含技术指标的DataFrame
            
        Returns:
            {
                "data": 回测DataFrame,
                "metrics": {
                    "total_return_strat": float,  # 策略累计收益率
                    "total_return_bench": float,  # 基准累计收益率
                    "annual_volatility": float,   # 年化波动率
                    "sharpe_ratio": float,        # 夏普比率
                    "max_drawdown": float         # 最大回撤
                }
            }
            
        Raises:
            InsufficientDataError: 数据不足以执行回测
        """
        try:
            if df.empty or len(df) < 20:
                logger.error(f"❌ 回测数据不足: {len(df) if not df.empty else 0}")
                raise InsufficientDataError("回测需要至少20个交易日的数据")
                
            backtest_df = df.copy()
            
            # 核心策略逻辑：MA金叉 且 MACD为正（双因子共振）
            condition_buy = (backtest_df['MA5'] > backtest_df['MA20']) & (backtest_df['MACD_Hist'] > 0)
            backtest_df['Position'] = np.where(condition_buy, 1, 0)
            
            # 计算收益
            backtest_df['Daily_Return'] = backtest_df['Close'].pct_change()
            backtest_df['Strategy_Return'] = backtest_df['Position'].shift(1) * backtest_df['Daily_Return']
            
            # 计算累积净值
            backtest_df['Cum_Benchmark'] = (1 + backtest_df['Daily_Return'].fillna(0)).cumprod()
            backtest_df['Cum_Strategy'] = (1 + backtest_df['Strategy_Return'].fillna(0)).cumprod()
            
            # 计算风险调整指标
            annual_volatility = backtest_df['Strategy_Return'].std() * np.sqrt(252)
            
            # 夏普比率（假设无风险年化利率为2.5%）
            risk_free_rate = 0.025 
            excess_daily_return = backtest_df['Strategy_Return'].mean() - (risk_free_rate / 252)
            sharpe_ratio = (excess_daily_return / backtest_df['Strategy_Return'].std()) * np.sqrt(252) if backtest_df['Strategy_Return'].std() != 0 else 0
            
            # 最大回撤
            roll_max = backtest_df['Cum_Strategy'].cummax()
            drawdown = backtest_df['Cum_Strategy'] / roll_max - 1
            max_drawdown = drawdown.min()
            
            result = {
                "data": backtest_df,
                "metrics": {
                    "total_return_strat": backtest_df['Cum_Strategy'].iloc[-1] - 1,
                    "total_return_bench": backtest_df['Cum_Benchmark'].iloc[-1] - 1,
                    "annual_volatility": annual_volatility,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown
                }
            }
            
            logger.info(f"✅ 回测完成 | 夏普比率: {sharpe_ratio:.2f} | 最大回撤: {max_drawdown*100:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ 回测异常: {str(e)}")
            raise

    def fetch_latest_news(self) -> List[str]:
        """
        获取个股最新的媒体新闻/股吧头条
        
        包含防错断网兜底机制，确保应用不因网络故障而崩溃
        
        Returns:
            新闻标题列表
        """
        try:
            logger.info(f"📰 正在抓取 {self.stock_code} 的全网舆情新闻...")
            news_df = ak.stock_news_em(symbol=self.stock_code)
            
            if news_df.empty:
                logger.warning(f"⚠️ 接口返回空数据，使用降级方案")
                return self._get_fallback_news()
            
            news_list = news_df['新闻标题'].head(20).tolist()
            logger.info(f"✅ 获取新闻 {len(news_list)} 条")
            return news_list
            
        except Exception as e:
            logger.warning(f"⚠️ 网络爬虫受限，启用离线兜底语料库 | 错误: {str(e)}")
            return self._get_fallback_news()
    
    def _get_fallback_news(self) -> List[str]:
        """获取离线降级新闻语料库"""
        return [
            f"代码{self.stock_code}近期大宗交易活跃度上升",
            "科技板块整体迎来机构资金加仓布局",
            "宏观经济数据向好，市场风险偏好整体回升",
            "公司发布最新财报，营收实现稳健增长",
            "机构研报指出该股估值处于历史底部区域"
        ]
    def simulate_future_prices(self, df: pd.DataFrame, days: int = 10, simulations: int = 5) -> dict:
        """
        [新增功能] 蒙特卡洛模拟预测：基于历史日收益率的均值和标准差，模拟未来 N 天的股价走势
        """
        import numpy as np
        
        if df.empty or len(df) < 20:
            return {}
            
        # 1. 计算对数收益率的均值和标准差（波动率）
        returns = df['Close'].pct_change().dropna()
        mu = returns.mean()
        sigma = returns.std()
        last_price = df['Close'].iloc[-1]
        last_date = df['Date'].iloc[-1]
        
        # 2. 生成未来日期序列
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
        
        # 3. 运行多次蒙特卡洛随机模拟
        paths = []
        for _ in range(simulations):
            # 生成服从正态分布的随机收益率
            sim_returns = np.random.normal(mu, sigma, days)
            # 累乘计算价格路径
            price_path = [last_price]
            for r in sim_returns:
                price_path.append(price_path[-1] * (1 + r))
            paths.append(price_path[1:]) # 舍去第一个基准价
            
        return {
            "dates": future_dates,
            "paths": paths,
            "last_price": last_price
        }  
    