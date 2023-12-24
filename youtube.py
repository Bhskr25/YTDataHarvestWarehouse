_='''==========================================================================================================
================<---{ IMPORT THE REQUIRED PACKAGES }--->======================================================
============================================================================================================'''

from datetime import datetime, timedelta
from googleapiclient.discovery import build
import pymongo
import pymysql
import pandas as pd
import streamlit as st

_='''==========================================================================================================
================<---{ YOUTUBE DATA API-Key CONNECTION }--->====================================================
============================================================================================================'''

def api_connect():
    api_id = "AIzaSyDo2e9YbzLOCWFuwGwe2oCkBfusGt1Aqy8"
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_id)
    return youtube

# Establish Youtube Data API-Key Connection
youtube = api_connect()

_='''==========================================================================================================
================<---{ COLLECT CHANNEL DATA }--->===============================================================
============================================================================================================'''

#<============<---{ COLLECT THE CHANNEL DETAILS }--->========================================================>
def get_channel_data(channel_id):
    """function to collect data using youtube data api-key and create a dictionary "channel_data" using the retrived data"""
    request = youtube.channels().list(part="snippet,contentDetails,statistics",
                                      id=channel_id)
    ch_response = request.execute()
    for ch_i in ch_response['items']:
        channel_data = {'Channel_Name': ch_i['snippet']['title'],
                        'Channel_Id': ch_i['id'],
                        'Subscription_Count': ch_i['statistics']['subscriberCount'],
                        'Channel_Views': ch_i['statistics']['viewCount'],
                        'Channel_Description': ch_i['snippet']['description'],
                        'Total_Videos': ch_i['statistics']['videoCount'],
                        'Playlist_Id': ch_i['contentDetails']['relatedPlaylists']['uploads']}
    return channel_data

#<============<---{ COLLECT THE VIDEO_ID DETAILS }--->========================================================>

def get_video_id(channel_id):
    """function to collect data using youtube data api-key and create a list of "video_id" using the retrived data"""
    video_Id = []
    response = youtube.channels().list(id=channel_id,
                                       part='contentDetails').execute()
    PlayList_Id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    while True:
        response_pl = youtube.playlistItems().list(part='snippet',
                                                   playlistId=PlayList_Id,
                                                   maxResults=15,
                                                   pageToken=next_page_token).execute()
        
        # Get video_id's data   
        for v_i in range(0, len(response_pl['items'])):
            video_Id.append(response_pl['items'][v_i]['snippet']['resourceId']['videoId'])
        # If data present in Next_Page, Get nextPageToken 
        next_page_token = response_pl.get('nextPageToken')

        if next_page_token is None:
            break

    return video_Id

#<============<---{ COLLECT THE VIDEO DETAILS }--->===========================================================>

def get_Videos_data(video_id):
    """function to collect data using youtube data api-key and create a dictionary "video_data" using the retrived data"""
    video_data = []
    for id_video in video_id:
        v_response = youtube.videos().list(part='snippet,contentDetails,statistics',
                                           id=id_video).execute()

        for i_v in v_response['items']:
            video_info = {'Channel_Id': i_v['snippet']['channelId'],
                         'Video_Id': i_v['id'],
                         'Video_Name': i_v['snippet']['title'],
                         'Video_Description': i_v['snippet'].get('description'),
                         'Video_Thumbnail': i_v['snippet']['thumbnails']['default']['url'],
                         'Published_At': i_v['snippet']['publishedAt'],
                         'View_Count': i_v['statistics'].get('viewCount'),
                         'Likes_Count': i_v['statistics'].get('likeCount'),
                         'Tags': i_v['snippet'].get('tags'),
                         'Favorite_Count': i_v['statistics']['favoriteCount'],
                         'Comments_Count': i_v['statistics'].get('commentCount'),
                         'Duration': i_v['contentDetails']['duration'],
                         'Caption_Status': i_v['contentDetails']['caption']}
        video_data.append(video_info)

    return video_data

#<============<---{ COLLECT THE COMMENTS DETAILS }--->========================================================>

