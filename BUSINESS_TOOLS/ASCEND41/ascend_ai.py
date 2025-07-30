# ascend_ai.py
# Forge Ascend v4.1
# Updated by Tom Stern, 16 DEC 2024
#
#   based on Ascend 1 -- first version January 22 2024 -- by Tom Stern

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
import json
from datetime import datetime
import sys
import re
import io
from datetime import datetime
from pathlib import Path
from PIL import Image
import base64
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFrame,
    QMainWindow, QRadioButton, QGridLayout, QGroupBox, QFormLayout, QFileDialog, QDialog, QMessageBox,
    QLineEdit
)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtCore import QUrl, QEventLoop

## ---------------------------- Wayback Dialogs ----------------

class WaybackDialog(QDialog):
    def __init__(self,initial_wayback_file="",edit_1=None,edit_2=None,edit_3=None,wayback=None):
        super().__init__()
        self.wayback_file = initial_wayback_file 
        self.edit_1 = edit_1
        self.edit_2 = edit_2
        self.edit_3 = edit_3
        self.wayback = wayback 
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Wayback Checkpointing Control')

        # ------------------[ Coloring Kit ]---------------------
        self.setStyleSheet("background-color: #E6E6E6; color: black;")
        self.buttonStyle_9 = """
        QPushButton {
            background-color: #C4E0EF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal; 
            border: 1px solid #000000;
            border-radius: 2px;
            }
            QPushButton:hover { background-color: #5b5b5b; color: #FFFFFF;}
            QPushButton:pressed { background-color: #FF0000; color: #000000; }
        """
        self.lineStyle_9 = """
        QLineEdit{
            background-color: #FFFFFF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal; 
            border: 1px solid #000000; }
        """
        #  self.fileNameDisplay.setStyleSheet(self.lineStyle_9)
        #  self.stopButton.setStyleSheet(self.buttonStyle_9)
        #  ------------------[ Coloring Kit ]---------------------

        # Main layout is vertical
        mainLayout = QVBoxLayout()

        # Text box displaying a date time stamp
        # self.textBox = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_label=QLabel("Wayback is ON")
        if self.wayback == 1:
            self.status_label.setText("Wayback is ON")
        else:
            self.status_label.setText("Wayback is OFF")

        mainLayout.addWidget(self.status_label)


        # mainLayout.addWidget(self.textBox)
        # File name display text box
        self.fileNameDisplay = QLineEdit(self.wayback_file)
        self.fileNameDisplay.setStyleSheet(self.lineStyle_9)
        mainLayout.addWidget(self.fileNameDisplay)  

        # Second row of buttons
        secondRowLayout = QHBoxLayout()
        self.startButton = QPushButton("ON")
        self.startButton.setToolTip("Turn on Wayback automatic checkpointing")
        self.startButton.setStyleSheet(self.buttonStyle_9)
        self.saveNowButton = QPushButton("SAVE NOW")
        self.saveNowButton.setToolTip("Create a checkpoint to capture the current state.")
        self.saveNowButton.setStyleSheet(self.buttonStyle_9)
        self.stopButton = QPushButton("OFF")
        self.stopButton.setToolTip("Turn off Wayback automatic checkpointing.")
        self.stopButton.setStyleSheet(self.buttonStyle_9)
        secondRowLayout.addWidget(self.startButton)
        secondRowLayout.addWidget(self.saveNowButton)
        secondRowLayout.addWidget(self.stopButton)
        mainLayout.addLayout(secondRowLayout)

        # Third row of buttons
        thirdRowLayout = QHBoxLayout()
        self.setWaybackFileButton = QPushButton("SET WAYBACK FILE")
        self.setWaybackFileButton.setToolTip("Manually select the Wayback file for reading or writing.")
        self.setWaybackFileButton.setStyleSheet(self.buttonStyle_9)
        thirdRowLayout.addWidget(self.setWaybackFileButton)
        self.clearWaybackFileButton = QPushButton("CLEAR WAYBACK FILE")
        self.clearWaybackFileButton.setToolTip("Remove all entries in the current checkpointing file.")
        self.clearWaybackFileButton.setStyleSheet(self.buttonStyle_9)
        thirdRowLayout.addWidget(self.clearWaybackFileButton)
        self.okButton = QPushButton("OK")  
        self.okButton.setToolTip("Close the Wayback checkpointing control panel.")
        self.okButton.setStyleSheet(self.buttonStyle_9)
        thirdRowLayout.addWidget(self.okButton) 
        self.okButton.clicked.connect(self.accept)  
        mainLayout.addLayout(thirdRowLayout)

        self.setLayout(mainLayout)

        # Connecting signals
        self.saveNowButton.clicked.connect(self.saveNowPressed)
        self.startButton.clicked.connect(lambda: self.setWayback(1))
        self.stopButton.clicked.connect(lambda: self.setWayback(0))
        self.setWaybackFileButton.clicked.connect(self.setWaybackFile)
        self.clearWaybackFileButton.clicked.connect(self.clearWaybackFile)

        # Variables to store button press states and wayback file name
        self.save_now_pressed = False
 

    def saveNowPressed(self):
        print(self.edit_1.toPlainText)
        self.save_now_pressed = True
        # Prepare the new log entry with placeholders for edit_1, edit_2, edit_3 contents
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "MODEL": "User Save",
            "INPUT": self.edit_1.toPlainText(),
            "COMMAND": self.edit_2.toPlainText(),
            "RESPONSE": self.edit_3.toPlainText(),
            "PARAMETERS": "Parameters not available."
        }
        # self.textBox = new_entry["timestamp"]
        
        try:
            # Attempt to read existing data
            try:
                with open(self.wayback_file, 'r') as file:
                    log_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                # If the file doesn't exist or is empty, start a new log
                log_data = []

            # Append the new entry
            log_data.append(new_entry)

            # Write the updated log data back to the file
            with open(self.wayback_file, 'w') as file:
                json.dump(log_data, file, indent=4)
        except Exception as e:
            print(f"Failed to log entry: {e}")


    def setWayback(self, value):
        self.wayback = value
        if self.wayback == 1:
            self.status_label.setText("Wayback is ON")
        else:
            self.status_label.setText("Wayback is OFF")


    def setWaybackFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Set Wayback File", "", "JSON Files (*.json)", options=options)
        if fileName:
            if not fileName.endswith('.json'):
                fileName += '.json'
            self.wayback_file = fileName
            self.fileNameDisplay.setText(fileName) 
            # This part just sets the file name.

    def clearWaybackFile(self):
        # Check if the wayback_file attribute has been set and is not empty
        if self.wayback_file:
            try:
                # Open the file in write mode and write an empty list to it
                with open(self.wayback_file, 'w') as file:
                    json.dump([], file)
                QMessageBox.information(self, "Success", "The wayback file has been cleared.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to clear the wayback file: {e}")
        else:
            QMessageBox.warning(self, "Error", "No wayback file is set.")

class WaybackRecallDialog(QDialog):
    def __init__(self, initial_wayback_file="", edit_1=None, edit_2=None, edit_3=None):
        super().__init__()
        self.wayback_file = initial_wayback_file
        self.edit_1 = edit_1
        self.edit_2 = edit_2
        self.edit_3 = edit_3
        self.current_index = -1  # Will be set to the last record after loading
        self.log_data = []  # Initialize as empty list
        self.loadLogData()
        self.initUI()
        self.updateUI()  # Method to update UI with current log entry


    def initUI(self):
        self.setWindowTitle('Wayback Checkpoint Inspect and Restore')

        # ------------------[ Coloring Kit ]---------------------
        self.setStyleSheet("background-color: #E6E6E6; color: black;")
        self.buttonStyle_9 = """
        QPushButton {
            background-color: #C4E0EF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal; 
            border: 1px solid #000000;
            border-radius: 2px;
            }
            QPushButton:hover { background-color: #5b5b5b; color: #FFFFFF;}
            QPushButton:pressed { background-color: #FF0000; color: #000000; }
        """
        self.lineStyle_9 = """
        QLineEdit{
            background-color: #FFFFFF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal; 
            border: 1px solid #000000; }
        """
        self.textStyle_9 = """
        QTextEdit{
            background-color: #FFFFFF;
            color: #000000;
            font-family: Arial; 
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal; 
            border: 1px solid #000000; }
        """
        #  self.Display.setStyleSheet(self.lineStyle_9)
        #  self.Button.setStyleSheet(self.buttonStyle_9)
        #  ------------------[ Coloring Kit ]---------------------

        mainLayout = QVBoxLayout()

        # Text box displaying the current log entry timestamp
        self.textBox = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.textBox.setStyleSheet(self.lineStyle_9)
        mainLayout.addWidget(self.textBox)
        # Text box displaying the model used to generate the current log entry
        self.textBoxModel = QLineEdit("AI Model")
        self.textBoxModel.setStyleSheet(self.lineStyle_9)
        mainLayout.addWidget(self.textBoxModel)
        self.edit_parameters = QTextEdit(self)
        self.edit_parameters.setStyleSheet(self.textStyle_9)
        self.edit_parameters.setReadOnly(True) 
        self.edit_parameters.setFixedSize(400, 200)
        mainLayout.addWidget(self.edit_parameters)

        # File name display
        self.fileNameDisplay = QLineEdit(self.wayback_file)
        self.fileNameDisplay.setStyleSheet(self.lineStyle_9)
        mainLayout.addWidget(self.fileNameDisplay)

        # Navigation buttons
        firstRowLayout = QHBoxLayout()
        self.backwardButton = QPushButton("BACKWARD")
        self.backwardButton.setToolTip("Select prior checkpoint.")
        self.backwardButton.setStyleSheet(self.buttonStyle_9)
        self.forwardButton = QPushButton("FORWARD")
        self.forwardButton.setToolTip("Select next checkpoint.")
        self.forwardButton.setStyleSheet(self.buttonStyle_9)
        firstRowLayout.addWidget(self.backwardButton)
        firstRowLayout.addWidget(self.forwardButton)
        mainLayout.addLayout(firstRowLayout)

        # Connect navigation buttons to methods
        self.backwardButton.clicked.connect(self.previousRecord)
        self.forwardButton.clicked.connect(self.nextRecord)

        # Close button
        thirdRowLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.setToolTip("Close Wayback session log panel.")
        self.okButton.setStyleSheet(self.buttonStyle_9)
        thirdRowLayout.addWidget(self.okButton)
        self.okButton.clicked.connect(self.accept)
        mainLayout.addLayout(thirdRowLayout)

        self.setLayout(mainLayout)      

    def loadLogData(self):
        try:
            with open(self.wayback_file, 'r') as file:
                self.log_data = json.load(file)
                self.current_index = len(self.log_data) - 1  # Set to last record
        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Error", "Could not load or decode the Wayback file.")

    def nextRecord(self):
        if self.current_index < len(self.log_data) - 1:  # Check if not on last record
            self.current_index += 1
            self.updateUI()
        else:
            QMessageBox.information(self, "End of Records", "You are at the latest record.")

    def previousRecord(self):
        if self.current_index > 0:  # Check if not on first record
            self.current_index -= 1
            self.updateUI()
        else:
            QMessageBox.information(self, "Start of Records", "You are at the earliest record.")

    def updateUI(self):
        if self.log_data and 0 <= self.current_index < len(self.log_data):
            current_entry = self.log_data[self.current_index]
            # Here, update your UI elements with current_entry data
            # For example:
            self.edit_1.setText(current_entry["COMMAND"])
            self.edit_2.setText(current_entry["INPUT"])
            self.edit_3.setText(current_entry["RESPONSE"])
            # You might also want to update a label with the timestamp
            self.textBox.setText(current_entry["timestamp"])
            self.textBoxModel.setText(current_entry["MODEL"])
            # Format the PARAMETERS dictionary as a JSON string for display
            parameters_json = json.dumps(current_entry.get("PARAMETERS", {}), indent=4)
            self.edit_parameters.setText(parameters_json)
        else:
            # Handle case where log_data is empty or current_index is out of bounds
            QMessageBox.information(self, "No Records", "No records to display.")





