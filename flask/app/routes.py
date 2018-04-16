from flask import render_template, flash, redirect, request
from app import app
from app.forms import UrlSearchForm

@app.route('/', methods=['GET','POST'])
def search():
    search = UrlSearchForm()
    if request.method == 'POST':
        return find_results(search)
    return render_template('index.html', title='Home', form=search)

@app.route('/results')
def find_results(url):
    results = []
    url_string = url.data['url']

    # Todo: Call functions which return list of results.

    return render_template('results.html', results=results, url=url_string)
