import requests
import json
import tweepy
import logging
import datetime
from config import create_api, youtube_api_key, twitter_user
from math import floor
import os
import random
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def update_status(api,text,latest,member):
    image_list = os.listdir('pics/'+member.lower()+'/')
    if(len(str(latest))==0):
        image_name = random.choice(image_list)
        api.update_with_media('pics/'+member.lower()+'/'+image_name,text)
    else:
        api.update_status(text,latest)
    print('updated')

def scrape_youtube(latest_views, title_video_id, title_list, api_key):
    print("Scraping Youtube Views...")
    part = [ 'snippet','contentDetails','statistics']
    id_str = ','.join(title_video_id)
    part_str = ','.join(part)
    url = 'https://www.googleapis.com/youtube/v3/videos?part='+part_str+'&id='+id_str+'&key='+api_key

    r = requests.get(url)
    result = json.loads(r.text)
    count=0
    outtext = []
    views_in_millions = []
    latest_views_updated = []
    for i in result['items']:
        difference = int(i['statistics']['viewCount']) - latest_views[count]
        tmp = title_list[count] + '\n' + str(i['statistics']['viewCount'])+' (+' + str(difference) +')'
        latest_views_updated.append(int(i['statistics']['viewCount']))
        per_million = int(i['statistics']['viewCount'])/1000000
        diff_truncated = math.floor(per_million*10**1)/10**1
        views_in_millions.append(diff_truncated)
        count+=1
        outtext.append(tmp)
    print("Done scraping, sending data to Twitter API")
    return outtext, latest_views_updated, views_in_millions

def surpass_message(api,title_list,views_in_millions,views_in_millions_updated,member):
    image_list = os.listdir('pics/'+member.lower()+'/')
    image_name = random.choice(image_list)
    for i in range(len(views_in_millions)):
        if(views_in_millions_updated[i]>views_in_millions[i]):
            message = ('[SURPASSED]\n'+title_list[i]+ ' has surpassed '+ str(views_in_millions_updated[i])+'M Views\n'+member.capitalize()+ '! @GFRDOfficial #GFRIEND')
            print('Tweeting achievement message for '+ title_list[i])
            api.update_with_media('pics/'+member.lower()+'/'+image_name,message)

def run_scraper(twt_api,yt_api,kst_time,member,username):
    #Start thread's head
    print("Starting views scraper for "+ member.capitalize() +' ...')
    update_status(twt_api,'[Individual Update MV Views] -- '+member.capitalize() +'\nper '+ kst_time.strftime('%x %X')+' KST'+'\n@GFRDOfficial #GFRIEND #여자친구','',member)
    #Grab latest tweet's ID to reply (threaded tweets)
    tweets = twt_api.user_timeline('GFRDTracker',count=1)
    for tweet in tweets:
        latest = tweet.id
    #Load member's video ID and Title
    c = open('additional/data/'+member+'_video_id','r').read()
    title_video_id = json.loads(c)
    d = open('additional/data/'+member+'_video_title','r').read()
    title_list = json.loads(d)
    #Load latest views data (raw and millions)
    e = open('additional/data/'+member+'_views_in_millions','r').read()
    views_in_millions = json.loads(e)
    f = open('additional/data/'+member+'_latest_views','r').read()
    latest_views = json.loads(f)
    #Start scraping
    outtext, latest_views_updated, views_in_millions_updated = scrape_youtube(latest_views, title_video_id, title_list, yt_api)
    #Saving updated latest views(in raw and millions)
    g = open('additional/data/'+member+'_latest_views','w')
    g.write(json.dumps(latest_views_updated))
    g.close()
    h = open('additional/data/'+member+'_views_in_millions','w')
    h.write(json.dumps(views_in_millions_updated))
    h.close()

    ##Post tweets about updated MV Views
    for i in range(0,len(outtext),6):
        print("Tweeting {} out of {}".format(i+1,len(outtext)))
        update_status(twt_api,'\n'.join(outtext[i:i+6]),latest,'')
        tweets = twt_api.user_timeline(username,count=1)
        for tweet in tweets:
            latest = tweet.id

    ##Running Surpassing Message Congratulation Function
    print("Checking any achievements surpassed")
    surpass_message(twt_api,title_list,views_in_millions,views_in_millions_updated,member)


def main():
    #Set Twitter API
    api = create_api()
    username = twitter_user()
    #Set time to KST
    kst_time = datetime.datetime.now() + datetime.timedelta(hours=2)
    #Set Youtube API
    yt_api = youtube_api_key()
    run_scraper(api,yt_api,kst_time,'yerin',username)
    run_scraper(api,yt_api,kst_time,'eunha',username)
    run_scraper(api,yt_api,kst_time,'yuju',username)
    run_scraper(api,yt_api,kst_time,'sinb',username)
    run_scraper(api,yt_api,kst_time,'umji',username)


if __name__ == "__main__":
    main()


