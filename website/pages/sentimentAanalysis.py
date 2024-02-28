import pickle
import streamlit as st
import requests

# Load Pickle Files
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit App
st.header('Sentiment Analysis on the Reviews of the Movies')

# Assuming 'movies' DataFrame has a 'movie_id' column
movie_list = movies['title'].values
selected_movie = st.selectbox('Type or select a movie from the dropdown', movie_list)

def fetch_reviews(movie_id):
    api_key = '472483140ad07905a27f7ff2eed59152'
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={api_key}&language=en-US")
    
    if response.status_code == 200:
        data = response.json()
        reviews = data.get('results', [])
        
        all_reviews_content = ""  
        for review in reviews[:4]:  # Limit to first 4 reviews
            all_reviews_content += f"**Author:** {review.get('author')}\n**Content:** {review.get('content')}\n\n"
        
        return all_reviews_content.strip()
    else:
        return "Failed to fetch reviews."

if st.button('Show Reviews'):
    # Find the movie ID from the selected movie
    movie_id = movies[movies['title'] == selected_movie]['movie_id'].values[0]
    reviews_content = fetch_reviews(movie_id)
    
    if reviews_content:
        st.markdown(reviews_content)
    else:
        st.error("No reviews found or failed to fetch reviews.")

