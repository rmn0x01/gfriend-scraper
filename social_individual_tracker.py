import logging
from config import create_api, youtube_api_key
import requests
import datetime
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def scrape_instagram(username):
    ##Gfriend Instagram     [https://stackoverflow.com/a/52225638/12066506]
    print('scraping instagram ' + username)
    url = 'https://www.instagram.com/' + username
    r = requests.get(url).text
    start = '"edge_followed_by":{"count":'
    end = '},"followed_by_viewer"'
    followers= r[r.find(start)+len(start):r.rfind(end)]
    start = '"edge_follow":{"count":'
    end = '},"follows_viewer"'
    instagram_count = followers
    return int(instagram_count)

def update_status(api,text):
    api.update_status(text)
    print('Updated')

def surpass_message(api,hundreds, new_counts, individual_name):
    new_hundreds = []
    for i in new_counts:
        tmp = str(i)
        if(len(tmp) == 6):
            new_hundreds.append(int(tmp[0]))
        elif(len(tmp) == 7):
            new_hundreds.append(int(tmp[:2]))
        else:
            new_hundreds.append(0)
    for i in range(len(individual_name)):
        if(new_hundreds[i] > hundreds[i]):
            if(len(str(new_hundreds[i])) == 1):
                text = "[SURPASSED]\n"+individual_name[i]+' has surpassed '+ str(new_hundreds[i])+'00000 followers on Instagram, congratulations!\n\n@GFRDOfficial #GFRIEND #여자친구'
                api.update_status(text)
            elif(len(new_hundreds[i]) == 2):
                text = "[SURPASSED]\n"+individual_name[i]+' just surpassed '+ str(new_hundreds[i][0])+'.'+str(new_hundreds[i][1])+'Millions Followers on Instagram, congratulations!\n\n@GFRDOfficial #GFRIEND #여자친구'
                api.update_status(text)
            print(individual_name[i]+' new surpass point')

def main():
    individual_name = ['Sowon', 'Yerin', 'Eunha', 'Yuju', 'SinB', 'Umji']
    individual_handle = ['onedayxne','every__nn','rlo.ldl','yuuzth','bscenez','ummmmm_j.i']
    e = open('additional/social_individual_counts','r').read()
    counts = json.loads(e)
    hundreds = []
    for i in counts:
        tmp = str(i)
        if(len(tmp) == 6):
            hundreds.append(int(tmp[0]))
        elif(len(tmp) == 7):
            hundreds.append(int(tmp[:2]))
        else:
            hundreds.append(0)
    new_counts = []
    twitter_api = create_api()
    for i in range(len(individual_name)):
        new_counts.append(scrape_instagram(individual_handle[i]))
        time.sleep(1)
    kst_time = datetime.datetime.now() + datetime.timedelta(hours=2)
    message = "[Gfriend Individual Instagram Updates]\nper "+ kst_time.strftime("%x %X")+" KST\n"
    # for i in range(len(individual_name)):
    #     try:
    #         difference = new_counts[i]-counts[i]
    #     except:
    #         difference = 0
    #     if(difference>=0):
    #         difference = '+' + str(difference)
    #     else:
    #         difference = str(difference)
    #     tmp = individual_name[i] + ': ' + str(new_counts[i]) + ' (' + difference+')'
    #     message+=tmp+'\n'
    
    difference = sum(new_counts) - sum(counts)
    message+='All members combined: ' + str(sum(new_counts)) + ' (+'+ str(difference)+')\n\n'
    message+='@GFRDOfficial #GFRIEND #여자친구'
    update_status(twitter_api,message)
    print("Checking surpass message")
    surpass_message(twitter_api,hundreds, new_counts, individual_name)
    f = open('additional/social_individual_counts','w+')
    f.write(json.dumps(new_counts))
    f.close()

if __name__ == "__main__":
    main()
