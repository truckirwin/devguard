# ascend.py
# Forge Ascend v4.1
# Updated by Tom Stern, 16 DEC 2024
#
#   based on Ascend 1 -- first version January 22 2024 -- by Tom Stern

import os
import sys
import json
import webbrowser
import pygame
import tempfile
import shutil
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox, 
    QFrame, QRadioButton, QGridLayout, QInputDialog, QDialogButtonBox, QFormLayout, QFileDialog, 
    QDialog, QMessageBox, QLineEdit, QStyle
)
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, QUrl



from ascend_ed import EDitorActions
from ascend_ed import FileMerge
from ascend_ai import AIModelInteraction
from ascend_img import ImageGen
from ascend_cd import CurDev


import ascendAWSClientManager

## -- Custom Language Dialog
#
#
#
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QMessageBox
)
import sys

class LanguageSelector(QDialog):
    def __init__(self, parent=None, input_language=None, output_language=None, spoken_language=None):
        super().__init__(parent)
        self.setWindowTitle("Select Languages")

        # Language dictionary
        self.languages = {
            "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar", "Armenian": "hy",
            "Azerbaijani": "az", "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
            "Chinese (Simplified)": "zh", "Chinese (Traditional)": "zh-TW", "Croatian": "hr",
            "Czech": "cs", "Danish": "da", "Dari": "fa-AF", "Dutch": "nl", "English": "en",
            "Estonian": "et", "Farsi (Persian)": "fa", "Filipino, Tagalog": "tl", "Finnish": "fi",
            "French": "fr", "French (Canada)": "fr-CA", "Georgian": "ka", "German": "de",
            "Greek": "el", "Gujarati": "gu", "Haitian Creole": "ht", "Hausa": "ha", "Hebrew": "he",
            "Hindi": "hi", "Hungarian": "hu", "Icelandic": "is", "Indonesian": "id", "Irish": "ga",
            "Italian": "it", "Japanese": "ja", "Kannada": "kn", "Kazakh": "kk", "Korean": "ko",
            "Latvian": "lv", "Lithuanian": "lt", "Macedonian": "mk", "Malay": "ms", "Malayalam": "ml",
            "Maltese": "mt", "Marathi": "mr", "Mongolian": "mn", "Norwegian (Bokmål)": "no",
            "Pashto": "ps", "Polish": "pl", "Portuguese (Brazil)": "pt", "Portuguese (Portugal)": "pt-PT",
            "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Serbian": "sr", "Sinhala": "si",
            "Slovak": "sk", "Slovenian": "sl", "Somali": "so", "Spanish": "es", "Spanish (Mexico)": "es-MX",
            "Swahili": "sw", "Swedish": "sv", "Tamil": "ta", "Telugu": "te", "Thai": "th", "Turkish": "tr",
            "Ukrainian": "uk", "Urdu": "ur", "Uzbek": "uz", "Vietnamese": "vi", "Welsh": "cy"
        }

        self.spoken_languages = {
            "Arabic": "arb", 
            "Arabic (Gulf)": "ar-AE", 
            "Catalan": "ca-ES", 
            "Chinese (Cantonese)": "yue-CN", 
            "Chinese (Mandarin)": "cmn-CN", 
            "Czech": "cs-CZ", 
            "Danish": "da-DK", 
            "Dutch (Belgian)": "nl-BE", 
            "Dutch": "nl-NL", 
            "English (Australian)": "en-AU", 
            "English (British)": "en-GB", 
            "English (Indian)": "en-IN", 
            "English (New Zealand)": "en-NZ", 
            "English (South African)": "en-ZA", 
            "English (US)": "en-US", 
            "English (Welsh)": "en-GB-WLS", 
            "Finnish": "fi-FI", 
            "French": "fr-FR", 
            "French (Belgian)": "fr-BE", 
            "French (Canadian)": "fr-CA", 
            "Hindi": "hi-IN", 
            "German": "de-DE", 
            "German (Austrian)": "de-AT", 
            "German (Swiss standard)": "de-CH", 
            "Icelandic": "is-IS", 
            "Italian": "it-IT", 
            "Japanese": "ja-JP", 
            "Korean": "ko-KR", 
            "Norwegian": "nb-NO", 
            "Polish": "pl-PL", 
            "Portuguese (Brazilian)": "pt-BR", 
            "Portuguese (European)": "pt-PT", 
            "Romanian": "ro-RO", 
            "Russian": "ru-RU", 
            "Spanish (Spain)": "es-ES", 
            "Spanish (Mexican)": "es-MX", 
            "Spanish (US)": "es-US", 
            "Swedish": "sv-SE", 
            "Turkish": "tr-TR", 
            "Welsh": "cy-GB"
        }

        self.voice_options = {
            "arb": {"voices": ["Zeina"]},
            "ar-AE": {"voices": ["Hala", "Zayd"]},
            "nl-BE": {"voices": ["Lisa"]},
            "ca-ES": {"voices": ["Arlet"]},
            "cs-CZ": {"voices": ["Jitka"]},
            "yue-CN": {"voices": ["Hiujin"]},
            "cmn-CN": {"voices": ["Zhiyu"]},
            "da-DK": {"voices": ["Naja", "Mads", "Sofie"]},
            "nl-NL": {"voices": ["Laura", "Lotte", "Ruben"]},
            "en-AU": {"voices": ["Nicole", "Olivia", "Russell"]},
            "en-GB": {"voices": ["Amy", "Emma", "Brian", "Arthur"]},
            "en-IN": {"voices": ["Aditi", "Raveena", "Kajal"]},
            "en-IE": {"voices": ["Niamh"]},
            "en-NZ": {"voices": ["Aria"]},
            "en-ZA": {"voices": ["Ayanda"]},
            "en-US": {"voices": ["Danielle", "Gregory", "Ivy", "Joanna"]},
            "en-GB-WLS": {"voices": ["Geraint"]},
            "fi-FI": {"voices": ["Suvi"]},
            "fr-FR": {"voices": ["Celine", "Lea", "Mathieu", "Remi"]},
            "fr-BE": {"voices": ["Isabelle"]},
            "fr-CA": {"voices": ["Chantal", "Gabrielle", "Liam"]},
            "de-DE": {"voices": ["Marlene", "Vicki", "Hans", "Daniel"]},
            "de-AT": {"voices": ["Hannah"]},
            "de-CH": {"voices": ["Sabrina"]},
            "hi-IN": {"voices": ["Aditi", "Kajal"]},
            "is-IS": {"voices": ["Dora", "Karl"]},
            "it-IT": {"voices": ["Carla", "Bianca", "Giorgio", "Adriano"]},
            "ja-JP": {"voices": ["Mizuki", "Takumi", "Kazuha", "Tomoko"]},
            "ko-KR": {"voices": ["Seoyeon"]},
            "nb-NO": {"voices": ["Liv", "Ida"]},
            "pl-PL": {"voices": ["Ewa", "Maja", "Jacek", "Jan", "Ola"]},
            "pt-BR": {"voices": ["Camila", "Vitória", "Ricardo", "Thiago"]},
            "pt-PT": {"voices": ["Ines", "Cristiano"]},
            "ro-RO": {"voices": ["Carmen"]},
            "ru-RU": {"voices": ["Tatyana", "Maxim"]},
            "es-ES": {"voices": ["Conchita", "Lucia", "Alba", "Enrique", "Sergio", "Raul"]},
            "es-MX": {"voices": ["Mia", "Andres"]},
            "es-US": {"voices": ["Lupe", "Penélope", "Miguel", "Pedro"]},
            "sv-SE": {"voices": ["Astrid", "Elin"]},
            "tr-TR": {"voices": ["Filiz", "Burcu"]},
            "cy-GB": {"voices": ["Gwyneth"]}
        }

        # Layout
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Input Language:"))
        self.input_language_combo = QComboBox()
        self.input_language_combo.addItems(self.languages.keys())
        if input_language:
            language_name = next((name for name, code in self.languages.items() if code == input_language), None)
            if language_name:
                self.input_language_combo.setCurrentText(language_name)
        layout.addWidget(self.input_language_combo)

        layout.addWidget(QLabel("Select Output Language:"))
        self.output_language_combo = QComboBox()
        self.output_language_combo.addItems(self.languages.keys())
        if output_language:
            language_name = next((name for name, code in self.languages.items() if code == output_language), None)
            if language_name:
                self.output_language_combo.setCurrentText(language_name)
        layout.addWidget(self.output_language_combo)

        layout.addWidget(QLabel("Select Spoken Language:"))
        self.spoken_language_combo = QComboBox()
        self.spoken_language_combo.addItems(self.spoken_languages.keys())
        if spoken_language:
            language_name = next((name for name, code in self.spoken_languages.items() if code == spoken_language), None)
            if language_name:
                self.spoken_language_combo.setCurrentText(language_name)
        layout.addWidget(self.spoken_language_combo)

        # Voice Selector Combo Box
        self.voice_selector_combo = QComboBox()
        layout.addWidget(self.voice_selector_combo)

        self.input_language_combo.currentTextChanged.connect(self.update_voices)
        self.spoken_language_combo.currentTextChanged.connect(self.update_voices)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.update_voices()

    def update_voices(self):
        # Update the voice selector based on the selected language and spoken language
        selected_spoken_language = self.spoken_language_combo.currentText()
        selected_language = self.input_language_combo.currentText()

        # Determine voice options based on selected spoken language or default to input language
        spoken_language_code = self.spoken_languages.get(selected_spoken_language, None)
        language_code = self.languages.get(selected_language, None)

        if spoken_language_code:
            available_voices = self.voice_options.get(spoken_language_code, {}).get("voices", [])
        elif language_code:
            available_voices = self.voice_options.get(language_code, {}).get("voices", [])
        else:
            available_voices = []

        self.voice_selector_combo.clear()
        self.voice_selector_combo.addItems(available_voices)

    def accept(self):
        input_lang = self.languages.get(self.input_language_combo.currentText())
        output_lang = self.languages.get(self.output_language_combo.currentText())
        spoken_lang = self.spoken_languages.get(self.spoken_language_combo.currentText())
        selected_voice = self.voice_selector_combo.currentText()

        # Return selected language details
        super().accept()
        return input_lang, output_lang, spoken_lang, selected_voice