def get_comments_data(video_id):
    comments_data = []
    try:
        for id_video in video_id:
            comments_response = youtube.commentThreads().list(part='snippet',
                                                              videoId=id_video,
                                                              maxResults=15).execute()

            for i_c in comments_response['items']:
                data = {'Comment_Id': i_c['id'],
                        'Video_Id': i_c['snippet']['topLevelComment']['snippet']['videoId'],
                        'Comment_Text': i_c['snippet']['topLevelComment']['snippet']['textDisplay'],
                        'Comment_Author': i_c['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        'Comment_PublishedAt': i_c['snippet']['topLevelComment']['snippet']['publishedAt']}
                comments_data.append(data)
    except:
        pass
    return comments_data

_='''==========================================================================================================
================<---{ UPLOAD DATA TO MONGO_DB }--->============================================================
============================================================================================================'''

#<============<---{ CONNECT TO MONGO_DB DATABASE }--->========================================================>

# Create new client and Connect to server
client = pymongo.MongoClient(
    'mongodb+srv://pranay:pranay25@cluster0.x4wd2rx.mongodb.net/?retryWrites=true&w=majority')
db = client['Youtube_Data']             # Create client Database     <-- "Youtube_Data" -->
collection = db['Channel_Details']      # Create Database Collection <-- "Channel_Details" -->

#<=============<---{ UPLOAD DATA IN DATABASE COLLECTION }--->=================================================>

def Channel_Details(channel_id):
    # Collect the Channel data using API, Store in MongoDB Database
    channel_data = get_channel_data(channel_id)
    video_id = get_video_id(channel_id)
    video_data = get_Videos_data(video_id)
    comments_data = get_comments_data(video_id)

    ch_collection = db['Channel_Details']
    ch_collection.insert_one({'Channels_Data': channel_data,
                              'Videos_Data': video_data,
                              'Comments_Data': comments_data})
    return "Data Uploaded Successfully"

_='''==========================================================================================================
================<---{ TRANSFER MONGO_DB DATA INTO SQL DATABASE }--->===========================================
============================================================================================================'''

#<============<---{ CREATE CHANNELS TABLE FOR CHANNEL DATA }--->==============================================>

def channels_table():
    youtube_db = pymysql.connect(host='localhost',
                                 user='root',
                                 password='Pranay@25',
                                 database='youtube_data')
    cursor = youtube_db.cursor()

    drop_query = '''drop table if exists channels'''
    cursor.execute(drop_query)
    youtube_db.commit()

    #<===( SQL Query To Create Channel Table )================================================================>
    try:
        create_query = '''create table if not exists channels(Channel_Name varchar(200),
                                                            Channel_Id varchar(200) primary key,
                                                            Subscription_Count bigint,
                                                            Channel_Views bigint,
                                                            Channel_Description text,
                                                            Total_Videos int,
                                                            Playlist_Id varchar(200)
                                                            )'''
        cursor.execute(create_query)
        youtube_db.commit()
    except Exception as e:
        print(e)

    # <===( Transfer Channels Data From MongoDB To SQL Table )================================================>

    # <--- Get Channel Data From MongoDB --->
    ch_df_list = []
    db = client['Youtube_Data']
    collection = db['Channel_Details']
    for ch_d in collection.find({}, {'_id': 0, "Channels_Data": 1}):
        ch_df_list.append(ch_d['Channels_Data'])

    ch_df = pd.DataFrame(ch_df_list)           # Convert List To Dataframe

    #<--- Inserting Data From Dataframe Into Table --->
    for index, rows in ch_df.iterrows():
        insert_query = '''insert into channels(Channel_Name,
                                               Channel_Id,
                                               Subscription_Count,
                                               Channel_Views,
                                               Channel_Description,
                                               Total_Videos,
                                               Playlist_Id)
                                               values(%s,%s,%s,%s,%s,%s,%s)'''
        values = (rows['Channel_Name'],
                  rows['Channel_Id'],
                  rows['Subscription_Count'],
                  rows['Channel_Views'],
                  rows['Channel_Description'],
                  rows['Total_Videos'],
                  rows['Playlist_Id'])
        try:
            cursor.execute(insert_query, values)
            youtube_db.commit()
        except Exception as e:
            print(e)

#<============<---{ CREATE VIDEOS TABLE FOR VIDEO DATA }--->=================================================>

def videos_table():
    youtube_db = pymysql.connect(host='localhost',
                                 user='root',
                                 password='Pranay@25',
                                 database='youtube_data')
    cursor = youtube_db.cursor()

    drop_query = '''drop table if exists videos'''
    cursor.execute(drop_query)
    youtube_db.commit()

    #<===( SQL Query To Create Videos Table )================================================================>
    try:
        create_query = '''create table if not exists videos(Channel_Id varchar(200),
                                                            Video_Id varchar(200) primary key,
                                                            Video_Name varchar(200),
                                                            Video_Description text,
                                                            Video_Thumbnail varchar(200),
                                                            Published_At timestamp,
                                                            View_Count bigint,
                                                            Likes_Count bigint,
                                                            Tags text ,
                                                            Favorite_Count int,
                                                            Comments_Count int,
                                                            Duration varchar(10),
                                                            Caption_Status varchar(50)
                                                            )'''
        cursor.execute(create_query)
        youtube_db.commit()
    except Exception as e:
        print(e)
    # <===( Transfer Viedos Data From MongoDB To SQL Table )==================================================>

    # <--- Get Videos Data From MongoDB --->
    v_df_list = []
    db = client['Youtube_Data']
    collection = db['Channel_Details']
    for v_d in collection.find({}, {'_id': 0, "Videos_Data": 1}):
        for i in range(len(v_d['Videos_Data'])):
            v_df_list.append((v_d['Videos_Data'][i]))

    v_df = pd.DataFrame(v_df_list)                                    # Convert List to Dataframe

    v_df['Published_At'] = pd.to_datetime(v_df['Published_At'])       # Format Published date

    # Format Duration time in dataframe
    v_df['Duration'] = pd.to_timedelta(v_df['Duration']) 
    v_df['Duration'] = v_df['Duration'].apply(lambda x: str(x).split()[-1])
    v_df['Duration'] = pd.to_datetime(v_df['Duration'], format='%H:%M:%S').dt.time

    #<--- Alter The Duration Column Datatype --->
    alter_query = '''alter table videos modify column Duration time'''
    cursor.execute(alter_query)
    youtube_db.commit()

    #<--- Inserting Data From Dataframe Into Table --->
    for _, rows in v_df.iterrows():

        tags_value = ','.join(rows['Tags']) if rows['Tags'] else None   # Check if Tags column is not empty

        insert_query = '''insert into videos(Channel_Id,
                                            Video_Id,
                                            Video_Name,
                                            Video_Description,
                                            Video_Thumbnail,
                                            Published_At,
                                            View_Count,
                                            Likes_Count,
                                            Tags,
                                            Favorite_Count,
                                            Comments_Count,
                                            Duration,
                                            Caption_Status)
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        values = (rows['Channel_Id'],
                  rows['Video_Id'],
                  rows['Video_Name'],
                  rows['Video_Description'],
                  rows['Video_Thumbnail'],
                  rows['Published_At'],
                  rows['View_Count'],
                  rows['Likes_Count'],
                  tags_value,
                  rows['Favorite_Count'],
                  rows['Comments_Count'],
                  rows['Duration'],
                  rows['Caption_Status']
                  )
        try:
            cursor.execute(insert_query, values)
            youtube_db.commit()
        except Exception as e:
            print(e)

#<============<---{ CREATE COMMENTS TABLE FOR COMMENTS DATA }--->=============================================>

def comments_table():
    youtube_db = pymysql.connect(host='localhost',
                                 user='root',
                                 password='Pranay@25',
                                 database='youtube_data')
    cursor = youtube_db.cursor()

    drop_query = '''drop table if exists comments'''
    cursor.execute(drop_query)
    youtube_db.commit()

    #<===( SQL Query To Create Comments Table )===============================================================>
    try:
        create_query = '''create table if not exists comments(Comment_Id varchar(200) primary key,
                                                            Video_Id varchar(200),
                                                            Comment_Text text,
                                                            Comment_Author varchar(200),
                                                            Comment_PublishedAt timestamp
                                                            )'''
        cursor.execute(create_query)
        youtube_db.commit()
    except Exception as e:
        print(e)
    # <===( Transfer Viedos Data From MongoDB To SQL Table )==================================================>

    # <--- Get Comments Data From MongoDB --->
    cm_df_list = []
    db = client['Youtube_Data']
    collection = db['Channel_Details']
    for cm_d in collection.find({}, {'_id': 0, "Comments_Data": 1}):
        for i in range(len(cm_d['Comments_Data'])):
            cm_df_list.append(cm_d['Comments_Data'][i])

    c_df = pd.DataFrame(cm_df_list)                                          # Convert List to Dataframe

    c_df['Comment_PublishedAt'] = pd.to_datetime(c_df['Comment_PublishedAt']) # Format Published Date

    #<--- Inserting Data From Dataframe Into Table --->
    for index, rows in c_df.iterrows():
        insert_query = '''insert into comments(Comment_Id ,
                                                Video_Id ,
                                                Comment_Text,
                                                Comment_Author ,
                                                Comment_PublishedAt 
                                                )
                                            values(%s,%s,%s,%s,%s)'''
        values = (rows['Comment_Id'],
                  rows['Video_Id'],
                  rows['Comment_Text'],
                  rows['Comment_Author'],
                  rows['Comment_PublishedAt']
                  )
        try:
            cursor.execute(insert_query, values)
            youtube_db.commit()
        except:
            print('Comment values are already inserted')

#<============<---{ CREATE TABLES FOR CHANNEL DATA IN MYSQL DATABASE }--->====================================>
def create_tables():
    channels_table()
    videos_table()
    comments_table()
    return 'Tables Created Successfully'

_='''==========================================================================================================
================<---{ STREAMLIT WEB APPLICATION }--->==========================================================
============================================================================================================'''
def main():
    # <--- Set Page Configuration ------------------------------------------->
    st.set_page_config(page_title="Youtube Data Harvesting and Ware Housing",
                    page_icon='image\youtube_icon.png',
                    layout='wide')

    #=============<---{ Create Streamlit Dataframe }--->=======================================================

    # <--- Streamlit Dataframe For Channel Data --------------------------->
    def Channels_Table():
        ch_df_list = []
        db = client['Youtube_Data']
        collection = db['Channel_Details']
        for ch_d in collection.find({}, {'_id': 0, "Channels_Data": 1}):
            ch_df_list.append(ch_d['Channels_Data'])

        channel_df = st.dataframe(ch_df_list)               # Convert list data into streamlit dataframe
        return channel_df

    # <--- Streramlit Dataframe For Video Data --------------------------->
    def Videos_Table():
        v_df_list = []
        db = client['Youtube_Data']
        collection = db['Channel_Details']
        for v_d in collection.find({}, {'_id': 0, "Videos_Data": 1}):
            for i in range(len(v_d['Videos_Data'])):
                v_df_list.append((v_d['Videos_Data'][i]))

        v_df = pd.DataFrame(v_df_list)                               
        v_df['Published_At'] = pd.to_datetime(v_df['Published_At'])  
        v_df['Duration'] = pd.to_timedelta(v_df['Duration'])
        v_df['Duration'] = v_df['Duration'].apply(lambda x: str(x).split()[-1])
        
        video_df = st.dataframe(v_df)                                # Convert list data into streamlit datframe
        return video_df

    # <--- Streamlit Dataframe For Comments Data --------------------------->

    def Comments_Table():
        cm_df_list = []
        db = client['Youtube_Data']
        collection = db['Channel_Details']
        for cm_d in collection.find({}, {'_id': 0, "Comments_Data": 1}):
            for i in range(len(cm_d['Comments_Data'])):
                cm_df_list.append(cm_d['Comments_Data'][i])

        comment_df = st.dataframe(cm_df_list)                        # Convert list data into streamlit dataframe
        return comment_df

    #=============<---{ STREAMLIT WEB APPLICATION }--->========================================================

    # <--- Create Sidebar -------------------->
    st.sidebar.title("Guvi Capstone Project")

    # <--- Create Main Content Area For Navigation --------------------------------------------------------------->

    page = ["Home", "Queries", "About"]
    tab_1, tab_2, tab_3 = st.tabs(page)      # Display different content based on user's choice

    # <--- TAB_1 - HOME PAGE --------------------------------------------------->
    with tab_1:
        col_1, mid, col_2 = st.columns([0.05, 0.05, 0.9])
        with col_1:
            st.image('image\youtube_icon.png', width=90)
        with col_2:
            st.title("YouTube Data Harvesting and Warehousing")

        # <--- Search Bar ------------------------------------------------>
        channel_id = st.text_input("", placeholder="Enter the Channel ID")

        # <--- Button: To Collect and Store Data ------------------------->
        if st.button("Collect and Store Data"):
            ch_id_list = []
            db = client['Youtube_Data']
            collection = db['Channel_Details']
            for chd in collection.find({}, {"_id": 0, "Channels_Data": 1}):
                ch_id_list.append(chd['Channels_Data']['Channel_Id'])
            if channel_id in ch_id_list:
                st.success("Channel details of the given channel id: \' " +
                        channel_id + "\' already exist")
            else:
                y_data = Channel_Details(channel_id)
                st.success(y_data)
        # <--- Button: To Transfer Data ---------------------------------->
        if st.button("Migrate to SQL"):
            sql_table = create_tables()
            st.success(sql_table)

        #<--- SIDEBAR: Select Box To Choose The Table TO Display ------------------------------------------------->
        display_table = st.sidebar.selectbox(label="Select the table",
                                            label_visibility='hidden',
                                            options=["Channels", "Videos", "Comments"],
                                            placeholder="Select the table to display",
                                            index=None)
        if display_table == "Channels":
            Channels_Table()
        elif display_table == "Videos":
            Videos_Table()
        elif display_table == "Comments":
            Comments_Table()

    with tab_3:
        col_1, mid, col_2 = st.columns([0.08, 0.04, 0.9])
        with col_1:
            st.image('image\youtube_icon.png', width=100)
        with col_2:
            st.title("YouTube Data Harvesting and Warehousing")
            st.subheader("using MongoDB, MySQL and Streamlit")

        # Display project details here

    # <--- TAB_2: Queries ---------------------------------------------------------------------------------------->
    with tab_2:
        query = st.selectbox(label="Select a qurey",
                            label_visibility='hidden',
                            options=["1. What are the names of all the videos and their corresponding chanels?",
                                    "2. Which channels have the most number of videos, and how many videos do they have?",
                                    "3. What are the top 10 most viewed videos and their respective channels?",
                                    "4. How many commments were made on each video, and what are their corresponding video names?",
                                    "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
                                    "6. What is the total number of likes for each video, and what are their corresponding video names?",
                                    "7. What is thw total number of views for each channel, and what are their corresponding channel names?",
                                    "8. What are the names of all the channels that have published videos in the year 2022?",
                                    "9. What is the average duration of all videos in each channel, and what are their coressponding channel names?",
                                    "10. Which videos have the highest number of comments, and what are their corresponding channel names?"],
                            index=None,
                            placeholder="Select any query to view the result")

        youtube_db = pymysql.connect(host='localhost',
                                    user='root',
                                    password='Pranay@25',
                                    database='youtube_data')
        cursor = youtube_db.cursor()
        # <--- Quries To Analyse The Data ------------------------------------------------------------------------>

        # <--- Query_1 ------------------------------------------------------------------------>
        if query == "1. What are the names of all the videos and their corresponding chanels?":
            query_1 = '''select videos.Video_Name, channels.Channel_Name from videos
                        inner join channels
                        on channels.Channel_Id = videos.Channel_Id;'''
            cursor.execute(query_1)
            youtube_db.commit()
            result_1 = cursor.fetchall()
            q_1_df = pd.DataFrame(result_1, columns=["Video Name", "Channel Name"])
            st.write(q_1_df)

        # <--- Query_2 ------------------------------------------------------------------------>
        elif query == "2. Which channels have the most number of videos, and how many videos do they have?":
            query_2 = '''select Channel_Name as ChannelName, Total_Videos from channels order by Total_Videos desc;'''
            cursor.execute(query_2)
            youtube_db.commit()
            result_2 = cursor.fetchall()
            q_2_df = pd.DataFrame(
                result_2, columns=["Channel Name", "Total no.of Videos"])
            st.write(q_2_df)

        # <--- Query_3 ------------------------------------------------------------------------>
        elif query == "3. What are the top 10 most viewed videos and their respective channels?":
            query_3 = '''select videos.Video_Name,videos.View_Count as No_of_Views, channels.Channel_Name from videos
                        right join channels
                        on channels.Channel_Id = videos.Channel_Id
                        order by View_Count desc limit 10 ;'''
            cursor.execute(query_3)
            youtube_db.commit()
            result_3 = cursor.fetchall()
            q_3_df = pd.DataFrame(
                result_3, columns=["Video Name", "No.of Views", "Channel Name"])
            st.write(q_3_df)
        # <--- Query_4 ------------------------------------------------------------------------>
        elif query == "4. How many commments were made on each video, and what are their corresponding video names?":
            query_4 = '''select Video_Name, Comments_Count as No_of_comments from videos;'''
            cursor.execute(query_4)
            youtube_db.commit()
            result_4 = cursor.fetchall()
            q_4_df = pd.DataFrame(
                result_4, columns=["Video Name", "No.of Comments"])
            st.write(q_4_df)
        # <--- Query_5 ------------------------------------------------------------------------>
        elif query == "5. Which videos have the highest number of likes, and what are their corresponding channel names?":
            query_5 = '''select videos.Video_Name, videos.Likes_Count as No_of_Likes, channels.Channel_Name 
                        from videos
                        inner join channels
                        on channels.Channel_Id=videos.Channel_Id
                        order by Likes_Count desc;'''
            cursor.execute(query_5)
            youtube_db.commit()
            result_5 = cursor.fetchall()
            q_5_df = pd.DataFrame(
                result_5, columns=["Video Name", "No.of Likes", "Channel Name"])
            st.write(q_5_df)

        # <--- Query_6 ------------------------------------------------------------------------>
        elif query == "6. What is the total number of likes for each video, and what are their corresponding video names?":
            query_6 = '''select Video_Name, Likes_Count as No_of_Likes from videos order by Likes_Count desc;'''
            cursor.execute(query_6)
            youtube_db.commit()
            result_6 = cursor.fetchall()
            q_6_df = pd.DataFrame(result_6, columns=["Video Name", "No.of Likes"])
            st.write(q_6_df)

        # <--- Query_7 ------------------------------------------------------------------------>
        elif query == "7. What is thw total number of views for each channel, and what are their corresponding channel names?":
            query_7 = '''select Channel_Name, Channel_Views as Total_No_of_Views from channels;'''
            cursor.execute(query_7)
            youtube_db.commit()
            result_7 = cursor.fetchall()
            q_7_df = pd.DataFrame(
                result_7, columns=["Channel Name", "Total No.of channel views"])
            st.write(q_7_df)

        # <--- Query_8 ------------------------------------------------------------------------>
        elif query == "8. What are the names of all the channels that have published videos in the year 2022?":
            query_8 = '''select channels.Channel_Name, videos.Video_Name, videos.Published_At as Published_Year 
                        from channels
                        inner join videos
                        on channels.Channel_Id=videos.Channel_Id
                        where year(Published_At)=2022;'''
            cursor.execute(query_8)
            youtube_db.commit()
            result_8 = cursor.fetchall()
            q_8_df = pd.DataFrame(
                result_8, columns=["Channel Name", "Video Name", "Published Year"])
            st.write(q_8_df)

        # <--- Query_9 ------------------------------------------------------------------------>
        elif query == "9. What is the average duration of all videos in each channel, and what are their coressponding channel names?":
            query_9 = '''select channels.Channel_Name, avg(videos.Duration) as Average_Duration from channels
                        inner join videos
                        on channels.Channel_Id=videos.Channel_Id
                        group by Channel_Name;'''
            cursor.execute(query_9)
            youtube_db.commit()
            result_9 = cursor.fetchall()
            q_9_df = pd.DataFrame(
                result_9, columns=["Channel Name", "Average Duration(in seconds)"])
            st.write(q_9_df)

        # <--- Query_10 ------------------------------------------------------------------------>
        elif query == "10. Which videos have the highest number of comments, and what are their corresponding channel names?":
            query_10 = '''select videos.Video_Name, channels.Channel_Name, Comments_Count as No_of_Comments from videos
                        inner join channels 
                        on channels.Channel_Id=videos.Channel_Id
                        order by Comments_Count desc;'''
            cursor.execute(query_10)
            youtube_db.commit()
            result_10 = cursor.fetchall()
            q_10_df = pd.DataFrame(result_10, columns=["Video Name", "Channel Name", "No.of Comments"])
            st.write(q_10_df)

#<============<---{ CALL MAIN(): STREAMLIT APPLICATION }--->==================================================>
if __name__ == "__main__":
    main()