from flask import render_template, flash, redirect, request
from app import app
from app.forms import UrlSearchForm

import sys, os
sys.path.append(os.path.abspath('../'))
from utilities.flask_interface import Interface

interface = Interface(abs_path=os.path.abspath('../utilities') + '/')

@app.route('/', methods=['GET', 'POST'])
def search():
    search = UrlSearchForm()
    if request.method == 'POST':
        return find_results(search)
    return render_template('index.html', title='Home', form=search)


@app.route('/results')
def find_results(url):
    url_string = url.data['url']
    # Keep it from checking junk or empty strings, which can occasionally
    # return results for some reason.
    if 'http' in url_string:
        results = interface.flask_packaging(url=url_string, max_number=5)
    else:
        results = {}
    results = [r for r in results if r['comment_count'] > 0]
    return render_template('results.html', results=results, url=url_string)
