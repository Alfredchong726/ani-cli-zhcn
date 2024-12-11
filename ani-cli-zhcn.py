from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from cursesmenu import CursesMenu
from selenium import webdriver
from parsel import Selector
import subprocess
import requests
import argparse
import time

BASE_URL = "https://www.agedm.org/"

def search_anime(keyword, count):
    search_url = f"{BASE_URL}/search?query={keyword}&page={count}"
    response = requests.get(search_url)
    if response.status_code != 200:
        print("Failed to fetch search results.")
        input("\nPress Enter to return to the main menu.")
        return []

    selector = Selector(response.text)
    results = []
    
    for content in selector.css(".card.cata_video_item.py-4 .card-title"):
        results.append({
            "title": content.css("::text").get(),
            "link": content.css("::attr(href)").get()
        })

    if selector.css(".page-item:nth-last-child(2) a::text").get() == "下一页":
        count += 1
        returns = search_anime(keyword=keyword, count=count)
        results.extend(returns)

    return results


def fetch_video_links(anime_url):
    response = requests.get(anime_url)
    if response.status_code != 200:
        print("Failed to fetch anime details.")
        input("\nPress Enter to return to the main menu.")
        return []

    selector = Selector(response.text)
    episodes = []

    for ep in selector.css(".video_detail_episode:nth-child(1) li"):
        episodes.append({
            "episode": ep.css("a::text").get(),
            "link": ep.css("a::attr(href)").get()
        })
    return episodes

def fetch_video_url_with_wait(episode_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(episode_url)
        time.sleep(3)

        video_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.art-video-player video'))
        )
        
        video_url = video_element.get_attribute('src')
        if video_url:
            return video_url
        else:
            return None
    
    except Exception as e:
        print(f"Error fetching video URL: {e}")
        return None
    finally:
        driver.quit()

def play_video(episode_url):
    response = requests.get(episode_url)
    if response.status_code != 200:
        print("Failed to fetch episode details.")
        input("\nPress Enter to return to the main menu.")
        return

    selector = Selector(response.text)
    video_url = selector.css("#iframeForVideo::attr(src)").get()
    video_url = fetch_video_url_with_wait(video_url)

    if video_url:
        subprocess.run(["mpv", "--no-resume-playback", video_url])

def tui_select(items, title_key="title", display_message="Select an option"):
    try:
        options = [item[title_key] for item in items]
        selection = CursesMenu.get_selection(options, title=display_message)
        if selection < 0:
            print("Exiting...")
            return None
        return selection
    except Exception as e:
        print(f"\nError occurred during selection: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Anime CLI Tool with TUI")
    parser.add_argument('query', help="Search keyword for anime")

    args = parser.parse_args()

    results = search_anime(args.query, 1)
    if not results:
        print("No results found.")
        input("\nPress Enter to return to the main menu.")
        return

    selected_index = tui_select(results, "title", "Select anime:")
    if selected_index is None:
        print("No anime selected.")
        input("\nPress Enter to return to the main menu.")
        return

    anime_url = results[selected_index]['link']

    episodes = fetch_video_links(anime_url)
    if not episodes:
        print("No episodes found.")
        input("\nPress Enter to return to the main menu.")
        return

    while True:
        selected_episode_index = tui_select(episodes, "episode", "Select episode:")
        if selected_episode_index is None:
            print("Returning to main menu.")
            break

        episode_url = episodes[selected_episode_index]['link']

        if episode_url:
            play_video(episode_url)
        else:
            print("Failed to fetch video URL.")

if __name__ == "__main__":
    main()
