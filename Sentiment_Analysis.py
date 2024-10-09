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

# Initialisation de l'analyseur de sentiments VADER
analyzer = Vader.SentimentIntensityAnalyzer()

# Fonction pour traduire un texte en anglais avant analyse
def translate_text(text):
    try:
        # Détection automatique de la langue du texte
        from_lang = detect(text)
        # Initialisation du traducteur avec la langue détectée et traduction en anglais
        translator = Translator(to_lang='en', from_lang=from_lang)
        translated = translator.translate(text)
        # Retourne le texte traduit ou le texte d'origine si aucune traduction
        return translated.text if translated and hasattr(translated, 'text') else text
    except Exception as e:
        # Log de l'erreur de traduction
        logging.error(f"Error translating text: {text}. Error: {e}")
        return text

# Fonction pour analyser une liste de textes (contenu)
def analyse_text(content):
    detailed_results = []

    # Pour chaque ligne de texte, on traduit et analyse les sentiments
    for line in content:
        trans_line = translate_text(line)  # Traduction
        if trans_line:
            # Analyse des sentiments du texte traduit
            score = analyzer.polarity_scores(trans_line)
            detailed_results.append({
                'text': line,
                'translated_text': trans_line,
                'negative': score.get("neg"),
                'neutral': score.get("neu"),
                'positive': score.get("pos"),
                'compound': score.get("compound")
            })
            time.sleep(0.4)  # Pause pour éviter les limites de taux d'API

    # Calcul des moyennes des scores de sentiments
    avg_neg = average_table([result['negative'] for result in detailed_results])
    avg_neu = average_table([result['neutral'] for result in detailed_results])
    avg_pos = average_table([result['positive'] for result in detailed_results])
    avg_com = average_table([result['compound'] for result in detailed_results])

    # Génération d'un résumé du sentiment général
    summary_text = (f"Negative: {avg_neg:.3f}\n"
                    f"Neutral: {avg_neu:.3f}\n"
                    f"Positive: {avg_pos:.3f}\n"
                    f"Compound: {avg_com:.3f}\n"
                    f"Text has a {'negative' if avg_com < 0 else 'positive' if avg_com > 0 else 'neutral'} connotation")

    # Retourne les résultats détaillés et le résumé
    return detailed_results, summary_text, avg_neg, avg_neu, avg_pos, avg_com

# Fonction pour calculer la moyenne d'une liste de valeurs
def average_table(table):
    return sum(table) / len(table) if table else 0

