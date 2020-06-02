# This is a web scraping project that uses ParseHub tool to extract (scrape)
# data from a target web page (https://www.worldometers.info/coronavirus/)
# and generate a json data, this can access via a webservice.
# Note: data from API needs to run the project periodically to get
# the latest data from target webpage

import os
import sys
import requests
import json
import time
import threading

pipe = sys.argv
# credentials provided by parseHub, configured on enviroment variables
API_KEY = os.environ.get("ParseHub_API_KEY")
PROJECT_TOKEN = os.environ.get("ParseHub_PROJECT_TOKEN")
GET_DATA_URL = f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data"
POST_UPDATE_URL = f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/run"


class ParseHubData:
    # initialize class and its properties
    def __init__(self, api_key):
        self.api_key = api_key
        self.params = {
            "api_key": self.api_key,
            "format": "json"
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(GET_DATA_URL, params=self.params)
        dat = json.loads(response.content)
        return dat

    def update_data(self):
        response = None
        try:
            print("Fetching new updates of Covid-19 from Worldometer.com ...")
            response = requests.post(POST_UPDATE_URL, params=self.params)

        except Exception as e:
            print("Something went wrong when updating data. ", e)

        def run_update():
            # this will allow the current thread to give way to main thread processing
            time.sleep(0.1)
            old_data = self.data
            # check for new data every 5 seconds
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("========================================================")
                    print("New data for Covid-19 from Worldometer is now available.")
                    print("========================================================")
                    break
                time.sleep(5)

        if response.status_code == 200:
            # create and start the thread for updating the data from parseHub API
            update_thread = threading.Thread(target=run_update)
            update_thread.start()

    def find_data(self, key, value, isWorldwide=False):
        found_dict = []
        key = key.lower()
        value = value.lower()

        def convert_number(value):
            val = str(value).strip()

            if val != "":
                return int(str(val).replace(",", ""))
            else:
                return "0"

        if isWorldwide:
            for item in self.data["Summary"]:
                found = False
                if key in item and key in "total_cases" and convert_number(value) in range(convert_number(item["total_cases"])):
                    found = True
                elif key in item and key in "total_deaths" and convert_number(value) in range(convert_number(item["total_deaths"])):
                    found = True
                elif key in item and key in "total_recoveries" and convert_number(value) in range(convert_number(item["total_recoveries"])):
                    found = True
                if found:
                    found_dict.append(item)
        else:
            for item in self.data["countries"]:
                found = False
                if key in item and key in "total_cases" and convert_number(value) in range(convert_number(item["total_cases"])):
                    found = True
                elif key in item and key in "new_cases" and convert_number(value) in range(convert_number(item["new_cases"])):
                    found = True
                elif key in item and key in "total_deaths" and convert_number(value) in range(convert_number(item["total_deaths"])):
                    found = True
                elif key in item and key in "new_deaths" and convert_number(value) in range(convert_number(item["new_deaths"])):
                    found = True
                elif key in item and key in "total_recoveries" and convert_number(value) in range(convert_number(item["total_recoveries"])):
                    found = True
                elif key in item and key in "total_tests" and convert_number(value) in range(convert_number(item["total_tests"])):
                    found = True
                elif key in item and key in "name" and (value in item["name"].lower() or item["name"].lower() in value):
                    found = True
                if found:
                    found_dict.append(item)
        return found_dict

    def find_by_country_name(self, country):
        found_dict = []
        for item in self.data["countries"]:
            if country.lower() in item["name"].lower():
                print("-------------------------")
                print(item["name"])
                print("-------------------------")
                if "total_cases" in item and item["total_cases"]:
                    print(f"Total Cases: {item['total_cases']}")
                if "new_cases" in item and item["new_cases"]:
                    print(f"New Cases: {item['new_cases']}")
                if "total_deaths" in item and item["total_deaths"]:
                    print(f"Total Deaths: {item['total_deaths']}")
                if "new_deaths" in item and item["new_deaths"]:
                    print(f"New Deaths: {item['new_deaths']}")
                if "total_recoveries" in item and item["total_recoveries"]:
                    print(f"Recoveries: {item['total_recoveries']}")
                if "total_tests" in item and item["total_tests"]:
                    print(f"Tests: {item['total_tests']}")
                if "population" in item and item["population"]:
                    print(f"Population: {item['population']}")
                print("")
                found_dict.append(item)

        return found_dict

    def find_by_country_names(self, countries):
        found_dict = []
        for country in countries:
            found_dict.append(self.find_by_country_name(country))

        if not found_dict:
            print(f"Data not found for {countries}")


if __name__ == "__main__":
    data = ParseHubData(API_KEY)
    # d = data.get_data()

    if len(pipe) > 2:
        while True:
            key = pipe[1]
            value = pipe[2]
            data_found = data.find_data(key, value)
            data.find_by_country_names([item["name"]
                                        for item in data_found if "name" in item])
            search_again = input("Search again (y/n): ")
            if search_again.lower() == "y":
                pipe[1] = input("Search key: ")
                pipe[2] = input("Search value: ")
                continue
            else:
                print("")
                break
    else:
        print("Invalid input: e.g. main.py <key> <value>")
    # data.update_data()
