import urllib.request
import json
import sys

def getIGJson(payload):
  startIndex = payload.find("{\"config\":")
  resStartIndex = payload[startIndex:]
  lastIndex = resStartIndex.find(";</script>")
  resLastIndex = resStartIndex[:lastIndex]

  jsonFormat = json.loads(resLastIndex)
  return jsonFormat

def getExcerptTitle(title):
  title = title.replace('/', '')
  title = title.replace('\n', '')
  if len(title) >= 15:
    return title[:15]
  return title

def fetchTimeline(timeline):
  for node in timeline:
    if node["node"]["__typename"] == 'GraphVideo':
      linkId = node["node"]["shortcode"]
      videoLink = "https://www.instagram.com/p/" + linkId
      videoReader = urllib.request.urlopen(videoLink)
      videoFile = videoReader.read()
      responseVideo = videoFile.decode('utf-8')
      jsonVideo = getIGJson(responseVideo)
      videoURL = jsonVideo["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["video_url"]
      postId = jsonVideo["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["id"]
      caption = ""
      if len(jsonVideo["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"]) != 0:
        caption = jsonVideo["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"][0]["node"]["text"].encode('utf-8').decode()
      urllib.request.urlretrieve(videoURL, getExcerptTitle(caption) + "-" + postId + ".mp4")
      print(getExcerptTitle(caption) + "-" + postId + " => downloaded 🎉")

    elif node["node"]["__typename"] == 'GraphSidecar':
      linkId = node["node"]["shortcode"]
      slidesLink = "https://www.instagram.com/p/" + linkId
      f = urllib.request.urlopen(slidesLink)
      myfile = f.read()
      response = myfile.decode('utf-8')
      jsonSlide = getIGJson(response)

      
      slidesId = jsonSlide["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["id"]
      slides = jsonSlide["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_sidecar_to_children"]["edges"]
      slideCaption = ""
      if len(jsonSlide["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"]) != 0:
        slideCaption = jsonSlide["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
      
      count = 1
      for slideNode in slides:
        slideURL = slideNode["node"]["display_resources"][2]["src"].encode('utf-8').decode()
        urllib.request.urlretrieve(slideURL, getExcerptTitle(slideCaption) + "-" + str(count) + slidesId + ".jpg")
        count += 1
        print(getExcerptTitle(slideCaption) + "-" + slidesId + " => downloaded 🎉")
      
    else:
      postId = node["node"]["id"]
      filename = ""
      if len(node["node"]["edge_media_to_caption"]["edges"]) != 0:
        filename = node["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"].encode('utf-8').decode()
      
      imageURL = node["node"]["thumbnail_resources"][4]["src"].encode('utf-8').decode()
      urllib.request.urlretrieve(imageURL, getExcerptTitle(filename) + "-" + postId + ".jpg")
      print(getExcerptTitle(filename) + "-" + postId + " => downloaded 🎉")

link = "https://www.instagram.com/" + sys.argv[1]
f = urllib.request.urlopen(link)
myfile = f.read()
response = myfile.decode('utf-8')

jsonFormat = getIGJson(response)

profileId = jsonFormat["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
totalPost = jsonFormat["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]

timelines = jsonFormat["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]

fetchTimeline(timelines)

# TODO:
# FETCH DATA AFTER FIRST 50 POST USING THIS ENDPOINT
# https://www.instagram.com/graphql/query/?query_hash=58b6785bea111c67129decbe6a448951&variables={"id":"4310360","first":12,"after":"QVFCRnBwSXZyOWRiaFlMZkdUYWxoTUJWWnZPNEFTX1hoYTVrc21BS3ZITGxCSDRoVW12a2ZhcWJJa3NaQmNmZmxsUU9NSngzcWYtekxLMHVmaWRVWTN3Yw=="}


afterHash = ''
fetchedPost = 12

while totalPost > fetchedPost:
  ajaxLink = 'https://www.instagram.com/graphql/query/?query_hash=58b6785bea111c67129decbe6a448951&variables={"id":"' + profileId + '","first":50,"after":"'+ afterHash + '"}'
  fileReader = urllib.request.urlopen(ajaxLink)
  responseJson = fileReader.read()
  responseJsonDecode = responseJson.decode('utf-8')

  nextJsonFormat = json.loads(responseJsonDecode)

  nextTimeline = nextJsonFormat["data"]["user"]["edge_owner_to_timeline_media"]["edges"]

  fetchTimeline(nextTimeline)

  afterHash = nextJsonFormat["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
  fetchedPost = fetchedPost + 50

