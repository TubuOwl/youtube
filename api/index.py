from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


def walk(obj, videos):
    if not isinstance(obj, (dict, list)):
        return

    if isinstance(obj, dict):
        if "videoRenderer" in obj:
            v = obj["videoRenderer"]

            video_id = v.get("videoId")
            if video_id:
                videos.append({
                    "videoId": video_id,
                    "title": v.get("title", {}).get("runs", [{}])[0].get("text", ""),
                    "channel":
                        v.get("ownerText", {}).get("runs", [{}])[0].get("text", "") or
                        v.get("longBylineText", {}).get("runs", [{}])[0].get("text", ""),
                    "duration": v.get("lengthText", {}).get("simpleText", ""),
                    "views":
                        v.get("shortViewCountText", {}).get("simpleText", "") or
                        v.get("viewCountText", {}).get("simpleText", ""),
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
            return

        for value in obj.values():
            walk(value, videos)

    elif isinstance(obj, list):
        for item in obj:
            walk(item, videos)


@app.route("/")
def home():
    return jsonify({
        "status": True,
        "message": "YouTube Search API"
    })


@app.route("/youtube/search")
def youtube_search():
    query = request.args.get("video")

    if not query:
        return jsonify({
            "success": False,
            "error": "Missing parameter: video"
        }), 400

    payload = {
        "query": query,
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20231219.04.00",
                "hl": "id",
                "gl": "ID"
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-YouTube-Client-Name": "1",
        "X-YouTube-Client-Version": "2.20231219.04.00",
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.post(
        "https://www.youtube.com/youtubei/v1/search?prettyPrint=false",
        json=payload,
        headers=headers,
        timeout=30
    )

    data = r.json()

    videos = []
    walk(data, videos)

    return jsonify({
        "success": True,
        "total": len(videos),
        "results": videos
    })


# Penting untuk Vercel
app = app
