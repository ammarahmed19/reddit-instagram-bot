# reddit-instagram-bot
A bot that takes any subreddit from reddit, scrapes the top posts, and post each to instagram on a time interval.

# Guide

First of all, download the repository and open a command prompt at the path of the repository
Make sure you're using **Python 3**, *atleast version >= 3.72*

## 1. Install the dependencies
`pip install -r requirements.txt`
Depending on your OS, you may have to use `pip3` instead.

## 2. Setup Reddit API
### ⋅⋅1. Login to Reddit
### ⋅⋅2. Access the [Reddit API page](https://www.reddit.com/prefs/apps).
### ⋅⋅3. Create a new app
[![redditapp1.png](https://i.postimg.cc/c4Mb6P7f/redditapp1.png)](https://postimg.cc/dL3BxHx0)

The value of *name*, *description*, *about url* does not matter. The most important actions are to **select _script_ from the group of radio buttons** and **set _redirect url_ as _http://localhost:8080_**

**Finally click _create app_**
### ..4. Copy the *_client id_* and the *_client_secret_*, their locations are shown in the image. Store those values because they'll be inserted in the script's configuration file.
[![redditapp2.png](https://i.postimg.cc/pVqpJLBT/redditapp2.png)](https://postimg.cc/9zwmWVK5)

## 3. Setup Configuration File.
### ⋅⋅1. Run the script (You'll get an error, but 2 new files — *_config.json_* and *_app.log_*— will appear)
You can run the script using `python script.py`. Depending on your OS, you might have to use `python3` instead.
You'll see this when you run the script
```
Log Setted Up
config.json not found, creating new settings file.
config.json successfully created, please edit config.json with correct configuration and run the script again
```
### ⋅⋅2. Open and edit config.json
You should see this
```
{
    "subreddit": "ADD YOUR PREFERRED SUBREDDIT",
    "interval": "ADD YOUR INTERVAL IN MINUTES (PUT NUMBERS ONLY!!! NO DECIMALS OR LETTERS)",
    "reddit_api": "ADD YOUR REDDIT API SECRET",
    "reddit_client_id": "ADD YOUR REDDIT CLIENT ID",
    "reddit_username": "ADD YOUR REDDIT USERNAME HERE",
    "reddit_password": "ADD YOUR REDDIT PASSWORD HERE",
    "instagram_username": "ADD YOUR INSTAGRAM USERNAME HERE",
    "instagram_password": "ADD YOUR INSTAGRAM PASSWORD HERE",
    "instagram_comment": "ADD THE STANDARD COMMENT HERE"
}
```

⋅⋅⋅* *subreddit* is the subreddit you'd like to fetch posts from
⋅⋅⋅* *interval* describes the gap between the functions (in minutes), eg: if the interval is 5 minutes, a new photo will be posted to instagram every 5 minutes
⋅⋅⋅* *reddit_api* is the _client_secret_ I showed you above.
⋅⋅⋅* *reddit_client_id* is _client_id_ I showed you above.
⋅⋅⋅* *reddit_username* is the _username_ of the reddit account you used to create api app above
⋅⋅⋅* *reddit_password* is the _password_ of the reddit account you used to create api app above
⋅⋅⋅* *instagram_username* is the _username_ of the instagram account you want the media posted to
⋅⋅⋅* *instagram_password* is the _password_ of the instagram account you want the media posted to
⋅⋅⋅* *instagram_comment* is the _comment_ that will be commented on on the post right after it's posted. It's generally used for hashtags

**IMPORTANT: PLACE THE DATA BETWEEN THE DOUBLE QUOTES, DO NOT REMOVE THE DOUBLE QUOTES, THE COMMAS OR ANYTHING.**

**save _config.json_ after you're done**

## 4. Run the script.
The script should run fine then. Two new files will show up, `posts.json` and `posted.json`

**IMPORTANT: IF YOU'RE DONE OF THE SUBREDDIT YOU'RE USING AND WANT TO USE A DIFFERENT SUBREDDIT, DELETE `posts.json` and edit `config.json` to change the subreddit, RERUN THE SCRIPT. **
