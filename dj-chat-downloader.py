import concurrent.futures
import os
import time

import requests
from bs4 import BeautifulSoup

# Timing the script
f1 = time.perf_counter()

WORK_DIR = os.getcwd()


class Podcast:
    """
    Main class to download podcasts
    """

    def __init__(self, url):
        self.url = url

    def create_folder(self, folder="downloads"):
        """
        Create a 'downloads' folder.
        """
        os.makedirs(folder, exist_ok=True)
        return os.path.join(WORK_DIR, folder)

    def get_podcasts(self):
        """
        Scrape the RSS feed and get podcasts
        """
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "xml")
        podcasts = soup.find_all("item")
        return podcasts

    def get_size(self, length):
        """
        Get the size of a podcast, in MB
        """
        return round(length / (1024**2), 2)

    def convert_to_valid_name(self, string):
        """
        Convert podcast names to valid filenames
        """
        filename = "".join(c for c in string if c.isalnum() or c in " -_.# ")
        return os.path.splitext(filename)[0]

    def download_podcast(self, podcast):
        """
        Download podcasts using threading, tqdm, and with()
        """

        title = podcast.find("title").text
        episode = int(podcast.find("itunes:episode").text)
        mp3_file = requests.get(podcast.find("enclosure")["url"], stream=True)
        mp3_size = self.get_size(int(podcast.find("enclosure")["length"]))
        file_name = self.convert_to_valid_name(f"Django Chat #{episode:03d} - {title}")
        folder = self.create_folder()

        print(f">>> Downloading {file_name}")
        print(f">>> Size: {mp3_size} MB")

        with open(f"{folder}/{file_name}.mp3", "wb") as f:
            for data in mp3_file.iter_content(chunk_size=1024):
                f.write(data)
            print(f">>> Downloaded {file_name}")


if __name__ == "__main__":
    rss_feed_url = "https://feeds.simplecast.com/WpQaX_cs"  # Django podcast RSS
    podcast = Podcast(url=rss_feed_url)

    # Choose podcasts here by slicing
    # Choosing the first 2 podcasts
    podcasts = podcast.get_podcasts()[-3:-1]

    # Using threading to speed up downloads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(podcast.download_podcast, podcasts)

f2 = time.perf_counter()

print(f"Script finished in {round(f2-f1, 2)} second(s)")
