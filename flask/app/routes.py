from flask import render_template, flash, redirect, request
from app import app
from app.forms import UrlSearchForm

import sys, os
sys.path.append(os.path.abspath('../utilities'))
import reddit_toolkit as rt
from political_tools import Tagger

# Due to the time required to train the tagger, it's better to have one
tagger = Tagger(test=False)

@app.route('/', methods=['GET','POST'])
def search():
    search = UrlSearchForm()
    if request.method == 'POST':
        return find_results(search)
    return render_template('index.html', title='Home', form=search)

@app.route('/results')
def find_results(url):

    url_string = url.data['url']
    results = rt.flask_packaging(url_string, tagger)

    return render_template('results.html', results=results, url=url_string)
