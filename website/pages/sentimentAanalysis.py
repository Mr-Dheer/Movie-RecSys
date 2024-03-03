import pickle
import re
from bs4 import BeautifulSoup
import streamlit as st
import requests
from transformers import pipeline
import pandas as pd
import torch as pt

# Load Pickle Files
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit App
st.header('Sentiment Analysis on the Reviews of the Movies')

# Assuming 'movies' DataFrame has a 'movie_id' column
movie_list = movies['title'].values
selected_movie = st.selectbox('Type or select a movie from the dropdown', movie_list)

# Initialize BERT sentiment analysis pipeline
sentiment_pipeline = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")



# Function to clean the DataFrame and convert it to a list
def clean_dataframe_and_convert_to_list(df):
    def strip_html(text):
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()

    def remove_between_square_brackets(text):
        return re.sub(r'\[[^]]*\]', '', text)

    def denoise_text(text):
        text = strip_html(text)
        text = remove_between_square_brackets(text)
        return text

    def remove_special_characters(text, remove_digits=True):
        pattern = r'[^a-zA-Z0-9\s]' if not remove_digits else r'[^a-zA-Z\s]'
        text = re.sub(pattern, '', text)
        return text
    
    # Apply the cleaning functions
    df['Content'] = df['Content'].apply(lambda x: x.lower())
    df['Content'] = df['Content'].apply(denoise_text)
    df['Content'] = df['Content'].apply(remove_special_characters)
    df['Content'] = df['Content'].apply(lambda x: x + "\n")  # Append newline character
    
    # Convert the DataFrame into a list of dictionaries
    result_list = df.to_dict('records')
    
    return result_list

# Function to fetch reviews and return cleaned data as a list of dictionaries
def fetch_reviews(movie_id):
    api_key = '472483140ad07905a27f7ff2eed59152'
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={api_key}&language=en-US")
    
    if response.status_code == 200:
        data = response.json()
        reviews = data.get('results', [])
        
        reviews_data = []
        for review in reviews[:4]:  # Limit to first 4 reviews
            review_dict = {
                "Author": review.get('author'),
                "Content": review.get('content')
            }
            reviews_data.append(review_dict)
        
        # Convert list of dictionaries to DataFrame
        df_reviews = pd.DataFrame(reviews_data)
        
        # Clean the DataFrame and convert it back to a list of dictionaries
        cleaned_reviews_list = clean_dataframe_and_convert_to_list(df_reviews)
        
        return cleaned_reviews_list
    else:
        return []

# Function to print reviews with visible separation
def print_reviews(cleaned_reviews_list):
    for review in cleaned_reviews_list:
        print(f"Author: {review['Author']}")
        print(f"Content: {review['Content']}")
        print(review['Content'])  # This will respect the newline character
        print("------")  

if st.button('Show Reviews'):
    # Find the movie ID from the selected movie
    movie_id = movies[movies['title'] == selected_movie]['movie_id'].values[0]
    reviews_content = fetch_reviews(movie_id)
    
    if reviews_content:
        # Format and display each review properly with sentiment
        for review in reviews_content:
            # Format review for markdown display
            author = review['Author']
            content = review['Content'].replace('\n', '  \n')  # Markdown line break
            
            # Perform sentiment analysis
            sentiment_result = sentiment_pipeline(content[:512])  # BERT models typically have a max length of 512 tokens
            sentiment_score = int(sentiment_result[0]['label'].split()[0])  # Extracting the first number from the label
            confidence = sentiment_result[0]['score']
            
            # Determine sentiment color
            if sentiment_score > 3:
                color = "green"
                sentiment_message = "Positive"
            elif sentiment_score == 3:
                color = "orange"
                sentiment_message = "Neutral"
            else:
                color = "red"
                sentiment_message = "Negative"
            
            # Wrap the entire review in a colored div, with the sentiment message styled separately
            review_html = f'''
                <div style="color: {color};">
                     <strong style="color: white;">Author:</strong> <span style="color: white;">{author}</span><br>
                    <strong>Content:</strong> {content}<br>
                    <div style="color: white; font-weight: bold; font-size: 20px;">
                        <strong>Sentiment:</strong> {sentiment_message} (Confidence: {confidence:.2f})
                    </div>
                </div>
                <hr>
            '''
            
            st.markdown(review_html, unsafe_allow_html=True)
    else:
        st.error("No reviews found or failed to fetch reviews.")
