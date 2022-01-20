from youtube_transcript_api import YouTubeTranscriptApi
from datetime import timedelta
import subprocess 
from requests_html import HTMLSession
session = HTMLSession()


def generate_end_time(start_time, duration):
    return start_time + duration

def generate_timestamp_yt_url(video_id, timestamp):
    return f'https://www.youtube.com/watch?v={video_id}&t={timestamp}s'


def convert_transcript_to_obsidian_format(video_id, transcript):
    obsidian_formatted_str = ''
    for i in range(0, len(transcript)):
        start_time = transcript[i]['start']
        duration = transcript[i]['duration']
        end_time = generate_end_time(transcript[i]['start'], duration)
        start_time_url = generate_timestamp_yt_url(video_id, start_time)
        end_time_url = generate_timestamp_yt_url(video_id, end_time)
        # print(f'[{"{:0>8}".format(str(timedelta(seconds=round(start_time))))}]({start_time_url}) -> [{"{:0>8}".format(str(timedelta(seconds=round(end_time))))}]({end_time_url}) : {transcript[i]["text"]}')
        obsidian_formatted_str += f'[{"{:0>8}".format(str(timedelta(seconds=round(start_time))))}]({start_time_url}) -> [{"{:0>8}".format(str(timedelta(seconds=round(end_time))))}]({end_time_url}) : {transcript[i]["text"]}\n'

    return obsidian_formatted_str

def extract_id_channel_and_title_from_yt5_url(url):
    channel = url.split('&')[1].split('=')[1]
    v_id = url.split('=')[1].split('&')[0]

    res = session.get(url)
    title = res.html.xpath('.//title')[0].text

    return v_id, title, channel

def generate_metadata(url, channel, title):
    '''
    ## Metadata
    - Author: (yt_channel)
    - Full Title: (yt_title)
    - Category: #youtube_transcript
    - URL: (yt url -- iframeable)
    '''

    channel_tag = '#' + channel

    return f'# {title} \n## Metadata\n- Author: {channel_tag}\n- [{title}]({url})\n- Category: #youtube_transcript\n'

yt_url = input('Enter the youtube url: ')

print('Extracting video information...')
v_id, title, channel = extract_id_channel_and_title_from_yt5_url(yt_url)
print('Generating metadata for Obsidian...')
metadata = generate_metadata(yt_url, channel, title)
print('Generating transcript...')
transcript = YouTubeTranscriptApi.get_transcript(v_id)
print('Converting transcript to obsidian format...')
transcript = convert_transcript_to_obsidian_format(v_id, transcript)

print('Copying to clipboard...')
subprocess.run("pbcopy", universal_newlines=True, input=metadata + '\n\n\n' + transcript)
print('Done copying to clipboard!')