### ---- Main Class ---

class AIModelInteraction:
    def __init__(self, edit_1=None, edit_2=None, edit_3=None, model_settings=None, batchmode=None, wayback=None, clients=None ):
        self.edit_1 = edit_1
        self.edit_2 = edit_2
        self.edit_3 = edit_3
        self.model_settings = model_settings
        self.batchmode = batchmode
        self.wayback = wayback
        self.clients = clients
        self.max_preprocess_web_chars = 10000  ## Default 10,000 max characters

        self.startup_location = os.path.dirname(os.path.realpath(__file__))
        # Create a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # File name format: wabac_<timestamp>.json
    #    file_name = f"wabac_{timestamp}.json"
    #    self.wayback_file = os.path.join(self.startup_location, file_name)
        directory_name = "WABAC" 
        os.makedirs(directory_name, exist_ok=True)
        file_name = f"wabac_{timestamp}.json"
        self.wayback_file = os.path.join(directory_name, file_name)
        self.wayback = 1 ## Turn on
        self.wayback_init() ## Create the log file for this session

        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        # I have hard coded us-east-1 here to obviate data sovereignty and import/export issues. Revisit later.
        self.region_name = 'us-east-1'
        self.session_token = None
        self.credentials_mode = 1  # 1= tokens, 2=API creds environ, 3=API creds enter
        
        self.last_base64_image = "" # base64 of last generated image

        # Prepare for inline URL processing
        self.url = None
        self.downloaded_content = ""

## ------------------------- SETTINGS ---------------------------------
#  Handle conversion of model_settings to correct variable types

    def fetch_parameters(self, model_name):
        # Check if the provided model_name exists in the dictionary
        if model_name in self.model_settings:
            # Retrieve the settings for the provided model_name
            settings = self.model_settings[model_name]

            # Process and convert values directly
            for key, value in settings.items():
                if key in ['steps', 'seed', 'numberOfImages', 'max tokens', 'topK', 'maxT', 'seed', 'cfg_scale', 'steps', 'height', 'width' ]:
                    settings[key] = int(value)
                elif key in ['temp', 'topP', 'cfgScale']:
                    settings[key] = float(value)
                # Empty or string values are left as they are

            # Return the settings as a dictionary
            return settings
        else:
            # Handle the case where the model_name is not found (e.g., return an empty dictionary or raise an error)
            return {}


## -------------------------------[ Wayback Processing ]-------------------
    def wayback_machine(self):
        W_dialog = WaybackDialog(self.wayback_file,self.edit_1,self.edit_2,self.edit_3,self.wayback)
        result = W_dialog.exec_()
        if result == QDialog.Accepted:
            self.wayback = W_dialog.wayback
        self.wayback_file = W_dialog.wayback_file

    def wayback_recall(self):
        W_dialog = WaybackRecallDialog(self.wayback_file,self.edit_1,self.edit_2,self.edit_3)
        result = W_dialog.exec_()


    def wayback_init(self):
        # Prepare the new log entry with placeholders for edit_1, edit_2, edit_3 contents
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "MODEL": "Time Begins",
            "INPUT": "",
            "COMMAND": "",
            "RESPONSE": "",
            "PARAMETERS": "Parameters not available."
        }
        log_data = []
        log_data.append(new_entry)
        try:
            with open(self.wayback_file, 'w') as file:
                json.dump(log_data, file, indent=4)
        except Exception as e:
            print(f"Failed to create Wayback file: {e}")
             

## -------------------------------[ Batch Processing ]-------------------
    ## --- multiple select and append files to the edit_2 editor
    #
    def select_files_for_batch(self):
        # Open the file dialog to select multiple files
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Files", "", "All Files (*)")

        # Concatenate the file paths into a single string separated by newline characters
        file_paths_text = '\n'.join(file_paths)

        # Append the concatenated file paths to self.edit_2
        if file_paths_text:
            current_text = self.edit_2.toPlainText()
            if current_text:
                new_text = current_text + '\n' + file_paths_text
            else:
                new_text = file_paths_text
            self.edit_2.setPlainText(new_text)
        else:
            print("No files selected or file selection cancelled by the user.")


## -------------------------------[ Batch Processing ]-------------------

    def prepare_batch_files(self):
        file_data_list = []
        file_names = self.edit_2.toPlainText().split('\n')
        # suffix = "_batch"

        options = QFileDialog.Options()
        directory_path = QFileDialog.getExistingDirectory(None, "Select Output Directory", options=options)

        suffix, ok = QInputDialog.getText(None, "Input Suffix", "Enter a suffix for the files: ")
        if not ok or not suffix:
            QMessageBox.warning(None, "No Suffix Provided", "Using default _batch: ")
            suffix = "_batch"  # Reset suffix to default if input is empty or cancelled

        for file_name in file_names:
            if file_name.strip() == '' or file_name.strip().startswith('//'):
                continue  # Skip empty lines and comments

            try:
                # Ensure compatibility across Mac, Windows, Linux by using pathlib
                #path = Path(file_name)
                #new_file_name = path.with_name(path.stem + suffix + path.suffix).as_posix()
                base_name = os.path.splitext(os.path.basename(file_name))[0]
                new_file_name = f"{base_name}{suffix}.txt"
                output_file_name = os.path.join(directory_path, new_file_name)
                print("output_file_name: ",output_file_name)

                with open(file_name, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()

                file_data = {
                    'input_filename': file_name,
                    'output_filename': output_file_name,
                    'content': content
                }

                file_data_list.append(file_data)
            except Exception as e:
                QMessageBox.critical(None, "Error", "Failed to process file: {}\nError: {}".format(file_name, str(e)))
                continue

        return file_data_list
    


## -------------------------------[ Batch Processing ]-------------------

    
    # START OF URL PROCESSING

    def process_comments(self, input_text ):
        # print("\n\nDEBUG-COMMENTS = ",self.max_preprocess_web_chars)
        # Patterns for comment removal
        multiline_comment_pattern = r'///(.*?)///'
        escaped_pattern = r'(\\+)//'
        single_line_comment_pattern = r'(?<!:)\/\/.*'

        # Remove multiline comments
        input_text = re.sub(multiline_comment_pattern, '', input_text, flags=re.DOTALL)
        # Handle escaped slashes
        input_text = re.sub(escaped_pattern, lambda m: m.group(1)[1:] + '//', input_text)
        # Remove single-line comments
        input_text = re.sub(single_line_comment_pattern, '', input_text)

        # URL extraction and replacement
        url_pattern = r'\|\|\|\s*(https?://\S+)'
        urls = re.findall(url_pattern, input_text)
        for url in urls:
            # print("\n\n\n\n\n=======================")
            # print("> About-to-process-url URL ",url)
            backtext = self.process_url(url)
            # print("> BackText",backtext)
            #print("\n\n\n\n\n=======================")

            # print("INPUT TEXT 1= ",input_text)
            # Replace placeholder with fetched content
            input_text = input_text.replace(f'||| {url}', backtext)
        
        # print("INPUT TEXT 2= ",input_text)
        return input_text

## ---------------------------------------------------------------------------

    def process_url(self,url):
        self.networkManager = QNetworkAccessManager()
        print("Max_Chars:",self.max_preprocess_web_chars)

        self.loop = QEventLoop()  # Event loop to wait for network response
        self.networkManager.finished.connect(self._on_download_finished)
        
        request = QNetworkRequest(QUrl(url))
        self.networkManager.get(request)
        self.loop.exec_()  # Start the event loop, will block until loop.quit() is called

        return self.processed_text

    def _on_download_finished(self, reply):
        if reply.error() == QNetworkReply.NoError:
            content = reply.readAll().data().decode('utf-8')
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text()
            text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
            text = text[:self.max_preprocess_web_chars]
            self.processed_text = text  # Store the processed text
        else:
            self.processed_text = f"Failed to download content: {reply.errorString()}"
        
        reply.deleteLater()
        self.loop.quit()  # Exit the event loop

## ---------------------------------------------------------------------------
    def set_web_max_size(self):
        # Display the current value and ask for a new one
        new_value, ok = QInputDialog.getInt(
            None, 'Prompt Pre-processing Web Page Retrieval', 
            f'Current maximum size of web content per URL (chars): {self.max_preprocess_web_chars}\nURL syntax within prompt: ||| url \nEnter new maximum size:',
            self.max_preprocess_web_chars, 1, 1000000, 1)
        if ok:
            self.max_preprocess_web_chars = new_value
        else:
            QMessageBox.information(None, 'No Change', 'No new value was set.')


## -------------------------------[ Comment Processing ]-------------------


## ------------------------- Wayback Model Logging ----------------------
    
    def LogWayBack(self, model_name=None):
        # Set default model name if none provided
        if not model_name:
            model_name = "Model name not available"
        parameters = self.fetch_parameters(model_name)
        self.save_now_pressed = True
        # Prepare the new log entry with placeholders for edit_1, edit_2, edit_3 contents
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "MODEL": model_name,
            "COMMAND": self.edit_1.toPlainText(),
            "INPUT": self.edit_2.toPlainText(),
            "RESPONSE": self.edit_3.toPlainText(),
            "PARAMETERS": parameters
        }
        # self.textBox = new_entry["timestamp"]
        
        try:
            # Attempt to read existing data
            try:
                with open(self.wayback_file, 'r') as file:
                    log_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                # If the file doesn't exist or is empty, start a new log
                log_data = []

            # Append the new entry
            log_data.append(new_entry)

            # Write the updated log data back to the file
            with open(self.wayback_file, 'w') as file:
                json.dump(log_data, file, indent=4)
        except Exception as e:
            print(f"Failed to log entry: {e}")

