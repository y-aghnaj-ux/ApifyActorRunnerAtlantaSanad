import time
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import vaderSentiment.vaderSentiment as Vader
from translate import Translator
from langdetect import detect
import shared_variables as shv
import logging
from logging_window import LoggingWindow, TextHandler

analyzer = Vader.SentimentIntensityAnalyzer()

def translate_text(text):
    try:
        from_lang = detect(text)
        translator = Translator(to_lang='en', from_lang=from_lang)
        translated = translator.translate(text)
        return translated.text if translated and hasattr(translated, 'text') else text
    except Exception as e:
        logging.error(f"Error translating text: {text}. Error: {e}")
        return text

def analyse_text(content):
    detailed_results = []

    for line in content:
        trans_line = translate_text(line)
        if trans_line:
            score = analyzer.polarity_scores(trans_line)
            detailed_results.append({
                'text': line,
                'translated_text': trans_line,
                'negative': score.get("neg"),
                'neutral': score.get("neu"),
                'positive': score.get("pos"),
                'compound': score.get("compound")
            })
            time.sleep(0.4)  # Delay to avoid hitting API rate limits

    avg_neg = average_table([result['negative'] for result in detailed_results])
    avg_neu = average_table([result['neutral'] for result in detailed_results])
    avg_pos = average_table([result['positive'] for result in detailed_results])
    avg_com = average_table([result['compound'] for result in detailed_results])

    summary_text = (f"Negative: {avg_neg:.3f}\n"
                    f"Neutral: {avg_neu:.3f}\n"
                    f"Positive: {avg_pos:.3f}\n"
                    f"Compound: {avg_com:.3f}\n"
                    f"Text has a {'negative' if avg_com < 0 else 'positive' if avg_com > 0 else 'neutral'} connotation")

    return detailed_results, summary_text, avg_neg, avg_neu, avg_pos, avg_com

def average_table(table):
    return sum(table) / len(table) if table else 0

class SentimentAnalysisApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Sentiment Analysis")
        self.root.geometry("800x1000")
        ctk.set_appearance_mode(shv.appearance)
        ctk.set_default_color_theme(shv.theme)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Initialize the logging window but don't show it yet
        self.logging_window = None

        self.file_type = tk.StringVar(value="txt")
        self.file_path = ""
        self.input_columns = []
        self.output_columns = []

        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self.main_frame, text="File Type:").pack(pady=5)
        self.file_type_combo = ctk.CTkComboBox(self.main_frame, values=["csv", "json"], variable=self.file_type)
        self.file_type_combo.pack(pady=5)

        path_frame = ctk.CTkFrame(self.main_frame)
        path_frame.pack(pady=5, fill=tk.X)

        ctk.CTkLabel(path_frame, text="File Path:").pack(pady=5, padx=(10, 0))
        self.file_path_entry = ctk.CTkEntry(path_frame)
        self.file_path_entry.pack(pady=20, expand=False)

        ctk.CTkButton(path_frame, text="Browse", command=self.browse_file).pack(pady=10, padx=10)

        self.include_columns_frame = ctk.CTkFrame(self.main_frame)
        self.include_columns_frame.pack(pady=5, fill=tk.X)

        self.output_columns_frame = ctk.CTkFrame(self.main_frame)
        self.output_columns_frame.pack(pady=5, fill=tk.X)

        ctk.CTkLabel(self.main_frame, text="Output Type:").pack(pady=5)
        self.output_type_combo = ctk.CTkComboBox(self.main_frame, values=["csv", "json"])
        self.output_type_combo.pack(pady=5)

        ctk.CTkButton(self.main_frame, text="Analyze", command=self.analyze).pack(pady=10)

        self.result_label = ctk.CTkLabel(self.main_frame, text="")
        self.result_label.pack(pady=5)

        self.open_log_button = ctk.CTkButton(self.main_frame, text="Open Log Window", command=self.open_log_window)
        self.open_log_button.pack(pady=20)

    def open_log_window(self):
        if self.logging_window is None:
            self.logging_window = LoggingWindow(ctk.CTk())
            self.handler = TextHandler(self.logging_window.text_area)
            self.logger.addHandler(self.handler)
            self.logging_window.root.mainloop()

    def browse_file(self):
        file_type = self.file_type_combo.get()
        filetypes = {
            'csv': [("CSV files", "*.csv")],
            'json': [("JSON files", "*.json")]
        }
        path = filedialog.askopenfilename(filetypes=filetypes[file_type])
        if path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, path)
            self.file_path = path

            if file_type in ['csv', 'json']:
                df = pd.read_csv(path) if file_type == 'csv' else pd.read_json(path)
                self.input_columns = df.columns.tolist()
                self.display_include_columns()

    def display_include_columns(self):
        self._clear_frame(self.include_columns_frame)
        self._clear_frame(self.output_columns_frame)

        ctk.CTkLabel(self.include_columns_frame, text="Input Columns select:").pack(pady=5)
        self.column_vars = {col: tk.BooleanVar() for col in self.input_columns}
        for col, var in self.column_vars.items():
            ctk.CTkCheckBox(self.include_columns_frame, text=col, variable=var).pack(anchor='w')

        ctk.CTkLabel(self.output_columns_frame, text="Output Columns select:").pack(pady=5)
        self.output_vars = {col: tk.BooleanVar() for col in self.input_columns}
        for col, var in self.output_vars.items():
            ctk.CTkCheckBox(self.output_columns_frame, text=col, variable=var).pack(anchor='w')

    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def analyze(self):
        path = self.file_path_entry.get()
        file_type = self.file_type_combo.get()
        output_type = self.output_type_combo.get()

        if not path:
            messagebox.showerror("Error", "Please select a file")
            return

        try:
            df = pd.read_csv(path, encoding="utf-8") if file_type == 'csv' else pd.read_json(path, encoding="utf-8")
            selected_input_columns = [col for col, var in self.column_vars.items() if var.get()]
            selected_output_columns = [col for col, var in self.output_vars.items() if var.get()]

            filtered_content = df[selected_input_columns].astype(str).values.flatten().tolist() if selected_input_columns else df.astype(str).values.flatten().tolist()
            detailed_results, summary_text, avg_neg, avg_neu, avg_pos, avg_com = analyse_text(filtered_content)

            for col in selected_input_columns:
                df[f'{col}_Negative'] = [result['negative'] for result in detailed_results]
                df[f'{col}_Neutral'] = [result['neutral'] for result in detailed_results]
                df[f'{col}_Positive'] = [result['positive'] for result in detailed_results]
                df[f'{col}_Compound'] = [result['compound'] for result in detailed_results]

                selected_output_columns.extend([f'{col}_Negative', f'{col}_Neutral', f'{col}_Positive', f'{col}_Compound'])

            save_path = filedialog.asksaveasfilename(defaultextension=f".{output_type}",
                                                     filetypes=[(f"{output_type.upper()} files", f"*.{output_type}")])
            if save_path:
                if output_type == 'csv':
                    df.to_csv(save_path, columns=selected_output_columns, index=False, encoding='utf-8')
                elif output_type == 'json':
                    df.to_json(save_path, orient='records', force_ascii=False)

            self.result_label.configure(text=summary_text)

        except Exception as e:
            self.logger.error(f"Error during analysis: {e}")
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = SentimentAnalysisApp()
    app.run()
