from snownlp import SnowNLP
import numpy as np
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import platform
import logging
from typing import List, Dict, Optional
import matplotlib
from exceptions import NLPProcessingError, SentimentAnalysisError, WordCloudGenerationError

logger = logging.getLogger(__name__)

# 防止matplotlib在没有显示器时崩溃
matplotlib.use('Agg')


class TextSentimentAnalyzer:
    """
    核心智能NLP分析引擎
    
    功能包括：
    - 贝叶斯情感打分
    - Jieba分词与词云渲染
    - 多层次文本处理
    """
    
    def __init__(self):
        """
        初始化TextSentimentAnalyzer
        
        预设中文停用词表，过滤无效词汇，提升词云专业度
        """
        self.stopwords = {
            "的", "了", "和", "是", "在", "公司", "股份", "股票", "市场", 
            "与", "及", "等", "或", "将", "为", "被", "由", "从", "到", 
            "一", "个", "两", "三", "年", "月", "日", "本", "中", "国"
        }
        logger.info("✅ NLP引擎初始化完成")

    def analyze_sentence_score(self, text: str) -> float:
        """
        对单条文本进行情感打分
        
        Args:
            text: 输入文本
            
        Returns:
            情感分数 (0-1，>0.5为正向)
        """
        try:
            if not text or not isinstance(text, str):
                return 0.5
            return float(SnowNLP(text).sentiments)
        except Exception as e:
            logger.warning(f"⚠️ 情感分析异常: {e}")
            return 0.5

    def batch_sentiment_pipeline(self, news_list: List[str]) -> Dict[str, any]:
        """
        批量计算舆情情感指数
        
        Args:
            news_list: 新闻标题列表
            
        Returns:
            {
                "mean": float,           # 平均情感分 (0-1)
                "status": str,           # 定性评价 ("多头狂热"/"理性震荡"/"空头恐慌")
                "scores": List[float],   # 逐条新闻得分
                "raw_titles": List[str]  # 原始标题
            }
        """
        try:
            if not news_list:
                logger.warning("⚠️ 新闻列表为空，返回中性评价")
                return {
                    "mean": 0.5, 
                    "status": "中性", 
                    "scores": [],
                    "raw_titles": []
                }
                
            scores = [self.analyze_sentence_score(title) for title in news_list]
            avg_score = float(np.mean(scores))
            
            if avg_score > 0.65:
                status = "多头狂热 (Bullish)"
            elif avg_score < 0.35:
                status = "空头恐慌 (Bearish)"
            else:
                status = "理性震荡 (Neutral)"
            
            result = {
                "mean": round(avg_score, 3),
                "status": status,
                "scores": scores,
                "raw_titles": news_list
            }
            
            logger.info(f"✅ 情感分析完成 | 平均分: {avg_score:.3f} | 定性: {status}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 批量情感分析异常: {e}")
            raise SentimentAnalysisError(f"情感分析失败: {str(e)}")

    def generate_wordcloud(self, news_list: List[str]) -> Optional[plt.Figure]:
        """
        基于新闻头条生成动态舆情词云图
        
        Args:
            news_list: 新闻标题列表
            
        Returns:
            matplotlib Figure对象，或None（失败时）
        """
        try:
            if not news_list:
                logger.warning("⚠️ 新闻列表为空，无法生成词云")
                return None
            
            # 1. 文本合并与 Jieba 分词
            text = " ".join(news_list)
            words = jieba.cut(text)
            filtered_words = " ".join([w for w in words if w not in self.stopwords and len(w) > 1])
            
            # 2. 动态匹配操作系统中的中文字体
            sys_type = platform.system()
            font_path = "simhei.ttf" if sys_type == "Windows" else "Arial Unicode.ttf"
            
            wc = WordCloud(
                font_path=font_path,
                width=600, height=400,
                background_color="white",
                max_words=50,
                colormap="viridis"
            ).generate(filtered_words)
            
            # 3. 消除边框和留白
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            
            logger.info("✅ 词云生成成功")
            return fig
            
        except Exception as e:
            logger.error(f"❌ 词云生成失败: {e}")
            raise WordCloudGenerationError(f"词云生成失败（可能缺少中文字体）: {str(e)}")
        
    def extract_core_summary(self, news_list: List[str], limit: int = 3) -> List[str]:
        """
        核心摘要提取：利用 TextRank 算法提取舆情中最关键的 N 句话
        
        Args:
            news_list: 新闻标题列表
            limit: 摘要条数
            
        Returns:
            摘要列表
        """
        try:
            if not news_list:
                return []
            
            # 将所有新闻标题拼接成一篇"长文章"
            full_text = "。".join(news_list)
            
            # SnowNLP 内置的基于 TextRank 的摘要提取
            s = SnowNLP(full_text)
            summary = s.summary(limit)
            
            logger.info(f"✅ 摘要提取完成 | 条数: {len(summary)}")
            return summary
            
        except Exception as e:
            logger.warning(f"⚠️ 摘要提取失败，返回原标题: {e}")
            # 防错机制
            return news_list[:limit]