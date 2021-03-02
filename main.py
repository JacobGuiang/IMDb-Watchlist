from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import requests

app = Flask(__name__)

output_error = ''

soup = None

search_list = []
seen_movies = []
watchlist_movies = []


@app.route('/', methods=['GET'])
def index():
    global output_error
    global search_list
    global seen_movies
    global watchlist_movies
    
    return render_template(
        'index.html',
        output_error=output_error,
        search_list=search_list,
        seen_movies=seen_movies,
        watchlist_movies=watchlist_movies)


@app.route('/search', methods=['POST'])
def search():
    global output_error
    global soup
    global search_list

    movie_title_search = request.form.get('movie-title-search')

    title_url = quote_plus(movie_title_search)
    imdb_url = f'https://www.imdb.com/search/title/?title={title_url}&title_type=feature'
    imdb_page = requests.get(imdb_url)

    soup = BeautifulSoup(imdb_page.content, 'html.parser')
    search_results = soup.find_all('div', class_='lister-item mode-advanced')
    search_list = []

    if len(search_results) == 0:
        output_error = 'No results found.'
    else:
        output_error = ''
        length = min(10, len(search_results))
        for i in range(length):
            title = search_results[i].h3.a.text
            search_list.append(title)

    return redirect('/')


@app.route('/display', methods=['POST'])
def display():
    global output_error
    global soup
    global seen_movies
    global watchlist_movies

    movie_index = int(request.form.get('selected-movie'))
    movie_status = request.form.get('parameter')

    movie_details = soup.find_all('div', class_='lister-item mode-advanced')[movie_index]
    title = movie_details.h3.a.text

    try:
        rating = movie_details.strong.text
        description = movie_details.find_all('p')[1].text.strip()
    except:
        output_error = 'Problem with retrieving data for the movie.'
        return redirect('/')

    if any(movie['title'] == title for movie in seen_movies) or any(movie['title'] == title for movie in watchlist_movies):
        output_error = 'Movie already exists in data.'
    else:
        output_error = ''
        if movie_status == 'seen':
            seen_movies.append({'title': title, 'rating': rating, 'description': description})
        elif movie_status == 'watchlist':
            watchlist_movies.append({'title': title, 'rating': rating, 'description': description})

    return redirect('/')


app.run(host='0.0.0.0', port=8080)
