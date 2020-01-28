from googleapiclient.discovery import build

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


class YouTube(object):
    def __init__(self, app=None):
        self.app = app
        self.api_key = None
        self.youtube = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.api_key = app.config['YOUTUBE_API_KEY']

        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.api_key)

    def list_channel_videos(self, channel_id, max_results=50, order='rating'):
        search_items = []

        # Get videos of specific channel
        search_response = self.youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            maxResults=max_results,
            order=order,
            type='video',
            safeSearch='none'
        ).execute()
        page_search_items = search_response.get('items', [])
        search_next_page_token = search_response.get('nextPageToken')
        search_items += [search_item for search_item in page_search_items]

        # Get video ids
        page_videos_ids = [search_item['id']['videoId'] for search_item in page_search_items]

        # Get number of likes/dislikes for each video
        videos_response = self.youtube.videos().list(
            part='id,statistics',
            id=','.join(page_videos_ids),
            maxResults=max_results
        ).execute()
        page_videos_items = videos_response.get('items', [])

        for search_item in search_items:
            if 'video' in search_item:
                continue

            for video_item in page_videos_items:
                if search_item['id']['videoId'] == video_item['id']:
                    search_item['video'] = video_item
                    continue

        while search_next_page_token:
            search_response = self.youtube.search().list(
                part='id,snippet',
                channelId=channel_id,
                maxResults=max_results,
                order=order,
                type='video',
                safeSearch='none',
                pageToken=search_next_page_token
            ).execute()
            page_search_items = search_response.get('items', [])
            search_next_page_token = search_response.get('nextPageToken')
            search_items += [search_item for search_item in page_search_items]

            # Get video ids
            page_videos_ids = [search_item['id']['videoId'] for search_item in page_search_items]

            # Get number of likes/dislikes for each video
            videos_response = self.youtube.videos().list(
                part='id,statistics',
                id=','.join(page_videos_ids),
                maxResults=max_results
            ).execute()
            page_videos_items = videos_response.get('items', [])

            for search_item in search_items:
                if 'video' in search_item:
                    continue

                for video_item in page_videos_items:
                    if search_item['id']['videoId'] == video_item['id']:
                        search_item['video'] = video_item
                        continue

        return search_items
