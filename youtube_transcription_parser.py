from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os, re
import pandas as pd

driver = Firefox()  # path to the web driver


def scroll():
    driver.execute_script("window.scrollTo(0, window.scrollY + 2000);")


def read_urls():
    video_links = []
    with open('transcriptindex.txt', 'r') as file:
        for line in file:
            if re.search(r'https://www\.youtube\.com/c.*', line):
                rv = read_videos(line)
                video_links += rv
            else:
                video_links.append(line.rstrip('\n'))
    return video_links


def read_videos(url):
    driver.get(url + '/videos')
    video_containers = driver.find_elements(By.CSS_SELECTOR,
                                            '.ytd-grid-video-renderer a.yt-simple-endpoint.inline-block.style-scope.ytd-thumbnail')
    scroll()
    ln1, ln2 = 0, len(video_containers)
    while ln1 != ln2:
        time.sleep(0.5)
        scroll()
        video_containers = driver.find_elements(By.CSS_SELECTOR,
                                                '.ytd-grid-video-renderer a.yt-simple-endpoint.inline-block.style-scope.ytd-thumbnail')
        ln1, ln2 = ln2, len(video_containers)
    return list(map(lambda x: x.get_attribute('href'), video_containers))


def write_csv(df, title):
    df.to_csv(f'output/{title}.csv', index=False)


def write_md(df, title, url):
    with open(f'output/{title}.md', 'w', encoding='utf-8') as file:
        file.write(url + '\n\n')
        for i, row in df.iterrows():
            file.write(f"{row['timing']}   {row['description']}\n")


def read_transcription(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'yt-icon.style-scope.ytd-menu-renderer'))).click()
    try:
        driver.find_element(By.CSS_SELECTOR,
                            'tp-yt-paper-item.style-scope.ytd-menu-service-item-renderer yt-icon').click()
    except:
        df = pd.DataFrame({'timing': ['no transcript'], 'description': ['']})
    else:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-transcript-body-renderer')))
        timings = driver.find_elements(By.CSS_SELECTOR, 'div.cue-group-start-offset.style-scope.ytd-transcript-body-renderer')
        descriptions = driver.find_elements(By.CSS_SELECTOR, 'div.cues.style-scope.ytd-transcript-body-renderer')
        get_text = lambda item: item.text
        df = pd.DataFrame({'timing': map(get_text, timings), 'description': map(get_text, descriptions)})
    title = driver.find_element(By.CSS_SELECTOR, 'h1 yt-formatted-string.style-scope.ytd-video-primary-info-renderer').text
    write_csv(df, title)
    write_md(df, title, url)


def main():
    for link in read_urls():
        read_transcription(link)
    driver.close()


main()
