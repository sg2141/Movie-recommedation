# save this as app.py
from flask import Flask, request, render_template

import pickle
import requests
import pandas as pd
from patsy import dmatrices

movies = pickle.load(open('model/movie_list.pkl','rb'))
similarity = pickle.load(open('model/similarity.pkl','rb'))

def fetch_poster(movie_id):
    url="https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-Us".format(movie_id)
    data= requests.get(url)
    data= data.json()
    poster_path= data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500"+poster_path
    return full_path


def recommend(movie):
    index = movies[movies['title']==movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse = True, key= lambda x:x[1])
    recommend_movie_name=[]
    recommend_movie_poster=[]
    for i in distances[1:6]:
        movie_id= movies.iloc[i[0]].movie_id
        recommend_movie_poster.append(fetch_poster(movie_id))
        recommend_movie_name.append(movies.iloc[i[0]].title)

    return recommend_movie_name, recommend_movie_poster

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/model', methods=['GET','POST'])
def model():
    movie_list = movies['title'].values
    status = False

    if request.method=="POST":
        try:
            if request.form:
                movies_name= request.form['movies']
                recommend_movies_name, recommend_movies_poster = recommend(movies_name)
                status = True
                return render_template("model.html", movies_name = recommend_movies_name, poster = recommend_movies_poster, movie_list = movie_list, status = status)

        except Exception as e:
            error = {'error': e}
            return render_template("model.html",error= error, movie_list = movie_list, status = status)
    else:
        return render_template("model.html", movie_list = movie_list, status = status)


if __name__=='__main__':
    app.debug=True
    app.run()