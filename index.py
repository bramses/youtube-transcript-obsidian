from youtube_transcript_api import YouTubeTranscriptApi
from datetime import timedelta
import subprocess
import sys
from requests_html import HTMLSession
session = HTMLSession()

data = sys.argv[1]

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
        obsidian_formatted_str += f'[{"{:0>8}".format(str(timedelta(seconds=round(start_time))))}]({start_time_url}) -> {"{:0>8}".format(str(timedelta(seconds=round(end_time))))} : {transcript[i]["text"]}\n'

    return obsidian_formatted_str

def extract_id_channel_and_title_from_yt5_url(url):
    res = session.get(url)
    if len(url.split('&')) > 1: # regular url
        channel = url.split('&')[1].split('=')[1]
        v_id = url.split('=')[1].split('&')[0]
    else:
        if len(url.split('=')) > 1: # yt url no ab channel
            v_id = url.split('=')[1]
            channel_html = res.html.find('body')
            if "channelId" in channel_html[0].text:
                channel = channel_html[0].text.split('channelId')[1].strip().split('author')[1].strip().split(':')[1].strip().split(',')[0].strip().replace('"', '')
        else: # yt share shortlink
            v_id = url.split('be/')[1]
            channel_html = res.html.find('body')
            if "channelId" in channel_html[0].text:
                channel = channel_html[0].text.split('channelId')[1].strip().split('author')[1].strip().split(':')[1].strip().split(',')[0].strip().replace('"', '')
    
    title = res.html.xpath('.//title')[0].text
    channel = channel.replace(' ', '_')

    return v_id, title, channel

def generate_metadata(url, channel, title, video_id):
    '''
    ## Metadata
    - Author: (yt_channel)
    - Full Title: (yt_title)
    - Category: #youtube_transcript
    - URL: (yt url -- iframeable)

    <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    '''

    channel_tag = '#' + channel

    return f'# {title} \n## Metadata\n- Author: {channel_tag}\n- Title: [{title}]({url})\n- Category: #youtube_transcript\n<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

if data:
    yt_url = data
else:
    yt_url = input('Enter the youtube url: ')
    if len(yt_url) == 0 or len(yt_url) > 150:
        raise Exception('Please enter a valid youtube url')


print('Extracting video information...')
v_id, title, channel = extract_id_channel_and_title_from_yt5_url(yt_url)
print(f'Video ID: {v_id}')
print(f'Title: {title}')
print(f'Channel: {channel}')
print('Generating metadata for Obsidian...')
metadata = generate_metadata(yt_url, channel, title, v_id)
print('Generating transcript...')
transcript = YouTubeTranscriptApi.get_transcript(v_id)
print('Converting transcript to obsidian format...')
transcript = convert_transcript_to_obsidian_format(v_id, transcript)

print('Copying to clipboard...')
subprocess.run("pbcopy", universal_newlines=True, input=metadata + '\n\n\n' + transcript)
print('Done copying to clipboard!')
