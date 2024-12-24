from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from urllib.parse import parse_qs, urlparse
import os
from typing import Dict, List, Any
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
    return None

def fetch_youtube_data(category_dict: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch YouTube video data including transcripts, thumbnails, comments, and metadata.
    
    Args:
        category_dict: Dictionary with category name as key and list of video dictionaries as value
        
    Returns:
        Dictionary containing processed video data
    """
    # Initialize YouTube API client
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("YouTube API key not found in environment variables")
    
    youtube = build('youtube', 'v3', developerKey=api_key)
    processed_data = {}
    
    for category, videos in category_dict.items():
        processed_videos = []
        
        for video in videos:
            try:
                video_id = get_video_id(video['URL'])
                if not video_id:
                    raise ValueError(f"Invalid YouTube URL: {video['URL']}")
                
                # Fetch video details
                video_response = youtube.videos().list(
                    part='snippet,statistics',
                    id=video_id
                ).execute()
                
                if not video_response['items']:
                    raise ValueError(f"Video not found: {video_id}")
                
                video_data = video_response['items'][0]
                
                # Fetch transcript
                transcript_text = ""
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript_text = " ".join([entry['text'] for entry in transcript])
                except (TranscriptsDisabled, NoTranscriptFound) as e:
                    transcript_text = f"Transcript unavailable: {str(e)}"
                
                # Fetch comments
                comments = []
                try:
                    comments_response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=10,
                        textFormat='plainText'
                    ).execute()
                    
                    comments = [{
                        'author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        'text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        'likes': item['snippet']['topLevelComment']['snippet']['likeCount'],
                        'published_at': item['snippet']['topLevelComment']['snippet']['publishedAt']
                    } for item in comments_response.get('items', [])]
                except HttpError:
                    comments = ["Comments disabled or error fetching comments"]
                
                # Compile video information
                processed_video = {
                    'title': video['Title'],
                    'source': video['Source'],
                    'url': video['URL'],
                    'video_id': video_id,
                    'description': video_data['snippet']['description'],
                    'publish_date': video_data['snippet']['publishedAt'],
                    'thumbnail_urls': {
                        'default': video_data['snippet']['thumbnails']['default']['url'],
                        'medium': video_data['snippet']['thumbnails']['medium']['url'],
                        'high': video_data['snippet']['thumbnails']['high']['url']
                    },
                    'statistics': {
                        'views': video_data['statistics'].get('viewCount', '0'),
                        'likes': video_data['statistics'].get('likeCount', '0'),
                        'comments': video_data['statistics'].get('commentCount', '0')
                    },
                    'transcript': transcript_text,
                    'comments': comments
                }
                
                processed_videos.append(processed_video)
                
            except Exception as e:
                # Log error and continue with next video
                error_entry = {
                    'title': video['Title'],
                    'source': video['Source'],
                    'url': video['URL'],
                    'error': str(e)
                }
                processed_videos.append(error_entry)
        
        processed_data[category] = processed_videos
    
    return processed_data

def save_to_json(data: Dict[str, Any], filename: str = 'youtube_data.json'):
    """Save the processed data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__":
    # Example dictionary data
    category_dict = {
        "Lottery": [
            {
                "Title": "Powerball 12-16-24",
                "Source": "WITN-TV",
                "URL": "https://www.youtube.com/watch?v=duAeRtYeC0E"
            },
            {
                "Title": "Powerball: December 16, 2024",
                "Source": "News 19 WLTX",
                "URL": "https://www.youtube.com/watch?v=pZfZRybbCTA"
            },
            {
                "Title": "Powerball 12-14-24",
                "Source": "WITN-TV",
                "URL": "https://www.youtube.com/watch?v=Dvx_L3_2Bkc"
            },
            {
                "Title": "No big winner: Mega Millions jackpot grows to $825 million",
                "Source": "KTSM 9 NEWS",
                "URL": "https://www.youtube.com/watch?v=SUUaR2cpAOI"
            },
            {
                "Title": "Mega Million Jackpot climbs to $825 million",
                "Source": "PAHomepage.com",
                "URL": "https://www.youtube.com/watch?v=zlmdubztPLU"
            },
            {
                "Title": "Mega Millions reaches $825 million",
                "Source": "KCENNews",
                "URL": "https://www.youtube.com/watch?v=S8DQTx1bRzs"
            },
            {
                "Title": "Mega Millions Jackpot jumps to $825 million",
                "Source": "WUSA9",
                "URL": "https://www.youtube.com/watch?v=t9qGo-6I-SA"
            },
            {
                "Title": "Mega Millions jackpot grows to $825M",
                "Source": "Atlanta News First",
                "URL": "https://www.youtube.com/watch?v=D2Y8EfwXyho"
            },
            {
                "Title": "Mega Millions jackpot rises to $825M",
                "Source": "WCNC",
                "URL": "https://www.youtube.com/watch?v=DunhkRLJl0w"
            },
            {
                "Title": "Mega Millions draws rare consecutive numbers but no winner",
                "Source": "TODAY",
                "URL": "https://www.youtube.com/watch?v=u3JXD2fE3Is"
            },
            {
                "Title": "Numbers drawn in Tuesday's Mega Millions jackpot",
                "Source": "Eyewitness News ABC7NY",
                "URL": "https://www.youtube.com/watch?v=cu9xSZ5PAe0"
            },
            {
                "Title": "Mega Millions 12-17-24",
                "Source": "WITN-TV",
                "URL": "https://www.youtube.com/watch?v=MlTKxrYu2EQ"
            },
            {
                "Title": "Lottery fever grows at the jackpot increases",
                "Source": "WFAA",
                "URL": "https://www.youtube.com/watch?v=LNpjln4H0Ok"
            },
            {
                "Title": "Mega Millions jackpot swells to $825M",
                "Source": "NBC10 Philadelphia",
                "URL": "https://www.youtube.com/watch?v=FV7oPEAskVo"
            },
            {
                "Title": "MegaMillions: December 17, 2024",
                "Source": "News 19 WLTX",
                "URL": "https://www.youtube.com/watch?v=oKgV2FQxBps"
            }
        ]
    }
    
    try:
        # Fetch data
        results = fetch_youtube_data(category_dict)
        
        # Save to JSON file
        save_to_json(results, 'lottery_videos_data.json')
        print("Data successfully fetched and saved to lottery_videos_data.json")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
