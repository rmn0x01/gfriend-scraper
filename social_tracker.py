from weibo_scraper import get_weibo_profile
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
from config import create_api, youtube_api_key, twitter_user
import re
import json
import logging
import datetime
import pytz



#Track any follower/subscriber count for GFRIEND

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def scrape_weibo():
    ##Gfriend Weibo [https://pypi.org/project/weibo-scraper/]
    print('scraping weibo')
    weibo_profile = get_weibo_profile(name='GFRIEND_OFFICIAL')
    weibo_count = weibo_profile.followers_count
    return int(weibo_count)

def scrape_facebook():
    ##Gfriend Facebook [https://stackoverflow.com/a/49063101/12066506]
    print('scraping facebook')
    user="gfrdofficial"
    url = 'https://www.facebook.com/'+ user
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'lxml')
    f = soup.find('div', attrs={'class': '_4-u3 _5sqi _5sqk'})
    likes=f.find('span',attrs={'class':'_52id _50f5 _50f7'}) #finding span tag inside class
    facebook_count = likes.text.split(' ')[0]
    facebook_count = int(facebook_count.replace('.',''))
    return int(facebook_count)

def scrape_twitter(api):
    ##Gfriend Twitter [https://stackoverflow.com/a/11835250/12066506]
    print('scraping twitter')
    twitter_count = api.get_user('gfrdofficial').followers_count
    return int(twitter_count)

def scrape_twitter_jp(api):
    ##Gfriend Twitter [https://stackoverflow.com/a/11835250/12066506]
    print('scraping twitter jp')
    twitter_count = api.get_user('GFRDofficialJP').followers_count
    return int(twitter_count)

def scrape_instagram():
    ##Gfriend Instagram     [https://stackoverflow.com/a/52225638/12066506]
    print('scraping instagram')
    username = "gfriendofficial"
    url = 'https://www.instagram.com/' + username
    r = requests.get(url).text
    start = '"edge_followed_by":{"count":'
    end = '},"followed_by_viewer"'
    followers= r[r.find(start)+len(start):r.rfind(end)]
    start = '"edge_follow":{"count":'
    end = '},"follows_viewer"'
    instagram_count = followers
    return int(instagram_count)

def scrape_instagram_jp():
    ##Gfriend Instagram     [https://stackoverflow.com/a/52225638/12066506]
    print('scraping instagram jp')
    username = "gfriend_japan_official"
    url = 'https://www.instagram.com/' + username
    r = requests.get(url).text
    start = '"edge_followed_by":{"count":'
    end = '},"followed_by_viewer"'
    followers= r[r.find(start)+len(start):r.rfind(end)]
    start = '"edge_follow":{"count":'
    end = '},"follows_viewer"'
    instagram_count = followers
    return int(instagram_count)

def scrape_youtube(api_key):
    ##Gfriend Youtube
    print('scraping youtube')
    channel_id = 'UCRDd3x33kfF0IW6g2MRUkRw'
    url = 'https://www.googleapis.com/youtube/v3/channels?part=statistics&id='+channel_id+'&key='+api_key
    r = requests.get(url)
    result = json.loads(r.text)
    youtube_count = result['items'][0]['statistics']['subscriberCount']
    return int(youtube_count)

#Newly implemented, havent added to the main scraper !!!
def scrape_spotify():
    print("Scraping Spotify")
    r = requests.get('https://open.spotify.com/artist/0qlWcS66ohOIi0M8JZwPft')
    text = r.text
    m = re.search('followers":(.+?),"genres', text)
    followers = json.loads(m.group(1))['total']
    m = re.search('Monthly Listeners: (.+?), Where People Listen', text)
    monthly_listeners = int(m.group(1))
    return int(followers),int(monthly_listeners)
    
#Newly implemented, havent added to the main scraper !!!
def scrape_vlive():
    #driver = webdriver.Firefox(executable_path='gecko/geckodriver') << taruh di main 
    driver.get('https://channels.vlive.tv/F73FF/home')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    z = str(soup.find_all('div', class_='cnt_follow ng-star-inserted'))
    m = re.search('class="value">(.+?)</span>\n</div>]',z)
    s = m.group(1)
    s = s.replace(',','')
    d = int(s)
    print("Followers %s" % (d))


def update_status(api,text,latest=False):
    if(not latest):
        kst_time = datetime.datetime.now() + datetime.timedelta(hours=2)
        message = "[Gfriend Social Updates] per "+ kst_time.strftime("%x %X")+" KST\n"
        send = message+text+'@GFRDOfficial #GFRIEND #여자친구'
        api.update_status(send)
    else:
        #print('boink')
        api.update_status(text,latest)
    print('Updated')

def main():
    social_name = ['Twitter', 'Instagram', 'Youtube', 'Facebook', 'Weibo', 'Twitter Japan', 'Instagram Japan','Spotify Followers','Spotify Monthly Listeners']
    e = open('additional/social_media_counts','r').read()
    counts = json.loads(e)
    new_counts = []
    twitter_api = create_api()
    youtube_api = youtube_api_key()
    username = twitter_user()
    new_counts.append(scrape_twitter(twitter_api))
    new_counts.append(scrape_instagram())
    new_counts.append(scrape_youtube(youtube_api))
    new_counts.append(scrape_facebook())
    new_counts.append(scrape_weibo())
    new_counts.append(scrape_twitter_jp(twitter_api))
    new_counts.append(scrape_instagram_jp())
    spotify = scrape_spotify()
    new_counts.append(spotify[0])
    new_counts.append(spotify[1])
    #today = datetime.datetime.now().date()  
    
    
    contents = []
    for i in range(len(social_name)):
        difference = new_counts[i]-counts[i]
        if(difference>=0):
            difference = '+' + str(difference)
        else:
            difference = str(difference)
        tmp = social_name[i] + ': ' + str(new_counts[i]) + ' (' + difference+')'
        contents.append(tmp+'\n')

    latest = False
    for i in range(0,len(new_counts),7):
        print("Tweeting {} out of {}".format(i+1,len(new_counts)))
        update_status(twitter_api,''.join(contents[i:i+7]),latest)
        tweets = twitter_api.user_timeline(username,count=1)
        for tweet in tweets:
            latest = tweet.id

    f = open('additional/social_media_counts','w+')
    f.write(json.dumps(new_counts))
    f.close()

if __name__ == "__main__":
    main()

