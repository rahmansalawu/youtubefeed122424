# YouTube Video Data Fetcher

This application fetches detailed information about YouTube videos, including transcripts, comments, and metadata.

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory and add your YouTube API key:
```
YOUTUBE_API_KEY=your-api-key-here
```

3. To get a YouTube API key:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create credentials (API key)
   - Copy the API key to your `.env` file

## Usage

1. Modify the `category_dict` in `youtube_data_fetcher.py` with your desired videos
2. Run the script:
```bash
python youtube_data_fetcher.py
```

The script will create a JSON file containing all the fetched data, including:
- Video metadata (title, description, publish date)
- Thumbnail URLs
- Statistics (views, likes, comments)
- Video transcript (if available)
- Top comments (if available)

## Error Handling

The script handles various scenarios gracefully:
- Unavailable transcripts
- Disabled comments
- Private videos
- Invalid URLs
- API errors

## Output

The data is saved in a structured JSON format to `lottery_videos_data.json` by default.
