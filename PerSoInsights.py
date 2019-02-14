from watson_developer_cloud import PersonalityInsightsV3
import json
import PerSoCred
from watson_developer_cloud import WatsonApiException
import csv

#### Authentication ###### 
def authendicate():
    auth = PersonalityInsightsV3(
	   version = '2018-12-13' ,
	   iam_apikey = PerSoCred.API_KEY ,
	   url = PerSoCred.URL
    )
    return auth

personality_insights = authendicate()

file_list = ['Law.txt']

try: 

    for file in file_list:
        with open(file) as profile_text:
            profile = personality_insights.profile(
                profile_text.read(),
                content_type='text/plain',
                accept= 'text/csv',
                consumption_preferences=True,
                raw_scores=True,
                csv_headers=True
            ).get_result()
        #print(profile)
        write_csv = "Lawresults.csv"
        with open(write_csv, 'a') as personality_file:
            writer = csv.writer(personality_file)
            reader = csv.reader(profile.text.splitlines())
            for row in reader:
                writer.writerow(row)
            #("Personality insights of results of :", file)

except WatsonApiException as ex :
    print ("Method failed with status code " + str(ex.code) + ":" + ex.message)