# -- Custom Settings Dialog
#
# 
class SettingsForm(QDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings  # Dictionary holding model settings
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Model Settings")
        layout = QVBoxLayout(self)

        grid_layout = QGridLayout()
        row, col = 0, 0
        self.setting_widgets = {}
        for model_name, settings in self.current_settings.items():
            group_box = QGroupBox(model_name)  # Use QGroupBox to display model names
            form_layout = QFormLayout(group_box)
            self.setting_widgets[model_name] = {}
            for setting, value in settings.items():
                setting_edit = QLineEdit(str(value))
                form_layout.addRow(QLabel(setting), setting_edit)
                self.setting_widgets[model_name][setting] = setting_edit
            
            grid_layout.addWidget(group_box, row, col)  # Add group box to the grid
            col += 1
            if col >= 6:  # Move to the next row after every 5th model
                row += 1
                col = 0
        
        layout.addLayout(grid_layout)

        # Open and Save buttons
        open_button = QPushButton('Open Settings')
        open_button.setToolTip("Load model settings from JSON file.")
        open_button.clicked.connect(self.open_settings)
        save_button = QPushButton('Save Settings')
        save_button.setToolTip("Save model settings to JSON file.")
        save_button.clicked.connect(self.save_settings)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(open_button)
        buttons_layout.addWidget(save_button)
        
        ok_button = QPushButton('OK')
        ok_button.setToolTip("Store and use any changes to model settings.")
        ok_button.clicked.connect(self.accept_and_save)
        cancel_button = QPushButton('Cancel')
        cancel_button.setToolTip("Close panel without changing settings.")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)

    def accept_and_save(self):
        # Update self.current_settings with the values from the dialog
        for model_name, settings in self.setting_widgets.items():
            for setting, widget in settings.items():
                self.current_settings[model_name][setting] = widget.text()
        self.accept()

    # Get Settings
    def getSettings(self):
        return self.current_settings

    # Open Settings
    def open_settings(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Settings File", "", "JSON Files (*.json);;All Files (*)", options=options)

        if file_name:
            with open(file_name, 'r') as file:
                try:
                    settings = json.load(file)
                    # Update self.current_settings with the loaded settings
                    self.current_settings.update(settings)
                    # Update the dialog with the new settings
                    self.updateDialogWithSettings()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error loading settings: {str(e)}")

    def updateDialogWithSettings(self):
        # Update dialog elements with the new settings
        for model_name, settings in self.setting_widgets.items():
            for setting, widget in settings.items():
                if setting in self.current_settings[model_name]:
                    widget.setText(str(self.current_settings[model_name][setting]))

    # Save Settings
    def save_settings(self):

        # Update self.current_settings with the values from the dialog
        for model_name, settings in self.setting_widgets.items():
            for setting, widget in settings.items():
                self.current_settings[model_name][setting] = widget.text()

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings File", "", "JSON Files (*.json);;All Files (*)", options=options)

        if file_name:
            with open(file_name, 'w') as file:
                try:
                    # Save self.current_settings to a JSON file
                    json.dump(self.current_settings, file, indent=4)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")
        # Accept the dialog after saving settings
        self.accept()

# -- Custom Settings Dialog

# -- Custom Split Save Dialog
class SplitSaveDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Split and Save File")
        self.initUI()
        self.filename = ""
        self.marker = ""

    def initUI(self):
        layout = QVBoxLayout()

        # Filename input
        filename_label = QLabel("Split File Name:")
        self.filename_input = QLineEdit()
        layout.addWidget(filename_label)
        layout.addWidget(self.filename_input)

        # Split marker input with default value "|||"
        marker_label = QLabel("Split Marker:")
        self.marker_input = QLineEdit("|||")
        layout.addWidget(marker_label)
        layout.addWidget(self.marker_input)

        # Buttons
        button_layout = QHBoxLayout()
        continue_button = QPushButton("Continue")
        continue_button.setToolTip("Split the contents of Response editor and store in separate files.")
        cancel_button = QPushButton("Cancel")
        cancel_button.setToolTip("Close panel without saving split files.")
        button_layout.addWidget(continue_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons
        continue_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def getInputs(self):
        return self.filename_input.text(), self.marker_input.text()
# -- Custom Split Save Dialog

# -- Custom "About" Message
class CreatorInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About this program")
        self.init_ui()
        
    def init_ui(self):
        self.about = QTextEdit()
        self.about.setReadOnly(True)
        # message = '<p style="color: red; font-size: 24px;">Test</p>'
        html_content = "<!DOCTYPE html> \n\
<html lang=\"en\"> \n\
<head> \n\
<meta charset=\"UTF-8\"> \n\
<title></title> \n\
<style> \n\
    body { \n\
        font-family: Arial, sans-serif; \n\
        color: black; \n\
    } \n\
    table { \n\
        width: 100%; \n\
        border-collapse: collapse; \n\
    } \n\
    th, td { \n\
        padding: 8px; \n\
        text-align: left; \n\
        border-bottom: 1px solid #ddd; \n\
    } \n\
    th { \n\
        background-color: ##E5E5E5; \n\
    } \n\
</style> \n\
</head> \n\
<body> \n\
<p style='color: #030F4F; font-size: 24px;'><b>FORGE </b><b style='color: #CC9200; font-size: 24px;'>Ascend    </b><b style='color: #030F4F; font-size: 20px;'><i>4.1</i></b></p> \n\
<p><i style='color: #77769A; font-size: 14px;'>A research and development tool for Forge Project.</i></p> \n\
<p><i>26 AUG 2024  </i></p> \n\
<br>\n\
<table> \n\
    <tr> \n\
        <th><h3>Forge Ascend Project Team</h3></th> \n\
        <th><h3>Forge Project Team</h3></th> \n\
    </tr> \n\
    <tr> \n\
        <td> \n\
            <strong>Team Members:</strong> Candice Barrow, Martha Bowen, Nicole Cliff, Willam Gonzalez, Robert Irwin, Jason Smith, Jeremy Sobek, Katie Micallef<br> \n\
             <br>\n\
            <strong>Lead:</strong> Tom Stern<br>  \n\
        </td> \n\
        <td> \n\
            <strong>Team Members:</strong> Barbara Ristau, Steve Grigalunas, Devin Hicks, Martha Bowen, Jason Smith, Florian Celli, Zach Hunter, Cindy Kirklin, Chester Manuel, Scott Stewart, Gregory Villatte, Tony Gayed<br> \n\
             <br>\n\
            <strong>Lead:</strong> Lance Baldwin <br> \n\
             \n\
             \n\
        </td> \n\
    </tr> \n\
</table> \n\
<h3>Sponsors</h3> \n\
<p> \n\
    <strong>Christopher Wilson</strong><br> \n\
    <strong>Jeannie Lacy</strong><br> \n\
    <strong>Kes Nielsen</strong><br> \n\
</p> \n\
</body> \n\
</html>"
        self.about.setHtml( html_content )
        self.about.setStyleSheet("background-color: #f0f0f0;")
        self.about.setFixedSize(500,400)
        layout = QVBoxLayout()
        layout.addWidget(self.about)
        
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.close)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
# -- Custom "About" Message

## --- Main begins here

class AscendWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #F6F6F6; color: black;")

        self.aws = ascendAWSClientManager.ascendAWSClientManager() # -- aws is the client manager instance
        self.clients= {"Dog":"Rosie"} 
        # Localization
        self.input_language = 'en'
        self.output_language = 'fr'
        self.spoken_language = 'en-GB'
        self.voice_name = 'Arthur'
        self.output_audio_file = ""

        ## Reading setup
        # Initialize Pygame mixer
        pygame.mixer.init()
        self.reading_audio_file = None
        # Set the fixed MP3 file path with a unique name
        startup_dir = os.path.dirname(os.path.abspath(__file__))
        self.reading_dir = os.path.join(startup_dir, "reading")
        # Create the "reading" directory if it doesn't exist
        os.makedirs(self.reading_dir, exist_ok=True)

        # Load the audio file
        # pygame.mixer.music.load(self.reading_audio_file)
        # Track play/pause state
        self.is_playing = False
        self.last_edit_3 = ""


        # Set application to use OS icons for QTreeView 
        style = QApplication.style()
        self.bucket_icon = style.standardIcon(QStyle.SP_DriveNetIcon)
        self.folder_icon = style.standardIcon(QStyle.SP_DirIcon)
        self.file_icon = style.standardIcon(QStyle.SP_FileIcon)

        self.initUI()

        # --- Editor setting variables
        self.font_size_edit_1 = 14
        self.font_family_edit_1 = "Monospace"
        self.font_size_edit_2 = 14
        self.font_family_edit_2 = "Monospace"
        self.font_size_edit_3 = 14
        self.font_family_edit_3 = "Monospace"

    def initUI(self):
        
        self.bedrock = ""
        self.batchmode = 0
        self.wayback = 0    
        self.accessibility = 0
        self.max_web_chars = 10000   # Maxium fetch URL characters
        self.startup_location = os.path.dirname(os.path.realpath(__file__))


## ------------------- Make Settings global
        self.model_settings = {
            'Claude 2.1': {'temp': "0.5", 
                           'topP': "1", 'topK': "250", 
                           'maxT': "2000", 'stopSeq': ""}, 
            'Claude 3S': {'temp': "0.5", 
                           'topP': "1", 'topK': "250", 
                           'maxT': "2000", 'stopSeq': ""},
            'Claude 35S': {'temp': "0.5", 
                           'topP': "1", 'topK': "250", 
                           'maxT': "2000", 'stopSeq': ""},
            'Claude 3H': {'temp': "0.5", 
                           'topP': "1", 'topK': "250", 
                           'maxT': "2000", 'stopSeq': ""},
            'Titan P':      {'temp': "1", 
                             'topP': "1", 'maxT': "2000", 'stopSeq': ""},
            'Titan T-G1-E': {'temp': "1", 
                             'topP': "1", 'maxT': "2000", 'stopSeq': ""},
            'Titan T-G1-L': {'temp': "1", 
                             'topP': "1", 'maxT': "2000", 'stopSeq': ""},
            'Llama 2 13B': {'temp': "0.5", 'topP': "0.9", 'maxT': "512" },
            'Llama 2 70B': {'temp': "0.5", 'topP': "0.9", 'maxT': "512" },
            'Jurassic 2 Ultra': {'temp': "1", 
                                 'topP': "1", 'maxT': "2000", 'stopSeq': "",
                                 'presencePenalty': "", 'countPenalty': "", 'frequencyPenalty': ""},
            'Jurassic 2 Mid': {'temp': "1", 
                               'topP': "1", 'maxT': "2000", 'stopSeq': "",
                               'presencePenalty': "", 'countPenalty': "", 'frequencyPenalty': ""},
            'Cohere R': {'temp': "0.3", 
                         'topP': "0.75", 'topK': "250", 
                         'maxT': "2000", 'stopSeq': ""},
            'Cohere R+': {'temp': "0.3", 
                         'topP': "0.75", 'topK': "250", 
                         'maxT': "2000", 'stopSeq': ""},
            'Cohere': {'temp': "0.5", 
                         'topP': "0.5", 'topK': "250", 
                         'maxT': "2000", 'stopSeq': ""},
            'Mistral 7B': {'temp': "0.5", 
                           'topP': "0.9", 'topK': "50", 
                           'maxT': "2000", 'stopSeq': ""},
            'Mixtral 8X7B': {'temp': "0.5", 
                           'topP': "0.9", 'topK': "50", 
                           'maxT': "2000", 'stopSeq': ""},
            'Mistral Large': {'temp': "0.7", 
                           'topP': "1.0", 'topK': "50", # In Mistral Large topK is disabled
                           'maxT': "8192", 'stopSeq': ""},
            'Stability XL': {'seed': "0", 
                           'cfg_scale': "10",  
                           'steps': "30" },
            'Titan G1': {'seed': "0", 
                           'cfgScale': "8.0",  
                           'quality' : "standard",
                           'height' : "512",
                           'width' : "512",
                           'numberOfImages' : "1" },
            'Titan G2': {'seed': "0", 
                           'cfgScale': "8.0",  
                           'quality' : "standard",
                           'height' : "512",
                           'width' : "512",
                           'numberOfImages' : "1" },
            'Nova Pro': {'max_new_tokens': "2000", 
                           'top_p': "0.9", 'top_k': "20",  
                           "temperature": "0.7" },
            'Nova Lite': {'max_new_tokens': "2000", 
                           'top_p': "0.9", 'top_k': "20",  
                           "temperature": "0.7" },
            'Nova Micro': {'max_new_tokens': "2000", 
                           'top_p': "0.9", 'top_k': "20",  
                           "temperature": "0.7" },
            'Nova Canvas': {'seed': "0", 
                           'cfgScale': "8.0",  
                           'quality' : "standard",
                           'height' : "512",
                           'width' : "512",
                           'numberOfImages' : "1" },
            # Add initial settings for all models
        }
        # Amazon Nova Micro amazon.nova-micro-v1:0  Text-in Text-out inf_params = {"max_new_tokens": 500, "top_p": 0.9, "top_k": 20, "temperature": 0.7}
        # Amazon Nova Lite amazon.nova-lite-v1:0  Text, Image, Video in, Text-out
        # Amazon Nova Pro amazon.nova-pro-v1:0 Text, Image, Video in, Text-out
        # Amazon Nova Canvas ...

        font = QFont()
        font.setItalic(True)

        bH = 20
        bW = 65
        bW2 = 30
        self.buttonStyle_1 = """
        QPushButton {
            background-color: #FFFFCC;
            color: #000000;
            font-family: Arial; 
            font-size: 14px;    
            font-weight: normal;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #FFC200; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """

        self.buttonStyle_2 = """
        QPushButton {
            background-color: #FFFFCC;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: bold;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 0px;
            }
            QPushButton:hover { background-color: #FFC200; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """
        self.buttonStyle_3 = """
        QPushButton {
            background-color: #E6F0FF;
            color: #000000;
            font-family: Arial; 
            font-size: 14px;    
            font-weight: bold;  
            font-style: normal;  
            border: 3px solid #005999;
            border-radius: 0px;
            }
            QPushButton:hover { background-color: #00BFFF; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """
        self.buttonStyle_4 = """
        QPushButton {
            background-color: #E6F0FF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #00BFFF; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """
        self.buttonStyle_4warn = """
        QPushButton {
            background-color: #FFE0D5;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #FFBF00; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """

        self.buttonStyle_5 = """
        QPushButton {
            background-color: #E6E6E6;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal; 
            border: 2px solid #C2C2C2;
            border-radius: 7px;
            }
            QPushButton:hover { background-color: #3a3a3a; color: #FFFFFF;}
            QPushButton:pressed { background-color: #FF0000; color: #000000; }
        """

        self.buttonStyle_6 = """
        QPushButton {
            background-color: #C4E0EF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: bold;  
            font-style: normal; 
            border: 2px solid #000000;
            border-radius: 7px;
            }
            QPushButton:hover { background-color: #3a3a3a; color: #FFFFFF;}
            QPushButton:pressed { background-color: #FF0000; color: #000000; }
        """
        self.buttonStyle_7 = """
        QPushButton {
            background-color: #F0F0F0;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: bold;  
            font-style: normal; 
            border: 0px solid #000000;
            border-radius: 0px;
            }
            QPushButton:hover { background-color: #6a6a6a; color: #FFFFFF;}
            QPushButton:pressed { background-color: #FF0000; color: #000000; }
        """

        self.buttonStyle_8 = """
        QPushButton {
            background-color: #D5F0FF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #22DEEE; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """
        self.groupboxStyle_1 = """
            QGroupBox {
                border: 1px dashed black;
                margin-top: 10px; /* Adjust this value to control the space above the title */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center; /* Adjust this to change the position of the title */
                padding: 0 3px; /* Adjust this to change the padding around the title */
                color: #C06000; /* Color of the title text */
            }
        """

        # Main horizontal layout
        horizontal_layout = QHBoxLayout()

        # Frame for editors and control layouts
        frame = QFrame()

        # Vertical layout 1 to hold editors
        vertical_layout_1 = QVBoxLayout()

        # Editors section
        # Editor 1
        horizontal_layout_editors = QHBoxLayout()
        vertical_layout_edit_1 = QVBoxLayout()
        top_line_edit_1 = QHBoxLayout()
        label1 = QLabel("COMMAND:")
        self.edit_1 = QTextEdit()
#        buttons_1 = QPushButton("Button 1")
        
        # -- Copy to Clipboard button for Editor 1
        b_C001 = QPushButton("📋") 
        b_C001.setFixedSize(20,20)
        b_C001.setToolTip("Copy Command editor to clipboard.")
        b_C001.setStyleSheet(self.buttonStyle_7)
        b_C001.clicked.connect(self.ed1_clipboard)  ## copy ed_1
        top_line_edit_1.addWidget(label1)
        top_line_edit_1.addStretch
        top_line_edit_1.addWidget(b_C001)  ## Copy button
        vertical_layout_edit_1.addLayout(top_line_edit_1)

        vertical_layout_edit_1.addWidget(self.edit_1)
        horizontal_layout_buttons_1 = QHBoxLayout()
        horizontal_layout_buttons_1b = QHBoxLayout()
        vertical_layout_edit_1.addLayout(horizontal_layout_buttons_1)
        vertical_layout_edit_1.addLayout(horizontal_layout_buttons_1b)
        horizontal_layout_buttons_1b.addStretch()
        horizontal_layout_buttons_1.addStretch

 #       vertical_layout_edit_1.addWidget(buttons_1)

        b_0001 = QPushButton("Open")
        b_0001.setToolTip("Load a text file into the Command editor.")
        b_0001.setFixedSize(bW,bH)
        b_0001.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_1.addWidget(b_0001)
        b_0001.clicked.connect(self.open_ed1) 

        b_0002 = QPushButton("Append")
        b_0002.setToolTip("Load multiple files into the Command editor.")
        b_0002.setFixedSize(bW,bH)
        b_0002.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_1.addWidget(b_0002)
        b_0002.clicked.connect(self.append_ed1) 

        b_0003 = QPushButton("Save")
        b_0003.setToolTip("Save Command editor to a text file.")
        b_0003.setFixedSize(bW,bH)
        b_0003.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_1.addWidget(b_0003)
        b_0003.clicked.connect(self.save_ed1) 

        b_0004 = QPushButton("ƒ")
        b_0004.setToolTip("Switch between proportional and monospace font.")
        b_0004.setFixedSize(bW2,bH)
        b_0004.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_1b.addWidget(b_0004)
        b_0004.clicked.connect(self.toggle_font_family_edit_1)

        b_0005 = QPushButton("↑")
        b_0005.setToolTip("Increase font size.")
        b_0005.setFixedSize(bW2,bH)
        b_0005.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_1b.addWidget(b_0005)
        b_0005.clicked.connect(self.increase_font_size_edit_1) 

        b_0006 = QPushButton("↓")
        b_0006.setToolTip("Decrease font size.")
        b_0006.setFixedSize(bW2,bH)
        b_0006.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_1b.addWidget(b_0006)
        b_0006.clicked.connect(self.decrease_font_size_edit_1) 

        b_0007 = QPushButton("Clear")
        b_0007.setToolTip("Clear the Command editor.")
        b_0007.setFixedSize(bW,bH)
        b_0007.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_1b.addWidget(b_0007)
        b_0007.clicked.connect(self.ed1_clear) 

        horizontal_layout_buttons_1.addStretch

        b_0008 = QPushButton("▶")
        b_0008.setToolTip("Copy contents of Command editor to Input editor.")
        b_0008.setFixedSize(bW2,bH)
        b_0008.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_1.addWidget(b_0008)
        b_0008.clicked.connect(self.copy_1_2) 


## ------------------- Batch toggle --------------
        # Controls section
        vertical_layout_controls = QVBoxLayout()


        # -- Copy to Clipboard button for Editor 2
        b_C002 = QPushButton("📋") 
        b_C002.setToolTip("Copy Input editor to clipboard.")
        b_C002.setFixedSize(20,20)
        b_C002.setStyleSheet(self.buttonStyle_7)
        b_C002.clicked.connect(self.ed2_clipboard)  ## copy ed_1

##      Batch radio buttons
        # Create the radio buttons
        self.radioButtonBatchOn = QRadioButton("Batch On")
        self.radioButtonBatchOff = QRadioButton("Batch Off")
        # Set default checked state
        self.radioButtonBatchOff.setChecked(True)
        # Connect the signal to the slot
        self.radioButtonBatchOn.toggled.connect(self.batchModeChanged)
        self.radioButtonBatchOff.toggled.connect(self.batchModeChanged)
        
        # Editor 2
        vertical_layout_edit_2 = QVBoxLayout()
        label2 = QLabel("INPUT:")
        self.edit_2 = QTextEdit()
        buttons_2 = QPushButton("Button 2")
        horizontal_layout_batch = QHBoxLayout()
        horizontal_layout_batch.addWidget(label2)
        # Add radio buttons to the layout
        horizontal_layout_batch.addWidget(self.radioButtonBatchOn)
        horizontal_layout_batch.addWidget(self.radioButtonBatchOff)
        horizontal_layout_batch.addWidget(b_C002)

        vertical_layout_edit_2.addLayout(horizontal_layout_batch)
        vertical_layout_edit_2.addWidget(self.edit_2)
        horizontal_layout_buttons_2 = QHBoxLayout()
        horizontal_layout_buttons_2b = QHBoxLayout()
        vertical_layout_edit_2.addLayout(horizontal_layout_buttons_2)
        vertical_layout_edit_2.addLayout(horizontal_layout_buttons_2b)
        horizontal_layout_buttons_2b.addStretch()

        b_0011 = QPushButton("◀")
        b_0011.setToolTip("Copy contents from Input editor to Command editor.")
        b_0011.setFixedSize(bW2,bH)
        b_0011.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2.addWidget(b_0011)
        b_0011.clicked.connect(self.copy_2_1) 

        horizontal_layout_buttons_2.addStretch

        self.b_batch = QPushButton("Select")
        self.b_batch.setToolTip("Select multiple files for batch processing.")
        self.b_batch.setFixedSize(bW,bH)
        self.b_batch.setStyleSheet(self.buttonStyle_3)
        horizontal_layout_buttons_2b.addWidget(self.b_batch)
        self.b_batch.setVisible(False)  # Hide the batch button
        self.b_batch.clicked.connect(self.select_files)  ####
        
        b_0012 = QPushButton("Open")
        b_0012.setFixedSize(bW,bH)
        b_0012.setToolTip("Load a text file into the Input editor.")
        b_0012.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2.addWidget(b_0012)
        b_0012.clicked.connect(self.open_ed2) 

        b_0013 = QPushButton("Append")
        b_0013.setToolTip("Load multiple files into the Input editor.")
        b_0013.setFixedSize(bW,bH)
        b_0013.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2.addWidget(b_0013)
        b_0013.clicked.connect(self.append_ed2) 

        b_0014 = QPushButton("Save")
        b_0014.setToolTip("Save contents of the Input editor to a text file.")
        b_0014.setFixedSize(bW,bH)
        b_0014.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2.addWidget(b_0014)
        b_0014.clicked.connect(self.save_ed2) 

        b_0015 = QPushButton("ƒ")
        b_0015.setToolTip("Switch between proportional and monospace font.")
        b_0015.setFixedSize(bW2,bH)
        b_0015.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_2b.addWidget(b_0015)
        b_0015.clicked.connect(self.toggle_font_family_edit_2)

        b_0016 = QPushButton("↑")
        b_0016.setToolTip("Increase font size.")
        b_0016.setFixedSize(bW2,bH)
        b_0016.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_2b.addWidget(b_0016)
        b_0016.clicked.connect(self.increase_font_size_edit_2) 

        b_0017 = QPushButton("↓")
        b_0017.setToolTip("Decrease font size.")
        b_0017.setFixedSize(bW2,bH)
        b_0017.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_2b.addWidget(b_0017)
        b_0017.clicked.connect(self.decrease_font_size_edit_2) 

        b_0018a = QPushButton("Languages")
        b_0018a.setToolTip("Select languages.")
        b_0018a.setFixedSize(85,bH)
        b_0018a.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2b.addWidget(b_0018a)
        b_0018a.clicked.connect(self.language_selector) 

        b_0018 = QPushButton("Clear")
        b_0018.setToolTip("Clear the contents of the Input editor.")
        b_0018.setFixedSize(bW,bH)
        b_0018.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2b.addWidget(b_0018)
        b_0018.clicked.connect(self.ed2_clear) 

        horizontal_layout_buttons_2.addStretch

        b_0019a = QPushButton("Translate ▶")
        b_0019a.setToolTip("Copy the contents of the Input editor to the Response editor.")
        b_0019a.setFixedSize(85,bH)
        b_0019a.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2.addWidget(b_0019a)
        b_0019a.clicked.connect(self.translate) 


        b_0019 = QPushButton("▶")
        b_0019.setToolTip("Copy the contents of the Input editor to the Response editor.")
        b_0019.setFixedSize(bW-24,bH)
        b_0019.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_2.addWidget(b_0019)
        b_0019.clicked.connect(self.copy_2_3) 
        



        # Editor 3
        vertical_layout_edit_3 = QVBoxLayout()
        top_line_edit_3 = QHBoxLayout()
        label3 = QLabel("RESPONSE:")
        self.edit_3 = QTextEdit()
        buttons_3 = QPushButton("Button 3")

        # -- Copy to Clipboard button for Editor 3
        b_C003 = QPushButton("📋") 
        b_C003.setToolTip("Copy Response editor to clipboard.")
        b_C003.setFixedSize(20,20)
        b_C003.setStyleSheet(self.buttonStyle_7)
        b_C003.clicked.connect(self.ed3_clipboard)  ## copy ed_3
        top_line_edit_3.addWidget(label3)
        top_line_edit_3.addStretch
        top_line_edit_3.addWidget(b_C003)  ## Copy button
        vertical_layout_edit_3.addLayout(top_line_edit_3)

        vertical_layout_edit_3.addWidget(self.edit_3)
        horizontal_layout_buttons_3 = QHBoxLayout()
        horizontal_layout_buttons_3b = QHBoxLayout()
        vertical_layout_edit_3.addLayout(horizontal_layout_buttons_3)
        vertical_layout_edit_3.addLayout(horizontal_layout_buttons_3b)
        horizontal_layout_buttons_3b.addStretch()

        b_0021 = QPushButton("◀")
        b_0021.setToolTip("Copy contents from Response editor to Input editor.")
        b_0021.setFixedSize(bW2,bH)
        b_0021.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3.addWidget(b_0021)
        b_0021.clicked.connect(self.copy_3_2) 

        b_0021a = QPushButton("Read")
        b_0021a.setToolTip("Read the Response in the chosen language and voice.")
        b_0021a.setFixedSize(65,bH)
        b_0021a.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3.addWidget(b_0021a)
        b_0021a.clicked.connect(self.read_edit_3) 
    
        b_0021b = QPushButton("Save Speech")
        b_0021b.setToolTip("Saves the text to MP3 using Polly.")
        b_0021b.setFixedSize(95,bH)
        b_0021b.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3.addWidget(b_0021b)
        b_0021b.clicked.connect(self.save_spoken_language) 


        self.fm = FileMerge(self.edit_3)

        horizontal_layout_buttons_3.addStretch

        b_0022 = QPushButton("Chat")
        b_0022.setToolTip("Move and label Input and Resposnse to Command editor.")
        b_0022.setFixedSize(bW,bH)
        b_0022.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3b.addWidget(b_0022)
        b_0022.clicked.connect(self.chat) 

        b_0023 = QPushButton("Open")
        b_0023.setToolTip("Load text file into Response editor.")
        b_0023.setFixedSize(bW,bH)
        b_0023.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3.addWidget(b_0023)
        b_0023.clicked.connect(self.open_ed3) 
        
        b_0024 = QPushButton("Append")
        b_0024.setToolTip("Load multiple files into Response editor.")
        b_0024.setFixedSize(bW,bH)
        b_0024.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3.addWidget(b_0024)
        b_0024.clicked.connect(self.append_ed3) 

        b_0025 = QPushButton("Save")
        b_0025.setToolTip("Save contents of Response editor to text file.")
        b_0025.setFixedSize(bW,bH)
        b_0025.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3.addWidget(b_0025)
        b_0025.clicked.connect(self.save_ed3) 

        b_0026 = QPushButton("Split")
        b_0026.setToolTip("Split Response editor contents at markers and store in enumerated files.")
        b_0026.setFixedSize(bW,bH)
        b_0026.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3b.addWidget(b_0026)
        b_0026.clicked.connect(self.split_ed3)  
        
        b_0027 = QPushButton("ƒ")
        b_0027.setToolTip("Switch between proportional and monospace font.")
        b_0027.setFixedSize(bW2,bH)
        b_0027.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_3b.addWidget(b_0027)
        b_0027.clicked.connect(self.toggle_font_family_edit_3)

        b_0028 = QPushButton("↑")
        b_0028.setToolTip("Increase font size.")
        b_0028.setFixedSize(bW2,bH)
        b_0028.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_3b.addWidget(b_0028)
        b_0028.clicked.connect(self.increase_font_size_edit_3) 

        b_0029 = QPushButton("↓")
        b_0029.setToolTip("Decrease font size.")
        b_0029.setFixedSize(bW2,bH)
        b_0029.setStyleSheet(self.buttonStyle_2)
        horizontal_layout_buttons_3b.addWidget(b_0029)
        b_0029.clicked.connect(self.decrease_font_size_edit_3) 

        b_0030 = QPushButton("Clear")
        b_0030.setToolTip("Clear the contents of the Response editor.")
        b_0030.setFixedSize(bW,bH)
        b_0030.setStyleSheet(self.buttonStyle_1)
        horizontal_layout_buttons_3b.addWidget(b_0030)
        b_0030.clicked.connect(self.ed3_clear) 

        
        # Adding editors to the horizontal editors layout
        horizontal_layout_editors.addLayout(vertical_layout_edit_1)
        horizontal_layout_editors.addLayout(vertical_layout_edit_2)
        horizontal_layout_editors.addLayout(vertical_layout_edit_3)
        self.set_editor_defaults()

        vSpace = 2

        # Row 1
        horizontal_layout_button_row_1 = QHBoxLayout()
        vertical_models_0 = QVBoxLayout()
        vertical_models_0.setSpacing(vSpace)
        vertical_models_1 = QVBoxLayout()
        vertical_models_1.setSpacing(vSpace)
        vertical_models_2 = QVBoxLayout()
        vertical_models_2.setSpacing(vSpace)
        vertical_models_3 = QVBoxLayout()
        vertical_models_3.setSpacing(vSpace)
        vertical_models_4 = QVBoxLayout()
        vertical_models_4.setSpacing(vSpace)
        vertical_models_5 = QVBoxLayout()
        vertical_models_5.setSpacing(vSpace)
        vertical_models_6 = QVBoxLayout()
        vertical_models_6.setSpacing(vSpace)
        vertical_models_7 = QVBoxLayout()
        vertical_models_7.setSpacing(vSpace)
        vertical_models_8 = QVBoxLayout()
        vertical_models_8.setSpacing(vSpace)
        vertical_models_9 = QVBoxLayout()
        vertical_models_9.setSpacing(vSpace)
        vertical_models_a = QVBoxLayout()
        vertical_models_a.setSpacing(vSpace)
        vertical_controls_7 = QVBoxLayout()
        vertical_controls_7.setSpacing(vSpace)
        vertical_controls_8 = QVBoxLayout()
        vertical_controls_8.setSpacing(vSpace)
        horizontal_controls_8b = QHBoxLayout()

        # Group Box Layouts

        # Bedrock Model QGroupBox
        model_box = QGroupBox("Bedrock Models")
        model_box_layout = QHBoxLayout()
        model_box_layout.addLayout(vertical_models_0)
        model_box_layout.addLayout(vertical_models_1)
        model_box_layout.addLayout(vertical_models_2)
        model_box_layout.addLayout(vertical_models_3)
        model_box_layout.addLayout(vertical_models_4)
        model_box_layout.addLayout(vertical_models_5)
        model_box.setStyleSheet(self.groupboxStyle_1)
        model_box.setLayout(model_box_layout) 

        # Curriculum Development QGroupBox
        curdev_box = QGroupBox("Curriculum Development")
        curdev_box_layout = QHBoxLayout()
        curdev_box_layout.addLayout(vertical_models_6)
        curdev_box_layout.addLayout(vertical_models_7)
        curdev_box.setStyleSheet(self.groupboxStyle_1)
        curdev_box.setLayout(curdev_box_layout)       

       # Application Tools QGroupBox
        tool_box = QGroupBox("Application Tools")
        tool_box_layout = QHBoxLayout()
        tool_box_layout.addLayout(vertical_models_8)
        tool_box_layout.addLayout(vertical_models_9)
        tool_box_layout.addLayout(vertical_models_a)
        tool_box.setStyleSheet(self.groupboxStyle_1)
        tool_box.setLayout(tool_box_layout) 

        horizontal_layout_button_row_1.addWidget(model_box)
        horizontal_layout_button_row_1.addWidget(curdev_box)
        horizontal_layout_button_row_1.addWidget(tool_box)
        horizontal_layout_button_row_1.addStretch()

        horizontal_layout_button_row_1.addLayout(vertical_controls_7)
        horizontal_layout_button_row_1.addLayout(vertical_controls_8)      

        configlabelv = QLabel(" ")
        configlabelv.setFont(font)
        configlabelv.setStyleSheet("color: #C06000;")
        configlabel = QLabel(" ")
        vertical_controls_7.addWidget(configlabelv)
        vertical_controls_7.addWidget(configlabel)

        b_1001 = QPushButton("Model Settings")
        b_1001.setToolTip("Open the Model Setting Panel.")
        b_1001.setFixedSize(90,bH)
        b_1001.setStyleSheet(self.buttonStyle_4)
        vertical_controls_7.addWidget(b_1001)
        b_1001.clicked.connect(self.adjust_settings) 
        
        b_1002 = QPushButton("Credentials")
        b_1002.setToolTip("Open the Credentials Panel.")
        b_1002.setFixedSize(90,bH)
        b_1002.setStyleSheet(self.buttonStyle_4)
        vertical_controls_7.addWidget(b_1002)
        b_1002.clicked.connect(self.adjust_credentials) 

        b_1003 = QPushButton(" ")
        b_1003.setFixedSize(90,bH)
        b_1003.setStyleSheet(self.buttonStyle_5)
        vertical_controls_7.addWidget(b_1003)
       # b_1003.clicked.connect(self.adjust_credentials) 

        b_2002 = QPushButton("About")
        b_2002.setToolTip("View Ascend information.")
        b_2002.setFixedSize(90,bH)
        b_2002.setStyleSheet(self.buttonStyle_4)
        vertical_controls_7.addWidget(b_2002)
        b_2002.clicked.connect(self.show_creator_message) 

        b_1005 = QPushButton(" ")
        b_1005.setFixedSize(90,bH)
        b_1005.setStyleSheet(self.buttonStyle_5)
        vertical_controls_7.addWidget(b_1005)
       # b_1005.clicked.connect(self.adjust_credentials) 

## ----- 

        b_2004 = QPushButton("Clear All")
        b_2004.setToolTip("Clear the contents of all editors.")
        b_2004.setFixedSize(120,bH)
        b_2004.setStyleSheet(self.buttonStyle_1)
        vertical_controls_8.addWidget(b_2004)
        b_2004.clicked.connect(self.edAll_clear) 

        #b_2005a = QPushButton("Read")
        #b_2005a.setToolTip("Speak the text.")
        #b_2005a.setFixedSize(120,bH)
        #b_2005a.setStyleSheet(self.buttonStyle_1)
        #vertical_controls_8.addWidget(b_2005a)
        #b_2005a.clicked.connect(self.read_edit_3)  
        # b_2005a.clicked.connect(self.play_or_pause_reading)  

        #b_2005b = QPushButton("◀ Translate")
        #b_2005b.setToolTip("Show the contents of the Response editor translated in the Input editor.")
        #b_2005b.setFixedSize(120,bH)
        #b_2005b.setStyleSheet(self.buttonStyle_1)
        #vertical_controls_8.addWidget(b_2005b)
        #b_2005b.clicked.connect(self.translate)  

        b_2005 = QPushButton("◀ Display md")
        b_2005.setToolTip("Show the contents of the Response editor formatted in the Input editor.")
        b_2005.setFixedSize(120,bH)
        b_2005.setStyleSheet(self.buttonStyle_1)
        vertical_controls_8.addWidget(b_2005)
        b_2005.clicked.connect(self.display_as_markdown)  

        vertical_controls_8.addLayout(horizontal_controls_8b)

        b_2006 = QPushButton("Way")
        b_2006.setToolTip("Open the Wayback controls panel.")
        b_2006.setFixedSize(50,bH)
        b_2006.setStyleSheet(self.buttonStyle_1)
        horizontal_controls_8b.addWidget(b_2006)
        b_2006.clicked.connect(self.wayback_machine) 

        b_2007 = QPushButton("Back")
        b_2007.setToolTip("Browse session history.")
        b_2007.setFixedSize(50,bH)
        b_2007.setStyleSheet(self.buttonStyle_1)
        horizontal_controls_8b.addWidget(b_2007)
        b_2007.clicked.connect(self.wayback_recall)   
        
        b_2003 = QPushButton("Accessibility")
        b_2003.setToolTip("Switch between large and standard font size.")
        b_2003.setFixedSize(120,bH)
        b_2003.setStyleSheet(self.buttonStyle_2)
        vertical_controls_8.addWidget(b_2003)
        b_2003.clicked.connect(self.set_editor_accessibility) 


## --- Amazon Nova models
        modelmaker0 = QLabel("Amazon Nova")
        modelmaker0.setAlignment(Qt.AlignCenter)
        vertical_models_0.addWidget(modelmaker0)

        ## Opus is only available in us-west Region
        ## Sonnet 3.5 might be throttled to 1 per minute
        b_0181c = QPushButton("Nova Pro")
        b_0181c.setToolTip("Amazon Nova Pro multimodal AI")
        b_0181c.setFixedSize(86,bH)
        b_0181c.setStyleSheet(self.buttonStyle_4)
        vertical_models_0.addWidget(b_0181c)
        b_0181c.clicked.connect(self.talk_with_novaPro) 

        b_0181d = QPushButton("MM Nova Pro")
        b_0181d.setToolTip("Amazon Nova Pro multimodal AI")
        b_0181d.setFixedSize(86,bH)
        b_0181d.setStyleSheet(self.buttonStyle_4)
        vertical_models_0.addWidget(b_0181d)
        b_0181d.clicked.connect(self.talk_with_novaPro_MM) 

        b_0181e = QPushButton("Nova Lite")
        b_0181e.setToolTip("Amazon Nova Lite multimodal AI")
        b_0181e.setFixedSize(86,bH)
        b_0181e.setStyleSheet(self.buttonStyle_4)
        vertical_models_0.addWidget(b_0181e)
        b_0181e.clicked.connect(self.talk_with_novaLite) 

        b_0181f = QPushButton("MM Nova Lite") #Nova Reel
        b_0181f.setToolTip("Amazon Nova Reel Video Generation ")
        b_0181f.setFixedSize(86,bH)
        b_0181f.setStyleSheet(self.buttonStyle_4)
        vertical_models_0.addWidget(b_0181f)
        b_0181f.clicked.connect(self.talk_with_novaLite_MM) 

        b_0181g = QPushButton("Nova Micro")
        b_0181g.setToolTip("Amazon Nova Micro super-fast AI")
        b_0181g.setFixedSize(86,bH)
        b_0181g.setStyleSheet(self.buttonStyle_4)
        vertical_models_0.addWidget(b_0181g)
        b_0181g.clicked.connect(self.talk_with_novaMicro) 

        #b_0182 = QPushButton("Nova Canvas")
        #b_0182.setToolTip("Amazon Nova Canvas Image Generation")
        #b_0182.setFixedSize(80,bH)
        #b_0182.setStyleSheet(self.buttonStyle_4)
        #vertical_models_0.addWidget(b_0182)
        #b_0182.clicked.connect(self.talk_with_novaCanvas) 

        #b_0192 = QPushButton("Nova Lite") #Nova Reel
        #b_0192.setToolTip("Amazon Nova Reel Video Generation ")
        #b_0192.setFixedSize(80,bH)
        #b_0192.setStyleSheet(self.buttonStyle_5)
        #vertical_models_0.addWidget(b_0192)
        #b_0192.clicked.connect(self.talk_with_novaLite_MM) 
        # b_0192.clicked.connect(self.talk_with_novaReel) 

## --- Amazon Nova models

## --- Anthropic models
        modelmaker1 = QLabel("Anthropic")
        modelmaker1.setAlignment(Qt.AlignCenter)
        vertical_models_1.addWidget(modelmaker1)

        ## Opus is only available in us-west Region
        ## Sonnet 3.5 might be throttled to 1 per minute
        b_0101c = QPushButton("Sonnet35")
        b_0101c.setToolTip("Anthropic Claude Sonnet 3.5.")
        b_0101c.setFixedSize(80,bH)
        b_0101c.setStyleSheet(self.buttonStyle_4)
        vertical_models_1.addWidget(b_0101c)
        b_0101c.clicked.connect(self.talk_with_claudev35) 

        b_0101 = QPushButton("Sonnet")
        b_0101.setToolTip("Anthropic Claude 3 Sonnet.")
        b_0101.setFixedSize(80,bH)
        b_0101.setStyleSheet(self.buttonStyle_4)
        vertical_models_1.addWidget(b_0101)
        b_0101.clicked.connect(self.talk_with_claudev3) 

        b_0101b = QPushButton("Haiku")
        b_0101b.setToolTip("Anthropic Claude 3 Haiku.")
        b_0101b.setFixedSize(80,bH)
        b_0101b.setStyleSheet(self.buttonStyle_4)
        vertical_models_1.addWidget(b_0101b)
        b_0101b.clicked.connect(self.talk_with_claudeH) 

        b_0102 = QPushButton("2.1")
        b_0102.setToolTip("Anthropic Claude 2.1.")
        b_0102.setFixedSize(80,bH)
        b_0102.setStyleSheet(self.buttonStyle_4)
        vertical_models_1.addWidget(b_0102)
        b_0102.clicked.connect(self.talk_with_claudev21) 

        b_0162 = QPushButton("MM Sonnet")
        b_0162.setToolTip("Multimodal Anthropic Claude 3 Sonnet: Text + Image ")
        b_0162.setFixedSize(80,bH)
        b_0162.setStyleSheet(self.buttonStyle_4)
        vertical_models_1.addWidget(b_0162)
        b_0162.clicked.connect(self.claude_3_image) 

## --- Anthropic models
## --- Amazon Titan models
        modelmaker2 = QLabel("Amazon Titan")
        modelmaker2.setAlignment(Qt.AlignCenter)
        vertical_models_2.addWidget(modelmaker2)

        b_0150 = QPushButton("Premiere")
        b_0150.setToolTip("Amazon: Titan G1 Premiere")
        b_0150.setFixedSize(80,bH)
        b_0150.setStyleSheet(self.buttonStyle_4)
        vertical_models_2.addWidget(b_0150)
        b_0150.clicked.connect(self.talk_with_titan_premiere) 

        b_0151 = QPushButton("G1 Express")
        b_0151.setToolTip("Amazon: Titan G1 Express")
        b_0151.setFixedSize(80,bH)
        b_0151.setStyleSheet(self.buttonStyle_4)
        vertical_models_2.addWidget(b_0151)
        b_0151.clicked.connect(self.talk_with_titan_express) 

        b_0152 = QPushButton("G1 Lite")
        b_0152.setToolTip("Amazon: Titan G1 Lite")
        b_0152.setFixedSize(80,bH)
        b_0152.setStyleSheet(self.buttonStyle_4)
        vertical_models_2.addWidget(b_0152)
        b_0152.clicked.connect(self.talk_with_titan_lite) 

        b_0153 = QPushButton("Text Embed")
        b_0153.setToolTip("Amazon: Titan Text Embeddings")
        b_0153.setFixedSize(80,bH)
        b_0153.setStyleSheet(self.buttonStyle_4)
        vertical_models_2.addWidget(b_0153)
        b_0153.clicked.connect(self.titan_text_embed) 

        b_0154 = QPushButton("MM Embed")
        b_0154.setToolTip("Amazon: Titan Multimodal Embeddings (Text + Image)")
        b_0154.setFixedSize(80,bH)
        b_0154.setStyleSheet(self.buttonStyle_4)
        vertical_models_2.addWidget(b_0154)
        b_0154.clicked.connect(self.titan_G1_embed) 


## --- Amazon Titan models

## --- Image models
        modelmaker3 = QLabel("Image Gen")
        modelmaker3.setAlignment(Qt.AlignCenter)
        vertical_models_3.addWidget(modelmaker3)

        b_0130 = QPushButton("ImaGen")
        b_0130.setFixedSize(82,bH)
        b_0130.setStyleSheet(self.buttonStyle_2)
        vertical_models_3.addWidget(b_0130)
        b_0130.clicked.connect(self.ImageGen) 

        b_0131 = QPushButton("Nova Canvas")  #Titan Image G1
        b_0131.setToolTip("Amazon Nova Canvas Image Generation")
        b_0131.setFixedSize(80,bH)
        b_0131.setStyleSheet(self.buttonStyle_4)
        vertical_models_3.addWidget(b_0131)
        b_0131.clicked.connect(self.talk_with_novaCanvas) 

        b_0132 = QPushButton("Titan Image")  #Titan Image G1 v2
        b_0132.setToolTip("Amazon: Titan G2 (Image)")
        b_0132.setFixedSize(82,bH)
        b_0132.setStyleSheet(self.buttonStyle_4)
        vertical_models_3.addWidget(b_0132)
        b_0132.clicked.connect(self.titan_image2) 

        #b_0132 = QPushButton("Titan G1")  #Titan Image G1
        #b_0132.setToolTip("Amazon: Titan G1 (Image)")
        #b_0132.setFixedSize(82,bH)
        #b_0132.setStyleSheet(self.buttonStyle_4)
        #vertical_models_3.addWidget(b_0132)
        #b_0132.clicked.connect(self.titan_image) 

        b_0134 = QPushButton("Stability XL")
        b_0134.setToolTip("Stable Diffusion: Stability XL (Image)")
        b_0134.setFixedSize(82,bH)
        b_0134.setStyleSheet(self.buttonStyle_4)
        vertical_models_3.addWidget(b_0134)
        b_0134.clicked.connect(self.stability_image) 

        vertical_models_3_h1 = QHBoxLayout()
        vertical_models_3.addLayout(vertical_models_3_h1)

        b_0135 = QPushButton("PNG")
        b_0135.setToolTip("Save last image as a PNG file.")
        b_0135.setFixedSize(40,bH)
        b_0135.setStyleSheet(self.buttonStyle_2)
        vertical_models_3_h1.addWidget(b_0135)
        b_0135.clicked.connect(self.save_image_png) 

        b_0136 = QPushButton("JPEG")  
        b_0136.setToolTip("Save last image as a JPEG file.")
        b_0136.setFixedSize(40,bH)
        b_0136.setStyleSheet(self.buttonStyle_2)
        vertical_models_3_h1.addWidget(b_0136)
        b_0136.clicked.connect(self.save_image_jpeg) 

## --- Image Generation

## --- AI21 labs models and Cohere Moels
        modelmaker4 = QLabel("AI21|Cohere")
        modelmaker4.setAlignment(Qt.AlignCenter)
        vertical_models_4.addWidget(modelmaker4)

        b_0111 = QPushButton("Ultra")
        b_0111.setToolTip("AI21 Labs: Jurassic Ultra")
        b_0111.setFixedSize(80,bH)
        b_0111.setStyleSheet(self.buttonStyle_4)
        vertical_models_4.addWidget(b_0111)
        b_0111.clicked.connect(self.talk_with_jurassic_ultra) 

        b_0112 = QPushButton("Mid")
        b_0112.setToolTip("AI21 Labs: Jurassic Mid")
        b_0112.setFixedSize(80,bH)
        b_0112.setStyleSheet(self.buttonStyle_4)
        vertical_models_4.addWidget(b_0112)
        b_0112.clicked.connect(self.talk_with_jurassic_mid) 

        b_0113 = QPushButton("Command")
        b_0113.setToolTip("Cohere: Command")
        b_0113.setFixedSize(80,bH)
        b_0113.setStyleSheet(self.buttonStyle_4)
        vertical_models_4.addWidget(b_0113)
        b_0113.clicked.connect(self.talk_with_cohere) 

        b_0114 = QPushButton("Command R")
        b_0114.setFixedSize(80,bH)
        b_0114.setStyleSheet(self.buttonStyle_4)
        vertical_models_4.addWidget(b_0114)
        b_0114.clicked.connect(self.talk_with_cohereR) 

        b_0115 = QPushButton("Command R+")
        b_0115.setFixedSize(80,bH)
        b_0115.setStyleSheet(self.buttonStyle_4)
        vertical_models_4.addWidget(b_0115)
        b_0115.clicked.connect(self.talk_with_cohereRP) 

## --- AI21 labs models and Cohere models


## --- Meta models and Mistral Models
        #modelmaker5v = QLabel("Meta & Mistral")
        #modelmaker5v.setFont(font)
        #modelmaker5v.setStyleSheet("color: #C06000;")
        modelmaker5 = QLabel("M&M Test")
        #vertical_models_5.addWidget(modelmaker5v)
        vertical_models_5.addWidget(modelmaker5)

        b_0121 = QPushButton("70B")
        b_0121.setToolTip("Meta: Llama 70B")
        b_0121.setFixedSize(60,bH)
        b_0121.setStyleSheet(self.buttonStyle_4warn)
        vertical_models_5.addWidget(b_0121)
        b_0121.clicked.connect(self.talk_with_llama_70B) 

        b_0122 = QPushButton("13B")
        b_0122.setToolTip("Meta: Llama 13B")
        b_0122.setFixedSize(60,bH)
        b_0122.setStyleSheet(self.buttonStyle_4warn)
        vertical_models_5.addWidget(b_0122)
        b_0122.clicked.connect(self.talk_with_llama_13B) 

        b_0123 = QPushButton("Large")
        b_0123.setToolTip("Mistral AI: Mistral Large")
        b_0123.setFixedSize(60,bH)
        b_0123.setStyleSheet(self.buttonStyle_4warn)
        vertical_models_5.addWidget(b_0123)
        b_0123.clicked.connect(self.talk_with_mistral_large)

        b_0124 = QPushButton("8X7B")
        b_0124.setToolTip("Mistral AI: Mixtral 8X7B")
        b_0124.setFixedSize(60,bH)
        b_0124.setStyleSheet(self.buttonStyle_4warn)
        vertical_models_5.addWidget(b_0124)
        b_0124.clicked.connect(self.talk_with_mistral8x)

        b_0125 = QPushButton("7B")
        b_0125.setToolTip("Mistral AI: Mistral 7B")
        b_0125.setFixedSize(60,bH)
        b_0125.setStyleSheet(self.buttonStyle_4warn)
        vertical_models_5.addWidget(b_0125)
        b_0125.clicked.connect(self.talk_with_mistral) 

## --- Meta models and Mistral Models


## --- CurDev
        modelmaker6v = QLabel("Prompts")
        # modelmaker6v.setFont(font)
        modelmaker6v.setAlignment(Qt.AlignCenter)
        #modelmaker6v.setStyleSheet("color: #C06000;")
        #modelmaker6 = QLabel(" ")
        vertical_models_6.addWidget(modelmaker6v)
        #vertical_models_6.addWidget(modelmaker6)

        b_0141 = QPushButton("Prompt Catalog")
        b_0141.setFixedSize(95,bH)
        b_0141.setStyleSheet(self.buttonStyle_2)
        vertical_models_6.addWidget(b_0141)
        b_0141.clicked.connect(self.open_webpage_promptlib)

        b_0142 = QPushButton("")
        b_0142.setFixedSize(95,bH)
        b_0142.setStyleSheet(self.buttonStyle_5)
        vertical_models_6.addWidget(b_0142)
        # b_0142.clicked.connect(self.lib_expand) ## Future use

        b_0143 = QPushButton("")
        b_0143.setFixedSize(95,bH)
        b_0143.setStyleSheet(self.buttonStyle_5)
        vertical_models_6.addWidget(b_0143)
        # b_0143.clicked.connect(self.lib_expand) ## Future use

        b_0144 = QPushButton(" ")
        b_0144.setFixedSize(95,bH)
        b_0144.setStyleSheet(self.buttonStyle_5)
        vertical_models_6.addWidget(b_0144)
        # b_0144.clicked.connect(self.lib_expand) ## Future use

        b_0145 = QPushButton("List Voices")
        b_0145.setFixedSize(95,bH)
        b_0145.setStyleSheet(self.buttonStyle_5)
        vertical_models_6.addWidget(b_0145)
        b_0145.clicked.connect(self.get_voice_engine_support) 

## --- CurDev

## --- CurDev 2
        modelmaker7 = QLabel("Text Tools")
        modelmaker7.setAlignment(Qt.AlignCenter)
        # modelmaker7.setFont(font)
        #modelmaker7.setStyleSheet("color: #C06000;")
        vertical_models_7.addWidget(modelmaker7)  
        #modelmaker7b = QLabel("")
        #vertical_models_7.addWidget(modelmaker7b) 

        b_0171 = QPushButton(" Text Scan ")
        b_0171.setFixedSize(80,bH)
        b_0171.setStyleSheet(self.buttonStyle_8)
        vertical_models_7.addWidget(b_0171)
        b_0171.clicked.connect(self.scan_text_files) ## SCAN

        b_0172 = QPushButton("Select Dirs")
        b_0172.setFixedSize(80,bH)
        b_0172.setStyleSheet(self.buttonStyle_8)
        vertical_models_7.addWidget(b_0172)
        b_0172.clicked.connect(self.select_directories) ## Select directories for edit_2

        b_0173 = QPushButton("Save as CSV")
        b_0173.setFixedSize(80,bH)
        b_0173.setStyleSheet(self.buttonStyle_8)
        vertical_models_7.addWidget(b_0173)
        b_0173.clicked.connect(self.save_as_csv) ## Save edit_3 Scan text report as a CSV file

        b_0174 = QPushButton(" PDF Crusher ")
        b_0174.setFixedSize(80,bH)
        b_0174.setStyleSheet(self.buttonStyle_8)
        vertical_models_7.addWidget(b_0174)
        b_0174.clicked.connect(self.pdf_crusher) ## Provides text versions of all PDF files in a directory

        b_0175 = QPushButton(" ")
        b_0175.setFixedSize(80,bH)
        b_0175.setStyleSheet(self.buttonStyle_5)
        vertical_models_7.addWidget(b_0175)
        # b_0145.clicked.connect(self.lib_expand) ## Future use


 

## --- Image generation

## --- Custom models
        modelmaker8 = QLabel("File")
        modelmaker8.setAlignment(Qt.AlignCenter)
        vertical_models_8.addWidget(modelmaker8)

        b_0191 = QPushButton("S3")
        b_0191.setFixedSize(80,bH)
        b_0191.setToolTip("Launch S3 File Transporter.")
        b_0191.setStyleSheet(self.buttonStyle_2)
        vertical_models_8.addWidget(b_0191)
        b_0191.clicked.connect(self.S3_manager)

        b_0192 = QPushButton("Fetch File")
        b_0192.setToolTip("Load various kinds of files into Input editor.")
        b_0192.setFixedSize(80,bH)
        b_0192.setStyleSheet(self.buttonStyle_6)
        vertical_models_8.addWidget(b_0192)
        b_0192.clicked.connect(self.fetch_file) 

       # b_0193 = QPushButton(" ")
        b_0193 = QPushButton("Zip Parts")
        b_0193.setToolTip("Zips up to 6 groups of numbered files with different prefixes into new combined parts.")
        b_0193.setFixedSize(80,bH)
        b_0193.setStyleSheet(self.buttonStyle_6)
        vertical_models_8.addWidget(b_0193)
        b_0193.clicked.connect(self.fm.consolidate) 

        b_0194 = QPushButton("File Lister")
        b_0194.setFixedSize(80,bH)
        b_0194.setStyleSheet(self.buttonStyle_6)
        vertical_models_8.addWidget(b_0194)
        b_0194.clicked.connect(self.file_lister)

        b_0195 = QPushButton(" ")
        b_0195.setFixedSize(80,bH)
        b_0195.setStyleSheet(self.buttonStyle_5)
        vertical_models_8.addWidget(b_0195)
        # b_0195.clicked.connect(self.lib_expand) ## Future use

## --- Custom models


## -- Data Import ----   
        modelmaker9 = QLabel("Web")
        modelmaker9.setAlignment(Qt.AlignCenter)
        vertical_models_9.addWidget(modelmaker9)  

        #b_0184 = QPushButton("Fetch File")
        #b_0184.setToolTip("Load various kinds of files into Input editor.")
        #b_0184.setFixedSize(90,bH)
        #b_0184.setStyleSheet(self.buttonStyle_6)
        #vertical_models_9.addWidget(b_0184)
        #b_0184.clicked.connect(self.fetch_file)

        b_0181 = QPushButton("Fetch URL")  
        b_0181.setToolTip("Load web page into Input editor.")
        b_0181.setFixedSize(90,bH)
        b_0181.setStyleSheet(self.buttonStyle_6)
        vertical_models_9.addWidget(b_0181)
        b_0181.clicked.connect(self.fetch_url) 

        b_0185 = QPushButton("Max URL")
        #b_0185 = QPushButton(" S3 ")
        b_0185.setToolTip("Set the maximum number of characters in a web page fetch.")
        b_0185.setFixedSize(90,bH)
        b_0185.setStyleSheet(self.buttonStyle_6)
        #b_0185.setStyleSheet(self.buttonStyle_5)
        vertical_models_9.addWidget(b_0185)
        b_0185.clicked.connect(self.set_web_max_size) ## Future use

        b_0186 = QPushButton("||| web size")
        b_0186.setFixedSize(90,bH)
        b_0186.setStyleSheet(self.buttonStyle_6)
        vertical_models_9.addWidget(b_0186)
        b_0186.clicked.connect(self.set_preprocess_web_size)

        b_0184 = QPushButton(" ")
        b_0184.setFixedSize(90,bH)
        b_0184.setStyleSheet(self.buttonStyle_5)
        vertical_models_9.addWidget(b_0184)
        # b_0184.clicked.connect(self.lib_expand) ## Future use

        b_0185 = QPushButton(" ")
        b_0185.setFixedSize(90,bH)
        b_0185.setStyleSheet(self.buttonStyle_5)
        vertical_models_9.addWidget(b_0185)
        # b_0185.clicked.connect(self.lib_expand) ## Future use


## -- Data Import ----

## -- PowerPoint features ----
        modelmaker_ab = QLabel("Slides")
        modelmaker_ab.setAlignment(Qt.AlignCenter)
        vertical_models_a.addWidget(modelmaker_ab) 

        b_0161 = QPushButton("Save as PPT")
        b_0161.setToolTip("Save Resonse as slide deck.")
        b_0161.setFixedSize(90,bH)
        b_0161.setStyleSheet(self.buttonStyle_6)
        vertical_models_a.addWidget(b_0161)
        b_0161.clicked.connect(self.save_ppt) 

        b_0162 = QPushButton("PPT to Text")
        b_0162.setToolTip("Load slide deck into Input editor.")
        b_0162.setFixedSize(90,bH)
        b_0162.setStyleSheet(self.buttonStyle_6)
        vertical_models_a.addWidget(b_0162)
        b_0162.clicked.connect(self.load_ppt) 

        b_0163 = QPushButton("PPT Crusher")
        b_0163.setToolTip("Convert all PPT files in a directory to text.")
        b_0163.setFixedSize(90,bH)
        b_0163.setStyleSheet(self.buttonStyle_6)
        vertical_models_a.addWidget(b_0163)
        b_0163.clicked.connect(self.crush_ppt) 

        b_0164 = QPushButton("PPT Hatcher")  
        b_0164.setToolTip("Convert all text files in a directory to PPT files.")
        b_0164.setFixedSize(90,bH)
        b_0164.setStyleSheet(self.buttonStyle_6)
        vertical_models_a.addWidget(b_0164)
        b_0164.clicked.connect(self.hatch_ppt)  

        b_0165 = QPushButton(" ")
        b_0165.setFixedSize(90,bH)
        b_0165.setStyleSheet(self.buttonStyle_5)
        vertical_models_a.addWidget(b_0165)
        # b_0165.clicked.connect(self.lib_expand) ## Future use

## -- PowerPoint features ----

        vertical_layout_controls.addLayout(horizontal_layout_button_row_1)

        # Assembling the vertical layouts
        vertical_layout_1.addLayout(horizontal_layout_editors)
        vertical_layout_1.addLayout(vertical_layout_controls)

        # Adding everything to the main layout
        horizontal_layout.addLayout(vertical_layout_1)

        # Set the main layout
        self.setLayout(horizontal_layout)
        self.setWindowTitle('FORGE Ascend 4.1 ')
        self.move(100, 100)
        self.resize(1600, 800)

### ----------------------[ EditorActions instance ]------------------------------
        
        self.ed = EDitorActions(edit_1=self.edit_1, edit_2=self.edit_2, edit_3=self.edit_3)

### ----------------------[ AI Model Interaction ]------------------------------

        self.ai = AIModelInteraction(edit_1=self.edit_1, edit_2=self.edit_2, edit_3=self.edit_3, model_settings=self.model_settings, batchmode=self.batchmode)

### ----------------------[ ImageGen instance ]------------------------------
        
        self.im = ImageGen(edit_1=self.edit_1, edit_2=self.edit_2, edit_3=self.edit_3, ai_model=self.ai, model_settings=self.model_settings, clients=self.clients, startup_location=self.startup_location)

### ----------------------[ CurDev instance ]------------------------------        
        self.cd = CurDev(edit_1=self.edit_1, edit_2=self.edit_2, edit_3=self.edit_3, ai_model=self.ai, model_settings=self.model_settings, clients=self.clients, startup_location=self.startup_location)


## ------------------------------------------------------------
    def batchModeChanged(self):
        if self.radioButtonBatchOn.isChecked():
            print("Batch mode is ON")
            self.b_batch.setVisible(True)  # Show the button
            self.batchmode = 1
        else:
            print("Batch mode is OFF")
            self.b_batch.setVisible(False)  # Hide the button
            self.batchmode = 0

## ----------------------------------------------------------- Editor Methods

## -----------------------[ Text Editor UI control functions ]--------------
            
    # -- All Editors
    def set_editor_defaults(self):
        # --- Editor default settings
        self.edit_1.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 14pt;")
        self.edit_2.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 14pt;")
        self.edit_3.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 14pt;")

    def set_editor_accessibility(self):
        # --- Editor default settings
        if self.accessibility == 0:
            self.accessibility = 1
            self.edit_1.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 28pt;")
            self.edit_2.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 28pt;")
            self.edit_3.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 28pt;")
            self.font_size_edit_1 = 28
            self.font_size_edit_2 = 28
            self.font_size_edit_3 = 28
            self.font_family_edit_1 = "Monospace"
            self.font_family_edit_2 = "Monospace"
            self.font_family_edit_3 = "Monospace"
        else:
            self.accessibility = 0
            self.edit_1.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 14pt;")
            self.edit_2.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 14pt;")
            self.edit_3.setStyleSheet("background-color: white; color: black; font-family: Monospace; font-size: 14pt;")
            self.font_size_edit_1 = 14
            self.font_size_edit_2 = 14
            self.font_size_edit_3 = 14
            self.font_family_edit_1 = "Monospace"
            self.font_family_edit_2 = "Monospace"
            self.font_family_edit_3 = "Monospace"

    # -- EDIT-1
    def increase_font_size_edit_1(self):
        self.font_size_edit_1 += 2
        self.edit_1.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_1, self.font_size_edit_1))

    def decrease_font_size_edit_1(self):
        self.font_size_edit_1 -= 2
        if self.font_size_edit_1 < 2:  # Ensure font size doesn't go below 2pt
            self.font_size_edit_1 = 2
        self.edit_1.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_1, self.font_size_edit_1))

    def toggle_font_family_edit_1(self):
        if self.font_family_edit_1 == "Monospace":
            self.font_family_edit_1 = "Courier"
        else:
            self.font_family_edit_1 = "Monospace"
        self.edit_1.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_1, self.font_size_edit_1))

    # -- EDIT-2
    def increase_font_size_edit_2(self):
        self.font_size_edit_2 += 2
        self.edit_2.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_2, self.font_size_edit_2))

    def decrease_font_size_edit_2(self):
        self.font_size_edit_2 -= 2
        if self.font_size_edit_2 < 2:  # Ensure font size doesn't go below 2pt
            self.font_size_edit_2 = 2
        self.edit_2.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_2, self.font_size_edit_2))

    def toggle_font_family_edit_2(self):
        if self.font_family_edit_2 == "Monospace":
            self.font_family_edit_2 = "Courier"
        else:
            self.font_family_edit_2 = "Monospace"
        self.edit_2.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_2, self.font_size_edit_2))

    # -- EDIT-3
    def increase_font_size_edit_3(self):
        self.font_size_edit_3 += 2
        self.edit_3.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_3, self.font_size_edit_3))

    def decrease_font_size_edit_3(self):
        self.font_size_edit_3 -= 2
        if self.font_size_edit_3 < 2:  # Ensure font size doesn't go below 2pt
            self.font_size_edit_3 = 2
        self.edit_3.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_3, self.font_size_edit_3))

    def toggle_font_family_edit_3(self):
        if self.font_family_edit_3 == "Monospace":
            self.font_family_edit_3 = "Courier"
        else:
            self.font_family_edit_3 = "Monospace"
        self.edit_3.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_edit_3, self.font_size_edit_3))


