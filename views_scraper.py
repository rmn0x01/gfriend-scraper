import requests
import json
import tweepy
import logging
import datetime
from config import create_api, youtube_api_key, twitter_user
from math import floor
import os
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def update_status(api,text,latest,image):
    image_list = os.listdir('pics/header/')
    if(len(str(latest))==0):
        if(image=='random'):
            image_name = random.choice(image_list)
            api.update_with_media('pics/header/'+image_name,text)
        else:
            api.update_status(text)
    else:
        api.update_status(text,latest)
    print('updated')

def scrape_youtube(latest_views,api_key):
    print("Scraping Youtube Views...")
    title_video_id = ['GU7icQFVzHo', 'vKMeRMAVaDw', 'YYHyAIFG3iI', 'bjRMhQpOYAM', '0VKcLPdY9lI', 'r_6q_-d-7Sk', 'Se8bbsUFjC8', '1ZhDsPdvl6c', 'i1n_1jrUEjU', 'hRPrpLSo4To', 'lnXXfYA91Y8', 'wctRcg67E_g', 'ZsYwEV_ge4Y', 'k7npTim4Xj4','_XyBa8QsVQU','Oyf5o1zWMd0','9iPLjmz3_U4','M9P90QTo_uE','iciFwCnsyY4', 'TbPHPX3hSPA', 'Zll7O1v63aY', 'VMiYLPP4QCg', 'mc274HUFhQQ','YTWwz6R6jy0','gMHP8ZXvuMM','kx5TWKPE5sU','XQSse3b2ge4','LmBYPXGqtss']
    title_list = ['Glass Bead','Glass Bead','Me Gustas Tu','Me Gustas Tu','Rough','Rough','Navillera','Navillera','Fingertip','Fingertip','Love Whisper','Love Whisper','Summer Rain','Summer Rain','TFTMN','TFTMN','Sunny Summer','Sunny Summer','Sunrise','Sunrise','Fever','Fever','Fallin Light','Memoria','Flower','Crossroads', 'Apple','Mago']
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
        if(i['snippet']['channelId'] == 'UCweOkPb1wVVH0Q0Tlj4a5Pw'):
            uploader = '1theK'
        elif(i['snippet']['channelId'] == 'UCRDd3x33kfF0IW6g2MRUkRw'):
            uploader = 'GFRIEND OFFICIAL'
        elif(i['snippet']['channelId'] == 'UC3IZKseVpdzPSBaWxBxundA'):
            uploader = 'BH Labels'
        elif(i['snippet']['channelId'] == 'UC6KEU5-KSTszEOOnAl8ZwPQ'):
            uploader = 'King Records'
        else:
            uploader = i['snippet']['channelId']
        difference = int(i['statistics']['viewCount']) - latest_views[count]
        tmp = title_list[count] + ' [' + uploader +']\n' + str(i['statistics']['viewCount'])+' (+' + str(difference) +')'
        latest_views_updated.append(int(i['statistics']['viewCount']))
        views_in_millions.append(floor(int(i['statistics']['viewCount'])/1000000))
        count+=1
        outtext.append(tmp)
    print("Done scraping, sending data to Twitter API")
    return outtext, latest_views_updated, views_in_millions

def surpass_message(api,views_in_millions,views_in_millions_updated):
    title_list = ['Glass Bead [1theK]','Glass Bead','Me Gustas Tu','Me Gustas Tu [1theK]','Rough [1theK]','Rough','Navillera [1theK]','Navillera','Fingertip [1theK]','Fingertip','Love Whisper [1theK]','Love Whisper','Summer Rain [1theK]','Summer Rain','Time For The Moon Night [1theK]','Time For The Moon Night','Sunny Summer [1theK]','Sunny Summer','Sunrise [1theK]','Sunrise','Fever [1theK]','Fever','Fallin Light','Memoria','Flower','Crossroads','Apple','Mago']
    filename = ['glass_bead.jpeg','glass_bead.jpeg','me_gustas_tu.jpeg','me_gustas_tu.jpeg','rough.jpg','rough.jpg','navillera.jpg','navillera.jpg','fingertip.jpg','fingertip.jpg','love_whisper.jpg','love_whisper.jpg','summer_rain.jpg','summer_rain.jpg','tftmn.jpg','tftmn.jpg','sunny_summer.jpg','sunny_summer.jpg','sunrise.jpg','sunrise.jpg','fever.jpg','fever.jpg','fallin_light.jpg','memoria.jpg','flower.jpg','crossroads.jpg','apple.jpg','mago.jpg']
    for i in range(len(views_in_millions)):
        if(views_in_millions_updated[i]>views_in_millions[i]):
            message = ('[ACHIEVEMENT]\n'+title_list[i]+ ' has surpassed '+ str(views_in_millions_updated[i])+'M Views\nCongratulations! @GFRDOfficial #GFRIEND')
            print('Tweeting achievement message for '+ title_list[i])
            api.update_with_media('pics/'+filename[i],message)
            print("Updated")



def main():
    api = create_api()
    username = twitter_user()
    #Updating MV Views
    ##Get today's date
    #today = datetime.now().date()
    kst_time = datetime.datetime.now() + datetime.timedelta(hours=2)
    ##Tweet starter thread
    print("Creating thread's head...")
    update_status(api,'[Update MV Views]\nper '+ kst_time.strftime('%x %X')+' KST'+'\n@GFRDOfficial #GFRIEND #여자친구','',image='random')
    
    ##Get head tweet to create a thread
    tweets = api.user_timeline('GFRDTracker',count=1)
    for tweet in tweets:
        latest = tweet.id
    
    ##Opening latest views data (in raw and in millions)
    e = open('additional/views_in_millions','r').read()
    views_in_millions = json.loads(e)
    f = open('additional/latest_views','r').read()
    latest_views = json.loads(f)
    ##Running Scraper Function
    api_key = youtube_api_key()
    outtext, latest_views_updated, views_in_millions_updated = scrape_youtube(latest_views,api_key)

    #Saving updated latest views(in raw and millions)
    g = open('additional/latest_views','w')
    g.write(json.dumps(latest_views_updated))
    g.close()
    h = open('additional/views_in_millions','w')
    h.write(json.dumps(views_in_millions_updated))
    h.close()

    ##Post tweets about updated MV Views
    for i in range(0,len(outtext),6):
        print("Tweeting {} out of 26".format(i+1))
        update_status(api,'\n'.join(outtext[i:i+6]),latest,'')
        tweets = api.user_timeline(username,count=1)
        for tweet in tweets:
            latest = tweet.id

    ##Running Surpassing Message Congratulation Function
    print("Checking any achievements surpassed")
    surpass_message(api,views_in_millions,views_in_millions_updated)

if __name__ == "__main__":
    main()



