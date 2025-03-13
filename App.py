import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk
from transformers import pipeline
import re



#python -m streamlit run App.py  
# Download necessary NLTK data
nltk.download('punkt')

# Streamlit configuration
st.set_page_config(page_title='InNews 🇹🇷: A Summarised News📰 Portal', page_icon='./Meta/newspaper.ico')

# Initialize Hugging Face summarization pipeline
summarizer = pipeline("summarization")

# Fetch news based on search topic
def fetch_news_search_topic(topic):
    site = f'https://news.google.com/rss/search?q={topic}'
    op = urlopen(site)  # Open the site
    rd = op.read()  # Read data from site
    op.close()  # Close the object
    sp_page = soup(rd, 'xml')  # Scrape the data
    news_list = sp_page.find_all('item')  # Find news items
    return news_list

# Fetch top news articles
def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)  # Open the site
    rd = op.read()  # Read data from site
    op.close()  # Close the object
    sp_page = soup(rd, 'xml')  # Scrape the data
    news_list = sp_page.find_all('item')  # Find news items
    return news_list

# Fetch news based on category
def fetch_category_news(topic):
    site = f'https://news.google.com/news/rss/headlines/section/topic/{topic}'
    op = urlopen(site)  # Open the site
    rd = op.read()  # Read data from site
    op.close()  # Close the object
    sp_page = soup(rd, 'xml')  # Scrape the data
    news_list = sp_page.find_all('item')  # Find news items
    return news_list

# Fetch news article image
def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, use_container_width=True)
    except:
        image = Image.open('./Meta/no_image.jpg')
        st.image(image, use_container_width=True)

# Display the fetched news
# Display the fetched news with improved image extraction
def display_news(list_of_news, news_quantity):
    c = 0
    for news in list_of_news:
        c += 1
        # st.markdown(f"({c})[ {news.title.text}]({news.link.text})")
        st.write('**({}) {}**'.format(c, news.title.text))
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            st.error(e)
        fetch_news_poster(news_data.top_image)
        with st.expander(news.title.text):
            st.markdown(
                '''<h6 style='text-align: justify;'>{}"</h6>'''.format(news_data.summary),
                unsafe_allow_html=True)
            st.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))
        st.success("Published Date: " + news.pubDate.text)
        if c >= news_quantity:
            break


# Function to preprocess and clean text
def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove unwanted characters like punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text

# Function to summarize input text
def summarize_text(text):
    try:
        # Clean the text
        cleaned_text = clean_text(text)
        summary = summarizer(cleaned_text, max_length=150, min_length=50, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        st.error(f"Error in summarizing: {e}")
        return None

# Main function to run the app
def run():
    st.title("InNews 🇹🇷: A Summarised News📰 ")
    image = Image.open('./Meta/newspaper.png')

    col1, col2, col3 = st.columns([3, 5, 3])

    with col1:
        st.write("")

    with col2:
        st.image(image, use_container_width=False)

    with col3:
        st.write("")

    category = ['--Select--', 'Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic', 'Summarizer']
    cat_op = st.selectbox('Select your Category', category)
    
    if cat_op == category[0]:
        st.warning('Please select Type!!')
    elif cat_op == category[1]:
        st.subheader("✅ Here is the Trending🔥 news for you")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
        news_list = fetch_top_news()
        display_news(news_list, no_of_news)
    elif cat_op == category[2]:
        av_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        st.subheader("Choose your favourite Topic")
        chosen_topic = st.selectbox("Choose your favourite Topic", av_topics)
        if chosen_topic == av_topics[0]:
            st.warning("Please Choose the Topic")
        else:
            no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
            news_list = fetch_category_news(chosen_topic)
            if news_list:
                st.subheader(f"✅ Here are some {chosen_topic} News for you")
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News found for {chosen_topic}")
    elif cat_op == category[3]:
        user_topic = st.text_input("Enter your Topic🔍")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=15, step=1)

        if st.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(topic=user_topic_pr)
            if news_list:
                st.subheader(f"✅ Here are some {user_topic.capitalize()} News for you")
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News found for {user_topic}")
        else:
            st.warning("Please write Topic Name to Search🔍")
    
    elif cat_op == category[4]:  # Summarizer section
        st.subheader("📝 Enter your text below to summarize:")
        text_input = st.text_area("Paste your article/text here", height=300)
        
        if text_input:
            if st.button("Summarize"):
                summary = summarize_text(text_input)
                if summary:
                    st.write("### Summary:")
                    st.write(summary)
                else:
                    st.warning("Could not generate summary. Please try again.")

# Run the app
run()
