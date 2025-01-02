import requests
import json
import os
from bs4 import BeautifulSoup
import time
from urllib.parse import urlencode, quote
import datetime

REQUEST_URL = "https://biletinial.com/tr-tr/mekan/cukurova-devlet-senfoni-orkestrasi"
REQUEST_URL2 = "https://biletinial.com/tr-tr/mekan/mersin-devlet-opera-balesi"
NTFY_LINK = "https://ntfy.sh"
NTFY_TOPIC = "cdso_new_ticket_alert"
NTFY_TITLE = "Çukurova Devlet Senfoni Orkestrası"
RETRY_INTERVAL = 120


def new_request():
    """
    Makes a GET request to the specified URL and returns the response.
    """
    url = REQUEST_URL
    response = requests.get(url)
    return response


def parse_response(response):
    """
    Parses the HTML response to extract ticket information.

    Args:
        response: The HTTP response object.

    Returns:
        A list of dictionaries containing ticket details.
    """
    soup = BeautifulSoup(response.text, "html.parser")
    tickets = soup.find(
        "div", class_="yeniMekan__sayfalar__vizyondakiler content"
    ).find_all("li")
    result = []
    for ticket in tickets:
        try:
            title = ticket.find("h3").text.strip()
        except AttributeError:
            title = "No Title"

        result.append(
            {
                "title": title,
            }
        )

    return result


class SaveFile:
    def __init__(self, filepath):
        """
        Initializes the SaveFile class with the given file path.

        Args:
            filepath: The path to the file to be operated on.
        """
        self.file_name = filepath

    def update(self, tickets):
        """
        Updates the JSON file with the given key-value pair. If the key already exists and its value is a dictionary,
        the function will update the nested dictionary instead of overwriting it.

        Args:
            key: The key to be updated or added.
            value: The value to be associated with the key.
        """

        if os.path.exists(self.file_name):
            with open(self.file_name, "w") as file:
                json.dump(tickets, file, indent=4)

        else:
            with open(self.file_name, "w") as file:
                json.dump(tickets, file, indent=4)



    def check_if_key_exists(self, key):
        """
        Checks if the specified key exists in the JSON file.

        Args:
            key: The key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        _any = False
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as file:
                data = json.load(file)
                for entry in data:
                    if entry["title"] == key:
                        _any = True
                        break
        return _any


class NtfyManager:
    def __init__(self):
        self.url = NTFY_LINK
        self.topic = NTFY_TOPIC

    def send_ticket_notification(self, title,dt:str=""):
        headers = {
            "Title": NTFY_TITLE.encode("utf-8"),
            "click": REQUEST_URL,
            "time": str(int(time.time())),
        }
        message = f"Yeni bilet çıktı!\n\nBilet Adı:  {title}\nTarih:  {dt}"
        requests.post(
            self.url + "/" + self.topic, data=message.encode("utf-8"), headers=headers
        )
    
    def send_init_notification(self):
        headers = {
            "Title": NTFY_TITLE.encode("utf-8"),
            "time": str(int(time.time())),
        }
        message = f"Biletler Kontrol Edilmeye Başlandı."
        requests.post(
            self.url + "/" + self.topic, data=message.encode("utf-8"), headers=headers
        )
    
    def send_stop_notification(self,message=""):
        headers = {
            "Title": NTFY_TITLE.encode("utf-8"),
            "time": str(int(time.time())),
        }
        message = f"HATA: Uygulama çalışmayı durdurdu. Hata Kodu: {message}"
        requests.post(
            self.url + "/" + self.topic, data=message.encode("utf-8"), headers=headers
        )

class Listener():
    def __init__(self):
        pass
    
    def start(self):
        Ntfy_Manager = NtfyManager()
        Ntfy_Manager.send_init_notification()
        
        i = 1
        try:
            while True:
                response = new_request()
                tickets = parse_response(response)
                for ticket in tickets:
                    if not SaveFile("tickets.json").check_if_key_exists(ticket["title"]):
                        Ntfy_Manager.send_ticket_notification(ticket["title"])
                        print("New Ticket Found: ", ticket["title"])
                SaveFile("tickets.json").update(tickets)
                if i == 1:
                    print(f"App is running... Retrying every {RETRY_INTERVAL} seconds.")
                elif i % 10 == 0:
                    print(f"App is running... Tested {i} times. Last Test: {datetime.datetime.now().strftime('%d.%m.%Y - %H:%M')}")
                i += 1
                time.sleep(RETRY_INTERVAL)
        except Exception as e:
            Ntfy_Manager.send_stop_notification(message="Listener Exception: "+ str(e))
            print("An error occurred. Exiting...")
            exit(1)
            