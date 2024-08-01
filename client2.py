import customtkinter as ctk
from apify_client import ApifyClient
import json
import csv
import datetime
import shared_variables as shv

timestamp = datetime.datetime.now()
str_timestamp = timestamp.strftime("%Y-%m-%d %H-%M-%S")


def save_to_json(data, filename="output_tiktok " + str_timestamp + ".json"):
    with open(shv.output_folder_path + filename, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def save_to_csv(data, filename="output_tiktok " + str_timestamp + ".csv"):
    if not data:
        return
    keys = data[0].keys()
    with open(shv.output_folder_path + filename, "w", newline='', encoding='utf-8') as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


class Client2:
    def __init__(self, api_token):
        self.api_token = api_token

        self.init_ui()

    def init_ui(self):
        self.app = ctk.CTk()
        self.app.title("Tiktok Client")
        self.app.geometry("600x600")
        ctk.set_appearance_mode(shv.appearance)
        ctk.set_default_color_theme(shv.theme)
        self.label = ctk.CTkLabel(self.app, text="Running Tiktok Client")
        self.label.pack(pady=20)

        self.profile_label = ctk.CTkLabel(self.app, text="Profiles (comma separated):")
        self.profile_label.pack(pady=10)
        self.profile_entry = ctk.CTkEntry(self.app, placeholder_text="apifyoffice", width=150)
        self.profile_entry.pack(pady=10)

        self.results_per_page_label = ctk.CTkLabel(self.app, text="Results per Page:")
        self.results_per_page_label.pack(pady=10)
        self.results_per_page_entry = ctk.CTkEntry(self.app, placeholder_text="100", width=150)
        self.results_per_page_entry.pack(pady=10)

        self.download_videos_var = ctk.BooleanVar(value=False)
        self.download_videos_check = ctk.CTkCheckBox(self.app, text="Download Videos",
                                                     variable=self.download_videos_var)
        self.download_videos_check.pack(pady=10)

        self.download_covers_var = ctk.BooleanVar(value=False)
        self.download_covers_check = ctk.CTkCheckBox(self.app, text="Download Covers",
                                                     variable=self.download_covers_var)
        self.download_covers_check.pack(pady=10)

        self.download_subtitles_var = ctk.BooleanVar(value=False)
        self.download_subtitles_check = ctk.CTkCheckBox(self.app, text="Download Subtitles",
                                                        variable=self.download_subtitles_var)
        self.download_subtitles_check.pack(pady=10)

        self.download_slideshow_images_var = ctk.BooleanVar(value=False)
        self.download_slideshow_images_check = ctk.CTkCheckBox(self.app, text="Download Slideshow Images",
                                                               variable=self.download_slideshow_images_var)
        self.download_slideshow_images_check.pack(pady=10)

        self.save_as_json_var = ctk.BooleanVar()
        self.save_as_json_checkbox = ctk.CTkCheckBox(
            self.app, text="Save as JSON", variable=self.save_as_json_var)
        self.save_as_json_checkbox.pack(pady=5)

        self.save_as_csv_var = ctk.BooleanVar()
        self.save_as_csv_checkbox = ctk.CTkCheckBox(
            self.app, text="Save as CSV", variable=self.save_as_csv_var)
        self.save_as_csv_checkbox.pack(pady=5)

        self.run_button = ctk.CTkButton(self.app, text="Run Tiktok Actor", command=self.run_actor)
        self.run_button.pack(pady=10)

        self.Warning_label = ctk.CTkLabel(self.app,
                                          text="DO NOT INTERRUPT!!!!! \nIf it shows that the app do not respond it's "
                                               "normal, just wait. \nIn case it takes too long you can still check "
                                               "the logs on the apify website ")
        self.run_button.pack(pady=20)

    def run_actor(self):
        self.client = ApifyClient(self.api_token)
        profiles = self.profile_entry.get().split(',')
        results_per_page = int(self.results_per_page_entry.get())
        should_download_videos = self.download_videos_var.get()
        should_download_covers = self.download_covers_var.get()
        should_download_subtitles = self.download_subtitles_var.get()
        should_download_slideshow_images = self.download_slideshow_images_var.get()

        run_input = {
            "profiles": profiles,
            "resultsPerPage": results_per_page,
            "shouldDownloadVideos": should_download_videos,
            "shouldDownloadCovers": should_download_covers,
            "shouldDownloadSubtitles": should_download_subtitles,
            "shouldDownloadSlideshowImages": should_download_slideshow_images,
        }

        run = self.client.actor("0FXVyOXXEmdGcV88a").call(run_input=run_input)
        results = []
        results = [item for item in self.client.dataset(run["defaultDatasetId"]).iterate_items()]

        if self.save_as_json_var.get():
            save_to_json(results)
        if self.save_as_csv_var.get():
            save_to_csv(results)

    def start(self):
        self.app.mainloop()


if __name__ == "__main__":
    api_token = shv.default_token
    client2_app = Client2(api_token)
    client2_app.start()
