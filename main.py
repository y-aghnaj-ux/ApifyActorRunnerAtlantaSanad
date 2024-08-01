import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from client1 import Client1
from client2 import Client2
from client3 import Client3
from Sentiment_Analysis import SentimentAnalysisApp
import shared_variables as shv
from logging_window import LoggingWindow  # Import LoggingWindow class





class MainApp:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("Apify Actor Runner")
        self.app.geometry("800x600")
        self.api_token = ""
        ctk.set_appearance_mode(shv.appearance)
        self.app.configure(bg=shv.background)
        self.init_ui()

    def init_ui(self):
        # Create a menu bar
        menu_bar = tk.Menu(self.app)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Change Theme", command=self.change_theme)
        file_menu.add_command(label="Change Appearance", command=self.change_appearance)
        #file_menu.add_command(label="Open Sentiment Analysis", command=open_sentiment_analysis)
        file_menu.add_command(label="Open Output Folder", command=self.open_output_folder)
        file_menu.add_command(label="Change Output Path", command=self.change_output_path)
        file_menu.add_command(label="Open Logging Window", command=self.open_logging_window)  # New menu item

        # Attach the menu bar to the main app window
        self.app.config(menu=menu_bar)

        # Create input fields and labels for API token
        self.api_token_label = ctk.CTkLabel(self.app, text="API Token (Optional):")
        self.api_token_label.pack(pady=10)
        self.api_token_entry = ctk.CTkEntry(self.app, placeholder_text=shv.default_token, width=250)
        self.api_token_entry.pack(padx=300, pady=10)
        ctk.CTkLabel(self.app, text="Output Type:").pack(pady=5)
        self.api_token_select = ctk.CTkComboBox(self.app, values=shv.default_token_list)
        self.api_token_select.pack(pady=5)

        # Create buttons to open client windows
        self.client1_button = ctk.CTkButton(self.app, text="Run Instagram Client", command=self.open_client1)
        self.client1_button.pack(pady=10)
        self.client2_button = ctk.CTkButton(self.app, text="Run Tiktok Client", command=self.open_client2)
        self.client2_button.pack(pady=10)
        self.client3_button = ctk.CTkButton(self.app, text="Run Facebook Client", command=self.open_client3)
        self.client3_button.pack(pady=10)
        self.client1_button = ctk.CTkButton(self.app, text="Run Sentiment Analysis", command=self.open_sentiment_analysis)
        self.client1_button.pack(pady=10)

    def change_theme(self):
        theme_selector = ThemeSelector(self)

    def change_appearance(self):
        appearance_selector = AppearanceSelector(self)

    def open_output_folder(self):
        output_folder_path = shv.output_folder_path
        import os
        os.startfile(output_folder_path)

    def change_output_path(self):
        shv.output_folder_path = filedialog.askdirectory()

    def open_client1(self):
        self.api_token = self.api_token_select.get()
        if self.api_token == "":
            self.api_token = shv.default_token
        client1_app = Client1(self.api_token)
        client1_app.start()

    def open_client2(self):
        self.api_token = self.api_token_select.get()
        client2_app = Client2(self.api_token)
        client2_app.start()

    def open_sentiment_analysis(self):
        sentiment_analysis_app = SentimentAnalysisApp()
        sentiment_analysis_app.run()
        print("Opening sentiment analysis window")
    def open_client3(self):
        Client3()

    def open_logging_window(self):
        logging_window = tk.Toplevel(self.app)  # Create a new top-level window
        LoggingWindow(logging_window)  # Pass the top-level window to LoggingWindow

    def start(self):
        self.app.mainloop()


class ThemeSelector:
    def __init__(self, parent):
        self.parent = parent
        self.popup = tk.Toplevel(parent.app)
        self.popup.title("Select Theme")
        self.popup.geometry("300x200")
        ctk.set_appearance_mode(shv.appearance)
        self.popup.configure(bg=shv.background)
        self.theme_label = ctk.CTkLabel(self.popup, text="Theme:")
        self.theme_label.pack(pady=10)

        self.theme_label_entry = ctk.CTkComboBox(self.popup, values=["Dark Red", "Yellow", "Dark Blue", "Blue", "Green", "Rainbow"])
        self.theme_label_entry.pack(pady=10)

        self.theme_apply_button = ctk.CTkButton(self.popup, text="Apply", command=self.apply_theme)
        self.theme_apply_button.pack(pady=10)

    def apply_theme(self):
        selected_theme = self.theme_label_entry.get()
        shv.ChangeTheme(selected_theme)
        ctk.set_default_color_theme(shv.theme)
        self.popup.destroy()
        self.parent.app.destroy()
        new_main_app = MainApp()
        new_main_app.start()


class AppearanceSelector:
    def __init__(self, parent):
        self.parent = parent
        self.popup = tk.Toplevel(parent.app)
        self.popup.title("Select Appearance")
        self.popup.geometry("300x200")
        ctk.set_appearance_mode(shv.appearance)
        self.popup.configure(bg=shv.background)
        self.appearance_label = ctk.CTkLabel(self.popup, text="Appearance:")
        self.appearance_label.pack(pady=10)

        self.appearance_label_entry = ctk.CTkComboBox(self.popup, values=["Light", "Dark", "System"])
        self.appearance_label_entry.pack(pady=10)

        self.appearance_apply_button = ctk.CTkButton(self.popup, text="Apply", command=self.apply_appearance)
        self.appearance_apply_button.pack(pady=10)

    def apply_appearance(self):
        selected_appearance = self.appearance_label_entry.get()
        shv.ChangeAppearance(selected_appearance)
        self.popup.destroy()
        self.parent.app.destroy()
        new_main_app = MainApp()
        new_main_app.start()


if __name__ == "__main__":
    main_app = MainApp()
    main_app.start()
