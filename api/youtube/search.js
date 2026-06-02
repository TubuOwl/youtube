export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "*");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  try {
    const query = req.query.video;

    if (!query) {
      return res.status(400).json({
        success: false,
        error: "Missing video parameter"
      });
    }

    const yt = await fetch(
      "https://www.youtube.com/youtubei/v1/search?prettyPrint=false",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-YouTube-Client-Name": "1",
          "X-YouTube-Client-Version": "2.20231219.04.00"
        },
        body: JSON.stringify({
          query,
          context: {
            client: {
              clientName: "WEB",
              clientVersion: "2.20231219.04.00",
              hl: "id",
              gl: "ID"
            }
          }
        })
      }
    );

    const data = await yt.json();

    const videos = [];

    function walk(obj) {
      if (!obj || typeof obj !== "object") return;

      if (obj.videoRenderer) {
        const v = obj.videoRenderer;
        const videoId = v.videoId;

        if (videoId) {
          videos.push({
            videoId,
            title:
              v.title?.runs?.[0]?.text || "",

            channel:
              v.ownerText?.runs?.[0]?.text ||
              v.longBylineText?.runs?.[0]?.text ||
              "",

            duration:
              v.lengthText?.simpleText || "",

            views:
              v.shortViewCountText?.simpleText ||
              v.viewCountText?.simpleText ||
              "",

            thumbnail:
              `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`,

            url:
              `https://www.youtube.com/watch?v=${videoId}`
          });
        }

        return;
      }

      if (Array.isArray(obj)) {
        obj.forEach(walk);
      } else {
        Object.values(obj).forEach(walk);
      }
    }

    walk(data);

    return res.status(200).json({
      success: true,
      total: videos.length,
      results: videos
    });

  } catch (err) {
    return res.status(500).json({
      success: false,
      error: err.message
    });
  }
}