## -----------------------[ Split Save functions ]--------------
        
    def split_and_save_file(self):
        dialog = SplitSaveDialog()
        if dialog.exec_() == QDialog.Accepted:
            filename, marker = dialog.getInputs()
            # Correctly pass the obtained filename and marker to the method
            self.process_split_and_save(filename, marker)
        else:
            print("Dialog canceled.")

    def process_split_and_save(self, filename, marker):
        text_to_split = self.edit_3.toPlainText()
        parts = text_to_split.split(marker)

        for i, part in enumerate(parts, start=1):
            part_filename = f"{filename}_{i:03d}"
            try:
                with open(part_filename, 'w', encoding='utf-8') as file:
                    file.write(part)
            except Exception as e:
                print(f"Error saving {part_filename}: {str(e)}")

        QMessageBox.information(None, "Completed", "All parts have been processed and saved.")

    def show_creator_message(self):
        Aboutdialog = CreatorInfoDialog()
        Aboutdialog.exec_()


## -----------------------[ Text Editor essential functions ]--------------
    # Clear methods

    def ed1_clear(self):
        self.ed.clear_edit1()

    def ed2_clear(self):
        self.ed.clear_edit2()

    def ed3_clear(self):
        self.ed.clear_edit3()

    def edAll_clear(self):
        self.ed.clear_editALL()

    # Copy methods
    def copy_1_2(self):
        self.ed.copy_1_2()

    def copy_2_1(self):
        self.ed.copy_2_1()

    def copy_2_3(self):
        self.ed.copy_2_3()

    def copy_3_2(self):
        self.ed.copy_3_2()

    def chat(self):
        self.ed.chat_step()

    # File I/O methods
    # EDIT-1
    def open_ed1(self):
        self.ed.open_edit1()

    def append_ed1(self):       
        self.ed.append_multiple_1()

    def save_ed1(self):   
        self.ed.save_edit1()
    
    def ed1_clipboard(self):
        self.ed.clipboard_edit1()

    # EDIT-2
    def open_ed2(self):
        self.ed.open_edit2()

    def append_ed2(self):       
        self.ed.append_multiple_2()

    def save_ed2(self):   
        self.ed.save_edit2()

    def load_ppt(self):
        self.ed.load_ppt_to_edit2()

    def crush_ppt(self):
        self.ed.ppt_crusher()

    def ed2_clipboard(self):
        self.ed.clipboard_edit2()

    def fetch_url(self):
        self.ed.fetch_url(max_web_chars=self.max_web_chars)
    
    def fetch_file(self):
        self.ed.fetch_file()

    def S3_manager(self):
        self.aws.ascendS3Manager(self.clients,edit_1=self.edit_1, edit_2=self.edit_2, edit_3=self.edit_3)

    def file_lister(self):
        self.ed.file_lister()

    # EDIT-3
    def open_ed3(self):
        self.ed.open_edit3()

    def append_ed3(self):       
        self.ed.append_multiple_3()

    def save_ed3(self):   
        self.ed.save_edit3()

    def split_ed3(self): 
        self.split_and_save_file()

    def display_as_markdown(self): 
        self.ed.display_as_markdown()

    def ed3_clipboard(self):
        self.ed.clipboard_edit3()
    
    def save_ppt(self):
        self.ed.save_to_ppt(self.startup_location)

    def hatch_ppt(self):
        self.ed.hatch_ppt(self.startup_location)

    def file_merge(self):
        self.fm.file_merge()

    def scan_text_files(self):
        self.ed.scan_text_files()

    def select_directories(self):
        self.ed.select_directories()

    def save_as_csv(self):
        self.ed.save_as_csv()

    def pdf_crusher(self):
        self.ed.pdf_crusher()

