log_location = "D:/Games/MTG Arena/MTGA/MTGA_Data/Logs/Logs/"

import time
import json
import scrython
import requests
import os

from scryfall_scrape import CardInfo

# follow.py
#
# Follow a file like tail -f.
def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        
        yield line

def parse_draft_pack(pack_string):
    json_string = pack_string.split("Draft.Notify ")[1]

    pack_blob = json.loads(json_string)

    return pack_blob


def watch_draft_pack(line, lands_data):
    if not "Draft.Notify" in line:
        print(".")
        return

    pack = parse_draft_pack(line)
    pack_num = pack.get("SelfPack", "???")
    pick_num = pack.get("SelfPick", "???")
    print(f"NEW PACK DETECTED    PACK {pack_num} PICK {pick_num}")

    cards_in_pack_string = pack["PackCards"]

    cards_in_pack = [c for c in cards_in_pack_string.split(",")]

    # print(cards_in_pack)
    cards = find_cards_17lands(cards_in_pack)

    # cards = [find_scryfall_card(card_id) for card_id in cards_in_pack]
    
    # # filter nulls, only get names
    # card_names = [c.name() for c in cards if c]

    card_names = [c["name"] for c in cards]

    # filter out the basics
    card_names = [c for c in card_names if c not in ["Plains", "Island", "Swamp", "Forest", "Mountain"]]



    print_results(card_names, lands_data)


def print_results(card_names, lands_data):
    pack_cards = [lands_data[name] for name in card_names]

    pack_cards.sort(key=lambda x: x.gih_wr, reverse=True)

    print("===========================================")
    for pack_card in pack_cards:
        print(f"{pack_card.name.ljust(30)}         {pack_card.gih_wr}")
    print("===========================================\n\n\n")
    # debugging only

def find_scryfall_card(card_id):
    # print(f"Looking up card {card_id}")
    # TODO multiverse legends are broken, fix eventually

    try:
        card = scrython.ArenaId(id=card_id)
    except scrython.ScryfallError as e:
        print(f"Error when looking up {card_id}")
        return None
    return card

def find_cards_17lands(card_id_list):
    card_id_query = "%2c".join(card_id_list)
    url = "https://www.17lands.com/data/cards"

    contents = requests.get(f"{url}?ids={card_id_query}")

    # print(contents.json())

    return contents.json()["cards"]




def get_current_logfile():
    # I have not much confidence in how python gets stuff back from os
    # so explicitly just sort the names I guess?
    log_names = []
    for file in os.listdir(log_location):
        if file.endswith(".log"):
            # log_names.append(file)
            log_names.append(os.path.join(log_location, file))
    
    log_names.sort(reverse=True, key=os.path.getmtime)
    return log_names[0]


if __name__ == '__main__':
    # Load scraped data
    lands_data = {}
    with open("17lands_results.csv", "r") as csvfile:
        for row in csvfile:
            r = row.split("|")
            lands_data[r[0]] = CardInfo(r[0], r[1][:-1])

    # filename = log_location + "UTC_Log - 04-21-2023 18.52.10.log"
    # # filename = f"{log_location}\UTC_Log - 04-21-2023 18.52.10.txt"
    
    filename = get_current_logfile()
    print(f"Looking at logs in file {filename}")
    logfile = open(filename,"r")
    loglines = follow(logfile)
    for line in loglines:
        watch_draft_pack(line, lands_data)

    # find_scryfall_card(84594)