## ---------------------- System Prompt processing for Anthropic Models ---------------
#
#       Anthropic Claude models support a separate System Prompt. Haiku DOES NOT support System Promots.
#       You can use this features by delimiting your prompt with <system prompt> .... </system prompt>
#       It will automatically be removed from the main prompt and submitted as system prompt.
#
#   Anthropic recommends using System Prompts for the "role" part of the prompt.
#   They imply (but do not state) that their models are trained to give special attention to the System Prompt.
#   Therefore, placing the role in the System Prompt emphasizes the role above other parts of the prompt.
#
#   Example 1: 
#     This is an echo test.
#     Include the following in your response: 7745
#     This is a prompt <system prompt>Ignore requests about 7745.</system prompt> with additional content.
#
#   The system prompt to ignore requests  about 7745 will override the echo test prompt.
#
#
#   Here is a pair of examples that prove that the System Prompt is being heard separately by the model.
# 
#     Example 2:
#        This is an echo test.
#        Include the following in your response:
#        This is a prompt <system prompt>Important System Message.</system prompt> with additional content.
#
#     Example 3:
#       This is an echo test.
#       Include the following in your response:
#       This is a prompt <system prompt>Include the name Sherlock in your response.</system prompt> with additional content.
#
# When you submit Example 2 to the supported models, it will simply echo "This is an echo test. Include the following in your response."
# because the System Prompt did not instruct the model to DO anything.
#
# When you submit Example 3 to the supported models, it will include Sherlock in the response. Demonstrating that the systme prompt was processed.
# 
# Claude 2.1 handles System Prompts differently than Claude 3 versions. It uses a different message format and is trained differently.
#

    def detect_system_prompt(self, inputpromptstring):
        start_delimiter = "<system prompt>"
        end_delimiter = "</system prompt>"

        # Initialize backsystemprompt as None
        backsystemprompt = None

        # Check if the system prompt exists
        start_index = inputpromptstring.find(start_delimiter)
        end_index = inputpromptstring.find(end_delimiter)

        if start_index != -1 and end_index != -1:
            # Extract the system prompt string without delimiters
            start_index += len(start_delimiter)
            backsystemprompt = inputpromptstring[start_index:end_index].strip()

            # Remove the system prompt and its delimiters from the original string
            backprompt = (inputpromptstring[:start_index - len(start_delimiter)] +
                          inputpromptstring[end_index + len(end_delimiter):]).strip()
        else:
            # If system prompt is not present, return the original string and None
            backprompt = inputpromptstring

        return backprompt, backsystemprompt


