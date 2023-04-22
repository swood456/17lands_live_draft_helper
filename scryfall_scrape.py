from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
from typing import List

page_url = "https://www.17lands.com/card_ratings"

class CardInfo:
    name: str
    gih_wr: str
    # can add other things (color) if necessary

    def __init__(self, name, gih_wr):
        self.name = name
        self.gih_wr = gih_wr

def dump_cards_to_csv(cards: List[CardInfo]):
    with open("17lands_results.csv", "w", newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='|',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for datum in cards:
            spamwriter.writerow([datum.name, datum.gih_wr])

def scrape_data():
    driver = webdriver.Chrome()
    driver.implicitly_wait(0.5)

    driver.get(page_url)

    table_body = driver.find_element(By.XPATH, "//*[@id=\"card_ratings_app\"]/div/div[2]/table/tbody")

    rows = table_body.find_elements(By.TAG_NAME, "tr")

    cards = []

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        name = tds[0].text
        gih_wr = tds[14].text[:-1]

        card = CardInfo(name, gih_wr)
        cards.append(card)

    dump_cards_to_csv(cards)

if __name__ == '__main__':
    scrape_data()