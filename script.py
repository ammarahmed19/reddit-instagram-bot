import json
import logging
import requests
import praw
from InstagramAPI import InstagramAPI
import csv
from time import sleep
import os, os.path
import shutil


FB_OAUTH="https://www.facebook.com/v3.3/dialog/oauth"
FB_RDR="https://www.facebook.com/connect/login_success.html"
FB_ST="{st=rtoin,ds=20192019}"
REDDIT_OAUTH="https://www.reddit.com/api/v1/authorize"
LOCAL="http://localhost:8080"
USER_AGENT ="Mozilla/5.0"
TIMEOUT=60
image_exts = ['.jpeg', '.gif', '.png']

logger = None

def is_image(url):
    if any(image_ext in url for image_ext in image_exts):
        return True
    return False


def setupLog():
	global logger
	logger= logging.getLogger()
	logger.setLevel(logging.DEBUG) # or whatever
	handler = logging.FileHandler('app.log', 'w', 'utf-8') # or whatever
	handler.setFormatter(logging.Formatter('%(name)s %(message)s')) # or whatever
	logger.addHandler(handler)

	print ("Log Setted Up")
	logger.info("Log Created")

def examineConfig(data):
	assert data['interval'].strip().isdigit(), "interval must be numbers only, decimals and letters are not accepted"
	assert len(data['subreddit'].strip()) > 0, "subreddit cannot be empty"
	assert len(data['reddit_api'].strip()) > 0, "reddit api secret cannot be empty"
	assert len(data['reddit_client_id'].strip()) > 0, "reddit client id cannot be empty"
	assert len(data['reddit_username'].strip()) > 0, "reddit username cannot be empty"
	assert len(data['reddit_password'].strip()) >= 8, "reddit password cannot be less than 8 characters"
	assert len(data['instagram_username'].strip()) > 0, "instagram username cannot be empty"
	assert len(data['instagram_password'].strip()) >= 8, "instagram_password cannot be less than 8 characters"

def loadConfig():
	try:
		with open(os.path.join(os.getcwd(),'config.json'), 'r') as f:
			data = json.load(f)
			examineConfig(data)
			logger.info("config.json loaded successfully!")

	except FileNotFoundError:
		logger.error("config.json not found, creating new settings file.")
		print("config.json not found, creating new settings file.")

		with open(os.path.join(os.getcwd(),'config.json'), 'w') as f:
			data = {'subreddit':'ADD YOUR PREFERRED SUBREDDIT',
					'interval': 'ADD YOUR INTERVAL IN MINUTES (PUT NUMBERS ONLY!!! NO DECIMALS OR LETTERS)',
					'reddit_api': 'ADD YOUR REDDIT API SECRET',
					'reddit_client_id': 'ADD YOUR REDDIT CLIENT ID',
					'reddit_username': 'ADD YOUR REDDIT USERNAME HERE',
					'reddit_password': 'ADD YOUR REDDIT PASSWORD HERE',
					'instagram_username': 'ADD YOUR INSTAGRAM USERNAME HERE',
					'instagram_password': 'ADD YOUR INSTAGRAM PASSWORD HERE'
					}
			json.dump(data, f, indent=4)

		logger.critical("config.json successfully created, please edit config.json with correct configuration and run the script again")
		print("config.json successfully created, please edit config.json with correct configuration and run the script again")

		exit(1)

	return (data['subreddit'].strip(), int(data['interval'].strip()), 
		data['reddit_api'].strip(), data['reddit_client_id'].strip(), data['reddit_username'].strip(), data['reddit_password'].strip(), 
		data['instagram_username'].strip(), data['instagram_password'].strip())

'''def loginFb(fb_login):
	logger.info("logging to fb, please login")
	#print("a login window will show up, please login to your app")

	response = requests.get(
		FB_OAUTH, 
		params={
			'client_id':fb_login,
			'redirect_url':FB_RDR,
			'state':FB_ST
				}
		)
	logger.debug(f"status code: {response.status_code}\nheaders: {response.headers['content-type']}\nencoding: {response.encoding}")
	with open("fblogin.html", 'w', encoding="utf-8") as f:  # DEBUG
		f.write(response.text)'''

def loginReddit(reddit_api, reddit_client_id, reddit_username, reddit_password):
	logger.info("logging to reddit, please login")
	#print("a login window will show up, please login to your app")

	'''response = requests.get(
		REDDIT_OAUTH,
		params={
			'client_id':reddit_api,
			'response_type':'code',
			'state':FB_ST,
			'redirect_url':LOCAL,
			'duration':'permanent',
			'scope':'read'
		}
		)

	logger.debug(f"status code: {response.status_code}\nheaders: {response.headers['content-type']}\nencoding: {response.encoding}")
	#with open("redditlogin.html", 'w', encoding="utf-8") as f:  # DEBUG
	#	f.write(response.text)'''

	reddit = praw.Reddit(client_id=reddit_client_id,
                     client_secret=reddit_api, password=reddit_password,
                     user_agent=USER_AGENT, username=reddit_username)
	return reddit