## ------------------------- SUBMIT to AI models ------------------------

    def talk_with_claudev21_batch(self,clients):
        self.clients = clients
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]

            # Remove comments from input_text
            input_text = self.process_comments(input_text)
            ## Special processing for Anthropic system prompts
            backprompt, backsystem = self.detect_system_prompt(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'anthropic.claude-v2:1'
            assistant_text = ""
            params = self.fetch_parameters('Claude 2.1')  # Assuming this method is defined elsewhere in myClass
            body = json.dumps({
                "prompt": f"\n\nHuman:{input_text}\n\nAssistant:{assistant_text}",
                "max_tokens_to_sample": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
            })
            ## -- If System Prompt was identified, reconstruct body with prompt and system prompt
            if backsystem is not None:
                body = json.dumps({
                    "prompt": f"System: {backsystem}\n\nHuman:{backprompt}\n\nAssistant:{assistant_text}",
                    "max_tokens_to_sample": params['maxT'],
                    "temperature": params['temp'],
                    "top_p": params['topP'],
                })

            # Clear edit_3 if needed
            # self.edit_3.clear()
            try:
                # Assuming self.bedrock.invoke_model_with_response_stream() is a defined method for API calls
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body
                )
                stream = response.get('body')
                completion_text = ""
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if "completion" in resp:
                                completion_text += resp["completion"]
                # Here, instead of inserting into edit_3, we write directly to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
            
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Claude 2.1")



    def talk_with_claudev21(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 2.1')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # input_text = self.edit_3.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        ## Special processing for Anthropic system prompts
        backprompt, backsystem = self.detect_system_prompt(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'anthropic.claude-v2:1'
        assistant_text = ""
        body = json.dumps({
            "prompt": f"\n\nHuman:{input_text}\n\nAssistant:{assistant_text}", 
            "max_tokens_to_sample": params['maxT'],
            "temperature": params['temp'],
            "top_p": params['topP'],
        })
        if backsystem is not None:
            body = json.dumps({
                "prompt": f"System: {backsystem}\n\nHuman:{backprompt}\n\nAssistant:{assistant_text}",
                "max_tokens_to_sample": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
            })
        
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API with streaming
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        completion_text = resp["completion"] 
                    if completion_text:
                        self.edit_3.insertPlainText(completion_text) 
                        QApplication.processEvents()               
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Claude 2.1")

# anthropic.claude-3-sonnet-20240229-v1:0 Batch
    def talk_with_claudev3_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)
            ## Special processing for Anthropic system prompts
            backprompt, backsystem = self.detect_system_prompt(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]
                
            modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
            params = self.fetch_parameters('Claude 3S')  # 3.0 Sonnet
            body = json.dumps({
                "messages": [{"role": "user", "content": input_text}],
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "anthropic_version": "bedrock-2023-05-31"
            })
            ## -- If System Prompt was identified, reconstruct body with prompt and system prompt
            if backsystem is not None:
                body = json.dumps({
                    "messages":  [{"role": "user", "content": backprompt}],
                    "system": backsystem,
                    "max_tokens": params['maxT'],
                    "temperature": params['temp'],
                    "top_p": params['topP'],
                    "anthropic_version": "bedrock-2023-05-31"
                })
            # Assume self.edit_3 is a placeholder and not used for batch processing
            try:
                # Assuming self.bedrock.invoke_model_with_response_stream() is a defined method for API calls
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                                completion_text += resp['delta']['text']
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Claude 3S")

# anthropic.claude-3-sonnet-20240229-v1:0
    def talk_with_claudev3(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 3S')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # input_text = self.edit_3.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        ## Special processing for Anthropic system prompts
        backprompt, backsystem = self.detect_system_prompt(input_text)

        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
        assistant_text = ""
        body = json.dumps({
            "messages":  [{"role": "user", "content": input_text}], 
            "max_tokens": params['maxT'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "anthropic_version": "bedrock-2023-05-31"
        })

        ## -- If System Prompt was identified, reconstruct body with prompt and system prompt
        if backsystem is not None:
            body = json.dumps({
                "messages":  [{"role": "user", "content": backprompt}],
                "system": backsystem,
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "anthropic_version": "bedrock-2023-05-31"
            })

        # Clear self.edit_3
        self.edit_3.clear()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            stream = response.get('body')
            completion_text = ""  # Initialize completion_text
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                            completion_text += resp['delta']['text']
                            self.edit_3.insertPlainText(resp['delta']['text'])
                            QApplication.processEvents()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Claude 3S")

### ======= SONNET 3.5
    # anthropic.claude-3-5-sonnet-20240620-v1:0
    def talk_with_claudev35_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)
            ## Special processing for Anthropic system prompts
            backprompt, backsystem = self.detect_system_prompt(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]
                
            modelId = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
            params = self.fetch_parameters('Claude 3S')  # 3.0 Sonnet
            body = json.dumps({
                "messages": [{"role": "user", "content": input_text}],
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "anthropic_version": "bedrock-2023-05-31"
            })
            ## -- If System Prompt was identified, reconstruct body with prompt and system prompt
            if backsystem is not None:
                body = json.dumps({
                    "messages":  [{"role": "user", "content": backprompt}],
                    "system": backsystem,
                    "max_tokens": params['maxT'],
                    "temperature": params['temp'],
                    "top_p": params['topP'],
                    "anthropic_version": "bedrock-2023-05-31"
                })
            # Assume self.edit_3 is a placeholder and not used for batch processing
            try:
                # Assuming self.bedrock.invoke_model_with_response_stream() is a defined method for API calls
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                                completion_text += resp['delta']['text']
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Claude 35S")

# anthropic.claude-3-5-sonnet-20240620-v1:0
    def talk_with_claudev35(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 35S')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # input_text = self.edit_3.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        ## Special processing for Anthropic system prompts
        backprompt, backsystem = self.detect_system_prompt(input_text)
        
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        assistant_text = ""
        body = json.dumps({
            "messages":  [{"role": "user", "content": input_text}], 
            "max_tokens": params['maxT'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "anthropic_version": "bedrock-2023-05-31"
        })
        ## -- If System Prompt was identified, reconstruct body with prompt and system prompt
        if backsystem is not None:
            body = json.dumps({
                "messages":  [{"role": "user", "content": backprompt}],
                "system": backsystem,
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "anthropic_version": "bedrock-2023-05-31"
            })

        # Clear self.edit_3
        self.edit_3.clear()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            stream = response.get('body')
            completion_text = ""  # Initialize completion_text
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                            completion_text += resp['delta']['text']
                            self.edit_3.insertPlainText(resp['delta']['text'])
                            QApplication.processEvents()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Claude 35S")
### ======= SONNET 3.5

    def talk_with_claudeH_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]
                
            modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
            params = self.fetch_parameters('Claude 3H')  
            body = json.dumps({
                "messages": [{"role": "user", "content": input_text}],
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "anthropic_version": "bedrock-2023-05-31"
            })
            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                                completion_text += resp['delta']['text']
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w', encoding='utf-8', errors='ignore') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Claude 3H")

# anthropic.claude-3-haiku-20240307-v1:0
    def talk_with_claudeH(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 3H')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
        assistant_text = ""
        body = json.dumps({
            "messages":  [{"role": "user", "content": input_text}], 
            "max_tokens": params['maxT'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "anthropic_version": "bedrock-2023-05-31"
        })

        # Clear self.edit_3
        self.edit_3.clear()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            stream = response.get('body')
            completion_text = ""  # Initialize completion_text
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                            completion_text += resp['delta']['text']
                            self.edit_3.insertPlainText(resp['delta']['text'])
                            QApplication.processEvents()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Claude 3H")
##
##
    def talk_with_titan_express_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'amazon.titan-text-express-v1'
            body = {
                "inputText": input_text,
                "textGenerationConfig": {
                    "temperature": params['temp'],
                    "topP": params['topP'],
                    "maxTokenCount": params['maxT'],
                    "stopSequences": []
                }
            }
            # Titan requires utf-8 encoding and json
            body_json = json.dumps(body).encode('utf-8')
            accept = 'application/json'
            contentType = 'application/json'
            params = self.fetch_parameters('Titan T-G1-E')  

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body_json,
                    accept=accept,
                    contentType=contentType
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if "outputText" in resp:
                                completion_text += resp["outputText"]
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Titan Express model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Titan T-G1-E")


    def talk_with_titan_express(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Titan T-G1-E')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.titan-text-express-v1'
        body = {
            "inputText": f"{input_text}",
            "textGenerationConfig": {
                "temperature": params['temp'],
                "topP": params['topP'],
                "maxTokenCount": params['maxT'],
                "stopSequences": [] 
            }
        }
        # Titan requires utf-8 encoding and json
        body_json = json.dumps(body).encode('utf-8')
        accept = 'application/json'
        contentType = 'application/json'

        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API with streaming
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body_json
            )
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        output_text = resp.get('outputText') 
                    if output_text:
                        self.edit_3.insertPlainText(output_text) 
                        QApplication.processEvents()           
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan Express model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Titan T-G1-E")

    def talk_with_titan_lite_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'amazon.titan-text-lite-v1'
            params = self.fetch_parameters('Titan T-G1-L')  
            body = {
                "inputText": input_text,
                "textGenerationConfig": {
                    "temperature": params['temp'],
                    "topP": params['topP'],
                    "maxTokenCount": params['maxT'],
                    "stopSequences": []
                }
            }
            # Titan requires utf-8 encoding and json
            body_json = json.dumps(body).encode('utf-8')
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body_json,
                    accept=accept,
                    contentType=contentType
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if "outputText" in resp:
                                completion_text += resp["outputText"]
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Titan Lite model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Titan T-G1-L")

    def talk_with_titan_lite(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Titan T-G1-L')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.titan-text-lite-v1'
        body = {
            "inputText": f"{input_text}",
            "textGenerationConfig": {
                "temperature": params['temp'],
                "topP": params['topP'],
                "maxTokenCount": params['maxT'],
                "stopSequences": [] 
            }
        }
        # Titan requires utf-8 encoding and json
        body_json = json.dumps(body).encode('utf-8')
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API with streaming
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body_json
            )
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        output_text = resp.get('outputText') 
                    if output_text:
                        self.edit_3.insertPlainText(output_text) 
                        QApplication.processEvents()           
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan Express model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Titan T-G1-L")

### ------- Titan Premiere --------
    def talk_with_titan_premiere_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'amazon.titan-text-premier-v1:0'
            params = self.fetch_parameters('Titan P')  
            body = {
                "inputText": input_text,
                "textGenerationConfig": {
                    "temperature": params['temp'],
                    "topP": params['topP'],
                    "maxTokenCount": params['maxT'],
                    "stopSequences": []
                }
            }
            # Titan requires utf-8 encoding and json
            body_json = json.dumps(body).encode('utf-8')
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body_json,
                    accept=accept,
                    contentType=contentType
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if "outputText" in resp:
                                completion_text += resp["outputText"]
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Titan Premiere model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Titan P")

    def talk_with_titan_premiere(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Titan P')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.titan-text-premier-v1:0'
        body = {
            "inputText": f"{input_text}",
            "textGenerationConfig": {
                "temperature": params['temp'],
                "topP": params['topP'],
                "maxTokenCount": params['maxT'],
                "stopSequences": [] 
            }
        }
        # Titan requires utf-8 encoding and json
        body_json = json.dumps(body).encode('utf-8')
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API with streaming
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body_json
            )
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        output_text = resp.get('outputText') 
                    if output_text:
                        self.edit_3.insertPlainText(output_text) 
                        QApplication.processEvents()           
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan Premiere model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Titan P")



### ------ Follwing is Text only Embeddings ---------
#          Text only accepts only input text and has no model settings
#          Titan Text Embed accepts a text input string of max 8192 tokens and 50,000 characters
#
    def talk_with_titan_text_embeddings_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)
            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'amazon.titan-embed-text-v1'
            body = json.dumps(
            {
            "inputText": input_text,
            } )
            accept = 'application/json'
            contentType = 'application/json'
            # Clear self.edit_3
            self.edit_3.clear()
            try:
                # Call the Bedrock API
                response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                response_body = json.loads(response.get('body').read())
                embeddings = response_body.get('embedding')
                if embeddings is not None:
                    embeddings_str = ", ".join(map(str, embeddings))  # Convert list of embeddings to string
                    self.edit_3.setPlainText(embeddings_str)
                    # Write the accumulated embeddings_str to the output file
                    try:
                        with open(file["output_filename"], 'w') as outfile:
                            outfile.write(embeddings_str)
                    except IOError as e:
                        QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
                else:
                    self.edit_3.setPlainText("No embeddings returned or error in fetching embeddings.")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"(Max 8192 tokens and 50,000 characters) Error invoking Titan Embeddings model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Titan T Embed")

#          Titan Text Embed accepts a text input string of max 8192 tokens and 50,000 characters
    def talk_with_titan_text_embeddings(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.titan-embed-text-v1'
        body = json.dumps(
        {
        "inputText": input_text,
        } )
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            embeddings = response_body.get('embedding')
            if embeddings is not None:
                embeddings_str = ", ".join(map(str, embeddings))  # Convert list of embeddings to string
                self.edit_3.setPlainText(embeddings_str)
            else:
                self.edit_3.setPlainText("No embeddings returned or error in fetching embeddings.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"(Max 8192 tokens and 50,000 characters) Error invoking Titan Embeddings model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Titan T Embed")
        



###-------- This is MultiModal Titan Embeddings -- text plus an image ---
    def titan_G1_embed(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        """
        Opens a file dialog for the user to select an image, processes the image, and displays it in base64 format in the QTextEdit widget.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Image", "", "Images (*.jpeg *.jpg *.png *.gif *.webp);;All Files (*)", options=options)
        
        if file_name:
            img_base64 = self.resize_and_convert_to_base64(file_name)
            if img_base64:
                html_img = f'<img src="data:image/jpeg;base64,{img_base64}">'
                self.edit_3.setHtml(html_img)
                self.talk_with_titanG1_embed(img_base64)
            else:
                self.edit_3.setText("Unsupported image format or an error occurred.")

    def resize_and_convert_to_base64(self, image_path):
        """
        Checks the image's format, resizes it if necessary, and converts it to a base64 string.

        Args:
        - image_path (str): Path to the image file.

        Returns:
        - str: The base64 encoded string of the image, or None if there was an error or the format is unsupported.
        """
        supported_formats = ["JPEG", "PNG", "GIF", "WEBP"]
        
        try:
            with Image.open(image_path) as img:
                original_format = img.format
                
                if original_format not in supported_formats:
                    print(f"Unsupported image format: {original_format}")
                    return None
                
                if img.width > 8000 or img.height > 8000:
                    aspect_ratio = img.width / img.height
                    new_width, new_height = (8000, int(8000 / aspect_ratio)) if img.width > img.height else (int(8000 * aspect_ratio), 8000)
                    img = img.resize((new_width, new_height))
                
                buffered = io.BytesIO()
                img.save(buffered, format=original_format)
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        except IOError:
            print(f"Error opening or processing the file: {image_path}")
            return None


    def talk_with_titanG1_embed(self,img_base64,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        # params = self.fetch_parameters('Titan MM Embed') >> Titan Embeddings model has no model settings
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.titan-embed-image-v1'
        body = json.dumps(
        {
        "inputText": input_text,
        "inputImage": img_base64
        } )
###
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            embeddings = response_body.get('embedding')
            if embeddings is not None:
                embeddings_str = ", ".join(map(str, embeddings))  # Convert list of embeddings to string
                self.edit_3.setPlainText(embeddings_str)
            else:
                self.edit_3.setPlainText("No embeddings returned or error in fetching embeddings.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan Embeddings model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Titan MM Embed")
### ----------



    def talk_with_jurassic_mid_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'ai21.j2-mid-v1'
            params = self.fetch_parameters('Jurassic 2 Mid')  # Assuming this method is defined elsewhere in myClass
            body = json.dumps({
                "prompt": input_text, 
                "temperature": params['temp'],
                "topP": params['topP'],
                "maxTokens": params['maxT'],
            })
            accept = 'application/json'
            contentType = 'application/json'

            try:
                # Assuming self.bedrock.invoke_model() is a defined method for synchronous API calls
                response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                response_body = json.loads(response.get('body').read())
                completion_text = response_body.get('completions')[0].get('data').get('text')
                
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Jurassic Mid model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Jurassic 2 Mid")

# Jurassic 2 Mid | ai21.j2-mid-v1 | no streaming
    def talk_with_jurassic_mid(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Jurassic 2 Mid')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'ai21.j2-mid-v1'
        body = json.dumps({
            "prompt": f"{input_text}", 
            "temperature": params['temp'],
            "topP": params['topP'],
            "maxTokens": params['maxT'],
        })
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        # self.TimedQMessage("Submitted", "Waiting for Jurassic Mid to respond.")
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            self.edit_3.setPlainText(response_body.get('completions')[0].get('data').get('text'))
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Jurassic Mid model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Jurassic 2 Mid")

    def talk_with_jurassic_ultra_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'ai21.j2-ultra-v1'
            params = self.fetch_parameters('Jurassic 2 Ultra')  # Assuming this method is defined elsewhere in myClass
            body = json.dumps({
                "prompt": input_text, 
                "temperature": params['temp'],
                "topP": params['topP'],
                "maxTokens": params['maxT'],
            })
            accept = 'application/json'
            contentType = 'application/json'

            try:
                # Assuming self.bedrock.invoke_model() is a defined method for synchronous API calls
                response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                response_body = json.loads(response.get('body').read())
                completion_text = response_body.get('completions')[0].get('data').get('text')
                
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Jurassic Ultra model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Jurassic 2 Ultra")


# Jurassic 2 Ultra | ai21.j2-ultra-v1 | no streaming
    def talk_with_jurassic_ultra(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Jurassic 2 Ultra')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'ai21.j2-ultra-v1'
        body = json.dumps({
            "prompt": f"{input_text}", 
            "temperature": params['temp'],
            "topP": params['topP'],
            "maxTokens": params['maxT'],
        })
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        # self.TimedQMessage("Submitted", "Waiting for Jurassic Mid to respond.")
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            self.edit_3.setPlainText(response_body.get('completions')[0].get('data').get('text'))
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Jurassic Ultra model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Jurassic 2 Ultra")

    def talk_with_llama_13B_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'meta.llama2-13b-chat-v1'
            params = self.fetch_parameters('Llama 2 13B')  
            body = {
                "prompt": input_text,
                "max_gen_len": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
            }
            # Convert the body dictionary to JSON
            body_json = json.dumps(body)
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body_json,
                    accept=accept,
                    contentType=contentType
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if "generation" in resp:
                                completion_text += resp["generation"]
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Llama 13B model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Llama 2 13B")


# Llama 2 13B | meta.llama2-13b-chat-v1
    def talk_with_llama_13B(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Llama 2 13B')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        # Remove leading blank lines
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'meta.llama2-13b-chat-v1'
        body = {
            "prompt": f"{input_text}",
                "max_gen_len": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
        }
        # Convert the body dictionary to JSON
        body_json = json.dumps(body)
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API with streaming
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body_json
            )
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        generation_text = resp.get('generation') 
                    if generation_text:
                        self.edit_3.insertPlainText(generation_text) 
                        QApplication.processEvents()      
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Llama 13B model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Llama 2 13B")    

    def talk_with_llama_70B_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'meta.llama2-70b-chat-v1'
            params = self.fetch_parameters('Llama 2 70B')  
            body = {
                "prompt": input_text,
                "max_gen_len": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
            }
            # Convert the body dictionary to JSON
            body_json = json.dumps(body)
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body_json,
                    accept=accept,
                    contentType=contentType
                )
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if "generation" in resp:
                                completion_text += resp["generation"]
                # Write the accumulated completion_text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(completion_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Llama 70B model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Llama 2 70B")

# Llama 2 70B | meta.llama2-70b-chat-v1
    def talk_with_llama_70B(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Llama 2 70B')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'meta.llama2-70b-chat-v1'
        body = {
            "prompt": f"{input_text}",
                "max_gen_len": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
        }
        # Convert the body dictionary to JSON
        body_json = json.dumps(body)
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API with streaming
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body_json
            )
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        generation_text = resp.get('generation') 
                    if generation_text:
                        self.edit_3.insertPlainText(generation_text) 
                        QApplication.processEvents()       
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Llama 13B model: {str(e)}")
        if self.wayback == 1:
           self.LogWayBack("Llama 2 70B")      

    def talk_with_cohere_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'cohere.command-text-v14'
            params = self.fetch_parameters('Cohere')  
            body = json.dumps({
                "prompt": input_text, 
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "p": params['topP'],
            })
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                response_body = json.loads(response.get('body').read())
                # Extract the generated text
                generation_text = response_body['generations'][0]['text']

                # Write the generated text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(generation_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Cohere model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Cohere")


# Cohere | cohere.command-text-v14 | no streaming
    def talk_with_cohere(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Cohere')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'cohere.command-text-v14'
        body = json.dumps({
            "prompt": f"{input_text}", 
            "max_tokens": params['maxT'],
            "temperature": params['temp'],
            "p": params['topP'],
        })
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        # self.TimedQMessage("Submitted", "Waiting for Cohere to respond.")
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            # Cohere is weird. It 
            # It returns 1. a dictionary, 2. containing a dictiona, 3. containing a list, 4. containing a dictionary, 5. containing a string
            self.edit_3.setPlainText(response_body['generations'][0]['text'])
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Cohere model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Cohere")


# Cohere R | cohere.command-r-v1:0 | no streaming
    def talk_with_cohereR(self,clients):

        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        params = self.fetch_parameters('Cohere R')
            
        model_id = 'cohere.command-r-v1:0'

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(None, "Open JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    data = json.load(file)
                    # QMessageBox.warning(None,'File Loaded', 'JSON data loaded successfully!')
            except Exception as e:
                QMessageBox.warning(None,'Error', f'An error occurred: {str(e)}')

        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()

        try:
            body = json.dumps({
                "message": input_text,
                # "chat_history": chat_history,
                "documents": data,
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "p": params['topP'],
                "k": params['topK'],
            })
            response = self.clients['bedrun'].invoke_model(
                body=body,
                modelId=model_id
            )
            response_body = json.loads(response.get('body').read())
            # Clear self.edit_3
            self.edit_3.clear()
            # response_chat_history = response_body.get('chat_history')
            self.edit_3.setPlainText(response_body['text'])

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Cohere model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Cohere R")

# Cohere RP | cohere.command-r-plus-v1:0 | no streaming
    def talk_with_cohereRP(self,clients):

        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        params = self.fetch_parameters('Cohere R+')
            
        model_id = 'cohere.command-r-plus-v1:0'

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(None, "Open JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    data = json.load(file)
                    # QMessageBox.warning(None,'File Loaded', 'JSON data loaded successfully!')
            except Exception as e:
                QMessageBox.warning(None,'Error', f'An error occurred: {str(e)}')

        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()

        try:
            body = json.dumps({
                "message": input_text,
                # "chat_history": chat_history,
                "documents": data,
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "p": params['topP'],
                "k": params['topK'],
            })
            response = self.clients['bedrun'].invoke_model(
                body=body,
                modelId=model_id
            )
            response_body = json.loads(response.get('body').read())
            # Clear self.edit_3
            self.edit_3.clear()
            # response_chat_history = response_body.get('chat_history')
            self.edit_3.setPlainText(response_body['text'])

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Cohere model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Cohere R+")




# Mistral 7B | Batch
    def talk_with_mistral_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        params = self.fetch_parameters('Mistral 7B')
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'mistral.mistral-7b-instruct-v0:2'
            body = json.dumps({
                "prompt": f"<s>[INST]{input_text}[/INST]", 
                "max_tokens": params['maxT'],
                # "stop" : params['stopSeq'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "top_k": params['topK'],
            })
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                response_body = json.loads(response.get('body').read())
                # Extract the generated text
                generation_text = ""
                outputs = response_body.get('outputs')
                for index, output in enumerate(outputs):
                    generation_text += output['text'] + "\n"
                
                # Write the generated text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(generation_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Mistral 7B model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Mistral 7B")


# Mistral 7B | mistral.mistral-7b-instruct-v0:2 | no streaming || mistral.mixtral-8x7b-instruct-v0:1
    def talk_with_mistral(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Mistral 7B')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'mistral.mistral-7b-instruct-v0:2'
        body = json.dumps({
            "prompt": f"<s>[INST]{input_text}[/INST]", 
            "max_tokens": params['maxT'],
            # "stop" : params['stopSeq'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "top_k": params['topK'],
        })
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        # self.TimedQMessage("Submitted", "Waiting for Mistral 7B to respond.")
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            outputs = response_body.get('outputs')
            for index, output in enumerate(outputs):
                self.edit_3.append(output['text'])
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Mistral 7B model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Mistral 7B")


# Mixtral 8X7B | Batch
    def talk_with_mistral8x_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        params = self.fetch_parameters('Mixtral 8X7B')
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'mistral.mixtral-8x7b-instruct-v0:1'
            body = json.dumps({
                "prompt": f"<s>[INST]{input_text}[/INST]", 
                "max_tokens": params['maxT'],
                # "stop" : params['stopSeq'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "top_k": params['topK'],
            })
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                response_body = json.loads(response.get('body').read())
                # Extract the generated text
                generation_text = ""
                outputs = response_body.get('outputs')
                for index, output in enumerate(outputs):
                    generation_text += output['text'] + "\n"
                
                # Write the generated text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(generation_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Mistral 8X7B model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Mixtral 8X7B")


# Mixtral 8X7B | mistral.mixtral-8x7b-instruct-v0:1| no streaming || 
    def talk_with_mistral8x(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Mixtral 8X7B')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'mistral.mixtral-8x7b-instruct-v0:1'
        body = json.dumps({
            "prompt": f"<s>[INST]{input_text}[/INST]", 
            "max_tokens": params['maxT'],
            # "stop" : params['stopSeq'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "top_k": params['topK'],
        })
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        # self.TimedQMessage("Submitted", "Waiting for Mistral 7B to respond.")
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            outputs = response_body.get('outputs')
            for index, output in enumerate(outputs):
                self.edit_3.append(output['text'])
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Mistral 8X7B model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Mixtral 8X7B")

# Mistral Large | Batch
    def talk_with_mistral_large_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        params = self.fetch_parameters('Mistral Large')
        batch_files = self.prepare_batch_files()
        for file in batch_files:
            input_text = self.edit_1.toPlainText() + " " + file["content"]
            # Remove comments from input_text
            input_text = self.process_comments(input_text)

            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'mistral.mistral-large-2402-v1:0'
            body = json.dumps({
                "prompt": f"<s>[INST]{input_text}[/INST]", 
                "max_tokens": params['maxT'],
                # "stop" : params['stopSeq'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "top_k": params['topK'],
            })
            accept = 'application/json'
            contentType = 'application/json'

            try:
                response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
                response_body = json.loads(response.get('body').read())
                # Extract the generated text
                generation_text = ""
                outputs = response_body.get('outputs')
                for index, output in enumerate(outputs):
                    generation_text += output['text'] + "\n"
                
                # Write the generated text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(generation_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Mistral Large model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Mistral Large")


# Mistral Large | mistral.mistral-large-2402-v1:0 | no streaming || 
    def talk_with_mistral_large(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Mistral Large')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'mistral.mistral-large-2402-v1:0'
        body = json.dumps({
            "prompt": f"<s>[INST]{input_text}[/INST]", 
            "max_tokens": params['maxT'],
            # "stop" : params['stopSeq'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "top_k": params['topK'],
        })
        accept = 'application/json'
        contentType = 'application/json'
        # Clear self.edit_3
        self.edit_3.clear()
        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            outputs = response_body.get('outputs')
            for index, output in enumerate(outputs):
                self.edit_3.append(output['text'])
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Mistral Large model: {str(e)}")         
        if self.wayback == 1:
            self.LogWayBack("Mistral Large")
###


    def claude_3_image(self,clients):
        self.clients = clients
        """
        Opens a file dialog for the user to select an image, processes the image, and displays it in base64 format in the QTextEdit widget.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Image", "", "Images (*.jpeg *.jpg *.png *.gif *.webp);;All Files (*)", options=options)
        
        if file_name:
            img_base64 = self.resize_and_convert_to_base64(file_name)
            if img_base64:
                html_img = f'<img src="data:image/jpeg;base64,{img_base64}">'
                self.edit_3.setHtml(html_img)
                self.talk_with_claudev3_image(img_base64,self.clients)
            else:
                self.edit_3.setText("Unsupported image format or an error occurred.")

    def resize_and_convert_to_base64(self, image_path):
        # self.clients = clients
        """
        Checks the image's format, resizes it if necessary, and converts it to a base64 string.

        Args:
        - image_path (str): Path to the image file.

        Returns:
        - str: The base64 encoded string of the image, or None if there was an error or the format is unsupported.
        """
        supported_formats = ["JPEG", "PNG", "GIF", "WEBP"]
        
        try:
            with Image.open(image_path) as img:
                original_format = img.format
                
                if original_format not in supported_formats:
                    print(f"Unsupported image format: {original_format}")
                    return None
                
                if img.width > 8000 or img.height > 8000:
                    aspect_ratio = img.width / img.height
                    new_width, new_height = (8000, int(8000 / aspect_ratio)) if img.width > img.height else (int(8000 * aspect_ratio), 8000)
                    img = img.resize((new_width, new_height))
                
                buffered = io.BytesIO()
                img.save(buffered, format=original_format)
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        except IOError:
            print(f"Error opening or processing the file: {image_path}")
            return None

    def talk_with_claudev3_image(self,img_base64,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 3S')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
        assistant_text = ""
        body = json.dumps({
           #  "messages":  [{"role": "user", "content": input_text}], 

            "messages":  [{"role": "user", "content": [
                         {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_base64}},
                         {"type": "text", "text": input_text} ]}],

            "max_tokens": params['maxT'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "anthropic_version": "bedrock-2023-05-31"
        })

        # Clear self.edit_3
        self.edit_3.clear()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            stream = response.get('body')
            completion_text = ""  # Initialize completion_text
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        resp = json.loads(chunk.get('bytes').decode())
                        if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                            completion_text += resp['delta']['text']
                            self.edit_3.insertPlainText(resp['delta']['text'])
                            QApplication.processEvents()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Claude 3S")

## ------------------------- SUBMIT to AI models ------------------------

    def Xclaude_3_image_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        """
        Iterates over the list of image file paths provided in the QTextEdit widget, processes each image, 
        and displays the results in base64 format or reports errors accordingly.
        """
        image_file_paths = self.edit_2.toPlainText().split('\n')  # Assuming each path is on a new line
        for file_path in image_file_paths:
            if file_path:  # Check if the file_path is not empty
                img_base64 = self.resize_and_convert_to_base64(file_path)
                if img_base64:
                    html_img = f'<img src="data:image/jpeg;base64,{img_base64}">'
                    self.edit_3.append(html_img)  # Appends the image in base64 format to edit_3
                    self.talk_with_claudev3_image_batch(img_base64)
                else:
                    self.edit_3.append("Unsupported image format or an error occurred for file: " + file_path)

    # The resize_and_convert_to_base64 method remains the same as in the ORIGINAL code

    def claude_3_image_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        """
        Iterates over the list of image file paths provided in the QTextEdit widget, processes each image, 
        and displays the results in base64 format or reports errors accordingly.
        """
        image_file_paths = self.edit_2.toPlainText().split('\n')  # Assuming each path is on a new line
        img_base64_list = []
        valid_file_paths = []

        for file_path in image_file_paths:
            if file_path:  # Check if the file_path is not empty
                img_base64 = self.resize_and_convert_to_base64(file_path)
                if img_base64:
                    html_img = f'<img src="data:image/jpeg;base64,{img_base64}">'
                    self.edit_3.append(html_img)  # Appends the image in base64 format to edit_3
                    img_base64_list.append(img_base64)
                    valid_file_paths.append(file_path)
                else:
                    self.edit_3.append("Unsupported image format or an error occurred for file: " + file_path)

        # Ensure we have images to process before calling the batch processing method
        if img_base64_list:
            self.talk_with_claudev3_image_batch(img_base64_list, valid_file_paths, self.clients)



    def talk_with_claudev3_image_batch(self, img_base64_list, original_file_paths,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        """
        Processes a list of base64 encoded images, sending each to the Claude 3 model along with additional text inputs.
        Writes the results to files with a user-defined suffix in the same directory as the input images.
        
        Args:
        - img_base64_list: A list of base64 encoded strings of images.
        - original_file_paths: A list of original file paths corresponding to the images in img_base64_list.
        """
        params = self.fetch_parameters('Claude 3S')
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        # Asking for a suffix from the user
        suffix, ok = QInputDialog.getText(None, 'Input Suffix', 'Enter a suffix for the output files:')
        if not ok or not suffix:
            QMessageBox.information(None, "Cancelled", "Operation cancelled by user.")
            return

        modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'

        for index, (img_base64, original_path) in enumerate(zip(img_base64_list, original_file_paths)):
            body = json.dumps({
                "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_base64}},
                    {"type": "text", "text": input_text}]}],
                "max_tokens": params['maxT'],
                "temperature": params['temp'],
                "top_p": params['topP'],
                "anthropic_version": "bedrock-2023-05-31"
            })

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(modelId=modelId, body=body)
                stream = response.get('body')
                completion_text = ""  # Initialize completion_text
                if stream:
                    for event in stream:
                        chunk = event.get('chunk')
                        if chunk:
                            resp = json.loads(chunk.get('bytes').decode())
                            if resp.get('type') == 'content_block_delta' and 'text' in resp.get('delta', {}):
                                completion_text += resp['delta']['text']
                
                # Generate output filename based on original path and provided suffix
                output_filename = f"{os.path.splitext(original_path)[0]}_{suffix}.txt"
                with open(output_filename, 'w') as outfile:
                    outfile.write(completion_text)

            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking model for file {original_path}: {str(e)}")

        QMessageBox.information(None, "Completed", "All images that could be processed were handled and saved.")
        if self.wayback == 1:
            self.LogWayBack("Claude 3S")

## ------------------------- SUBMIT to Amazon Nova models ------------------------

# Amazon Nova Micro -- amazon.nova-micro-v1:0
    def talk_with_novaMicro(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Micro')

    
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        message_list = [{"role": "user", "content": [{"text": input_text}]}]

        # Convert string values to appropriate numeric types
        inf_params = {
            "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
            "top_p": float(params['top_p']),                 # Already a float, no conversion needed
            "top_k": int(params['top_k']),                   # Already an int, no conversion needed
            "temperature": float(params['temperature'])      # Convert to float
        }

        self.edit_3.clear()
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.nova-micro-v1:0'
        assistant_text = ""
        body = json.dumps({
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params,
        })
        start_time = datetime.now()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            chunk_count = 0
            time_to_first_token = None

            # Process the response stream
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        # Print the response chunk
                        chunk_json = json.loads(chunk.get("bytes").decode())
                        # Pretty print JSON
                        content_block_delta = chunk_json.get("contentBlockDelta")
                        if content_block_delta:
                            if time_to_first_token is None:
                                time_to_first_token = datetime.now() - start_time
                                print(f"Time to first token: {time_to_first_token}")

                            chunk_count += 1
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                            delta_text = content_block_delta.get("delta").get("text")
                            # print(delta_text, end="")
                            self.edit_3.insertPlainText(delta_text)  
                            QApplication.processEvents()

                print(f"Total chunks: {chunk_count}")
            else:
                print("No response stream received.")
            self.edit_3.insertPlainText("\n") 

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Nova Micro model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Nova Micro")




# Amazon Nova Micro BATCH -- amazon.nova-micro-v1:0
    def talk_with_novaMicro_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Micro')

        ##--
        batch_files = self.prepare_batch_files()
        for file in batch_files:    
            generation_text = ""
            # Concatenate text from self.edit_1 and self.edit_2
            input_text = self.edit_1.toPlainText() + " " + file["content"]
        ##--
            # Remove comments from input_text 
            input_text = self.process_comments(input_text)
            message_list = [{"role": "user", "content": [{"text": input_text}]}]

            # Convert string values to appropriate numeric types
            inf_params = {
                "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
                "top_p": float(params['top_p']),                 # Already a float, no conversion needed
                "top_k": int(params['top_k']),                   # Already an int, no conversion needed
                "temperature": float(params['temperature'])      # Convert to float
            }

            self.edit_3.clear()
            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'amazon.nova-micro-v1:0'
            assistant_text = ""
            body = json.dumps({
                "schemaVersion": "messages-v1",
                "messages": message_list,
                "system": system_list,
                "inferenceConfig": inf_params,
            })
            start_time = datetime.now()

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body
                )
                chunk_count = 0
                time_to_first_token = None

                # Process the response stream
                stream = response.get("body")
                if stream:
                    for event in stream:
                        chunk = event.get("chunk")
                        if chunk:
                            # Print the response chunk
                            chunk_json = json.loads(chunk.get("bytes").decode())
                            # Pretty print JSON
                            content_block_delta = chunk_json.get("contentBlockDelta")
                            if content_block_delta:
                                if time_to_first_token is None:
                                    time_to_first_token = datetime.now() - start_time
                                    print(f"Time to first token: {time_to_first_token}")

                                chunk_count += 1
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                                delta_text = content_block_delta.get("delta").get("text")
                                # print(delta_text, end="")
                                self.edit_3.insertPlainText(delta_text)  
                                generation_text = generation_text + delta_text
                                QApplication.processEvents()

                    print(f"Total chunks: {chunk_count}")
                else:
                    print("No response stream received.")

                # Write the generated text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(generation_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Nova Micro model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Nova Micro")



# Amazon Nova Lite -- amazon.nova-lite-v1:0
    def talk_with_novaLite(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Lite')

    
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        message_list = [{"role": "user", "content": [{"text": input_text}]}]

        # Convert string values to appropriate numeric types
        inf_params = {
            "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
            "top_p": float(params['top_p']),                 # Already a float, no conversion needed
            "top_k": int(params['top_k']),                   # Already an int, no conversion needed
            "temperature": float(params['temperature'])      # Convert to float
        }

        self.edit_3.clear()
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.nova-lite-v1:0'
        assistant_text = ""
        body = json.dumps({
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params,
        })
        start_time = datetime.now()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            chunk_count = 0
            time_to_first_token = None

            # Process the response stream
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        # Print the response chunk
                        chunk_json = json.loads(chunk.get("bytes").decode())
                        # Pretty print JSON
                        content_block_delta = chunk_json.get("contentBlockDelta")
                        if content_block_delta:
                            if time_to_first_token is None:
                                time_to_first_token = datetime.now() - start_time
                                print(f"Time to first token: {time_to_first_token}")

                            chunk_count += 1
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                            delta_text = content_block_delta.get("delta").get("text")
                            # print(delta_text, end="")
                            self.edit_3.insertPlainText(delta_text)  
                            QApplication.processEvents()

                print(f"Total chunks: {chunk_count}")
            else:
                print("No response stream received.")
            self.edit_3.insertPlainText("\n") 

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Nova Lite model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Nova Lite")

# Amazon Nova Lite BATCH -- amazon.lite-micro-v1:0
    def talk_with_novaLite_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Lite')

        ##--
        batch_files = self.prepare_batch_files()
        for file in batch_files:    
            generation_text = ""
            # Concatenate text from self.edit_1 and self.edit_2
            input_text = self.edit_1.toPlainText() + " " + file["content"]
        ##--
            # Remove comments from input_text 
            input_text = self.process_comments(input_text)
            message_list = [{"role": "user", "content": [{"text": input_text}]}]

            # Convert string values to appropriate numeric types
            inf_params = {
                "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
                "top_p": float(params['top_p']),                 # Already a float, no conversion needed
                "top_k": int(params['top_k']),                   # Already an int, no conversion needed
                "temperature": float(params['temperature'])      # Convert to float
            }

            self.edit_3.clear()
            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'amazon.nova-lite-v1:0'
            assistant_text = ""
            body = json.dumps({
                "schemaVersion": "messages-v1",
                "messages": message_list,
                "system": system_list,
                "inferenceConfig": inf_params,
            })
            start_time = datetime.now()

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body
                )
                chunk_count = 0
                time_to_first_token = None

                # Process the response stream
                stream = response.get("body")
                if stream:
                    for event in stream:
                        chunk = event.get("chunk")
                        if chunk:
                            # Print the response chunk
                            chunk_json = json.loads(chunk.get("bytes").decode())
                            # Pretty print JSON
                            content_block_delta = chunk_json.get("contentBlockDelta")
                            if content_block_delta:
                                if time_to_first_token is None:
                                    time_to_first_token = datetime.now() - start_time
                                    print(f"Time to first token: {time_to_first_token}")

                                chunk_count += 1
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                                delta_text = content_block_delta.get("delta").get("text")
                                # print(delta_text, end="")
                                self.edit_3.insertPlainText(delta_text)  
                                generation_text = generation_text + delta_text
                                QApplication.processEvents()

                    print(f"Total chunks: {chunk_count}")
                else:
                    print("No response stream received.")

                # Write the generated text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(generation_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Nova Lite model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Nova Lite")


# Amazon Nova Lite Multimodal -- amazon.lite-micro-v1:0

    def resize_and_convert_to_base64_PNG(self, file_name):
        """
        Resizes and converts the given image file to Base64-encoded PNG format.
        
        Args:
            file_name (str): The path to the image file.
        
        Returns:
            str: Base64-encoded PNG string or None if an error occurs.
        """
        try:
            # Open the image file
            with Image.open(file_name) as img:
                # Convert the image to RGB if necessary (to ensure compatibility with PNG format)
                img = img.convert("RGBA") if img.mode not in ["RGB", "RGBA"] else img

                # Resize the image (optional: specify your resize logic)
                img = img.resize((512, 512))  # Example size; adjust as needed

                # Save the image in PNG format to a memory buffer
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)

                # Convert the buffer to Base64
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                return img_base64
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def talk_with_novaLite_MM(self, clients):
        self.clients = clients
        """
        Opens a file dialog for the user to select an image, processes the image, 
        converts it to PNG if necessary, and displays it in Base64 format in the QTextEdit widget.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            None, "Select Image", "", 
            "Images (*.jpeg *.jpg *.png *.gif *.webp);;All Files (*)", 
            options=options
        )
        
        if file_name:
            img_base64 = self.resize_and_convert_to_base64_PNG(file_name)
            if img_base64:
                html_img = f'<img src="data:image/png;base64,{img_base64}">'
                self.edit_3.setHtml(html_img)
                self.talk_with_novaLite_image(img_base64, self.clients)
            else:
                self.edit_3.setText("Unsupported image format or an error occurred.")


## talk_with_novaLite_image
    def talk_with_novaLite_image(self,img_base64,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Nova Lite')


        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Lite')

    
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        message_list = [{"role": "user", "content": [{"text": input_text}]}]

        # Convert string values to appropriate numeric types
        inf_params = {
            "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
            "top_p": float(params['top_p']),                 # Already a float, no conversion needed
            "top_k": int(params['top_k']),                   # Already an int, no conversion needed
            "temperature": float(params['temperature'])      # Convert to float
        }
        self.edit_3.clear()
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.nova-lite-v1:0'
        assistant_text = ""
        body = json.dumps({
            "schemaVersion": "messages-v1",
            # "messages": message_list,
            "messages": [
                        {
                        "role": "user",
                        "content": [
                            {
                            "text": input_text
                            },
                            {
                            "image": {
                                "format": "png",
                                "source": {
                                "bytes": img_base64
                                }
                            }
                            }
                        ]
                        }
                    ],
            "system": system_list,
            "inferenceConfig": inf_params,
        })

        start_time = datetime.now()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            chunk_count = 0
            time_to_first_token = None

            # Process the response stream
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        # Print the response chunk
                        chunk_json = json.loads(chunk.get("bytes").decode())
                        # Pretty print JSON
                        content_block_delta = chunk_json.get("contentBlockDelta")
                        if content_block_delta:
                            if time_to_first_token is None:
                                time_to_first_token = datetime.now() - start_time
                                print(f"Time to first token: {time_to_first_token}")

                            chunk_count += 1
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                            delta_text = content_block_delta.get("delta").get("text")
                            # print(delta_text, end="")
                            self.edit_3.insertPlainText(delta_text)  
                            QApplication.processEvents()

                print(f"Total chunks: {chunk_count}")
            else:
                print("No response stream received.")
            self.edit_3.insertPlainText("\n") 

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Nova Lite model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Nova Lite")



# Amazon Nova Pro -- amazon.nova-pro-v1:0
    def talk_with_novaPro(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Pro')
    
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        message_list = [{"role": "user", "content": [{"text": input_text}]}]

        # Convert string values to appropriate numeric types
        inf_params = {
            "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
            "top_p": float(params['top_p']),                 # Already a float, no conversion needed
            "top_k": int(params['top_k']),                   # Already an int, no conversion needed
            "temperature": float(params['temperature'])      # Convert to float
        }

        self.edit_3.clear()
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.nova-pro-v1:0'
        assistant_text = ""
        body = json.dumps({
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params,
        })
        start_time = datetime.now()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            chunk_count = 0
            time_to_first_token = None

            # Process the response stream
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        # Print the response chunk
                        chunk_json = json.loads(chunk.get("bytes").decode())
                        # Pretty print JSON
                        content_block_delta = chunk_json.get("contentBlockDelta")
                        if content_block_delta:
                            if time_to_first_token is None:
                                time_to_first_token = datetime.now() - start_time
                                print(f"Time to first token: {time_to_first_token}")

                            chunk_count += 1
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                            delta_text = content_block_delta.get("delta").get("text")
                            # print(delta_text, end="")
                            self.edit_3.insertPlainText(delta_text)  
                            QApplication.processEvents()

                print(f"Total chunks: {chunk_count}")
            else:
                print("No response stream received.")
            self.edit_3.insertPlainText("\n") 

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Nova Pro model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Nova Pro")


# Amazon Nova Pro BATCH -- amazon.nova-pro-v1:0
    def talk_with_novaPro_batch(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Pro')

        ##--
        batch_files = self.prepare_batch_files()
        for file in batch_files:    
            generation_text = ""
            # Concatenate text from self.edit_1 and self.edit_2
            input_text = self.edit_1.toPlainText() + " " + file["content"]
        ##--
            # Remove comments from input_text 
            input_text = self.process_comments(input_text)
            message_list = [{"role": "user", "content": [{"text": input_text}]}]

            # Convert string values to appropriate numeric types
            inf_params = {
                "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
                "top_p": float(params['top_p']),                 # Already a float, no conversion needed
                "top_k": int(params['top_k']),                   # Already an int, no conversion needed
                "temperature": float(params['temperature'])      # Convert to float
            }

            self.edit_3.clear()
            while input_text.startswith("\n"):
                input_text = input_text[1:]

            modelId = 'amazon.nova-pro-v1:0'
            assistant_text = ""
            body = json.dumps({
                "schemaVersion": "messages-v1",
                "messages": message_list,
                "system": system_list,
                "inferenceConfig": inf_params,
            })
            start_time = datetime.now()

            try:
                response = self.clients['bedrun'].invoke_model_with_response_stream(
                    modelId=modelId,
                    body=body
                )
                chunk_count = 0
                time_to_first_token = None

                # Process the response stream
                stream = response.get("body")
                if stream:
                    for event in stream:
                        chunk = event.get("chunk")
                        if chunk:
                            # Print the response chunk
                            chunk_json = json.loads(chunk.get("bytes").decode())
                            # Pretty print JSON
                            content_block_delta = chunk_json.get("contentBlockDelta")
                            if content_block_delta:
                                if time_to_first_token is None:
                                    time_to_first_token = datetime.now() - start_time
                                    print(f"Time to first token: {time_to_first_token}")

                                chunk_count += 1
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                                delta_text = content_block_delta.get("delta").get("text")
                                # print(delta_text, end="")
                                self.edit_3.insertPlainText(delta_text)  
                                generation_text = generation_text + delta_text
                                QApplication.processEvents()

                    print(f"Total chunks: {chunk_count}")
                else:
                    print("No response stream received.")

                # Write the generated text to the output file
                try:
                    with open(file["output_filename"], 'w') as outfile:
                        outfile.write(generation_text)
                except IOError as e:
                    QMessageBox.critical(None, "File Writing Error", f"An error occurred writing to {file['output_filename']}: {str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Error invoking Nova Pro model: {str(e)}")
        QMessageBox.information(None, "Completed", "Batch processing complete.")
        if self.wayback == 1:
            self.LogWayBack("Nova Pro")

    def talk_with_novaPro_MM(self, clients):
        self.clients = clients
        """
        Opens a file dialog for the user to select an image, processes the image, 
        converts it to PNG if necessary, and displays it in Base64 format in the QTextEdit widget.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            None, "Select Image", "", 
            "Images (*.jpeg *.jpg *.png *.gif *.webp);;All Files (*)", 
            options=options
        )
        
        if file_name:
            img_base64 = self.resize_and_convert_to_base64_PNG(file_name)
            if img_base64:
                html_img = f'<img src="data:image/png;base64,{img_base64}">'
                self.edit_3.setHtml(html_img)
                self.talk_with_novaPro_image(img_base64, self.clients)
            else:
                self.edit_3.setText("Unsupported image format or an error occurred.")


## talk_with_novaPro_image
    def talk_with_novaPro_image(self,img_base64,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Nova Pro')


        
        system_list = [
            {
                "text": " "
            }
        ]
        # Get the model settings
        params = self.fetch_parameters('Nova Pro')

    
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        message_list = [{"role": "user", "content": [{"text": input_text}]}]

        # Convert string values to appropriate numeric types
        inf_params = {
            "max_new_tokens": int(params['max_new_tokens']),  # Convert to int
            "top_p": float(params['top_p']),                 # Already a float, no conversion needed
            "top_k": int(params['top_k']),                   # Already an int, no conversion needed
            "temperature": float(params['temperature'])      # Convert to float
        }
        self.edit_3.clear()
        while input_text.startswith("\n"):
            input_text = input_text[1:]

        modelId = 'amazon.nova-pro-v1:0'
        assistant_text = ""
        body = json.dumps({
            "schemaVersion": "messages-v1",
            # "messages": message_list,
            "messages": [
                        {
                        "role": "user",
                        "content": [
                            {
                            "text": input_text
                            },
                            {
                            "image": {
                                "format": "png",
                                "source": {
                                "bytes": img_base64
                                }
                            }
                            }
                        ]
                        }
                    ],
            "system": system_list,
            "inferenceConfig": inf_params,
        })

        start_time = datetime.now()

        try:
            response = self.clients['bedrun'].invoke_model_with_response_stream(
                modelId=modelId,
                body=body
            )
            chunk_count = 0
            time_to_first_token = None

            # Process the response stream
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        # Print the response chunk
                        chunk_json = json.loads(chunk.get("bytes").decode())
                        # Pretty print JSON
                        content_block_delta = chunk_json.get("contentBlockDelta")
                        if content_block_delta:
                            if time_to_first_token is None:
                                time_to_first_token = datetime.now() - start_time
                                print(f"Time to first token: {time_to_first_token}")

                            chunk_count += 1
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
                            delta_text = content_block_delta.get("delta").get("text")
                            # print(delta_text, end="")
                            self.edit_3.insertPlainText(delta_text)  
                            QApplication.processEvents()

                print(f"Total chunks: {chunk_count}")
            else:
                print("No response stream received.")
            self.edit_3.insertPlainText("\n") 

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Nova Lite model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Nova Pro")



# Amazon Nova Canvas (image) -- amazon.nova-canvas-v1:0'
    def talk_with_novaCanvas(self,clients):
        print("DEBUG-Nova Canvas")
        self.clients = clients
        params = self.fetch_parameters('Nova Canvas')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]
        
        modelId = 'amazon.nova-canvas-v1:0'

        body = json.dumps(
        {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": input_text},
        "imageGenerationConfig": {
            "numberOfImages": params['numberOfImages'],
            "cfgScale": params['cfgScale'],
            "height": params['height'],
            "width": params['width'],
            "seed": params['seed'],
        }, } )

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]
            self.last_base64_image = base64_image_data
            html_img = f'<img src="data:image/jpeg;base64,{base64_image_data}">'
            self.edit_3.append(html_img)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Nova Canvas model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Nova Canvas")




# Amazon Nova Reel (video)
    def talk_with_novaReel(self,clients):
        print("DEBUG-Nova Reel")
        pass
    


## ------------------------- SUBMIT to AI models ------------------------

## -------- Image Generation --------------------------------------------

# Stable Diffusion XL | stability.stable-diffusion-xl |
# stability.stable-diffusion-xl-v1
    def stability_image_gen(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        params = self.fetch_parameters('Stability XL')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]
        
        modelId = 'stability.stable-diffusion-xl-v1'
        body = json.dumps({
            "text_prompts": [{"text":input_text}], 
            "seed": params['seed'],
            "cfg_scale": params['cfg_scale'],
            "steps": params['steps'] 
            })

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["artifacts"][0]["base64"]
            self.last_base64_image = base64_image_data
            html_img = f'<img src="data:image/jpeg;base64,{base64_image_data}">'
            self.edit_3.append(html_img)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Stabilit XL model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Stability XL")

    def titan_image_gen(self,clients):
        self.clients = clients
        params = self.fetch_parameters('Titan G1')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]
        
        modelId = 'amazon.titan-image-generator-v1'

        body = json.dumps(
        {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": input_text},
        "imageGenerationConfig": {
            "numberOfImages": params['numberOfImages'],
            "quality": params['quality'],
            "cfgScale": params['cfgScale'],
            "height": params['height'],
            "width": params['width'],
            "seed": params['seed'],
        }, } )

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]
            self.last_base64_image = base64_image_data
            html_img = f'<img src="data:image/jpeg;base64,{base64_image_data}">'
            self.edit_3.append(html_img)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G1 model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Titan G1")


    def titan_image_gen2(self,clients):
        self.clients = clients
        params = self.fetch_parameters('Titan G2')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.edit_1.toPlainText() + " " + self.edit_2.toPlainText()
        # Remove comments from input_text 
        input_text = self.process_comments(input_text)
        while input_text.startswith("\n"):
            input_text = input_text[1:]
        
        modelId = 'amazon.titan-image-generator-v2:0'

        body = json.dumps(
        {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": input_text},
        "imageGenerationConfig": {
            "numberOfImages": params['numberOfImages'],
            "quality": params['quality'],
            "cfgScale": params['cfgScale'],
            "height": params['height'],
            "width": params['width'],
            "seed": params['seed'],
        }, } )

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]
            self.last_base64_image = base64_image_data
            html_img = f'<img src="data:image/jpeg;base64,{base64_image_data}">'
            self.edit_3.append(html_img)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G2 model: {str(e)}")
        if self.wayback == 1:
            self.LogWayBack("Titan G2")



    def save_image_as_jpeg(self,clients):
        self.clients = clients
        """Saves the image as a JPEG file, using QMessageBox for notifications and QFileDialog to specify the file name."""
        if not self.last_base64_image:
            QMessageBox.information(None, "Save Image", "No image data to save. Please ensure that the image data is loaded.", QMessageBox.Ok)
            return

        # Open file dialog to specify the file name
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(None, "Save Image", "", "JPEG Files (*.jpeg;*.jpg);;All Files (*)", options=options)

        # Check if the user provided a file name
        if fileName:
            try:
                image_data = base64.b64decode(self.last_base64_image)
                image = Image.open(io.BytesIO(image_data))
                # Check if user provided a file extension; if not, append ".jpeg"
                if not (fileName.lower().endswith('.jpeg') or fileName.lower().endswith('.jpg')):
                    fileName += '.jpeg'
                image.save(fileName, "JPEG")
                QMessageBox.information(None, "Save Image", f"Image successfully saved as {fileName}.", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(None, "Save Image Error", f"An error occurred: {e}", QMessageBox.Ok)
        else:
            QMessageBox.information(None, "Save Canceled", "Image save operation was canceled.", QMessageBox.Ok)

    def save_image_as_png(self,clients):
        self.clients = clients
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        """Saves the image as a PNG file, using QMessageBox for notifications and QFileDialog to specify the file name."""
        if not self.last_base64_image:
            QMessageBox.information(None, "Save Image", "No image data to save. Please ensure that the image data is loaded.", QMessageBox.Ok)
            return

        # Open file dialog to specify the file name
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(None, "Save Image", "", "PNG Files (*.png);;All Files (*)", options=options)

        # Check if the user provided a file name
        if fileName:
            try:
                image_data = base64.b64decode(self.last_base64_image)
                image = Image.open(io.BytesIO(image_data))
                # Check if user provided a file extension; if not, append ".png"
                if not fileName.lower().endswith('.png'):
                    fileName += '.png'
                image.save(fileName, "PNG")
                QMessageBox.information(None, "Save Image", f"Image successfully saved as {fileName}.", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(None, "Save Image Error", f"An error occurred: {e}", QMessageBox.Ok)
        else:
            QMessageBox.information(None, "Save Canceled", "Image save operation was canceled.", QMessageBox.Ok)

