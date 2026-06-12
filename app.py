import streamlit as st
import plotly.graph_objects as go
import datetime
from data_engine import MarketDataFetcher
from nlp_engine import TextSentimentAnalyzer

st.set_page_config(page_title="A股量化与舆情智能分析系统", layout="wide", page_icon="📈")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_and_process_data(stock_code, start_date):
    fetcher = MarketDataFetcher(stock_code)
    price_df = fetcher.fetch_history_prices(start_date=start_date)
    news_list = fetcher.fetch_latest_news()
    return price_df, news_list

class FinancialDashboardApp:
    def __init__(self):
        self.analyzer = TextSentimentAnalyzer()

    def render_sidebar(self, price_df=None):
        st.sidebar.header("🛠️ 系统控制面板")
        st.sidebar.markdown("---")
        
        stock_input = st.sidebar.text_input("请输入A股股票代码", value="688111", help="输入6位数字代码")
        default_start = datetime.date(2024, 1, 1)
        start_date = st.sidebar.date_input("选择行情起点", value=default_start)
        formatted_date = start_date.strftime("%Y%m%d") if start_date else "20240101"
        
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.sidebar.button("🚀 开始智能分析", type="primary", use_container_width=True)
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🧠 接入 Agent 大脑")
        api_key = st.sidebar.text_input(
            "🔑 DeepSeek API Key (选填)", 
            type="password", 
            help="用于驱动 AI 智能投研助手生成报告。没有Key也可正常使用看板。"
        )
        st.session_state.api_key = api_key
        
        if price_df is not None and not price_df.empty:
            st.sidebar.markdown("---")
            st.sidebar.subheader("📥 数据资产导出")
            csv = price_df.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("下载历史行情数据 (CSV)", data=csv, file_name=f'{stock_input}_quant_data.csv', mime='text/csv', use_container_width=True)
            
        return stock_input, formatted_date, submit_btn

    def display_charts(self, price_df, sentiment_dict, news_list):
        tab1, tab2 = st.tabs(["📊 实时行情与舆情监控看板", "🧪 量化策略历史回测沙盒"])
        
        # ================= Tab 1: 实时监控与 Agent 对话 =================
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 【修复点2：将聊天界面装入折叠面板，保护UI布局】
            if st.session_state.get('api_key'):
                with st.expander("🤖 点击展开你的专属 AI 量化投研助手 (支持多轮对话推演)", expanded=False):
                    if "messages" not in st.session_state:
                        st.session_state.messages = []

                    for msg in st.session_state.messages:
                        st.chat_message(msg["role"]).write(msg["content"])

                    if len(st.session_state.messages) == 0:
                        if st.button("✨ 一键注入今日大盘数据，生成基础研报", type="primary"):
                            # 【修复点3：增加数据空值保护，防止 IndexError 崩溃】
                            if not price_df.empty:
                                latest_price = price_df['Close'].iloc[-1]
                                ma_status = "均线金叉多头排列" if price_df['MA5'].iloc[-1] > price_df['MA20'].iloc[-1] else "均线死叉空头排列"
                                # 兼容性保护：确保含有 MACD_Hist 列
                                macd_status = "MACD红柱多头" if ('MACD_Hist' in price_df and price_df['MACD_Hist'].iloc[-1] > 0) else "MACD绿柱空头"
                                
                                from llm_agent import FinancialAgent
                                agent = FinancialAgent(api_key=st.session_state.api_key)
                                
                                init_prompt = agent.generate_initial_prompt(st.session_state.stock_code, latest_price, ma_status, macd_status, news_list)
                                st.session_state.messages.append({"role": "user", "content": "帮我看看今天这只票的情况。"})
                                st.chat_message("user").write("帮我看看今天这只票的情况。")
                                
                                with st.chat_message("assistant", avatar="🤖"):
                                    hidden_messages = [{"role": "user", "content": init_prompt}]
                                    stream = agent.stream_chat(hidden_messages)
                                    response = st.write_stream(stream)
                                    
                                st.session_state.messages.append({"role": "assistant", "content": response})
                                st.rerun()
                            else:
                                st.error("❌ 数据加载失败，无法生成研报。请检查股票代码。")

                    if len(st.session_state.messages) > 0:
                        if prompt := st.chat_input("您可以继续追问，例如：‘如果明晚发布利空财报，会跌破防守位吗？’"):
                            st.session_state.messages.append({"role": "user", "content": prompt})
                            st.chat_message("user").write(prompt)
                            
                            with st.chat_message("assistant", avatar="🤖"):
                                from llm_agent import FinancialAgent
                                agent = FinancialAgent(api_key=st.session_state.api_key)
                                stream = agent.stream_chat(st.session_state.messages)
                                response = st.write_stream(stream)
                                
                            st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.info("💡 提示：在左侧栏输入 API Key，即可唤醒 AI 投研助手。")

            # 渲染图表区域
            col1, col2 = st.columns([7, 3], gap="large") 
            with col1:
                if not price_df.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(x=price_df['Date'], open=price_df['Open'], high=price_df['High'], low=price_df['Low'], close=price_df['Close'], name='K线', increasing_line_color='#ef5350', decreasing_line_color='#26a69a'))
                    fig.add_trace(go.Scatter(x=price_df['Date'], y=price_df['MA5'], name='MA5 (周线)', line=dict(color='orange', width=1.5)))
                    fig.add_trace(go.Scatter(x=price_df['Date'], y=price_df['MA20'], name='MA20 (月线)', line=dict(color='blue', width=1.5)))
                    fig.update_layout(height=550, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), plot_bgcolor='rgba(250, 250, 250, 0.8)')
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                with st.container(border=True):
                    st.metric(label="综合市场情绪指数 (0-100%)", value=f"{sentiment_dict['mean'] * 100:.1f} %")
                    st.info(f"当前主力资金定性: **{sentiment_dict['status']}**")
                with st.container(border=True):
                    st.write("☁️ **近期头条高频词云**")
                    wc_fig = self.analyzer.generate_wordcloud(news_list)
                    if wc_fig: st.pyplot(wc_fig, use_container_width=True)
                with st.expander("查看原始新闻与逐句情感得分", expanded=False):
                    for title, score in zip(sentiment_dict['raw_titles'], sentiment_dict['scores']):
                        color = "🔴" if score > 0.55 else ("🟢" if score < 0.45 else "⚪")
                        st.caption(f"{color} [得分:{score:.2f}] {title}")

        # ================= Tab 2: 量化回测与风险评估 =================
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🧪 多因子共振策略验证 (均线 + MACD动量)")
            st.markdown("**策略逻辑**：引入 MACD 作为动量过滤器。当 `MA5 > MA20` 且 `MACD > 0` 时产生做多信号。")
            
            fetcher = MarketDataFetcher("dummy")
            bt_results = fetcher.run_strategy_backtest(price_df)
            
            if bt_results:
                bt_df = bt_results['data']
                metrics = bt_results['metrics']
                
                # 【修复点1：先创建 container，再创建 columns包裹在内】
                with st.container(border=True):
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("策略累计收益率", f"{metrics['total_return_strat']*100:.2f}%", delta=f"超越基准: {(metrics['total_return_strat'] - metrics['total_return_bench'])*100:.2f}%")
                    m2.metric("最大回撤 (Risk)", f"{metrics['max_drawdown']*100:.2f}%", delta_color="inverse")
                    m3.metric("夏普比率 (Sharpe Ratio)", f"{metrics['sharpe_ratio']:.2f}", help="大于1为优秀")
                    m4.metric("年化波动率 (Volatility)", f"{metrics['annual_volatility']*100:.2f}%")
                
                fig_bt = go.Figure()
                fig_bt.add_trace(go.Scatter(x=bt_df['Date'], y=bt_df['Cum_Strategy'], name='共振策略净值', line=dict(color='#ef5350', width=2.5)))
                fig_bt.add_trace(go.Scatter(x=bt_df['Date'], y=bt_df['Cum_Benchmark'], name='基准净值 (Buy & Hold)', line=dict(color='gray', width=1.5, dash='dash')))
                
                buy_signals = bt_df[(bt_df['Position'] == 1) & (bt_df['Position'].shift(1) == 0)]
                sell_signals = bt_df[(bt_df['Position'] == 0) & (bt_df['Position'].shift(1) == 1)]
                fig_bt.add_trace(go.Scatter(x=buy_signals['Date'], y=buy_signals['Cum_Strategy'], mode='markers', marker=dict(color='#00e676', size=12, symbol='triangle-up', line=dict(width=1, color='black')), name='共振买入'))
                fig_bt.add_trace(go.Scatter(x=sell_signals['Date'], y=sell_signals['Cum_Strategy'], mode='markers', marker=dict(color='#29b6f6', size=12, symbol='triangle-down', line=dict(width=1, color='black')), name='平仓规避'))
                
                fig_bt.update_layout(height=450, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_bt, use_container_width=True)

    def run_pipeline(self):
        st.title("📊 基于大数据的A股量化指标与舆情文本挖掘系统")
        st.markdown("**(包含金融接口、缓存加速、数据可视化与大模型Agent引擎)**")
        st.markdown("---")
        
        if 'stock_code' not in st.session_state:
            st.session_state.stock_code = "688111"
            st.session_state.start_date = "20240101"

        stock_code, start_date, submit_btn = self.render_sidebar(price_df=st.session_state.get('price_df', None))
        
        if submit_btn:
            st.session_state.stock_code = stock_code
            st.session_state.start_date = start_date
            
        with st.spinner("🚀 系统正在调度底层引擎抓取数据与NLP算法分析..."):
            price_df, news_list = fetch_and_process_data(st.session_state.stock_code, st.session_state.start_date)
            st.session_state['price_df'] = price_df 
            sentiment_dict = self.analyzer.batch_sentiment_pipeline(news_list)
            
        self.display_charts(price_df, sentiment_dict, news_list)

if __name__ == "__main__":
    app = FinancialDashboardApp()
    app.run_pipeline()