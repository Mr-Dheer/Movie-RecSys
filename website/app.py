import pickle
import streamlit as st
import requests
from random import randint
# Pickle Files
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))



# Custom CSS Styling
st.markdown(
    """
    <style>
    .title {
        color: #2e4057;
        text-align: center;
        font-size: 3em;
        padding: 20px;
        margin-bottom: 20px;
        border-bottom: 2px solid #2e4057;
    }
    .sidebar .widget-content {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar .st-eb {
        background-color: #2e4057;
        color: white;
        border-radius: 8px;
    }
    .sidebar .st-eb:hover {
        background-color: #1e2a38;
    }
    .recommendation {
        padding: 20px;
        margin-top: 30px;
        background-color: #f9f9f9;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .movie-name {
        font-size: 1.2em;
        font-weight: bold;
        color: #2e4057;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and Sidebar
st.title('🎬 Movie Recommender System')
st.markdown("---")
st.sidebar.header('Select a Movie')
movie_list = movies['title'].values
selected_movie = st.sidebar.selectbox("Type or select a movie from the dropdown", movie_list)

# Fetch Poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=472483140ad07905a27f7ff2eed59152&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path'] 
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path

# Fetch overView
def fetch_overview(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=472483140ad07905a27f7ff2eed59152&language=en-US"
    data = requests.get(url).json()
    overview_data = data['overview']
    return overview_data

def fetch_popularity(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=472483140ad07905a27f7ff2eed59152&language=en-US"
    data = requests.get(url).json()
    popularity_data = data['popularity']
    return popularity_data


# Fetch Reviews
def fetch_reviews(movie_id):
    api_key = '472483140ad07905a27f7ff2eed59152'
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={api_key}&language=en-US")
    
    data = response.json()
    
    reviews = data.get('results', [])  # This gets the list of reviews
    
    all_reviews_content = ""  
    for review in reviews[:4]:  

        all_reviews_content += f"Author: {review.get('author')}\nContent: {review.get('content')}\n\n"
    return all_reviews_content.strip() 
    
# print(fetch_reviews('49026'))


# Recommendation Logic
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommend_movie_overview = []
    popularity_movie=[]



    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        overview = fetch_overview(movie_id)
        poster = fetch_poster(movie_id) 
        popularity=fetch_popularity(movie_id)
        
        
        recommend_movie_overview.append(overview)
        popularity_movie.append(popularity)
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)

        


    return recommended_movie_names, recommended_movie_posters, recommend_movie_overview, popularity_movie

# Show Recommendation Button
if st.sidebar.button('Show Recommendation'):
    st.markdown("---")
    try:
        recommended_movie_names, recommended_movie_posters, recommend_movie_overviews, popularity_movie = recommend(selected_movie)
        st.markdown("<h2>Recommended Movies</h2>", unsafe_allow_html=True)
        for name, poster, overview, popularity in zip(recommended_movie_names, recommended_movie_posters, recommend_movie_overviews, popularity_movie ):
            col_poster, col = st.columns([2, 3])  # Adjust the column ratios as needed

            with col_poster:
                st.image(poster, use_column_width=True)

            with col:
                st.markdown(f"<h3>{name}</h3>", unsafe_allow_html=True)
                st.write("Overview:")
                st.write(overview)
            
            with col:
                st.write("Rating:")
                st.write(popularity)


    except Exception as e:
        st.error(f"Error: {e}")