import time
import pandas as pd
from scraper import InstaScrapper
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


if __name__ == '__main__':
    list_of_profile_urls = [
        "https://www.instagram.com/fkirkorov/",
        "https://www.instagram.com/justinbieber/",
        "https://www.instagram.com/madonna/",
        "https://www.instagram.com/billieeilish/",
        "https://www.instagram.com/chilipeppers/"
    ]
    scrapper = InstaScrapper(50)
    with ThreadPoolExecutor(max_workers = 3) as executor:
        executor.map(scrapper.getProfilePostsDetails, list_of_profile_urls)
    df1 = pd.DataFrame(scrapper.post_details)
    df2 = pd.DataFrame(scrapper.profiles_info)
    df1.to_csv('{}_{}_instagram.csv'.format(str(datetime.now()).replace(" ", "_").replace(":", "_"), scrapper.counter))
    df2.to_csv('{}_{}_instagram_total.csv'.format(str(datetime.now()).replace(" ", "_").replace(":", "_"), scrapper.counter))
