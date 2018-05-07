# What is this project?

![example](https://i.imgur.com/ivhpNPF.gif)

This project is a Flask application which takes in the link of a news article, and returns a list of the top 5 postings of it on Reddit, as well as the general political sentiment expressed within the comments of each posting. The hope is that this may lead people to being able to explore the different interpretations of the same story in different online communities, as well as have metrics for the spectrum of political discource within these communities.

# How do I launch it?


#### Requirements
Python3, install contents of requirements.txt. Add Reddit API keys to api_keys.py

Create a virtual environment, within this environment run the following command to install all of the requisite packages (nltk, tensorflow, etc).

  pip3 install -r requirements.txt

#### Flask Launch

Now traverse into the flask directory, and use the following command to point flask to this application.
  export FLASK_APP=launch_point.py
 
Run the webapp with 
  python3 -m flask run

*These instructions have only been tested on a narrow range of hardware. Contact us if they do not work for you.*

# Why did you make this project?

While the web application is relatively interesting in its own right, it mainly acts as a way for us to test in broad strokes the accuracy of our classifier. As this classifier improves, there are multiple interesting applications that can be formed from it, such as

* Currently, due to the recent increase of public awareness of the interations between online political speech and real-world politics, there is a growing interest in the field of Natural Language Processing for assessing the political affiliation of text. However, the current corpora for this task are lacking. One just takes samples of speeches and words used by officials with party affiliations, another uses twitter data in which politically-affiliated hashtags were mentioned, but neither of these matches the way people actually speak due to the verbosity of the former and character-limit-mandated brevity of the latter. Once this classifier is near-perfect at labeling speech in which a political entity is mentioned, we will be able to scan user profiles for all such mentions. If someone's speech which we can label due to a political entity being detected all falls within a certain political classification, we can assume that their other comments in political subreddits in which our model cannot clearly detect a specific entity falls under this same persuasion. We can then export all of their political comments into a more comprehensive corpus. Though this resulting corpus will of course still need to be checked by a person, prelimary results with our current rough classifier lead us to believe that will be a relatively easy process.

* As briefly mentioned earlier, many news sources are only really utilized by a certain political ideology. With very slight additions, this tool can be used to show what kind of political sentiments are most closely associated with what news source. 

# Plans for Upcoming Changes
* The biggest change is that currently we paint political speech with far, far too broad a brush, labeling a statement against a Republican the same as a statement in favor of a Democrat. We are currently looking into a much more nuanced, robust approach, as people of a wide variety of political persuasions criticize certain members of certain parties, and this of course does not dictate the entirety of their political affiliation. 

* Currently, we use the RPI Joint Information Extraction utility for our Named Entity Recognition. Though this system is accurate, the delay inherrent in pushing so much data to an API makes our application far less responsive and attractive, and we will very soon move to a local system for NER. 