# Classe principale de l'application d'analyse de sentiment
class SentimentAnalysisApp:
    def __init__(self):
        # Initialisation de la fenêtre principale avec customtkinter
        self.root = ctk.CTk()
        self.root.title("Sentiment Analysis")
        self.root.geometry("800x1000")
        ctk.set_appearance_mode(shv.appearance)  # Applique l'apparence choisie
        ctk.set_default_color_theme(shv.theme)  # Applique le thème de couleur choisi
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # Niveau de log à DEBUG

        # Initialisation de la fenêtre de logs (non visible au départ)
        self.logging_window = None

        # Variables de sélection du fichier
        self.file_type = tk.StringVar(value="txt")
        self.file_path = ""
        self.input_columns = []
        self.output_columns = []

        # Initialisation du cadre principal et création des widgets
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        self.create_widgets()

    # Fonction pour créer les widgets de l'interface
    def create_widgets(self):
        ctk.CTkLabel(self.main_frame, text="File Type:").pack(pady=5)
        self.file_type_combo = ctk.CTkComboBox(self.main_frame, values=["csv", "json"], variable=self.file_type)
        self.file_type_combo.pack(pady=5)

        # Cadre pour le chemin du fichier
        path_frame = ctk.CTkFrame(self.main_frame)
        path_frame.pack(pady=5, fill=tk.X)

        ctk.CTkLabel(path_frame, text="File Path:").pack(pady=5, padx=(10, 0))
        self.file_path_entry = ctk.CTkEntry(path_frame)
        self.file_path_entry.pack(pady=20, expand=False)

        # Bouton pour parcourir et sélectionner le fichier
        ctk.CTkButton(path_frame, text="Browse", command=self.browse_file).pack(pady=10, padx=10)

        # Cadres pour la sélection des colonnes d'entrée et de sortie
        self.include_columns_frame = ctk.CTkFrame(self.main_frame)
        self.include_columns_frame.pack(pady=5, fill=tk.X)

        self.output_columns_frame = ctk.CTkFrame(self.main_frame)
        self.output_columns_frame.pack(pady=5, fill=tk.X)

        ctk.CTkLabel(self.main_frame, text="Output Type:").pack(pady=5)
        self.output_type_combo = ctk.CTkComboBox(self.main_frame, values=["csv", "json"])
        self.output_type_combo.pack(pady=5)

        # Bouton pour démarrer l'analyse
        ctk.CTkButton(self.main_frame, text="Analyze", command=self.analyze).pack(pady=10)

        # Label pour afficher les résultats
        self.result_label = ctk.CTkLabel(self.main_frame, text="")
        self.result_label.pack(pady=5)

        # Bouton pour ouvrir la fenêtre de log
        self.open_log_button = ctk.CTkButton(self.main_frame, text="Open Log Window", command=self.open_log_window)
        self.open_log_button.pack(pady=20)

    # Fonction pour ouvrir la fenêtre de log
    def open_log_window(self):
        if self.logging_window is None:
            # Création et affichage de la fenêtre de log
            self.logging_window = LoggingWindow(ctk.CTk())
            self.handler = TextHandler(self.logging_window.text_area)
            self.logger.addHandler(self.handler)
            self.logging_window.root.mainloop()

    # Fonction pour parcourir et sélectionner un fichier
    def browse_file(self):
        file_type = self.file_type_combo.get()
        filetypes = {
            'csv': [("CSV files", "*.csv")],
            'json': [("JSON files", "*.json")]
        }
        # Ouvre une fenêtre de dialogue pour sélectionner un fichier
        path = filedialog.askopenfilename(filetypes=filetypes[file_type])
        if path:
            # Mise à jour du chemin sélectionné dans l'interface
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, path)
            self.file_path = path

            # Lecture du fichier et récupération des colonnes disponibles
            if file_type in ['csv', 'json']:
                df = pd.read_csv(path) if file_type == 'csv' else pd.read_json(path)
                self.input_columns = df.columns.tolist()
                self.display_include_columns()

    # Affiche les colonnes à inclure dans l'analyse
    def display_include_columns(self):
        self._clear_frame(self.include_columns_frame)
        self._clear_frame(self.output_columns_frame)

        # Affichage des colonnes d'entrée sous forme de cases à cocher
        ctk.CTkLabel(self.include_columns_frame, text="Input Columns select:").pack(pady=5)
        self.column_vars = {col: tk.BooleanVar() for col in self.input_columns}
        for col, var in self.column_vars.items():
            ctk.CTkCheckBox(self.include_columns_frame, text=col, variable=var).pack(anchor='w')

        # Affichage des colonnes de sortie sous forme de cases à cocher
        ctk.CTkLabel(self.output_columns_frame, text="Output Columns select:").pack(pady=5)
        self.output_vars = {col: tk.BooleanVar() for col in self.input_columns}
        for col, var in self.output_vars.items():
            ctk.CTkCheckBox(self.output_columns_frame, text=col, variable=var).pack(anchor='w')

    # Efface tous les widgets dans un cadre donné
    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    # Fonction principale pour effectuer l'analyse de sentiment
    def analyze(self):
        path = self.file_path_entry.get()
        file_type = self.file_type_combo.get()
        output_type = self.output_type_combo.get()

        # Vérifie si un fichier a été sélectionné
        if not path:
            messagebox.showerror("Error", "Please select a file")
            return

        try:
            # Lecture du fichier en fonction du type sélectionné
            df = pd.read_csv(path, encoding="utf-8") if file_type == 'csv' else pd.read_json(path, encoding="utf-8")
            selected_input_columns = [col for col, var in self.column_vars.items() if var.get()]
            selected_output_columns = [col for col, var in self.output_vars.items() if var.get()]

            # Extraction et analyse des données
            filtered_content = df[selected_input_columns].astype(str).values.flatten().tolist() if selected_input_columns else df.astype(str).values.flatten().tolist()
            detailed_results, summary_text, avg_neg, avg_neu, avg_pos, avg_com = analyse_text(filtered_content)

            # Mise à jour des résultats dans les colonnes de sortie
            for col in selected_input_columns:
                df["Score Sentiment"] = [result['compound'] for result in detailed_results]
                selected_output_columns.extend(["Score Sentiment"])

            # Enregistrement du fichier avec les résultats de l'analyse
            save_path = filedialog.asksaveasfilename(defaultextension=f".{output_type}",
                                                     filetypes=[(f"{output_type.upper()} files", f"*.{output_type}")])
            if save_path:
                if output_type == 'csv':
                    df.to_csv(save_path, columns=selected_output_columns, index=False, encoding='utf-8')
                elif output_type == 'json':
                    df.to_json(save_path, orient='records', force_ascii=False)

            # Affichage du résumé des résultats dans l'interface
            self.result_label.configure(text=summary_text)

        except Exception as e:
            # Log de l'erreur et affichage d'un message d'erreur
            self.logger.error(f"Error during analysis: {e}")
            messagebox.showerror("Error", str(e))

    # Démarrage de l'application
    def run(self):
        self.root.mainloop()

# Lancement de l'application
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = SentimentAnalysisApp()
    app.run()