## -----------------------[ Model Settings Control ]--------------
    def adjust_settings(self):
        dialog = SettingsForm(self.model_settings, self)
        if dialog.exec_():
            self.model_settings = dialog.getSettings()
            # Now self.model_settings contains the updated settings

## -----------------------[ Credentials Control ]--------------
            
    def adjust_credentials(self):  
        self.aws.load_credentials(self.clients)

## -----------------------[ Wayback Control ]--------------
    def wayback_machine(self):  
        self.ai.wayback_machine()

    def wayback_recall(self):  
        self.ai.wayback_recall()

## -----------------------[ Talk with AI Models ]--------------

    def talk_with_claudev21(self):  
        if self.batchmode == 1:
            self.ai.talk_with_claudev21_batch(self.clients)
        else:
            self.ai.talk_with_claudev21(self.clients)

    def talk_with_claudeOpus(self): 
        pass
    #    if self.batchmode == 1: 
    #        self.ai.talk_with_claudeOpus_batch(self.clients)
    #    else:
    #        self.ai.talk_with_claudeOpus(self.clients)

    def talk_with_claudev3(self): 
        if self.batchmode == 1: 
            self.ai.talk_with_claudev3_batch(self.clients)
        else:
            self.ai.talk_with_claudev3(self.clients)

    def talk_with_claudev35(self): 
        if self.batchmode == 1: 
            self.ai.talk_with_claudev35_batch(self.clients)
        else:
            self.ai.talk_with_claudev35(self.clients)

    def talk_with_claudeH(self): 
        if self.batchmode == 1: 
            self.ai.talk_with_claudeH_batch(self.clients)
        else:
            self.ai.talk_with_claudeH(self.clients)

    def talk_with_titan_premiere(self):  
        if self.batchmode == 1:
            self.ai.talk_with_titan_premiere_batch(self.clients)
        else:
            self.ai.talk_with_titan_premiere(self.clients)


    def talk_with_titan_express(self):  
        if self.batchmode == 1:
            self.ai.talk_with_titan_express_batch(self.clients)
        else:
            self.ai.talk_with_titan_express(self.clients)

    def talk_with_titan_lite(self):  
        if self.batchmode == 1:
            self.ai.talk_with_titan_lite_batch(self.clients)
        else:
            self.ai.talk_with_titan_lite(self.clients)

    def talk_with_jurassic_mid(self):  
        if self.batchmode == 1:
            self.ai.talk_with_jurassic_mid_batch(self.clients)
        else:
            self.ai.talk_with_jurassic_mid(self.clients)

    def talk_with_jurassic_ultra(self):  
        if self.batchmode == 1:
            self.ai.talk_with_jurassic_ultra_batch(self.clients)
        else:
            self.ai.talk_with_jurassic_ultra(self.clients)

    def talk_with_llama_13B(self):  
        if self.batchmode == 1:
            self.ai.talk_with_llama_13B_batch(self.clients)
        else:
            self.ai.talk_with_llama_13B(self.clients)

    def talk_with_llama_70B(self):  
        if self.batchmode == 1:
            self.ai.talk_with_llama_70B_batch(self.clients)
        else:
            self.ai.talk_with_llama_70B(self.clients)

    def talk_with_cohere(self):  
        if self.batchmode == 1:
            self.ai.talk_with_cohere_batch(self.clients)
            pass
        else:
            self.ai.talk_with_cohere(self.clients)

    def talk_with_cohereR(self):  
        if self.batchmode == 1:
            #self.ai.talk_with_cohereR_batch(self.clients)
            pass
        else:
            self.ai.talk_with_cohereR(self.clients)
            pass

    def talk_with_cohereRP(self):  
        if self.batchmode == 1:
            #self.ai.talk_with_cohereRP_batch(self.clients)
            pass
        else:
            self.ai.talk_with_cohereRP(self.clients)


    def talk_with_mistral(self):  
        if self.batchmode == 1:
            self.ai.talk_with_mistral_batch(self.clients)
        else:
            self.ai.talk_with_mistral(self.clients)

    def talk_with_mistral8x(self):  
        if self.batchmode == 1:
            self.ai.talk_with_mistral8x_batch(self.clients)
        else:
            self.ai.talk_with_mistral8x(self.clients)

    def talk_with_mistral_large(self):  
        if self.batchmode == 1:
            self.ai.talk_with_mistral_large_batch(self.clients)
        else:
            self.ai.talk_with_mistral(self.clients)

    def claude_3_image(self): 
        if self.batchmode == 1:
            self.ai.claude_3_image_batch(self.clients)
        else:
            self.ai.claude_3_image(self.clients)

    def titan_G1_embed(self): 
        if self.batchmode == 1:
            # self.ai.titan_G1_embed_batch(self.clients)
            pass
        else:
            self.ai.titan_G1_embed(self.clients)

    def titan_text_embed(self): 
        if self.batchmode == 1:
            self.ai.talk_with_titan_text_embeddings_batch(self.clients)
            pass
        else:
            self.ai.talk_with_titan_text_embeddings(self.clients)

    ## Nova models
    def talk_with_novaPro(self): 
        if self.batchmode == 1:
            self.ai.talk_with_novaPro_batch(self.clients)
            pass
        else:
            self.ai.talk_with_novaPro(self.clients)
            pass

    def talk_with_novaLite(self): 
        if self.batchmode == 1:
            self.ai.talk_with_novaLite_batch(self.clients)
            pass
        else:
            self.ai.talk_with_novaLite(self.clients)
            pass

    def talk_with_novaLite_MM(self): 
        if self.batchmode == 1:
            # self.ai.talk_with_novaLite_batch(self.clients)
            pass
        else:
            self.ai.talk_with_novaLite_MM(self.clients)
            pass

    def talk_with_novaPro_MM(self): 
        if self.batchmode == 1:
            # self.ai.talk_with_novaLite_batch(self.clients)
            pass
        else:
            self.ai.talk_with_novaPro_MM(self.clients)
            pass

    def talk_with_novaMicro(self): 
        if self.batchmode == 1:
            self.ai.talk_with_novaMicro_batch(self.clients)
            pass
        else:
            self.ai.talk_with_novaMicro(self.clients)
            pass

    def talk_with_novaCanvas(self): 
        if self.batchmode == 1:
            #self.ai.talk_with_novaCanvas_batch(self.clients)
            pass
        else:
            self.ai.talk_with_novaCanvas(self.clients)
            pass

    def talk_with_novaReel(self): 
        if self.batchmode == 1:
            #self.ai.talk_with_novaReel_batch(self.clients)
            pass
        else:
            #self.ai.talk_with_novaReel(self.clients)
            pass




    def ImageGen(self):   
        self.im.openIMG()
    
    def CurDev(self):   
        self.cd.openCD()

    def select_files(self):  
        self.ai.select_files_for_batch()

    def process_batch_files(self):  
        self.ai.test_batch(self.clients)

    def titan_image(self):  
        self.ai.titan_image_gen(self.clients)

    def titan_image2(self):  
        self.ai.titan_image_gen2(self.clients)

    def stability_image(self):  
        self.ai.stability_image_gen(self.clients)

    def save_image_jpeg(self):  
        self.ai.save_image_as_jpeg(self.clients)

    def save_image_png(self):  
        self.ai.save_image_as_png(self.clients)

    # This sets the value used when fetching a file into the INPUT editors
    def set_web_max_size(self):
        # Display the current value and ask for a new one
        new_value, ok = QInputDialog.getInt(
            None, 'Set Maximum Size Fetch to Input', 
            f'Current maximum size of web content (chars): {self.max_web_chars}\nTotal max characters loaded into INPUT. \nEnter new maximum size:',
            self.max_web_chars, 1, 1000000, 1)
        if ok:
            self.max_web_chars = new_value
        else:
            QMessageBox.information(None, 'No Change', 'No new value was set.')

    # This sets the value used when preprocessing commands in the PROMPT and replacing them with web content
    def set_preprocess_web_size(self):
        self.ai.set_web_max_size()

    def open_webpage_promptlib(self):
        url = "https://quip-amazon.com/ABNUAZuhr6ko/TC-Curriculum-Prompt-Catalog"  # Internal T&C Prompt Catalog URL
        webbrowser.open(url)
    def test(self):  
        # self.ai.processFilesNEW()
        pass


    ## -- Localiazation
    #
    def language_selector(self):
        # Call the LanguageSelector dialog with current language codes
        selector = LanguageSelector(
            self,
            input_language=self.input_language,
            output_language=self.output_language,
            spoken_language=self.spoken_language
        )
        
        if selector.exec_() == QDialog.Accepted:
            # Get the selected languages directly from the combo boxes
            input_language = selector.input_language_combo.currentText()
            output_language = selector.output_language_combo.currentText()
            spoken_language = selector.spoken_language_combo.currentText()
            selected_voice = selector.voice_selector_combo.currentText()  # Get the selected voice name

            # Print or use the selected values
            print(f"Input Language: {input_language}")
            print(f"Output Language: {output_language}")
            print(f"Spoken Language: {spoken_language}")
            print(f"Selected Voice: {selected_voice}")

            # You can now store or use these values as needed
            self.input_language = selector.languages.get(input_language, None)
            self.output_language = selector.languages.get(output_language, None)
            self.spoken_language = selector.spoken_languages.get(spoken_language, None)
            spoken_language_code = selector.spoken_languages.get(spoken_language, None)
            if spoken_language_code:
                self.voice_name = selected_voice  # The selected voice from the combo box
                print(f"Voice Name: {self.voice_name}")

    #
    def translate(self):
        if 'translate' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Retrieve the input text from self.edit3
        input_text = self.edit_2.toPlainText()

        #print("\n\n$$$$ DEBUG 01> input_text",input_text)
        if not input_text.strip():
            self.edit_3.setPlainText("No input text provided.")
            return

        try:
            # Perform translation using the client
            response = self.clients['translate'].translate_text(
                Text=input_text,
                SourceLanguageCode=self.input_language,  # Source text language
                TargetLanguageCode=self.output_language  # Target text language
            )
            #print("\n\n$$$$ DEBUG 02> response",response)
            # Extract the translated text
            translated_text = response['TranslatedText']

            # Display the translated text in self.edit2
            self.edit_3.setPlainText(translated_text)
        except Exception as e:
            # Handle any errors and display them in self.edit2
            # print("\n\n$$$$ DEBUG 03> Error ",e)
            error_message = f"Error during translation: {str(e)}"
            self.edit_3.setPlainText(error_message)


    def save_spoken_language(self):
        if 'polly' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the text to be converted to speech
        translated_text = self.edit_3.toPlainText()

        # Get the language code from self.spoken_language (assuming it's a valid language code string)
        # lang_name = self.voice_name

        # Get supported engines for the selected voice
        supported_engines = self.get_voice_engine_support(self.voice_name)
        if not supported_engines:
            QMessageBox.warning(None, 'Warning', f"The voice '{self.voice_name}' is not valid.")
            return

        # Favor the best quality
        if 'generative' in supported_engines:
            engine = 'generative'
        elif 'neural' in supported_engines:
            engine = 'neural'
        else:
            engine = 'standard'

        # Submit the text to Polly and get the audio response
        polly_response = self.clients['polly'].synthesize_speech(
            Text=translated_text,
            OutputFormat='mp3',
            Engine=engine,  # 'neural' for better quality
            VoiceId=self.voice_name  # Use the selected voice for the language
        )

        # Open file dialog to let the user choose the save location
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save MP3 File", "", "MP3 Files (*.mp3);;All Files (*)", options=options)

        if file_path:
            # Write the MP3 file to the chosen location
            with open(file_path, 'wb') as file:
                file.write(polly_response['AudioStream'].read())

            # Store the output audio file path for later playback
            self.output_audio_file = file_path

            # Optionally show confirmation message or log
            print(f"Speech saved to {file_path}")
        else:
            print("File save operation canceled.")


    def get_voice_engine_support(self, voice_id):
        response = self.clients['polly'].describe_voices()
        for voice in response['Voices']:
            if voice['Id'] == voice_id:
                return voice['SupportedEngines']
        return None
    
    

    def read_edit_3(self):
        if 'polly' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        # Check if the content in edit_3 has changed
        if self.edit_3.toPlainText() != self.last_edit_3:
            # Get the text to be converted to speech
            translated_text = self.edit_3.toPlainText()

            # Get supported engines for the selected voice
            supported_engines = self.get_voice_engine_support(self.voice_name)
            if not supported_engines:
                QMessageBox.warning(None, 'Warning', f"The voice '{self.voice_name}' is not valid.")
                return

            # Favor the best quality
            if 'generative' in supported_engines:
                engine = 'generative'
            elif 'neural' in supported_engines:
                engine = 'neural'
            else:
                engine = 'standard'



            # Submit the text to Polly and get the audio response
            polly_response = self.clients['polly'].synthesize_speech(
                Text=translated_text,
                OutputFormat='mp3',
                Engine=engine,  # 'neural' for better quality
                VoiceId=self.voice_name  # Use the selected voice for the language
            )

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.reading_audio_file = os.path.join(self.reading_dir, f"read_{timestamp}.mp3")
            # Write to audio file with the new content
            with open(self.reading_audio_file, 'wb') as file:
                file.write(polly_response['AudioStream'].read())

            # Update the last edit state
            self.last_edit_3 = self.edit_3.toPlainText()

            # Load and play the audio if it wasn't already playing
            if not pygame.mixer.music.get_busy():  # Check if music is already playing
                try:
                    pygame.mixer.music.load(self.reading_audio_file)
                    pygame.mixer.music.play(loops=0, start=0.0)
                    self.is_playing = True
                except pygame.error as e:
                    print(f"Error playing the audio: {e}")
                    QMessageBox.warning(None, 'Error', 'Unable to play audio.')
        else:
            # If the content hasn't changed, just toggle play/pause
            self.play_or_pause_reading()

    def play_or_pause_reading(self):
        if self.is_playing or pygame.mixer.music.get_busy():  # If music is playing, pause it
            pygame.mixer.music.pause()  # Pause the music
            self.is_playing = False
        else:
            pygame.mixer.music.unpause()  # Unpause and resume
            self.is_playing = True




