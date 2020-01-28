import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from lib.youtube import YouTube

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['YOUTUBE_API_KEY'] = os.environ.get('YOUTUBE_API_KEY')
db = SQLAlchemy(app)
youtube = YouTube(app)


@app.route('/')
def index():
    return 'test-flask'


@app.route('/youtube/most_rated/<string:channel_id>', methods=['GET', 'OPTIONS'])
def youtube_most_rated(channel_id):
    most_rated = youtube.list_channel_videos(channel_id=channel_id)

    def video_like_ratio(video):
        statistics = video['video']['statistics']

        if 'likeCount' not in statistics or 'dislikeCount' not in statistics:
            return 0

        like_count = int(statistics['likeCount'])
        dislike_count = int(statistics['dislikeCount'])

        return like_count / dislike_count

    videos_by_most_liked = sorted(most_rated, key=video_like_ratio, reverse=True)

    diff_a = []
    diff_b = []

    for a, b in zip(most_rated, videos_by_most_liked):
        if a['id']['videoId'] != b['id']['videoId']:
            diff_a.append(a)
            diff_b.append(b)

    return jsonify({
        'most_rated': most_rated,
        'most_liked': videos_by_most_liked,
        'diff_a': diff_a,
        'diff_b': diff_b,
    })


if __name__ == '__main__':
    app.run()
