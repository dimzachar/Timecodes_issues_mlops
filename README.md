# YouTube Timecode Generation Script

This Python script was created to automate the creation of timestamps of [MLOps Zoomcamp playlist](
https://www.youtube.com/playlist?list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK) that are missing and given that a [Github issue](https://github.com/DataTalksClub/mlops-zoomcamp/issues?q=is%3Aopen+is%3Aissue) is open. 

It generates timecodes for YouTube videos in a playlist and adds them as comments to corresponding open GitHub issues. The script utilizes the YouTube API, Google API Client Library, OpenAI API, and PyGitHub to interact with YouTube and GitHub, BeautifulSoup for web scraping, and the youtube_transcript_api for handling video transcripts.

You could potentially use it for other playlists.

Please be aware that using OpenAI's API key will incur costs. Using OpenAI's GPT-3.5-turbo model seems cheaper than text-davinci-003. You can easily change it to OpenAI's GPT-3.5-turbo model.


## Dependencies

- youtube_transcript_api
- google-api-python-client
- BeautifulSoup4
- openai
- python-dotenv
- PyGithub

## Usage

1. Set up API keys and access tokens for OpenAI, YouTube, and GitHub in your `.env` file.
2. Set the `REPO_NAME` and `playlist_url` variables to the GitHub repository and YouTube playlist URL you want to work with.
3. Run the script: `python main.py`

## Functions

- `get_video_urls_and_titles(api_key, playlist_id)`: Retrieves video URLs and titles from a YouTube playlist.
- `get_video_titles_from_issues(issues_url)`: Scrapes video titles from open GitHub issues.
- `match_titles_and_urls(issues_titles, video_info)`: Matches video titles from GitHub issues with their URLs.
- `clean_text(text)`: Cleans up the text by removing timestamps.
- `process_chunk(current_text_chunk, chunk_start_time)`: Generates a timestamp description using OpenAI API.
- `process_transcript(whole_transcript)`: Processes a video transcript by splitting it into chunks and generating timestamp descriptions.
- `add_issue_comment_with_confirmation(issue_titles, comment_body)`: Adds a comment with generated timecodes to the corresponding GitHub issue after user confirmation.

## Workflow

1. Load environment variables and authenticate with APIs.
2. Get video URLs and titles from the specified YouTube playlist.
3. Scrape video titles from open GitHub issues.
4. Match video titles from GitHub issues with their YouTube URLs.
5. Loop through matched_videos items and generate timestamp descriptions for video transcripts.
6. Add the generated timecodes as a comment to the corresponding GitHub issue after user confirmation.

