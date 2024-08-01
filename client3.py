import customtkinter as ctk
from apify_client import ApifyClient
import json
import csv
import datetime
import shared_variables as shv

class Client3:
    def __init__(self, api_token):
        self.client = ApifyClient(api_token)
        self.init_ui()

    def init_ui(self):
        self.app = ctk.CTk()
        self.app.title("Facebook Client")
        self.app.geometry("600x800")
        ctk.set_appearance_mode(shv.appearance)
        ctk.set_default_color_theme(shv.theme)
        self.direct_urls_label = ctk.CTkLabel(self.app, text="Direct URLs (comma-separated):")
        self.direct_urls_label.pack(pady=5)
        self.direct_urls_entry =  ctk.CTkEntry(self.app, placeholder_text="e.g. AtlantaSanad")
        self.direct_urls_entry.pack(pady=5)

        self.results_limit_label = ctk.CTkLabel(self.app, text="Results Limit:")
        self.results_limit_label.pack(pady=5)
        self.results_limit_entry = ctk.CTkEntry(self.app, placeholder_text="200")
        self.results_limit_entry.pack(pady=5)

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

        self.run_button = ctk.CTkButton(self.app, text="Run Actor", command=self.run_actor)
        self.run_button.pack(pady=20)
        self.Warning_label = ctk.CTkLabel(self.app, text="DO NOT INTERRUPT!!!!! \nIf it shows that the app do not " +
                                                         "respond it's normal, just wait. \nIn case it takes too long " +
                                                         "you can still check the logs on the apify website ")
        self.run_button.pack(pady=20)

    timestamp = datetime.datetime.now()
    str_timestamp = timestamp.strftime("%Y-%m-%d %H-%M-%S")
    def save_to_json(self, data, filename="output_facebook" + str_timestamp +".json"):
        with open(shv.output_folder_path+filename, "w", encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    def save_to_csv(self, data, filename="output_facebook " + str_timestamp + ".csv"):
        if not data:
            return
        keys = data[0].keys()
        with open(shv.output_folder_path+filename, "w", newline='', encoding='utf-8') as csv_file:
            dict_writer = csv.DictWriter(csv_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)

    def run_actor(self):
        direct_urls = ["https://www.facebook.com/" + url for url in list(self.direct_urls_entry.get().split(","))]
        results_limit = int(self.results_limit_entry.get())
        run_input = {
            "startUrls": direct_urls,
            "resultsLimit": results_limit,
        }

        run = self.client.actor("KoJrdxJCTtpon81KY").call(run_input=run_input)
        results = [item for item in self.client.dataset(run["defaultDatasetId"]).iterate_items()]

        if self.save_as_json_var.get():
            self.save_to_json(results)
        if self.save_as_csv_var.get():
            self.save_to_csv(results)

    def start(self):
        self.app.mainloop()


if __name__ == "__main__":
    api_token = shv.default_token
    client_app = Client3(api_token)
    client_app.start()