def main():
    app = QApplication(sys.argv)
    ex = AscendWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




'''
Voice:  {'Gender': 'Female', 'Id': 'Isabelle', 'LanguageCode': 'fr-BE', 'LanguageName': 'Belgian French', 'Name': 'Isabelle', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Danielle', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Danielle', 'SupportedEngines': ['generative', 'long-form', 'neural']}
Voice:  {'Gender': 'Male', 'Id': 'Gregory', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Gregory', 'SupportedEngines': ['long-form', 'neural']}
Voice:  {'Gender': 'Female', 'Id': 'Burcu', 'LanguageCode': 'tr-TR', 'LanguageName': 'Turkish', 'Name': 'Burcu', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Jitka', 'LanguageCode': 'cs-CZ', 'LanguageName': 'Czech', 'Name': 'Jitka', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Sabrina', 'LanguageCode': 'de-CH', 'LanguageName': 'Swiss Standard German', 'Name': 'Sabrina', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Patrick', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Patrick', 'SupportedEngines': ['long-form']}
Voice:  {'Gender': 'Female', 'Id': 'Alba', 'LanguageCode': 'es-ES', 'LanguageName': 'Castilian Spanish', 'Name': 'Alba', 'SupportedEngines': ['long-form']}
Voice:  {'Gender': 'Male', 'Id': 'Raul', 'LanguageCode': 'es-ES', 'LanguageName': 'Castilian Spanish', 'Name': 'Raul', 'SupportedEngines': ['long-form']}
Voice:  {'Gender': 'Female', 'Id': 'Joanna', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Joanna', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Ruth', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Ruth', 'SupportedEngines': ['generative', 'long-form', 'neural']}
Voice:  {'Gender': 'Female', 'Id': 'Lupe', 'LanguageCode': 'es-US', 'LanguageName': 'US Spanish', 'Name': 'Lupe', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Kevin', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Kevin', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Filiz', 'LanguageCode': 'tr-TR', 'LanguageName': 'Turkish', 'Name': 'Filiz', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Elin', 'LanguageCode': 'sv-SE', 'LanguageName': 'Swedish', 'Name': 'Elin', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Astrid', 'LanguageCode': 'sv-SE', 'LanguageName': 'Swedish', 'Name': 'Astrid', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Tatyana', 'LanguageCode': 'ru-RU', 'LanguageName': 'Russian', 'Name': 'Tatyana', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Maxim', 'LanguageCode': 'ru-RU', 'LanguageName': 'Russian', 'Name': 'Maxim', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Carmen', 'LanguageCode': 'ro-RO', 'LanguageName': 'Romanian', 'Name': 'Carmen', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Ines', 'LanguageCode': 'pt-PT', 'LanguageName': 'Portuguese', 'Name': 'Inês', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Cristiano', 'LanguageCode': 'pt-PT', 'LanguageName': 'Portuguese', 'Name': 'Cristiano', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Vitoria', 'LanguageCode': 'pt-BR', 'LanguageName': 'Brazilian Portuguese', 'Name': 'Vitória', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Ricardo', 'LanguageCode': 'pt-BR', 'LanguageName': 'Brazilian Portuguese', 'Name': 'Ricardo', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Camila', 'LanguageCode': 'pt-BR', 'LanguageName': 'Brazilian Portuguese', 'Name': 'Camila', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Maja', 'LanguageCode': 'pl-PL', 'LanguageName': 'Polish', 'Name': 'Maja', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Jan', 'LanguageCode': 'pl-PL', 'LanguageName': 'Polish', 'Name': 'Jan', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Jacek', 'LanguageCode': 'pl-PL', 'LanguageName': 'Polish', 'Name': 'Jacek', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Ewa', 'LanguageCode': 'pl-PL', 'LanguageName': 'Polish', 'Name': 'Ewa', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Ola', 'LanguageCode': 'pl-PL', 'LanguageName': 'Polish', 'Name': 'Ola', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Lisa', 'LanguageCode': 'nl-BE', 'LanguageName': 'Belgian Dutch', 'Name': 'Lisa', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Ruben', 'LanguageCode': 'nl-NL', 'LanguageName': 'Dutch', 'Name': 'Ruben', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Lotte', 'LanguageCode': 'nl-NL', 'LanguageName': 'Dutch', 'Name': 'Lotte', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Laura', 'LanguageCode': 'nl-NL', 'LanguageName': 'Dutch', 'Name': 'Laura', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Ida', 'LanguageCode': 'nb-NO', 'LanguageName': 'Norwegian', 'Name': 'Ida', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Liv', 'LanguageCode': 'nb-NO', 'LanguageName': 'Norwegian', 'Name': 'Liv', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Seoyeon', 'LanguageCode': 'ko-KR', 'LanguageName': 'Korean', 'Name': 'Seoyeon', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Kazuha', 'LanguageCode': 'ja-JP', 'LanguageName': 'Japanese', 'Name': 'Kazuha', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Tomoko', 'LanguageCode': 'ja-JP', 'LanguageName': 'Japanese', 'Name': 'Tomoko', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Takumi', 'LanguageCode': 'ja-JP', 'LanguageName': 'Japanese', 'Name': 'Takumi', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Mizuki', 'LanguageCode': 'ja-JP', 'LanguageName': 'Japanese', 'Name': 'Mizuki', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Bianca', 'LanguageCode': 'it-IT', 'LanguageName': 'Italian', 'Name': 'Bianca', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Giorgio', 'LanguageCode': 'it-IT', 'LanguageName': 'Italian', 'Name': 'Giorgio', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Carla', 'LanguageCode': 'it-IT', 'LanguageName': 'Italian', 'Name': 'Carla', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Karl', 'LanguageCode': 'is-IS', 'LanguageName': 'Icelandic', 'Name': 'Karl', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Dora', 'LanguageCode': 'is-IS', 'LanguageName': 'Icelandic', 'Name': 'Dóra', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Mathieu', 'LanguageCode': 'fr-FR', 'LanguageName': 'French', 'Name': 'Mathieu', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Lea', 'LanguageCode': 'fr-FR', 'LanguageName': 'French', 'Name': 'Léa', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Celine', 'LanguageCode': 'fr-FR', 'LanguageName': 'French', 'Name': 'Céline', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Chantal', 'LanguageCode': 'fr-CA', 'LanguageName': 'Canadian French', 'Name': 'Chantal', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Gabrielle', 'LanguageCode': 'fr-CA', 'LanguageName': 'Canadian French', 'Name': 'Gabrielle', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Penelope', 'LanguageCode': 'es-US', 'LanguageName': 'US Spanish', 'Name': 'Penélope', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Miguel', 'LanguageCode': 'es-US', 'LanguageName': 'US Spanish', 'Name': 'Miguel', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Mia', 'LanguageCode': 'es-MX', 'LanguageName': 'Mexican Spanish', 'Name': 'Mia', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Lucia', 'LanguageCode': 'es-ES', 'LanguageName': 'Castilian Spanish', 'Name': 'Lucia', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Enrique', 'LanguageCode': 'es-ES', 'LanguageName': 'Castilian Spanish', 'Name': 'Enrique', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Conchita', 'LanguageCode': 'es-ES', 'LanguageName': 'Castilian Spanish', 'Name': 'Conchita', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Geraint', 'LanguageCode': 'en-GB-WLS', 'LanguageName': 'Welsh English', 'Name': 'Geraint', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Salli', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Salli', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Matthew', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Matthew', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Kimberly', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Kimberly', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Kendra', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Kendra', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Justin', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Justin', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Joey', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Joey', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Ivy', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Ivy', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Aria', 'LanguageCode': 'en-NZ', 'LanguageName': 'New Zealand English', 'Name': 'Aria', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Ayanda', 'LanguageCode': 'en-ZA', 'LanguageName': 'South African English', 'Name': 'Ayanda', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Female', 'Id': 'Raveena', 'LanguageCode': 'en-IN', 'LanguageName': 'Indian English', 'Name': 'Raveena', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Aditi', 'LanguageCode': 'en-IN', 'LanguageName': 'Indian English', 'Name': 'Aditi', 'AdditionalLanguageCodes': ['hi-IN'], 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Emma', 'LanguageCode': 'en-GB', 'LanguageName': 'British English', 'Name': 'Emma', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Brian', 'LanguageCode': 'en-GB', 'LanguageName': 'British English', 'Name': 'Brian', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Amy', 'LanguageCode': 'en-GB', 'LanguageName': 'British English', 'Name': 'Amy', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Male', 'Id': 'Russell', 'LanguageCode': 'en-AU', 'LanguageName': 'Australian English', 'Name': 'Russell', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Nicole', 'LanguageCode': 'en-AU', 'LanguageName': 'Australian English', 'Name': 'Nicole', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Olivia', 'LanguageCode': 'en-AU', 'LanguageName': 'Australian English', 'Name': 'Olivia', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Female', 'Id': 'Vicki', 'LanguageCode': 'de-DE', 'LanguageName': 'German', 'Name': 'Vicki', 'SupportedEngines': ['generative', 'neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Marlene', 'LanguageCode': 'de-DE', 'LanguageName': 'German', 'Name': 'Marlene', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Hans', 'LanguageCode': 'de-DE', 'LanguageName': 'German', 'Name': 'Hans', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Naja', 'LanguageCode': 'da-DK', 'LanguageName': 'Danish', 'Name': 'Naja', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Male', 'Id': 'Mads', 'LanguageCode': 'da-DK', 'LanguageName': 'Danish', 'Name': 'Mads', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Sofie', 'LanguageCode': 'da-DK', 'LanguageName': 'Danish', 'Name': 'Sofie', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Gwyneth', 'LanguageCode': 'cy-GB', 'LanguageName': 'Welsh', 'Name': 'Gwyneth', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Zhiyu', 'LanguageCode': 'cmn-CN', 'LanguageName': 'Chinese Mandarin', 'Name': 'Zhiyu', 'SupportedEngines': ['neural', 'standard']}
Voice:  {'Gender': 'Female', 'Id': 'Zeina', 'LanguageCode': 'arb', 'LanguageName': 'Arabic', 'Name': 'Zeina', 'SupportedEngines': ['standard']}
Voice:  {'Gender': 'Female', 'Id': 'Hala', 'LanguageCode': 'ar-AE', 'LanguageName': 'Gulf Arabic', 'Name': 'Hala', 'AdditionalLanguageCodes': ['arb'], 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Arlet', 'LanguageCode': 'ca-ES', 'LanguageName': 'Catalan', 'Name': 'Arlet', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Hannah', 'LanguageCode': 'de-AT', 'LanguageName': 'Austrian German', 'Name': 'Hannah', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Stephen', 'LanguageCode': 'en-US', 'LanguageName': 'US English', 'Name': 'Stephen', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Female', 'Id': 'Kajal', 'LanguageCode': 'en-IN', 'LanguageName': 'Indian English', 'Name': 'Kajal', 'AdditionalLanguageCodes': ['hi-IN'], 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Female', 'Id': 'Hiujin', 'LanguageCode': 'yue-CN', 'LanguageName': 'Cantonese', 'Name': 'Hiujin', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Suvi', 'LanguageCode': 'fi-FI', 'LanguageName': 'Finnish', 'Name': 'Suvi', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Female', 'Id': 'Niamh', 'LanguageCode': 'en-IE', 'LanguageName': 'Irish English', 'Name': 'Niamh', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Arthur', 'LanguageCode': 'en-GB', 'LanguageName': 'British English', 'Name': 'Arthur', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Daniel', 'LanguageCode': 'de-DE', 'LanguageName': 'German', 'Name': 'Daniel', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Male', 'Id': 'Liam', 'LanguageCode': 'fr-CA', 'LanguageName': 'Canadian French', 'Name': 'Liam', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Pedro', 'LanguageCode': 'es-US', 'LanguageName': 'US Spanish', 'Name': 'Pedro', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Male', 'Id': 'Sergio', 'LanguageCode': 'es-ES', 'LanguageName': 'Castilian Spanish', 'Name': 'Sergio', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Male', 'Id': 'Andres', 'LanguageCode': 'es-MX', 'LanguageName': 'Mexican Spanish', 'Name': 'Andrés', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Male', 'Id': 'Remi', 'LanguageCode': 'fr-FR', 'LanguageName': 'French', 'Name': 'Rémi', 'SupportedEngines': ['generative', 'neural']}
Voice:  {'Gender': 'Male', 'Id': 'Adriano', 'LanguageCode': 'it-IT', 'LanguageName': 'Italian', 'Name': 'Adriano', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Thiago', 'LanguageCode': 'pt-BR', 'LanguageName': 'Brazilian Portuguese', 'Name': 'Thiago', 'SupportedEngines': ['neural']}
Voice:  {'Gender': 'Male', 'Id': 'Zayd', 'LanguageCode': 'ar-AE', 'LanguageName': 'Gulf Arabic', 'Name': 'Zayd', 'AdditionalLanguageCodes': ['arb'], 'SupportedEngines': ['neural']}
'''
