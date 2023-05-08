import re
from datetime import timedelta
import openai
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from github import Github

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
REPO_NAME = "DataTalksClub/mlops-zoomcamp"


issues_url = "https://github.com/DataTalksClub/mlops-zoomcamp/issues?q=is%3Aopen+is%3Aissue"
playlist_url = "https://www.youtube.com/playlist?list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
query_params = parse_qs(urlparse(playlist_url).query)
playlist_id = query_params["list"][0]

g = Github(GITHUB_ACCESS_TOKEN)
repo = g.get_repo(REPO_NAME)



def get_video_urls_and_titles(api_key, playlist_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_info = []

    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId=playlist_id
    )
    
    while request:
        response = request.execute()
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_info.append((video_title, video_url))

        request = youtube.playlistItems().list_next(request, response)

    return video_info



def get_video_titles_from_issues(issues_url):
    response = requests.get(issues_url)
    soup = BeautifulSoup(response.content, "html.parser")
    issue_titles = [el.text.strip() for el in soup.find_all("a", class_="Link--primary")]
    video_titles = [title.replace("Timecodes for ", "").replace('"', '') for title in issue_titles if title.startswith("Timecodes for ")]
    # print(video_titles)
    return video_titles


def match_titles_and_urls(issues_titles, video_info):
    matched_videos = {}
    for title in issues_titles:
        for video_title, url in video_info:
            if title.lower() == video_title.lower():
                video_id = url.split("watch?v=")[1]
                matched_videos[title] = video_id
                break
    return matched_videos

def clean_text(text):
    text = re.sub(r'(?<!^)(\d{1,2}:\d{2}:\d{2})|(\d{1,2}:\d{2})', '', text)
    return text

def process_chunk(current_text_chunk, chunk_start_time):
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"You are youtube timestamp description expert. Write a max=15 words, single line timestamp description, do not mention timestamp description: '{current_text_chunk}' ",  # noqa: E501
        max_tokens=350,
        n=1,
        stop=None,
        temperature=0.0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    timestamp_string = str(timedelta(seconds=int(chunk_start_time)))
    # chunk_summary = f"\n {timestamp_string} {completion.choices[0].text}"
    polished_timestamp = f"{timestamp_string} - {clean_text(completion.choices[0].text)}".replace("\n", " ").replace("Timestamp Description: ", "")
    print(polished_timestamp)
    os.makedirs("issues", exist_ok=True)

    with open(f"issues/{video_id}.txt", "a", encoding="utf-8") as file:
        file.write(polished_timestamp)
    return polished_timestamp


def process_transcript(whole_transcript):
    current_text_chunk = ""
    comment_body = ""
    chunk_start_time = 0

    for current_line in whole_transcript:
        if chunk_start_time == 0:
            chunk_start_time = current_line['start']

        current_text_chunk += " " + current_line['text']

        if len(current_text_chunk.split(" ")) > 200:
            polished_timestamp = process_chunk(current_text_chunk, chunk_start_time)
            comment_body += f"\n{polished_timestamp}"
            chunk_start_time = 0
            current_text_chunk = ""

    return comment_body



def add_issue_comment_with_confirmation(issue_titles, comment_body):
    issues = repo.get_issues(state="open")
    for issue in issues:
        if issue.title.strip() in issue_titles:
            print(f"\nAdding comment to issue '{issue.title}':\n")
            print(comment_body)
            proceed = input("\nProceed with commit? [y/N]: ")
            if proceed.lower() == "y":
                issue.create_comment(comment_body)
                print("Comment added.")
            else:
                print("Skipped.")
            break






if __name__ == "__main__":
    video_info = get_video_urls_and_titles(YOUTUBE_API_KEY, playlist_id)
    video_titles = get_video_titles_from_issues(issues_url)
    matched_videos = match_titles_and_urls(video_titles, video_info)
    
    
    # Loop through matched_videos items
    for title, video_id in matched_videos.items():
        print(title)
        
        # Create a new title
        new_title = f'Timecodes for "{title}"'

        # Process the transcript for the video
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            comment_body = process_transcript(transcript)
        except TranscriptsDisabled:
            print(f"Transcripts disabled for video {video_id}. Skipping...")

        # Add the comment to the issue
        add_issue_comment_with_confirmation(new_title, comment_body)