def scrapeSubreddit(subreddit):
	logger.info("scraping subreddit")

	try:
		with open(os.path.join(os.getcwd(), 'posts.json'), 'r', encoding='utf-8') as f:
			data = json.load(f)
			posts = data['posts']
	except FileNotFoundError:
		logger.error("posts.json not found, creating new posts.json")
		subposts = subreddit.hot()
		with open(os.path.join(os.getcwd(), 'posts.json'), 'w', encoding='utf-8') as f:
			data = {'posts':[]}
			for i in subposts:
				if i.stickied == False and is_image(i.url) == True:
					data['posts'].append({
						'title':i.title,
						'link':i.url
						})
			json.dump(data, f, indent=4)
		logger.critical("posts.json successfully created")
		print("posts.json successfully created")

		posts = data

	print("data loaded")

	try:
		with open(os.path.join(os.getcwd(), 'posted.json'), 'r', encoding='utf8') as f:
			pass
	except FileNotFoundError:
		with open(os.path.join(os.getcwd(), 'posted.json'), 'w', encoding='utf-8') as f:
			data = {'posted':[]}
			json.dump(data, f, indent=4)

	return posts

def loginInsta(instagram_username, instagram_password):
	insta_api = InstagramAPI(instagram_username, instagram_password)
	if (insta_api.login()):
		print("Logged to Instagram successfully")
	else:
		print("ERROR: Failed to login to Instagram, please make sure you've used the correct username and password and that the connection is not faulty as well.")
		logger.error("ERROR: Failed to login to Instagram, please make sure you've used the correct username and password and that the connection is not faulty as well.")
	return insta_api

def PostPhoto(insta_api, photolink, caption):
	if photolink.endswith('gif') or photolink.endswith('jpeg') or photolink.endswith('png'):
		photo = os.path.join(os.getcwd() ,'photo.'+photolink[-3:])

	else:
		logger.error(f"{photolink[-3:]} is unsupported format, skipping {photolink}")
		print(f"{photolink[-3:]} is unsupported format, skipping {photolink}")
		return 0

	response = requests.get(photolink, stream=True)

	if response.status_code == 200:

		with open(photo, 'wb') as f:
			shutil.copyfileobj(response.raw, f)

		status = insta_api.uploadPhoto(photo, caption=caption)
		print(status)
		print("Photo Posted")
		logger.info("Photo with caption '" + caption + "' posted")

	else:
		print("ERROR: invalid status code for image", photolink)
		logger.error("ERROR: invalid status code for image " + photolink)

def RemovePostFromJson(postlink):
	with open(os.path.join(os.getcwd(), 'posts.json'), 'r+', encoding='utf-8') as f:
		data = json.load(f)
		data['posts'][:] = [d for d in data['posts'] if d.get('link') != postlink]
		f.truncate()
		json.dump(data, f, indent=4)

def AddPostToPosted(postlink):
	with open(os.path.join(os.getcwd(), 'posted.json'), 'r+', encoding='utf-8') as f:
		data = json.load(f)
		data['posted'].append(postlink)
		f.truncate()
		json.dump(data, f, indent=4)

def CheckIfPosted(postlink):
	try:
		with open(os.path.join(os.getcwd(), 'posted.json'), 'r', encoding='utf-8') as f:
			data = json.load(f)
			if postlink in data['posted']:
				return True
			else:
				return False
	except:
		print("error in CheckIfPosted")
		logger.error("error in CheckIfPosted")

def IntervalThread(posts, insta_api, interval):
	print ("INTERVAL STARTED")
	accum = 0

	while accum < len(posts):
		print ("photo", accum)
		print (f"link: {posts[accum]['link']}")
		if not CheckIfPosted(posts[accum]['link']):
			PostPhoto(insta_api, posts[accum]['link'], posts[accum]['title'])
			RemovePostFromJson(posts[accum]['link'])
			AddPostToPosted(posts[accum]['link'])
		else:
			RemovePostFromJson(posts)
		accum += 1
		print("sleeping for", interval, "minutes")
		sleep(interval * 60)

	print("DONE!!! ALL POSTS HAVE BEEN POSTED!!")

def main():
	setupLog()
	subreddit, interval, reddit_api, reddit_client_id, reddit_username, reddit_password, instagram_username, instagram_password = loadConfig()
	print("config loaded")
	#loginFb(fb_login)
	#print("logged to fb")

	reddit = loginReddit(reddit_api, reddit_client_id, reddit_username, reddit_password)
	print("logged to reddit")

	print("scraping subreddit", subreddit)
	posts = scrapeSubreddit(reddit.subreddit(subreddit))

	print("logging to instagram")
	insta_api = loginInsta(instagram_username, instagram_password)

	print("starting interval")
	IntervalThread(posts, insta_api, interval)


if __name__ == "__main__":
	main()