import customtkinter as ctk
from apify_client import ApifyClient
import json
import csv
import datetime
import shared_variables as shv
from pandas import read_csv
import logging
from tkinter import filedialog
from logging_window import LoggingWindow, TextHandler  # Ensure this is correctly imported


def save_to_json(data, filename, root_path):
    if root_path:
        path = ""
    else:
        path = filedialog.asksaveasfilename(defaultextension=f".json",
                                            filetypes=[(f"JSON files", f"*.json")])
    with open(path + filename, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def save_to_csv(data, filename, root_path):
    if not data:
        return

    # Extract all field names from the data
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    if root_path:
        path = ""
    else:
        path = filedialog.asksaveasfilename(defaultextension=f".csv",
                                            filetypes=[(f"CSV files", f"*.csv")])
    with open(path + filename, "w", newline='', encoding='utf-8') as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=list(all_keys))
        dict_writer.writeheader()
        dict_writer.writerows(data)


class Client1:
    def __init__(self, api_token):
        self.first_actor_ran = False  # Flag to track if the first actor ran successfully
        self.client = ApifyClient(api_token)
        self.urls = []  # Initialize urls as an instance variable
        self.init_ui()
        timestamp = datetime.datetime.now()
        self.str_timestamp = timestamp.strftime("%Y-%m-%d %H-%M-%S")

        # Set up logging
        self.logger = logging.getLogger('apify')
        self.logger.setLevel(logging.DEBUG)

        # Initialize the logging window but don't show it yet
        self.logging_window = None

    def init_ui(self):
        self.app = ctk.CTk()
        self.app.title("Instagram Client")
        self.app.geometry("600x800")
        ctk.set_appearance_mode(shv.appearance)
        ctk.set_default_color_theme(shv.theme)

        # Initialize the logging window

        self.direct_urls_label = ctk.CTkLabel(self.app, text="usernames (comma separated)")
        self.direct_urls_label.pack(pady=5)
        self.direct_urls_entry = ctk.CTkEntry(self.app, placeholder_text="e.g. atlantasanad")
        self.direct_urls_entry.pack(pady=5)

        self.post_results_limit_label = ctk.CTkLabel(self.app, text="Post Results Limit:")
        self.post_results_limit_label.pack(pady=5)
        self.post_results_limit_entry = ctk.CTkEntry(self.app, placeholder_text="200")
        self.post_results_limit_entry.pack(pady=5)

        self.run_first_actor_button = ctk.CTkButton(self.app, text="Get posts", command=self.run_first_actor)
        self.run_first_actor_button.pack(pady=20)

        self.comments_results_limit_label = ctk.CTkLabel(self.app, text="Comment Results Limit:")
        self.comments_results_limit_label.pack(pady=5)
        self.comments_results_limit_entry = ctk.CTkEntry(self.app, placeholder_text="200")
        self.comments_results_limit_entry.pack(pady=5)

        self.run_second_actor_button = ctk.CTkButton(self.app, text="Get the Comments", command=self.run_second_actor)
        self.run_second_actor_button.pack(pady=20)

        self.add_parent_data_var = ctk.BooleanVar()
        self.add_parent_data_checkbox = ctk.CTkCheckBox(
            self.app, text="Add Parent Data", variable=self.add_parent_data_var)
        self.add_parent_data_checkbox.pack(pady=5)

        self.save_as_json_var = ctk.BooleanVar()
        self.save_as_json_checkbox = ctk.CTkCheckBox(
            self.app, text="Save as JSON", variable=self.save_as_json_var)
        self.save_as_json_checkbox.pack(pady=5)

        self.save_as_csv_var = ctk.BooleanVar()
        self.save_as_csv_checkbox = ctk.CTkCheckBox(
            self.app, text="Save as CSV", variable=self.save_as_csv_var)
        self.save_as_csv_checkbox.pack(pady=5)

        self.Warning_label = ctk.CTkLabel(self.app,
                                          text="DO NOT INTERRUPT!!!!! \nIf it shows that the app do not respond it's normal, just wait. \nIn case it takes too long you can still check the logs on the apify website ")
        self.Warning_label.pack(pady=20)

        self.open_log_button = ctk.CTkButton(self.app, text="Open Log Window", command=self.open_log_window)
        self.open_log_button.pack(pady=20)

    def open_log_window(self):
        if self.logging_window is None:
            self.logging_window = LoggingWindow(ctk.CTk())
            self.handler = TextHandler(self.logging_window.text_area)
            self.logger.addHandler(self.handler)
            self.logging_window.root.mainloop()

    def run_first_actor(self):
        try:
            direct_urls = ["https://www.instagram.com/" + url for url in
                           list(filter(None, self.direct_urls_entry.get().split(",")))]
            post_results_limit = self.post_results_limit_entry.get()
            post_search_type = "hashtag"
            post_search_limit = "1"
            add_parent_data = bool(self.add_parent_data_var.get())

            if post_results_limit and post_search_limit:
                post_results_limit = int(post_results_limit)
                post_search_limit = int(post_search_limit)
            else:
                raise ValueError("Results Limit and Search Limit must be provided")

            run_input = {
                "directUrls": direct_urls,
                "resultsType": "posts",
                "resultsLimit": post_results_limit,
                "searchType": post_search_type,
                "searchLimit": post_search_limit,
                "addParentData": add_parent_data,
            }

            run = self.client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
            results = [item for item in self.client.dataset(run["defaultDatasetId"]).iterate_items()]

            # Save results to CSV
            csv_filename = f"temp_instagram_post.csv"
            save_to_csv(results, csv_filename, True)
            self.urls = list(read_csv(csv_filename)["url"])

            # Log the obtained URLs
            self.logger.info(f"URLs obtained: {self.urls}")

        except Exception as e:
            self.logger.error(f"An error occurred while running the first actor: {e}")
            self.urls = []  # Clear URLs on error

    def run_second_actor(self):
        try:
            if not self.urls:
                self.logger.error(f"URLs is empty: {self.urls}")
                raise RuntimeError("First actor must run successfully and provide URLs before running the second actor")

            comments_results_limit = self.comments_results_limit_entry.get()
            comment_search_type = "hashtag"
            comments_search_limit = "1"
            add_parent_data = bool(self.add_parent_data_var.get())
            save_as_json = self.save_as_json_var.get()
            save_as_csv = self.save_as_csv_var.get()

            if comments_results_limit and comments_search_limit:
                comments_results_limit = int(comments_results_limit)
                comments_search_limit = int(comments_search_limit)
            else:
                raise ValueError("Results Limit and Search Limit must be provided")

            run_input = {
                "directUrls": self.urls,
                "resultsType": "comments",
                "resultsLimit": comments_results_limit,
                "searchType": comment_search_type,
                "searchLimit": comments_search_limit,
                "addParentData": add_parent_data,
            }

            run = self.client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
            results = [item for item in self.client.dataset(run["defaultDatasetId"]).iterate_items()]

            if save_as_json:
                json_filename = f"output_instagram_comments_{self.str_timestamp}.json"
                save_to_json(results, json_filename, root_path="")
                self.logger.info(f"Comments saved as JSON to {json_filename}")

            if save_as_csv:
                csv_filename = f"output_instagram_comments_{self.str_timestamp}.csv"
                save_to_csv(results, csv_filename, root_path="")
                self.logger.info(f"Comments saved as CSV to {csv_filename}")

        except Exception as e:
            self.logger.error(f"An error occurred while running the second actor: {e}")

    def start(self):
        self.app.mainloop()


if __name__ == "__main__":
    api_token = shv.default_token
    client_app = Client1(api_token)
    client_app.start()
