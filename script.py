import json
import logging
import requests
import praw
from InstagramAPI import InstagramAPI
import csv
from time import sleep
import os, os.path
import shutil
from PIL import Image


FB_OAUTH="https://www.facebook.com/v3.3/dialog/oauth"
FB_RDR="https://www.facebook.com/connect/login_success.html"
FB_ST="{st=rtoin,ds=20192019}"
REDDIT_OAUTH="https://www.reddit.com/api/v1/authorize"
LOCAL="http://localhost:8080"
USER_AGENT ="Mozilla/5.0"
TIMEOUT=60
image_exts = ['.jpeg', '.png', 'jpg']

logger = None

def is_image(url):
    if any(url.endswith(image_ext) for image_ext in image_exts):
        return True
    return False

def mpath(fpath):
	return os.path.join(os.getcwd(), fpath)

def plog(msg, log):
	print(msg)
	log(msg)


def setupLog():
	global logger
	logger= logging.getLogger()
	logger.setLevel(logging.DEBUG) # or whatever
	handler = logging.FileHandler('app.log', 'w', 'utf-8') # or whatever
	handler.setFormatter(logging.Formatter('%(name)s %(message)s')) # or whatever
	logger.addHandler(handler)

	plog ("Log Setted Up", logger.info)

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
		with open(mpath('config.json'), 'r') as f:
			data = json.load(f)
			examineConfig(data)
			plog("config.json loaded successfully!", logger.info)

	except FileNotFoundError:
		plog("config.json not found, creating new settings file.", logger.error)

		with open(mpath('config.json'), 'w') as f:
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

		plog("config.json successfully created, please edit config.json with correct configuration and run the script again", logger.critical)

		exit(1)

	return (data['subreddit'].strip(), int(data['interval'].strip()), 
		data['reddit_api'].strip(), data['reddit_client_id'].strip(), data['reddit_username'].strip(), data['reddit_password'].strip(), 
		data['instagram_username'].strip(), data['instagram_password'].strip())

'''def loginFb(fb_login):
	logger.info("logging to fb, please login")

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
	plog("logging to reddit, please login", logger.info)
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
	plog("scraping subreddit", logger.info)

	try:
		with open(mpath('posts.json'), 'r', encoding='utf-8') as f:
			data = json.load(f)
			posts = data['posts']
	except FileNotFoundError:
		plog("posts.json not found, creating new posts.json", logger.error)
		subposts = subreddit.hot()
		with open(mpath('posts.json'), 'w', encoding='utf-8') as f:
			data = {'posts':[]}
			for i in subposts:
				if i.stickied == False and is_image(i.url) == True:
					data['posts'].append({
						'title':i.title,
						'link':i.url
						})
			json.dump(data, f, indent=4)
		plog("posts.json successfully created", logger.critical)

		posts = data['posts']

	plog("data loaded", logger.info)

	try:
		with open(mpath('posted.json'), 'r', encoding='utf8') as f:
			pass
	except FileNotFoundError:
		with open(mpath('posted.json'), 'w', encoding='utf-8') as f:
			data = {'posted':[]}
			json.dump(data, f, indent=4)

	return posts

def loginInsta(instagram_username, instagram_password):
	insta_api = InstagramAPI(instagram_username, instagram_password)
	if (insta_api.login()):
		plog("Logged to Instagram successfully", logger.info)
	else:
		plog("ERROR: Failed to login to Instagram, please make sure you've used the correct username and password and that the connection is not faulty as well.", logger.error)
	return insta_api

def downloadPhoto(link, photo):
	response = requests.get(link, stream=True)

	if response.status_code == 200:
		with open(photo, 'wb') as f:
			shutil.copyfileobj(response.raw, f)

		if photo.endswith('jpg'):
			plog ("converting jpg", logger.info)
			im = Image.open(photo)
			rgb_im = im.convert('RGB')
			photo = mpath('photo.jpeg')
			rgb_im.save(photo)

		return photo

	else:
		plog("ERROR: invalid status code for image", photolink, logger.error)
		return None

def PostPhoto(insta_api, photolink, caption):
	if photolink.endswith('gif') or photolink.endswith('jpeg') or photolink.endswith('png') or photolink.endswith('jpg'):
		photo = mpath('photo.'+photolink[-3:])
	else:
		plog(f"{photolink[-3:]} is unsupported format, skipping {photolink}", logger.error)
		return 0

	plog(f"downloading photo from {photolink}", logger.info)

	photo = downloadPhoto(photolink, photo)
	if photo is None:
		return 0

	plog("photo downloaded, posting photo", logger.info)

	status = insta_api.uploadPhoto(photo, caption=caption)
	plog(status, logger.debug)
	plog(f"Photo with caption {caption} posted", logger.info)
	os.remove(photo)



def RemovePostFromJson(postlink):
	with open(mpath('posts.json'), 'r+', encoding='utf-8') as f:
		data = json.load(f)
		data['posts'][:] = [d for d in data['posts'] if d.get('link') != postlink]
		f.seek(0)
		f.truncate()
		json.dump(data, f, indent=4)

def AddPostToPosted(postlink):
	with open(mpath('posted.json'), 'r+', encoding='utf-8') as f:
		data = json.load(f)
		data['posted'].append(postlink)
		f.seek(0)
		f.truncate()
		json.dump(data, f, indent=4)

def CheckIfPosted(postlink):
	try:
		with open(mpath('posted.json'), 'r', encoding='utf-8') as f:
			data = json.load(f)
			if postlink in data['posted']:
				plog("skipping post because it's already posted", logger.error)
				return True
			else:
				plog("proceeding to posting photo", logger.info)
				return False
	except:
		plog("error in CheckIfPosted", logger.error)

def IntervalThread(posts, insta_api, interval):
	plog("INTERVAL STARTED", logger.info)
	accum = 0

	while accum < len(posts):
		plog (f"photo {accum}", logger.info)
		plog (f"link: {posts[accum]['link']}", logger.info)
		if not CheckIfPosted(posts[accum]['link']):
			PostPhoto(insta_api, posts[accum]['link'], posts[accum]['title'])
			RemovePostFromJson(posts[accum]['link'])
			AddPostToPosted(posts[accum]['link'])
		else:
			RemovePostFromJson(posts)
		accum += 1
		plog(f"sleeping for {interval} minutes", logger.info)
		sleep(interval * 60)

	plog("DONE!!! ALL POSTS HAVE BEEN POSTED!!", logger.info)

def main():
	setupLog()
	subreddit, interval, reddit_api, reddit_client_id, reddit_username, reddit_password, instagram_username, instagram_password = loadConfig()
	plog("config loaded", logger.info)
	#loginFb(fb_login)

	reddit = loginReddit(reddit_api, reddit_client_id, reddit_username, reddit_password)
	plog("logged to reddit", logger.info)

	plog("scraping subreddit " + subreddit, logger.info)
	posts = scrapeSubreddit(reddit.subreddit(subreddit))

	plog("logging to instagram", logger.info)
	insta_api = loginInsta(instagram_username, instagram_password)

	plog("starting interval", logger.info)
	IntervalThread(posts, insta_api, interval)


if __name__ == "__main__":
	main()