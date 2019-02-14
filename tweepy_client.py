from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from watson_developer_cloud import PersonalityInsightsV3
from watson_developer_cloud import WatsonApiException
 
import twitter_credentials

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import json
import csv
import pprint 


# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()    

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=hash_tag_list)


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True
          
    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    #def analyze_sentiment(self, tweet):
        #analysis = TextBlob(self.clean_tweet(tweet))

        #return response_lang

        #if analysis.sentiment.polarity > 0:
         #   return 1
        #elif analysis.sentiment.polarity == 0:
         #   return 0
        #else:
         #   return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[self.clean_tweet(tweet.text) for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df

    #def combine_tweets(self, tweets) :
     #   df = pd.DataFrame(data += [tweet.text for tweet in tweets]+ ' ', columns = 'alltweets')
      #  return df
 
if __name__ == '__main__':

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name= "realDonaldTrump", count=1200)
    
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    
    #all the tweets from a user and its details 
    with open (r'User_TimelineTweets.csv', 'a') as file:
        df.to_csv(file, sep='\t', encoding='utf-8')

    #print (df)
    #combine text of all the tweets 
    text_combined = ' '
    for tweet in tweets :
        if not 'RT' in tweet.text:
            text_combined += tweet_analyzer.clean_tweet(tweet.text) + ' ' 

    with open ('CombinedText.txt', 'a') as f:
        f.write(text_combined)
    #print(type(text_combined))

    personality_insights = PersonalityInsightsV3(
        version = '2019=01-15',
        iam_apikey = "fzdHkIS7UmVGDwkMIqAxebs6W0sw9hk5oSMwTV5SxnwQ",
        url= "https://gateway-fra.watsonplatform.net/personality-insights/api"
        )

    try:

        with open('CombinedText.txt', 'r') as r:

            profile = personality_insights.profile(
                r.read(),
                content_type = 'text/plain',
                consumption_preferences = True,
                raw_scores= True
                ).get_result()
            with open('PersonalityResults.json', 'a') as file:
                file.write(json.dumps(profile, indent= 5))

    except WatsonApiException as ex :
        print ("Method failed with status code " + str(ex.code) + ":" + ex.message)








