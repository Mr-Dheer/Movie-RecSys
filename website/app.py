import streamlit as st
import pickle
import pandas as pd


# Load the Pickled Files
movies = pickle.load(open('movies.pkl','rb'))
similarity=pickle.load(open('similarity.pkl','rb'))

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    
    recommeded_movies=[]
    for i in distances[1:6]:
        recommeded_movies.append(movies.iloc[i[0]].title)
    return recommeded_movies




#Title
st.title('Movie Recommender System')

# SearchBox
selected_movie_name=st.selectbox('Konsi Movie dhekao Sir',movies['title'].values)

# Button
if st.button('Reccommed karo na'):
    recommendations=recommend(selected_movie_name)
    for i in recommendations:
        st.write(i)