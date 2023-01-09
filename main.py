import requests
import os
import re
import xml.etree.ElementTree as ET
import whisper
import podcastparser
import urllib.request


def mp3ToTxt(mp3_file_name):
    # Load the Whisper model
    model = whisper.load_model("base")

    # Transcribe the MP3 file
    result = model.transcribe(mp3_file_name)
    transcription = result["text"]

    # Split the file name into the base name and the extension
    base_name, _ = os.path.splitext(mp3_file_name)

    # Construct the path to the text file
    text_file_name = base_name + ".txt"
    text_file_path = os.path.join(os.getcwd(), text_file_name)

    # Save the transcription to the text file
    with open(text_file_path, "w") as f:
        f.write(transcription)


# Function to download a file from a URL
def download_file(url, file_name):
    # os.makedirs(os.path.dirname(file_name), exist_ok=True)
    response = requests.get(url)
    open(file_name, "xb").write(response.content)


# Function to parse a podcast XML feed and extract the episode information
def parse_podcast_xml(xml_url, podcast_name):
    # Download the XML file
    print(xml_url)
    parsed = podcastparser.parse(xml_url, urllib.request.urlopen(xml_url))

    episodes = parsed["episodes"]
    for episode in episodes:
        episode["guid"] = "".join([i for i in episode["guid"] if i.isalpha()])

    return episodes


# Function to download and transcribe a podcast episode
def process_podcast_episode(podcast_name, episode):
    # Download the MP3 or MP4 file for the episode
    episode["description"] = ""
    episode["description_html"] = ""
    file_url = (
        episode["link"] if ".mp" in episode["link"] else episode["enclosures"][0]["url"]
    )
    file_extension = file_url.split(".")[-1]
    file_name = episode["guid"] + "." + file_extension
    print(file_name)
    print(file_url)
    # download_file(file_url, file_name)

    # Convert the MP3 or MP4 file to text
    text_file_name = episode["guid"] + ".txt"
    # mp3ToTxt(file_name)

    # Store the resulting text file in the folder for the podcast
    podcast_folder = f"{podcast_name}"
    if not os.path.exists(podcast_folder):
        os.makedirs(podcast_folder)
    os.rename(text_file_name, f"{podcast_folder}/{text_file_name}")


# Function to create an RSS feed for a podcast
def create_podcast_rss_feed(podcast_name, episodes):
    # Create the RSS root element
    rss = ET.Element("rss")
    rss.set("version", "2.0")

    # Create the channel element
    channel = ET.SubElement(rss, "channel")

    # Add the podcast title and link to the channel element
    title = ET.SubElement(channel, "title")
    title.text = podcast_name
    link = ET.SubElement(channel, "link")
    link.text = ""

    # Add the episodes to the channel element
    for episode in episodes:
        item = ET.SubElement(channel, "item")
        episode_title = ET.SubElement(item, "title")
        episode_title.text = episode["title"]
        episode_link = ET.SubElement(item, "link")
        episode_link.text = episode["link"]
        episode_guid = ET.SubElement(item, "guid")
        episode_guid.text = episode["guid"]
        episode_description = ET.SubElement(item, "description")
        episode_description.text = episode["description"]

        # Read the text file for the episode and add it to the description element
        with open(episode["guid"] + ".txt", "r") as f:
            episode_description.text += f.read()

    # Return the RSS feed as an ElementTree object
    return ET.ElementTree(rss)


# Function to save an RSS feed as an XML file
def save_rss_feed(rss_feed, xml_file_name):
    # Create the output folder if it doesn't exist
    if not os.path.exists("outputRssFeeds"):
        os.makedirs("outputRssFeeds")

    # Save the RSS feed as an XML file
    rss_feed.write(f"outputRssFeeds/{xml_file_name}.xml")


# List of podcast XML URLs
podcast_xml_urls = ["https://feed.podbean.com/bountyhuntershow/feed.xml"]

# Process each podcast
for xml_url in podcast_xml_urls:
    podcast_name = "".join([i for i in xml_url if i.isalpha()])

    # Parse the podcast XML feed and extract the episode information
    episodes = parse_podcast_xml(xml_url, podcast_name)

    # Extract the podcast name from the XML URL

    # Download and transcribe each episode
    for episode in episodes:
        process_podcast_episode(podcast_name, episode)

    # Create an RSS feed for the podcast
    rss_feed = create_podcast_rss_feed(podcast_name, episodes)

    # Save the RSS feed as an XML file
    save_rss_feed(rss_feed, podcast_name)
