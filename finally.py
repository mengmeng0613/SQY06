import jieba
import requests
import streamlit as st
from streamlit_echarts import st_echarts
from collections import Counter
from bs4 import BeautifulSoup
import re
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


# 读取停用词文件
def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().splitlines())
    return stopwords


# 清理文本函数
def preprocess_text(text):
    text = re.sub(r'\s+', '', text)  # 去除空白字符
    text = re.sub(r'[\n\r]', '', text)  # 去除换行符
    return text.strip()


# 分词函数
def word_segmentation(text, stopwords):
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    words = jieba.lcut(text)
    return [word for word in words if word not in stopwords]


# 移除标点和数字
def remove_noise(text):
    text = re.sub(r'[' + string.punctuation + ']+', '', text)
    return re.sub(r'\d+', '', text)


# 提取正文文本
def extract_main_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


# 生成词云图
def generate_wordcloud(word_counts):
    if word_counts:
        # 使用绝对路径指定字体文件
        font_path = r'D:\daima\Scripts\simhei.ttf'

        # 调试信息：打印字体路径
        st.write(f"字体文件路径：{font_path}")

        if not os.path.exists(font_path):
            st.error(f"字体文件未找到：{font_path}")
            return

        try:
            wordcloud = WordCloud(font_path=font_path, width=800, height=400,
                                  background_color='white').generate_from_frequencies(word_counts)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)
        except Exception as e:
            st.error(f"生成词云图时出现错误: {e}")
    else:
        st.write("没有足够的词语生成词云图。")


# 运行主程序
def main():
    st.set_page_config(
        page_title="文本处理示例",
        page_icon="📝",
    )

    st.title("欢迎使用 Streamlit 文本处理示例 📝")

    url = st.text_input('请输入 URL:')

    if url:
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'
            html_content = response.text

            st.write("网页内容获取成功")

            text = extract_main_text(html_content)
            st.write("提取的正文文本：", text[:500])  # 仅展示前500字符

            text = remove_noise(text)
            st.write("去除噪音后的文本：", text[:500])

            text = preprocess_text(text)
            st.write("预处理后的文本：", text[:500])

            # 加载停用词
            stopwords = load_stopwords(r'D:\daima\Scripts\stopwords.txt')
            words = word_segmentation(text, stopwords)
            st.write("分词结果：", words[:50])  # 仅展示前50个词

            word_count = Counter(words)
            most_common_words = word_count.most_common(20)

            st.write("词频统计结果：", most_common_words)

            if most_common_words:
                chart_options = {
                    "tooltip": {"trigger": 'item', "formatter": '{b} : {c}'},
                    "xAxis": [{
                        "type": "category",
                        "data": [word for word, count in most_common_words],
                        "axisLabel": {"interval": 0, "rotate": 45}
                    }],
                    "yAxis": [{"type": "value"}],
                    "series": [{
                        "type": "bar",
                        "data": [count for word, count in most_common_words]
                    }]
                }

                st_echarts(chart_options, height='500px')

                # 生成词云图
                st.write("词云图：")
                generate_wordcloud(dict(most_common_words))
            else:
                st.write("没有足够的词语生成可视化图表。")

        except Exception as e:
            st.error(f"出现错误: {e}")


if __name__ == "__main__":
    main()
