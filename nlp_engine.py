from snownlp import SnowNLP
import numpy as np
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import platform
import logging

class TextSentimentAnalyzer:
    """
    核心智能分析引擎：包含贝叶斯情感打分与Jieba分词词云渲染
    """
    def __init__(self):
        # 预设中文停用词表，过滤无效词汇，提升词云专业度
        self.stopwords = {"的", "了", "和", "是", "在", "公司", "股份", "股票", "市场", "与", "及", "等", "或", "将"}

    def analyze_sentence_score(self, text: str) -> float:
        if not text or not isinstance(text, str): return 0.5
        try:
            return SnowNLP(text).sentiments
        except:
            return 0.5

    def batch_sentiment_pipeline(self, news_list: list) -> dict:
        if not news_list:
            return {"mean": 0.5, "status": "中性", "scores": []}
            
        scores = [self.analyze_sentence_score(title) for title in news_list]
        avg_score = float(np.mean(scores))
        
        if avg_score > 0.65:
            status = "多头狂热 (Bullish)"
        elif avg_score < 0.35:
            status = "空头恐慌 (Bearish)"
        else:
            status = "理性震荡 (Neutral)"
            
        return {
            "mean": round(avg_score, 3),
            "status": status,
            "scores": scores,
            "raw_titles": news_list
        }

    def generate_wordcloud(self, news_list: list):
        """
        新增高阶功能：基于新闻头条生成动态舆情词云图
        """
        if not news_list: return None
        
        # 1. 文本合并与 Jieba 分词
        text = " ".join(news_list)
        words = jieba.cut(text)
        filtered_words = " ".join([w for w in words if w not in self.stopwords and len(w) > 1])
        
        # 2. 动态匹配操作系统中的中文字体（防止词云显示为方块）
        sys_type = platform.system()
        font_path = "simhei.ttf" if sys_type == "Windows" else "Arial Unicode.ttf"
        
        try:
            wc = WordCloud(
                font_path=font_path,
                width=600, height=400, # 稍微调整长宽比，更适合侧边栏
                background_color="white",
                max_words=50,
                colormap="viridis"
            ).generate(filtered_words)
            
            # 【修改点】：消除 matplotlib 默认的边框和留白，让词云更紧凑美观
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0) # 消除留白
            return fig
        except Exception as e:
            logging.error(f"词云生成失败(可能是系统缺少中文字体): {e}")
            return None
        
    def extract_core_summary(self, news_list: list, limit: int = 3) -> list:
        """
        [新增功能] 核心摘要提取：利用 TextRank 算法提取全网舆情中最关键的 N 句话
        """
        if not news_list: return []
        
        # 将所有新闻标题拼接成一篇“长文章”
        full_text = "。".join(news_list)
        
        try:
            # SnowNLP 内置了基于 TextRank 的摘要提取能力
            s = SnowNLP(full_text)
            return s.summary(limit)
        except Exception:
            # 防错机制
            return news_list[:limit]