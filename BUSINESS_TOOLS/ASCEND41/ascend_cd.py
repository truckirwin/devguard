# ascend_cd.py
# Forge Ascend v4.0
# Updated by Tom Stern, 05 NOV 2024
#
#   based on Ascend 1 -- first version January 22 2024 -- by Tom Stern
#


import os
import json
import sys
import webbrowser
import platform
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QGroupBox,
                             QPushButton, QFrame, QMainWindow, QRadioButton, QGridLayout, QInputDialog,
                             QFormLayout, QFileDialog, QDialog, QMessageBox, QLineEdit, QStyle, QTableWidget,
                             QTableWidgetItem, QTabWidget, QScrollArea, QComboBox)
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon, QTextCharFormat
from PyQt5.QtCore import Qt


### ----------------- [ BaseForm ]-------------------------------------------------------
##
##    The BaseForm provides default operations that are overloaded by the individual form.
##    It ensures that the forms all operate similarly to provide a consistent and simplified user experience.
##
class BaseForm:
    def __init__(self, form_id):
        self.form_id = form_id
        self.data = {}
        self.file_name = f"{form_id}_data.json"

    def save(self):
        self.data['header'] = {'form_id': self.form_id}
        with open(self.file_name, 'w') as f:
            json.dump(self.data, f)

    def load(self):
        try:
            with open(self.file_name, 'r') as f:
                self.data = json.load(f)
            self.validate_data()
        except FileNotFoundError:
            print(f"File {self.file_name} not found.")
    
    def validate_data(self):
        if 'header' not in self.data or self.data['header']['form_id'] != self.form_id:
            raise ValueError("Invalid data format for this form.")

    def submit_to_ai(self, input_data):
        # Implement AI submission logic here
        response = self.send_to_ai_service(input_data)
        self.handle_ai_response(response)
    
    def handle_ai_response(self, response):
        # Process the AI response and update form data
        self.data['ai_response'] = response
        self.save()

    def send_to_ai_service(self, input_data):
        # Placeholder method to simulate AI interaction
        return {"response": f"Processed {input_data}"}
    
### $$$ ### --------------------------[ STEP 1: Define the form functions here ]-------------------------- ### $$$ ###
###
###
### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###



## -------- FORM A  ----------------------------
##
##   FORM A is the basic structure of a Form for the CurDev feature of Ascend.
##   You copy this entire block of code and rename all the FormA items to something else, like FormB etc.
##   Then you customize all those parts that touch fields, including input, output, defaults, and ai submission
##
class FormA(BaseForm, QWidget):  # Inherit from QWidget
    def __init__(self, parent):  # Accept the CurDev instance as an argument
        super().__init__('FormA')
        self.parent = parent  # Store reference to the CurDev instance

    # Method to save the current form data to the default project directory
    def save_defaults(self, data):
        file_path = os.path.join(self.parent.current_project, "FormA.json")
        with open(file_path, 'w') as file:
            json.dump(data, file)

    # This is the method that is called to open the dialog form
    def launch_form_interaction(self):
        class FormInteraction(QDialog):
            def __init__(self, parent):
                super().__init__(parent)
                self.parent = parent
                self.setup_ui()
                self.load_defaults()

            def setup_ui(self):
                # ---- Add UI elements and layout...
                # Stylesheet for making the form look attractive and functional
                self.setStyleSheet("""
                    QLabel {
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        color: #333;
                        margin-bottom: 5px;
                    }
                    QLabel.explanation {
                        color: blue;
                        font-size: 12px;
                        margin-top: -5px;
                        margin-bottom: 10px;
                    }
                    QLineEdit, QTextEdit, QComboBox {
                        font-family: Arial, sans-serif;
                        font-size: 13px;
                        padding: 5px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }
                    QPushButton {
                        background-color: #5cb85c;
                        color: white;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        padding: 7px 15px;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #4cae4c;
                    }
                """)

                # Set the dialog to be resizable
                self.setMinimumSize(1200, 700)
                self.setWindowTitle("Form A Basic AI Interaction")

                # Create a scroll area to contain the form content
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)

                # Create a widget to hold the form fields
                form_widget = QWidget()
        
                # Main layout for the form
                self.main_layout = QVBoxLayout(form_widget)

                
                # Create a group box to enclose the instruction field
                instructions_group_box = QGroupBox()
                instructions_group_box_layout = QVBoxLayout(instructions_group_box)

                # Create the title label
                title_label = QLabel("INSTRUCTIONS:")
                title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                instructions_group_box_layout.addWidget(title_label)
    
                # Create the explanation label
                explanation_label = QLabel("Please provide detailed instructions below. These instructions will guide the AI's responses. You can include multiple lines of text if necessary.")
                explanation_label.setStyleSheet("color: blue; font-size: 12px;")
                explanation_label.setWordWrap(True)
                instructions_group_box_layout.addWidget(explanation_label)
    
                # Create the QTextEdit field
                self.instructions_input = QTextEdit()
                instructions_group_box_layout.addWidget(self.instructions_input)
    
                # Optional: Set a style for the bounding box
                instructions_group_box.setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        margin-top: 10px;
                    }
                """)

                self.main_layout.addWidget(instructions_group_box)

                self.add_field("DESTRUCTIONS", 
                       "Please provide detailed instructions below. These instructions will guide the AI's responses. You can include multiple lines of text if necessary.",
                       QTextEdit)

                # Set the form widget as the scroll area's widget
                scroll_area.setWidget(form_widget)
                # Set the scroll area as the main layout for the dialog
                layout = QVBoxLayout(self)
                layout.addWidget(scroll_area)
                self.setLayout(layout)

                # Buttons at the bottom of the form
                button_layout = QHBoxLayout()
                
                save_button = QPushButton("Save Form")
                save_button.clicked.connect(self.save_form)
                button_layout.addWidget(save_button)
                
                load_button = QPushButton("Load Form")
                load_button.clicked.connect(self.load_form)
                button_layout.addWidget(load_button)
                
                validate_button = QPushButton("Validate Check")
                validate_button.clicked.connect(self.validate_form)
                button_layout.addWidget(validate_button)
                
                clear_button = QPushButton("Clear Form")
                clear_button.clicked.connect(self.clear_form)
                button_layout.addWidget(clear_button)
                
                submit_button = QPushButton("Submit")               ## The Submit button calls aelf.accept
                submit_button.clicked.connect(self.accept)          ## This is how the data is collected from the form
                button_layout.addWidget(submit_button)              ## And stored in a dictionary.
                
                close_button = QPushButton("Close")
                close_button.clicked.connect(self.reject)  # Close form wihtout saving or submitting
                button_layout.addWidget(close_button)

                # Add button layout to main layout
                self.main_layout.addLayout(button_layout)
                
                self.setLayout(self.main_layout)


                # ---- End Add UI elements and layout...
        

            # --  Start of methods that are called by the form buttons
            #
            def load_defaults(self):
                file_path = os.path.join(self.parent.current_project, "FormA.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        self.instructions_input.setPlainText(data.get("instructions", ""))

            def save_form(self):
                initial_directory = os.path.join(self.parent.current_project)
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Form", os.path.join(initial_directory, "FormA.json"), "JSON Files (*.json)")
                if file_name:
                    data = {
                        "instructions": self.instructions_input.toPlainText(),
                    }
                    with open(file_name, 'w') as file:
                        json.dump(data, file)

            def get_inputs(self):
                # Collect form data into a dictionary
                # in the [CUSTOMIZATION] area you will assemble a prompt string from the dictionary
                return {
                    "instructions": self.instructions_input.toPlainText(),
                }
            
            def load_form(self):
                file_name, _ = QFileDialog.getOpenFileName(self, "Load Form", "", "JSON Files (*.json)")
                if file_name:
                    with open(file_name, 'r') as file:
                        data = json.load(file)
                        ##>> [CUSTOMIZE-1]
                        self.instructions_input.setPlainText(data.get("instructions", ""))

            def validate_form(self):
                # Simple validation logic
                ##>> [CUSTOMIZE-2]
                if not self.instructions_input.toPlainText():
                    QMessageBox.warning(self, "Validation", "Instructions cannot be empty.")
                else:
                    QMessageBox.information(self, "Validation", "Form is valid.")

            def clear_form(self):
                ##>> [CUSTOMIZE-3]
                self.instructions_input.clear()

            def add_field(self, title: str, explanation: str, widget_class):
                # Create a group box to enclose the field
                group_box = QGroupBox()
                group_box_layout = QVBoxLayout(group_box)
        
                # Create the title label
                title_label = QLabel(title + ":")
                title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                group_box_layout.addWidget(title_label)
        
                # Create the explanation label
                explanation_label = QLabel(explanation)
                explanation_label.setStyleSheet("color: blue; font-size: 12px;")
                explanation_label.setWordWrap(True)
                group_box_layout.addWidget(explanation_label)
        
                # Create the input widget
                input_widget = widget_class()
                group_box_layout.addWidget(input_widget)
        
                # Optional: Set a style for the bounding box
                group_box.setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        margin-top: 10px;
                    }
                """)

                # Add the group box to the main layout
                self.main_layout.addWidget(group_box)
        
                # Return the input widget in case you need to access it later
                return input_widget

            # --  End of methods that are called by the form buttons
     
        # -- This code launches the dialog, collects inputs, submits to ai, andprints diagnostics.
        dialog = FormInteraction(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            inputs = dialog.get_inputs()
            self.save_defaults(inputs)
            self.submit_to_ai(inputs)
            # self.print_basic_ai_interaction(inputs)  ## Uncomment to debug

    def submit_to_ai(self, inputs):
        # Convert the dictionary to a string. For example, concatenating values.
        # ##>> [CUSTOMIZE-4]
        input_text = self.convert_inputs_to_string(inputs)
        ## End of input_text construction.
        initial_directory = os.path.join(self.parent.current_project)
        output_filename = os.path.join(initial_directory, "FormA_OUT.txt") 
        # Call the parent's ai_action method with the converted string and output file
        self.parent.ai_action(self.parent.clients, input_text, output_filename)
        # This will result in calling Claude Sonnet 3.0 and storing the response in the CurDev QTextEdit self.cd_edit
    
    def convert_inputs_to_string(self, inputs):
        # Example conversion logic: concatenate all input fields with a delimiter (e.g., space)
        ## [CUSTOMIZATION] ==> This is where you assemble the form fields into the input string for submission to the AI.
        input_text = " ".join([str(value) for key, value in inputs.items()])
        return input_text
        
    def print_basic_ai_interaction(self, inputs):
        # Print all collected information from the inputs dictionary
        for key, value in inputs.items():
            print(f"{key.replace('_', ' ').title()}: {value}\n")

##
## -------- FORM A END ----------------------------
## ------------------------------------------------


## -------- FORM B  ----------------------------
##
##   FORM B is a template for producing a standard Product Requirements Document (PRD)
##   It generates FormB_PRD.txt which is used in subsequent steps. This only contains the
##   Information necessary to produce a Design. It lacks specifics for market or launch.
##
class FormB(BaseForm, QWidget):  # Inherit from QWidget
    def __init__(self, parent):  # Accept the CurDev instance as an argument
        super().__init__('FormB')
        self.parent = parent  # Store reference to the CurDev instance

    # Method to save the current form data to the default project directory
    def save_defaults(self, data):
        file_path = os.path.join(self.parent.current_project, "FormB.json")
        with open(file_path, 'w') as file:
            json.dump(data, file)

    # This is the method that is called to open the dialog form
    def launch_form_interaction(self):
        class FormInteraction(QDialog):
            def __init__(self, parent):
                super().__init__(parent)
                self.parent = parent
                self.setup_ui()
                self.load_defaults()

            def setup_ui(self):
                # ---- Add UI elements and layout...
                # Stylesheet for making the form look attractive and functional
                self.setStyleSheet("""
                    QLabel {
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        color: #333;
                        margin-bottom: 5px;
                    }
                    QLabel.explanation {
                        color: blue;
                        font-size: 12px;
                        margin-top: -5px;
                        margin-bottom: 10px;
                    }
                    QLineEdit, QTextEdit, QComboBox {
                        font-family: Arial, sans-serif;
                        font-size: 13px;
                        padding: 5px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }
                    QPushButton {
                        background-color: #5cb85c;
                        color: white;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        padding: 7px 15px;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #4cae4c;
                    }
                """)

                # Set the dialog to be resizable
                self.setMinimumSize(1200, 700)
                self.setWindowTitle("Form B: Product Requirements Document (PRD)")

                 # Create a scroll area to contain the form content
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)

                # Create a widget to hold the form fields
                form_widget = QWidget()

                # Main layout for the dialog
                self.main_layout = QVBoxLayout(form_widget)

                self.custom_instructions = self.add_field("CUSTOM INSTRUCTIONS", 
                       "You can modify the default PRD instructions here. Normally, leave this empty.",
                       QTextEdit)
    
                self.technology_input = self.add_field("TECHNOLOGY:", "Specify the technology area relevant to the training.", QLineEdit)
                self.market_input = self.add_field("MARKET:", "Identify the target market for this training product.", QLineEdit)
                self.product_objectives_input = self.add_field("PRODUCT OBJECTIVES:", "Briefly describe the primary goals of the training product.", QTextEdit)
                self.title_input = self.add_field("TITLE:", "Enter the title of the training program.", QLineEdit)
                self.key_objectives_input = self.add_field("KEY OBJECTIVES:", "Specify the key objectives of the training product.", QTextEdit)
                self.target_audience_input = self.add_field("TARGET AUDIENCE AND SPECIFIC LEARNING NEEDS:", "Identify the intended users and their learning needs.", QTextEdit)
                self.tc_goal_alignment_input = self.add_field("T&C GOAL ALIGNMENT:", "Explain how this product aligns with broader goals.", QTextEdit)
                self.financial_targets_input = self.add_field("FINANCIAL TARGETS:", "Define financial goals, such as revenue targets or cost savings.", QTextEdit)
                self.existing_solutions_input = self.add_field("EXISTING SOLUTIONS:", "List current solutions available in the curriculum or offered by AWS.", QTextEdit)
                self.product_differentiator_input = self.add_field("PRODUCT DIFFERENTIATOR:", "Describe what sets this product apart from existing solutions.", QTextEdit)
                self.customer_feedback_input = self.add_field("CUSTOMER FEEDBACK:", "Summarize feedback received from potential users.", QTextEdit)
                self.driving_technology_trends_input = self.add_field("DRIVING TECHNOLOGY TRENDS:", "Identify key technology trends addressed by the product.", QTextEdit)
                self.key_topics_input = self.add_field("KEY TOPICS:", "List the main topics the curriculum will cover.", QTextEdit)
                self.key_skills_input = self.add_field("KEY SKILLS:", "List the key skills that will be developed.", QTextEdit)
                self.key_services_features_input = self.add_field("KEY SERVICES FEATURES:", "List the key service features of the training product.", QTextEdit)
                self.key_solutions_input = self.add_field("KEY SOLUTIONS AND BEST PRACTICES:", "List the key solutions and best practices covered.", QTextEdit)
                self.modality_input = self.add_field("MODALITY:", "Specify the learning modalities (e.g., online, in-person, hybrid).", QLineEdit)
                self.level_input = self.add_field("LEVEL:", "Indicate the proficiency level targeted.", QComboBox, ["Beginner", "Intermediate", "Advanced"])
                self.duration_input = self.add_field("DURATION:", "Specify the total duration of the training program.", QLineEdit)
                self.certification_alignment_input = self.add_field("CERTIFICATION ALIGNMENT:", "Identify any certifications the training aligns with.", QTextEdit)
                self.assessment_requirements_input = self.add_field("ASSESSMENT REQUIREMENTS:", "Describe how learners' progress will be assessed.", QTextEdit)
                self.localization_requirements_input = self.add_field("LOCALIZATION REQUIREMENTS:", "Specify if the product needs to be adapted for different languages or regions.", QTextEdit)
                self.governance_requirements_input = self.add_field("GOVERNANCE AND COMPLIANCE REQUIREMENTS:", "List any industry or educational standards for compliance.", QTextEdit)
                self.launch_plan_input = self.add_field("LAUNCH PLAN:", "Specify the desired launch timeline and any dependencies.", QTextEdit)
                self.requested_launch_date_input = self.add_field("REQUESTED LAUNCH DATE:", "Indicate the requested launch date for the product.", QLineEdit)
                self.external_dependencies_input = self.add_field("EXTERNAL DEPENDENCIES:", "Identify any external dependencies that must be met.", QTextEdit)
                self.maintenance_plan_input = self.add_field("MAINTENANCE PLAN:", "Outline the plan for updating and maintaining the product.", QTextEdit)

                # Set the form widget as the scroll area's widget
                scroll_area.setWidget(form_widget)
                # Set the scroll area as the main layout for the dialog
                layout = QVBoxLayout(self)
                layout.addWidget(scroll_area)
                self.setLayout(layout)

                # Buttons at the bottom of the form
                button_layout = QHBoxLayout()
                
                save_button = QPushButton("Save Form")
                save_button.clicked.connect(self.save_form)
                button_layout.addWidget(save_button)
                
                load_button = QPushButton("Load Form")
                load_button.clicked.connect(self.load_form)
                button_layout.addWidget(load_button)
                
                validate_button = QPushButton("Validate Check")
                validate_button.clicked.connect(self.validate_form)
                button_layout.addWidget(validate_button)
                
                clear_button = QPushButton("Clear Form")
                clear_button.clicked.connect(self.clear_form)
                button_layout.addWidget(clear_button)
                
                submit_button = QPushButton("Submit")               ## The Submit button calls aelf.accept
                submit_button.clicked.connect(self.accept)          ## This is how the data is collected from the form
                button_layout.addWidget(submit_button)              ## And stored in a dictionary.
                
                close_button = QPushButton("Close")
                close_button.clicked.connect(self.reject)  # Close form wihtout saving or submitting
                button_layout.addWidget(close_button)

                # Add button layout to main layout
                self.main_layout.addLayout(button_layout)
                
                self.setLayout(self.main_layout)


                # ---- End Add UI elements and layout...
        

            # --  Start of methods that are called by the form buttons
 
            def load_defaults(self):
                file_path = os.path.join(self.parent.current_project, "FormB.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        self.custom_instructions.setPlainText(data.get("custom_instructions", ""))
                        self.technology_input.setText(data.get("technology", ""))
                        self.market_input.setText(data.get("market", ""))
                        self.product_objectives_input.setPlainText(data.get("product_objectives", ""))
                        self.title_input.setText(data.get("title", ""))
                        self.key_objectives_input.setPlainText(data.get("key_objectives", ""))
                        self.target_audience_input.setPlainText(data.get("target_audience", ""))
                        self.tc_goal_alignment_input.setPlainText(data.get("tc_goal_alignment", ""))
                        self.financial_targets_input.setPlainText(data.get("financial_targets", ""))
                        self.existing_solutions_input.setPlainText(data.get("existing_solutions", ""))
                        self.product_differentiator_input.setPlainText(data.get("product_differentiator", ""))
                        self.customer_feedback_input.setPlainText(data.get("customer_feedback", ""))
                        self.driving_technology_trends_input.setPlainText(data.get("driving_technology_trends", ""))
                        self.key_topics_input.setPlainText(data.get("key_topics", ""))
                        self.key_skills_input.setPlainText(data.get("key_skills", ""))
                        self.key_services_features_input.setPlainText(data.get("key_services_features", ""))
                        self.key_solutions_input.setPlainText(data.get("key_solutions", ""))
                        self.modality_input.setText(data.get("modality", ""))
                        self.level_input.setCurrentText(data.get("level", ""))  # For QComboBox
                        self.duration_input.setText(data.get("duration", ""))
                        self.certification_alignment_input.setPlainText(data.get("certification_alignment", ""))
                        self.assessment_requirements_input.setPlainText(data.get("assessment_requirements", ""))
                        self.localization_requirements_input.setPlainText(data.get("localization_requirements", ""))
                        self.governance_requirements_input.setPlainText(data.get("governance_requirements", ""))
                        self.launch_plan_input.setPlainText(data.get("launch_plan", ""))
                        self.requested_launch_date_input.setText(data.get("requested_launch_date", ""))
                        self.external_dependencies_input.setPlainText(data.get("external_dependencies", ""))
                        self.maintenance_plan_input.setPlainText(data.get("maintenance_plan", ""))

            def save_form(self):
                initial_directory = os.path.join(self.parent.current_project)
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Form", os.path.join(initial_directory, "FormB.json"), "JSON Files (*.json)")
                if file_name:
                    data = {
                        "custom_instructions": self.custom_instructions.toPlainText(),
                        "technology": self.technology_input.text(),
                        "market": self.market_input.text(),
                        "product_objectives": self.product_objectives_input.toPlainText(),
                        "title": self.title_input.text(),
                        "key_objectives": self.key_objectives_input.toPlainText(),
                        "target_audience": self.target_audience_input.toPlainText(),
                        "tc_goal_alignment": self.tc_goal_alignment_input.toPlainText(),
                        "financial_targets": self.financial_targets_input.toPlainText(),
                        "existing_solutions": self.existing_solutions_input.toPlainText(),
                        "product_differentiator": self.product_differentiator_input.toPlainText(),
                        "customer_feedback": self.customer_feedback_input.toPlainText(),
                        "driving_technology_trends": self.driving_technology_trends_input.toPlainText(),
                        "key_topics": self.key_topics_input.toPlainText(),
                        "key_skills": self.key_skills_input.toPlainText(),
                        "key_services_features": self.key_services_features_input.toPlainText(),
                        "key_solutions": self.key_solutions_input.toPlainText(),
                        "modality": self.modality_input.text(),
                        "level": self.level_input.currentText(),  # For QComboBox
                        "duration": self.duration_input.text(),
                        "certification_alignment": self.certification_alignment_input.toPlainText(),
                        "assessment_requirements": self.assessment_requirements_input.toPlainText(),
                        "localization_requirements": self.localization_requirements_input.toPlainText(),
                        "governance_requirements": self.governance_requirements_input.toPlainText(),
                        "launch_plan": self.launch_plan_input.toPlainText(),
                        "requested_launch_date": self.requested_launch_date_input.text(),
                        "external_dependencies": self.external_dependencies_input.toPlainText(),
                        "maintenance_plan": self.maintenance_plan_input.toPlainText(),
                    }
                    with open(file_name, 'w') as file:
                        json.dump(data, file)

            def get_inputs(self):
                # Collect form data into a dictionary
                return {
                    "custom_instructions": self.custom_instructions.toPlainText(),
                    "technology": self.technology_input.text(),
                    "market": self.market_input.text(),
                    "product_objectives": self.product_objectives_input.toPlainText(),
                    "title": self.title_input.text(),
                    "key_objectives": self.key_objectives_input.toPlainText(),
                    "target_audience": self.target_audience_input.toPlainText(),
                    "tc_goal_alignment": self.tc_goal_alignment_input.toPlainText(),
                    "financial_targets": self.financial_targets_input.toPlainText(),
                    "existing_solutions": self.existing_solutions_input.toPlainText(),
                    "product_differentiator": self.product_differentiator_input.toPlainText(),
                    "customer_feedback": self.customer_feedback_input.toPlainText(),
                    "driving_technology_trends": self.driving_technology_trends_input.toPlainText(),
                    "key_topics": self.key_topics_input.toPlainText(),
                    "key_skills": self.key_skills_input.toPlainText(),
                    "key_services_features": self.key_services_features_input.toPlainText(),
                    "key_solutions": self.key_solutions_input.toPlainText(),
                    "modality": self.modality_input.text(),
                    "level": self.level_input.currentText(),  # For QComboBox
                    "duration": self.duration_input.text(),
                    "certification_alignment": self.certification_alignment_input.toPlainText(),
                    "assessment_requirements": self.assessment_requirements_input.toPlainText(),
                    "localization_requirements": self.localization_requirements_input.toPlainText(),
                    "governance_requirements": self.governance_requirements_input.toPlainText(),
                    "launch_plan": self.launch_plan_input.toPlainText(),
                    "requested_launch_date": self.requested_launch_date_input.text(),
                    "external_dependencies": self.external_dependencies_input.toPlainText(),
                    "maintenance_plan": self.maintenance_plan_input.toPlainText(),
                } 


            #def load_form(self):
            #    file_name, _ = QFileDialog.getOpenFileName(self, "Load Form", "", "JSON Files (*.json)")
            #    if file_name:
            #        with open(file_name, 'r') as file:
            #            data = json.load(file)
            #            ##>> [CUSTOMIZE-1]
            #            self.instructions_input.setPlainText(data.get("instructions", ""))

            def load_form(self):
                file_name, _ = QFileDialog.getOpenFileName(self, "Load Form", "", "JSON Files (*.json)")
                if file_name:
                    with open(file_name, 'r') as file:
                        data = json.load(file)
                        self.custom_instructions.setPlainText(data.get("custom_instructions", ""))
                        self.technology_input.setText(data.get("technology", ""))
                        self.market_input.setText(data.get("market", ""))
                        self.product_objectives_input.setPlainText(data.get("product_objectives", ""))
                        self.title_input.setText(data.get("title", ""))
                        self.key_objectives_input.setPlainText(data.get("key_objectives", ""))
                        self.target_audience_input.setPlainText(data.get("target_audience", ""))
                        self.tc_goal_alignment_input.setPlainText(data.get("tc_goal_alignment", ""))
                        self.financial_targets_input.setPlainText(data.get("financial_targets", ""))
                        self.existing_solutions_input.setPlainText(data.get("existing_solutions", ""))
                        self.product_differentiator_input.setPlainText(data.get("product_differentiator", ""))
                        self.customer_feedback_input.setPlainText(data.get("customer_feedback", ""))
                        self.driving_technology_trends_input.setPlainText(data.get("driving_technology_trends", ""))
                        self.key_topics_input.setPlainText(data.get("key_topics", ""))
                        self.key_skills_input.setPlainText(data.get("key_skills", ""))
                        self.key_services_features_input.setPlainText(data.get("key_services_features", ""))
                        self.key_solutions_input.setPlainText(data.get("key_solutions", ""))
                        self.modality_input.setText(data.get("modality", ""))
                        self.level_input.setCurrentText(data.get("level", ""))  # For QComboBox
                        self.duration_input.setText(data.get("duration", ""))
                        self.certification_alignment_input.setPlainText(data.get("certification_alignment", ""))
                        self.assessment_requirements_input.setPlainText(data.get("assessment_requirements", ""))
                        self.localization_requirements_input.setPlainText(data.get("localization_requirements", ""))
                        self.governance_requirements_input.setPlainText(data.get("governance_requirements", ""))
                        self.launch_plan_input.setPlainText(data.get("launch_plan", ""))
                        self.requested_launch_date_input.setText(data.get("requested_launch_date", ""))
                        self.external_dependencies_input.setPlainText(data.get("external_dependencies", ""))
                        self.maintenance_plan_input.setPlainText(data.get("maintenance_plan", ""))


            def validate_form(self):
                # Simple validation logic
                ##>> [CUSTOMIZE-2]
                if not self.instructions_input.toPlainText():
                    QMessageBox.warning(self, "Validation", "Instructions cannot be empty.")
                else:
                    QMessageBox.information(self, "Validation", "Form is valid.")

            #def clear_form(self):
            #    ##>> [CUSTOMIZE-3]
            #    self.instructions_input.clear()

            def clear_form(self):
                self.custom_instructions.clear()
                self.technology_input.clear()
                self.market_input.clear()
                self.product_objectives_input.clear()
                self.title_input.clear()
                self.key_objectives_input.clear()
                self.target_audience_input.clear()
                self.tc_goal_alignment_input.clear()
                self.financial_targets_input.clear()
                self.existing_solutions_input.clear()
                self.product_differentiator_input.clear()
                self.customer_feedback_input.clear()
                self.driving_technology_trends_input.clear()
                self.key_topics_input.clear()
                self.key_skills_input.clear()
                self.key_services_features_input.clear()
                self.key_solutions_input.clear()
                self.modality_input.clear()
                self.level_input.setCurrentIndex(0)  # Reset QComboBox to the first item
                self.duration_input.clear()
                self.certification_alignment_input.clear()
                self.assessment_requirements_input.clear()
                self.localization_requirements_input.clear()
                self.governance_requirements_input.clear()
                self.launch_plan_input.clear()
                self.requested_launch_date_input.clear()
                self.external_dependencies_input.clear()
                self.maintenance_plan_input.clear()

            def add_field(self, title: str, explanation: str, widget_class,  combo_items=None):
                # Create a group box to enclose the field
                group_box = QGroupBox()
                group_box_layout = QVBoxLayout(group_box)
        
                # Create the title label
                title_label = QLabel(title + ":")
                title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                group_box_layout.addWidget(title_label)
        
                # Create the explanation label
                explanation_label = QLabel(explanation)
                explanation_label.setStyleSheet("color: blue; font-size: 12px;")
                explanation_label.setWordWrap(True)
                group_box_layout.addWidget(explanation_label)
        
                # Create the input widget
                input_widget = widget_class()
                group_box_layout.addWidget(input_widget)

                # Setup combo box items if provided
                if isinstance(input_widget, QComboBox) and combo_items:
                    input_widget.addItems(combo_items)

                # Optional: Set a style for the bounding box
                group_box.setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        margin-top: 10px;
                    }
                """)

                # Add the group box to the main layout
                self.main_layout.addWidget(group_box)
        
                # Return the input widget in case you need to access it later
                return input_widget

            # --  End of methods that are called by the form buttons
     
        # -- This code launches the dialog, collects inputs, submits to ai, andprints diagnostics.
        dialog = FormInteraction(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            inputs = dialog.get_inputs()
            self.save_defaults(inputs)
            self.submit_to_ai(inputs)
            # self.print_basic_ai_interaction(inputs)  ## Uncomment to debug

    def submit_to_ai(self, inputs):
        # Convert the dictionary to a string. For example, concatenating values.
        # ##>> [CUSTOMIZE-4]
        input_text = self.convert_inputs_to_string(inputs)
        ## End of input_text construction.
        initial_directory = os.path.join(self.parent.current_project)
        output_filename = os.path.join(initial_directory, "FormB_OUT.txt")  
        # Call the parent's ai_action method with the converted string and output file
        self.parent.ai_action(self.parent.clients, input_text, output_filename)
        # This will result in calling Claude Sonnet 3.0 and storing the response in the CurDev QTextEdit self.cd_edit
    
    #def convert_inputs_to_string(self, inputs):
    #    # Example conversion logic: concatenate all input fields with a delimiter (e.g., space)
    #    ## [CUSTOMIZATION] ==> This is where you assemble the form fields into the input string for submission to the AI.
    #    input_text = " ".join([str(value) for key, value in inputs.items()])
    #    return input_text

    def convert_inputs_to_string(self, inputs):
        # Begin constructing the prompt string
        input_text = (
            f"Act as a team of technical training Product Managers with expert technical knowledge in "
            f"TECHNOLOGY: {inputs['technology']} and deep marketing knowledge in market segments "
            f"MARKET: {inputs['market']}. Your job is to write a Product Requirements Document for a "
            f"technical training product. Read the PRODUCT OBJECTIVES: and write the Product Requirements "
            f"Document. The primary purpose of this document is to inform the Curriculum Development Team "
            f"about the product so that they can design it. The document should be complete, concise, direct, "
            f"comprehensive, and communicate exactly what requirements there are for the new training product. "
            f"Use passive voice transformation style.\n\n"
        )

        input_text += f"TECHNOLOGY:\n{inputs['technology']}\n\n"
        input_text += f"MARKET:\n{inputs['market']}\n\n"
        input_text += f"PRODUCT OBJECTIVES:\n{inputs['product_objectives']}\n\n"
        input_text += f"TITLE:\n{inputs['title']}\n\n"
        
        input_text += "[Briefly describe the primary goals of the training product.]\n"
        input_text += f"KEY OBJECTIVES:\n{inputs['key_objectives']}\n\n"
        
        input_text += "[Identify the intended users and outline their unique learning requirements.]\n"
        input_text += f"TARGET AUDIENCE AND SPECIFIC LEARNING NEEDS:\n{inputs['target_audience']}\n\n"
        
        input_text += "[Explain how this product aligns with the broader organizational or institutional objectives.]\n"
        input_text += f"T&C GOAL ALIGNMENT:\n{inputs['tc_goal_alignment']}\n\n"
        
        input_text += "[Define financial goals, such as revenue targets or cost savings.]\n"
        input_text += f"FINANCIAL TARGETS:\n{inputs['financial_targets']}\n\n"
        
        input_text += "---- Research ----\n\n"
        
        input_text += "[List current solutions available in the curriculum or offered by AWS.]\n"
        input_text += "[We may be able to reuse material from these sources.]\n"
        input_text += f"EXISTING SOLUTIONS:\n{inputs['existing_solutions']}\n\n"
        
        input_text += "[Describe what sets this product apart from existing solutions.]\n"
        input_text += f"PRODUCT DIFFERENTIATOR:\n{inputs['product_differentiator']}\n\n"
        
        input_text += "[Summarize feedback received from potential users about their needs and preferences.]\n"
        input_text += f"CUSTOMER FEEDBACK:\n{inputs['customer_feedback']}\n\n"
        
        input_text += "[Identify key trends in technology that the product will address.]\n"
        input_text += f"DRIVING TECHNOLOGY TRENDS:\n{inputs['driving_technology_trends']}\n\n"
        
        input_text += "---- Product Requirements ----\n\n"
        
        input_text += "[List the main topics, skills, features, and solutions the curriculum will cover.]\n"
        input_text += f"KEY TOPICS:\n{inputs['key_topics']}\n\n"
        input_text += f"KEY SKILLS:\n{inputs['key_skills']}\n\n"
        input_text += f"KEY SERVICES FEATURES:\n{inputs['key_services_features']}\n\n"
        input_text += f"KEY SOLUTIONS AND BEST PRACTICES:\n{inputs['key_solutions']}\n\n"
        
        input_text += "[Specify the learning modalities (e.g., online, in-person, hybrid) to be used.]\n"
        input_text += f"MODALITY:\n{inputs['modality']}\n\n"
        
        input_text += "[Indicate the proficiency level targeted (e.g., beginner, intermediate, advanced).]\n"
        input_text += f"LEVEL:\n{inputs['level']}\n\n"
        
        input_text += "[Specify the total duration of the training program.]\n"
        input_text += f"DURATION:\n{inputs['duration']}\n\n"
        
        input_text += "[Identify any certifications the training aligns with or prepares users for.]\n"
        input_text += f"CERTIFICATION ALIGNMENT:\n{inputs['certification_alignment']}\n\n"
        
        input_text += "[Describe how learners' progress and proficiency will be assessed.]\n"
        input_text += f"ASSESSMENT REQUIREMENTS:\n{inputs['assessment_requirements']}\n\n"
        
        input_text += "[Specify if the product needs to be adapted for different languages or regions.]\n"
        input_text += f"LOCALIZATION REQUIREMENTS:\n{inputs['localization_requirements']}\n\n"
        
        input_text += "[List any industry or educational standards for compliance.]\n"
        input_text += f"GOVERNANCE AND COMPLIANCE REQUIREMENTS:\n{inputs['governance_requirements']}\n\n"
        
        input_text += "[Specify the desired launch timeline and any dependencies that must be met.]\n"
        input_text += f"LAUNCH PLAN:\n{inputs['launch_plan']}\n\n"
        
        input_text += f"REQUESTED LAUNCH DATE:\n{inputs['requested_launch_date']}\n\n"
        
        input_text += f"EXTERNAL DEPENDENCIES:\n{inputs['external_dependencies']}\n\n"
        
        input_text += "[Outline the plan for updating and maintaining the product.]\n"
        input_text += f"MAINTENANCE PLAN:\n{inputs['maintenance_plan']}\n\n"

        return input_text

        
    def print_basic_ai_interaction(self, inputs):
        # Print all collected information from the inputs dictionary
        for key, value in inputs.items():
            print(f"{key.replace('_', ' ').title()}: {value}\n")

##
## -------- FORM B END ----------------------------
## ------------------------------------------------

## -------- FORM C  ----------------------------
##
##   FORM C generates the Detailed Design Document from the PRD.
##   Use the customization field to add references and restrict what information is used in the design.
##   
##
class FormC(BaseForm, QWidget):  # Inherit from QWidget
    def __init__(self, parent):  # Accept the CurDev instance as an argument
        super().__init__('FormC')
        self.parent = parent  # Store reference to the CurDev instance

    # Method to save the current form data to the default project directory
    def save_defaults(self, data):
        file_path = os.path.join(self.parent.current_project, "FormC.json")
        with open(file_path, 'w') as file:
            json.dump(data, file)

    # This is the method that is called to open the dialog form
    def launch_form_interaction(self):
        class FormInteraction(QDialog):
            def __init__(self, parent):
                super().__init__(parent)
                self.parent = parent
                self.setup_ui()
                self.load_defaults()

            def setup_ui(self):
                # ---- Add UI elements and layout...
                # Stylesheet for making the form look attractive and functional
                self.setStyleSheet("""
                    QLabel {
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        color: #333;
                        margin-bottom: 5px;
                    }
                    QLabel.explanation {
                        color: blue;
                        font-size: 12px;
                        margin-top: -5px;
                        margin-bottom: 10px;
                    }
                    QLineEdit, QTextEdit, QComboBox {
                        font-family: Arial, sans-serif;
                        font-size: 13px;
                        padding: 5px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }
                    QPushButton {
                        background-color: #5cb85c;
                        color: white;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        padding: 7px 15px;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #4cae4c;
                    }
                """)

                # Set the dialog to be resizable
                self.setMinimumSize(1200, 700)
                self.setWindowTitle("Form C: Detailed Design Document (DDD)")

                # Create a scroll area to contain the form content
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)

                # Create a widget to hold the form fields
                form_widget = QWidget()
        
                # Main layout for the form
                self.main_layout = QVBoxLayout(form_widget)

                self.ddd_file = self.add_field("FILE: PRODUCT REQUIREMENTS DOCUMENT (PRD):", 
                       "This should already contain the path to the PRD text file. You can override the path here.",
                       QTextEdit)

                initial_directory = os.path.join(self.parent.current_project)
                output_filename = os.path.join(initial_directory, "FormB_OUT.txt")
                self.ddd_file.setPlainText(output_filename)

                self.custom_instructions = self.add_field("CUSTOM INSTRUCTIONS", 
                       "You can modify the default PRD instructions here. Normally, leave this empty.",
                       QTextEdit)
                
                self.ddd_text = self.add_field("ADDITIONAL OR ALTERNATE TEXT: DETAILED DESIGN DOCUMENT (DDD):", 
                       "You can add to the DDD or provide text for the PRD here. Normally, leave this empty.",
                       QTextEdit)
                
                # Set the form widget as the scroll area's widget
                scroll_area.setWidget(form_widget)
                # Set the scroll area as the main layout for the dialog
                layout = QVBoxLayout(self)
                layout.addWidget(scroll_area)
                self.setLayout(layout)

                # Buttons at the bottom of the form
                button_layout = QHBoxLayout()
                
                save_button = QPushButton("Save Form")
                save_button.clicked.connect(self.save_form)
                button_layout.addWidget(save_button)
                
                load_button = QPushButton("Load Form")
                load_button.clicked.connect(self.load_form)
                button_layout.addWidget(load_button)
                
                validate_button = QPushButton("Validate Check")
                validate_button.clicked.connect(self.validate_form)
                button_layout.addWidget(validate_button)
                
                clear_button = QPushButton("Clear Form")
                clear_button.clicked.connect(self.clear_form)
                button_layout.addWidget(clear_button)
                
                submit_button = QPushButton("Submit")               ## The Submit button calls aelf.accept
                submit_button.clicked.connect(self.accept)          ## This is how the data is collected from the form
                button_layout.addWidget(submit_button)              ## And stored in a dictionary.
                
                close_button = QPushButton("Close")
                close_button.clicked.connect(self.reject)  # Close form wihtout saving or submitting
                button_layout.addWidget(close_button)

                # Add button layout to main layout
                self.main_layout.addLayout(button_layout)
                
                self.setLayout(self.main_layout)


                # ---- End Add UI elements and layout...
        

            # --  Start of methods that are called by the form buttons
            #
            def load_defaults(self):
                file_path = os.path.join(self.parent.current_project, "FormC.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        self.ddd_file.setPlainText(data.get("ddd_file", ""))
                        self.custom_instructions.setPlainText(data.get("custom_instructions", ""))
                        self.ddd_text.setPlainText(data.get("ddd_text", ""))

            def save_form(self):
                initial_directory = os.path.join(self.parent.current_project)
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Form", os.path.join(initial_directory, "FormC.json"), "JSON Files (*.json)")
                if file_name:
                    data = {
                        "ddd_file": self.ddd_file.toPlainText(),
                        "custom_instructions": self.custom_instructions.toPlainText(),
                        "ddd_text": self.ddd_text.toPlainText(),
                    }
                    with open(file_name, 'w') as file:
                        json.dump(data, file)

            def get_inputs(self):
                # Collect form data into a dictionary
                # in the [CUSTOMIZATION] area you will assemble a prompt string from the dictionary
                return {
                    "ddd_file": self.ddd_file.toPlainText(),
                    "custom_instructions": self.custom_instructions.toPlainText(),
                    "ddd_text": self.ddd_text.toPlainText(),
                }
            
            def load_form(self):
                file_name, _ = QFileDialog.getOpenFileName(self, "Load Form", "", "JSON Files (*.json)")
                if file_name:
                    with open(file_name, 'r') as file:
                        data = json.load(file)
                        ##>> [CUSTOMIZE-1]
                        self.ddd_file.setPlainText(data.get("ddd_file", ""))
                        self.custom_instructions.setPlainText(data.get("custom_instructions", ""))
                        self.ddd_text.setPlainText(data.get("ddd_text", ""))

            def validate_form(self):
                # Simple validation logic
                ##>> [CUSTOMIZE-2]
                if not self.instructions_input.toPlainText():
                    QMessageBox.warning(self, "Validation", "Instructions cannot be empty.")
                else:
                    QMessageBox.information(self, "Validation", "Form is valid.")

            def clear_form(self):
                ##>> [CUSTOMIZE-3]
                self.ddd_file.clear()
                self.custom_instructions.clear()
                self.ddd_text.clear()

            def add_field(self, title: str, explanation: str, widget_class):
                # Create a group box to enclose the field
                group_box = QGroupBox()
                group_box_layout = QVBoxLayout(group_box)
        
                # Create the title label
                title_label = QLabel(title + ":")
                title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                group_box_layout.addWidget(title_label)
        
                # Create the explanation label
                explanation_label = QLabel(explanation)
                explanation_label.setStyleSheet("color: blue; font-size: 12px;")
                explanation_label.setWordWrap(True)
                group_box_layout.addWidget(explanation_label)
        
                # Create the input widget
                input_widget = widget_class()
                group_box_layout.addWidget(input_widget)
        
                # Optional: Set a style for the bounding box
                group_box.setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        margin-top: 10px;
                    }
                """)

                # Add the group box to the main layout
                self.main_layout.addWidget(group_box)
        
                # Return the input widget in case you need to access it later
                return input_widget

            # --  End of methods that are called by the form buttons
     
        # -- This code launches the dialog, collects inputs, submits to ai, andprints diagnostics.
        dialog = FormInteraction(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            inputs = dialog.get_inputs()
            self.save_defaults(inputs)
            self.submit_to_ai(inputs)
            # self.print_basic_ai_interaction(inputs)  ## Uncomment to debug

    def submit_to_ai(self, inputs):
        # Convert the dictionary to a string. For example, concatenating values.
        # ##>> [CUSTOMIZE-4]
        input_text = self.convert_inputs_to_string(inputs)
        ## End of input_text construction.
        initial_directory = os.path.join(self.parent.current_project)
        output_filename = os.path.join(initial_directory, "FormC_OUT.txt") 
        # Call the parent's ai_action method with the converted string
        self.parent.ai_action(self.parent.clients, input_text,output_filename)
        # This will result in calling Claude Sonnet 3.0 and storing the response in the CurDev QTextEdit self.cd_edit
    
    def convert_inputs_to_string(self, inputs):
        # Begin constructing the prompt string
        input_text = (
            f"Act as a team of seasoned Technical Curriculum Architects with expert technical knowledge in AWS technology and training experience "
            f"and Instructional Designers with deep experience in the design of professional training for adult technology professionals. "
            f"I will provide you with a PRODUCT REQUIREMENTS DOCUMENT:. Your job is to follow these instructions to produce a Detailed Design Document."
            f"  "
            f"1. Read the Product Requirements document."
            f"2. Understand the context including  the target audience, the purpose of the training, and any relevant  information you need to design the course."
            f"3. Analyze the requirements, identify the key components, features, and functionalities to be covered."
            f"4. Develop a structured outline organized in a logical and hierarchical manner, with main sections and subsections clearly delineated."
            f"5. Ensure that the content is relevant, practical, and engaging for adult technology professionals."
            f"6. Consider instructional strategies including hands-on activities, case studies, group discussions, and other interactive elements."
            f"7. Verify appropriate level of technical depth for the target audience. Strike a balance between comprehensiveness and conciseness."
            f"8. Incorporate AWS technologies; integrate relevant AWS services, tools, and best practices throughout."
            f"9. Ensure coherence and logical flow, with smooth transitions between sections and subsections."
            f"10. Review for accuracy, completeness, and clarity and incorporate any revisions."
            f"11. Place one separation marker ||| alone on a line by itself between each section of the outline after the first. Do not add to titles."
            f"12. Omit greetings or introductory statements from your response. Omit wrap-ups, closing comments, and summary statements from your response."
            f"  "
        )

        # Add custom instructions to the input text
        input_text += f"ADDITIONAL INSTRUCTIONS:\n{inputs['custom_instructions']}\n\n"
    
        # Add the PRODUCT REQUIREMENTS DOCUMENT section
        input_text += f"PRODUCT REQUIREMENTS DOCUMENT:\n\n"

        # Load the text file from the path in self.ddd_file
        ddd_file_path = inputs['ddd_file'].strip()
        if ddd_file_path:
            try:
                with open(ddd_file_path, 'r', encoding='utf-8') as ddd_file:
                    ddd_file_content = ddd_file.read()
                    input_text += ddd_file_content + "\n\n"
            except (FileNotFoundError, IOError):
                # If the file cannot be loaded, simply ignore and move on
                pass

        # Add the additional or alternate text from self.ddd_text
        input_text += f"{inputs['ddd_text']}\n\n"

        print("DEBUG::: ", input_text)
        return input_text
    

    def print_basic_ai_interaction(self, inputs):
        # Print all collected information from the inputs dictionary
        for key, value in inputs.items():
            print(f"{key.replace('_', ' ').title()}: {value}\n")

##
## -------- FORM C END ----------------------------
## ------------------------------------------------

## -------- FORM D  ----------------------------
##
##   FORM D is the module summary and module split process.
##   Prerpare module summary that is used to provide context for each module
##   
##
class FormD(BaseForm, QWidget):  # Inherit from QWidget
    def __init__(self, parent):  # Accept the CurDev instance as an argument
        super().__init__('FormD')
        self.parent = parent  # Store reference to the CurDev instance

    # Method to save the current form data to the default project directory
    def save_defaults(self, data):
        file_path = os.path.join(self.parent.current_project, "FormD.json")
        with open(file_path, 'w') as file:
            json.dump(data, file)

    # This is the method that is called to open the dialog form
    def launch_form_interaction(self):
        class FormInteraction(QDialog):
            def __init__(self, parent):
                super().__init__(parent)
                self.parent = parent
                self.setup_ui()
                self.load_defaults()

            def setup_ui(self):
                # ---- Add UI elements and layout...
                # Stylesheet for making the form look attractive and functional
                self.setStyleSheet("""
                    QLabel {
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        color: #333;
                        margin-bottom: 5px;
                    }
                    QLabel.explanation {
                        color: blue;
                        font-size: 12px;
                        margin-top: -5px;
                        margin-bottom: 10px;
                    }
                    QLineEdit, QTextEdit, QComboBox {
                        font-family: Arial, sans-serif;
                        font-size: 13px;
                        padding: 5px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }
                    QPushButton {
                        background-color: #5cb85c;
                        color: white;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        padding: 7px 15px;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #4cae4c;
                    }
                """)

                # Set the dialog to be resizable
                self.setMinimumSize(1200, 700)
                self.setWindowTitle("Form D: Context Summary for Modular Development")

                # Create a scroll area to contain the form content
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)

                # Create a widget to hold the form fields
                form_widget = QWidget()
        
                # Main layout for the form
                self.main_layout = QVBoxLayout(form_widget)

                self.prd_file = self.add_field("FILE: PRODUCT REQUIREMENTS DOCUMENT (PRD):", 
                       "This is automatic. You can override the path here if necessary.",
                       QTextEdit)

                self.ddd_file = self.add_field("FILE: DETAILED DESIGN DOCUMENT (DDD):", 
                       "This is automatic. You can override the path here if necessary.",
                       QTextEdit)


                initial_directory = os.path.join(self.parent.current_project)
                output_filename = os.path.join(initial_directory, "FormB_OUT.txt")
                self.prd_file.setPlainText(output_filename)
                output_filename = os.path.join(initial_directory, "FormC_OUT.txt")
                self.ddd_file.setPlainText(output_filename)

                self.custom_instructions = self.add_field("CUSTOM INSTRUCTIONS", 
                       "You can modify the default Course Context Summary instructions here. Normally, leave this empty.",
                       QTextEdit)
                

                
                # Set the form widget as the scroll area's widget
                scroll_area.setWidget(form_widget)
                # Set the scroll area as the main layout for the dialog
                layout = QVBoxLayout(self)
                layout.addWidget(scroll_area)
                self.setLayout(layout)

                # Buttons at the bottom of the form
                button_layout = QHBoxLayout()
                
                save_button = QPushButton("Save Form")
                save_button.clicked.connect(self.save_form)
                button_layout.addWidget(save_button)
                
                load_button = QPushButton("Load Form")
                load_button.clicked.connect(self.load_form)
                button_layout.addWidget(load_button)
                
                validate_button = QPushButton("Validate Check")
                validate_button.clicked.connect(self.validate_form)
                button_layout.addWidget(validate_button)
                
                clear_button = QPushButton("Clear Form")
                clear_button.clicked.connect(self.clear_form)
                button_layout.addWidget(clear_button)
                
                submit_button = QPushButton("Submit")               ## The Submit button calls aelf.accept
                submit_button.clicked.connect(self.accept)          ## This is how the data is collected from the form
                button_layout.addWidget(submit_button)              ## And stored in a dictionary.
                
                close_button = QPushButton("Close")
                close_button.clicked.connect(self.reject)  # Close form wihtout saving or submitting
                button_layout.addWidget(close_button)

                # Add button layout to main layout
                self.main_layout.addLayout(button_layout)
                
                self.setLayout(self.main_layout)


                # ---- End Add UI elements and layout...
        

            # --  Start of methods that are called by the form buttons
            #
            def load_defaults(self):
                file_path = os.path.join(self.parent.current_project, "FormD.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        self.ddd_file.setPlainText(data.get("ddd_file", ""))
                        self.custom_instructions.setPlainText(data.get("custom_instructions", ""))
                        self.prd_file.setPlainText(data.get("prd_file", ""))

            def save_form(self):
                initial_directory = os.path.join(self.parent.current_project)
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Form", os.path.join(initial_directory, "FormC.json"), "JSON Files (*.json)")
                if file_name:
                    data = {
                        "ddd_file": self.ddd_file.toPlainText(),
                        "custom_instructions": self.custom_instructions.toPlainText(),
                        "prd_file": self.prd_file.toPlainText(),
                    }
                    with open(file_name, 'w') as file:
                        json.dump(data, file)

            def get_inputs(self):
                # Collect form data into a dictionary
                # in the [CUSTOMIZATION] area you will assemble a prompt string from the dictionary
                return {
                    "ddd_file": self.ddd_file.toPlainText(),
                    "custom_instructions": self.custom_instructions.toPlainText(),
                    "prd_file": self.prd_file.toPlainText(),
                }
            
            def load_form(self):
                file_name, _ = QFileDialog.getOpenFileName(self, "Load Form", "", "JSON Files (*.json)")
                if file_name:
                    with open(file_name, 'r') as file:
                        data = json.load(file)
                        ##>> [CUSTOMIZE-1]
                        self.ddd_file.setPlainText(data.get("ddd_file", ""))
                        self.custom_instructions.setPlainText(data.get("custom_instructions", ""))
                        self.prd_file.setPlainText(data.get("prd_file", ""))

            def validate_form(self):
                # Simple validation logic
                ##>> [CUSTOMIZE-2]
                if not self.instructions_input.toPlainText():
                    QMessageBox.warning(self, "Validation", "Instructions cannot be empty.")
                else:
                    QMessageBox.information(self, "Validation", "Form is valid.")

            def clear_form(self):
                ##>> [CUSTOMIZE-3]
                self.ddd_file.clear()
                self.custom_instructions.clear()
                self.prd_file.clear()

            def add_field(self, title: str, explanation: str, widget_class):
                # Create a group box to enclose the field
                group_box = QGroupBox()
                group_box_layout = QVBoxLayout(group_box)
        
                # Create the title label
                title_label = QLabel(title + ":")
                title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                group_box_layout.addWidget(title_label)
        
                # Create the explanation label
                explanation_label = QLabel(explanation)
                explanation_label.setStyleSheet("color: blue; font-size: 12px;")
                explanation_label.setWordWrap(True)
                group_box_layout.addWidget(explanation_label)
        
                # Create the input widget
                input_widget = widget_class()
                group_box_layout.addWidget(input_widget)
        
                # Optional: Set a style for the bounding box
                group_box.setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        margin-top: 10px;
                    }
                """)

                # Add the group box to the main layout
                self.main_layout.addWidget(group_box)
        
                # Return the input widget in case you need to access it later
                return input_widget

            # --  End of methods that are called by the form buttons
     
        # -- This code launches the dialog, collects inputs, submits to ai, andprints diagnostics.
        dialog = FormInteraction(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            inputs = dialog.get_inputs()
            self.save_defaults(inputs)
            self.submit_to_ai(inputs)
            # self.print_basic_ai_interaction(inputs)  ## Uncomment to debug

    def submit_to_ai(self, inputs):
        # Convert the dictionary to a string. For example, concatenating values.
        # ##>> [CUSTOMIZE-4]
        input_text = self.convert_inputs_to_string(inputs)
        ## End of input_text construction.
        initial_directory = os.path.join(self.parent.current_project)
        output_filename = os.path.join(initial_directory, "FormD_OUT.txt") 
        # Call the parent's ai_action method with the converted string
        self.parent.ai_action(self.parent.clients, input_text,output_filename)
        # This will result in calling Claude Sonnet 3.0 and storing the response in the CurDev QTextEdit self.cd_edit
    
    def convert_inputs_to_string(self, inputs):
        # Begin constructing the prompt string
        input_text = (

            f"Act as a team of seasoned techincal curriculum developers. Your job is to read the following "
            f"PRODUCT REQUIREMENTS DOCUMENT: and DETAILED DESIGN DOCUMENT:"
            f"Your job is to provide a single concise condensed paragraph that establishes the context of the course for a new member "
            f"working on the team to build the course. They will need a detailed overview of the course and a summary of the most important "
            f"parts of the input documents without getting into details that they will learn when they receive their assignment."
            f"  "
        )
        # Add custom instructions to the input text
        input_text += f"ADDITIONAL INSTRUCTIONS:\n{inputs['custom_instructions']}\n\n"
    
        # Add the PRODUCT REQUIREMENTS DOCUMENT section
        input_text += f"PRODUCT REQUIREMENTS DOCUMENT:\n\n"

        # Load the text file from the path in self.ddd_file
        prd_file_path = inputs['prd_file'].strip()
        if prd_file_path:
            try:
                with open(prd_file_path, 'r', encoding='utf-8') as prd_file:
                    prd_file_content = prd_file.read()
                    input_text += prd_file_content + "\n\n"
            except (FileNotFoundError, IOError):
                # If the file cannot be loaded, simply ignore and move on
                pass

        # Add the PRODUCT REQUIREMENTS DOCUMENT section
        input_text += f"DETAILED DESIGN DOCUMENT:\n\n"

        # Load the text file from the path in self.ddd_file
        ddd_file_path = inputs['ddd_file'].strip()
        if ddd_file_path:
            try:
                with open(ddd_file_path, 'r', encoding='utf-8') as ddd_file:
                    ddd_file_content = ddd_file.read()
                    input_text += ddd_file_content + "\n\n"
            except (FileNotFoundError, IOError):
                # If the file cannot be loaded, simply ignore and move on
                pass

        print("DEBUG::: ", input_text)
        return input_text
    

    def print_basic_ai_interaction(self, inputs):
        # Print all collected information from the inputs dictionary
        for key, value in inputs.items():
            print(f"{key.replace('_', ' ').title()}: {value}\n")


##
## -------- FORM D END ----------------------------






'''

## ---------------------------------------------
### $$$ ### --------------------------[ END STEP 1: Define the form functions here ]---------------------- ### $$$ ###
###
###
### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###
'''


### -----------------    CurDev  --- The Main application definition

class CurDev(QMainWindow):
    def __init__(self, edit_1, edit_2, edit_3, ai_model=None, model_settings=None, clients=None, startup_location=None):
        super().__init__()
        self.edit_1 = edit_1
        self.edit_2 = edit_2
        self.edit_3 = edit_3
        self.ai_model = ai_model  # Now ImageForge has access to AIModelInteraction
        self.model_settings = model_settings
        self.clients = clients    # And can directly call AWS services including Bedrock
        self.history1 = "" # Chat buffers
        self.history2 = ""
        self.left_view = None
        self.right_view = None
        self.left_scene = None
        self.right_scene = None
        self.left_image_storage = [None] * 5
        self.right_image_storage = [None] * 5
        # Detect the operating system
        self.current_os = platform.system()
        self.startup_location = startup_location
        self.current_project = os.path.join(self.startup_location, "projects", "default_project")


    ### $$$ ### --------------------------[ STEP 2: Instantiate forms in the app here ]----------------------- ### $$$ ###
    ###
    ###
    ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###

        self.form_a = FormA(self)  # Instantiate FormA here

        self.form_b = FormB(self)  # Instantiate FormB here

        self.form_c = FormC(self)  # Instantiate FormC here
    
        self.form_d = FormD(self)  # Instantiate FormD here


    ### $$$ ### --------------------------[ END STEP 2: Instantiate forms in the app here ]------------------- ### $$$ ###
    ###
    ###
    ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###


    ## ----------------------------------------------------------


    def some_method(self):
        if self.ai_model:
            result = self.ai_model.some_ai_feature()  # Use a feature from AIModelInteraction
            # Do something with result

    def openCD(self):
        # Set up the main window
        self.setWindowTitle("Ascend CurDev")
        self.setGeometry(100, 100, 800, 600)
        self.resize(1200, 800)

        # --- Editor setting variables
        self.font_size_cd_edit = 14
        self.font_family_cd_edit = "Monospace"
        self.default_format = QTextCharFormat()

        # Debugging to verify usage of self.clients for access to AWS services including Bedrock
        if self.clients:
            print("Clients are available:", self.clients)
            print(self.clients)
        else:
            print("No clients available.")
        # print(self.model_settings)


        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)

        edit_layout = QHBoxLayout()
        control_layout = QHBoxLayout()
        self.projects_layout = QHBoxLayout()
        tab_holder = QHBoxLayout()

        main_layout.addLayout(edit_layout)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(self.projects_layout)
        main_layout.addLayout(tab_holder)

        ## ---------------- BUTTONS -----------------
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
            font-size: 10px;    
            font-weight: normal;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 1px;
            }
            QPushButton:hover { background-color: #FFC200; }
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
        self.buttonStyle_8 = """
        QPushButton {
            background-color: #D5F0FF;
            color: #000000;
            font-family: Arial; 
            font-size: 14px;    
            font-weight: normal;  
            font-style: bold;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #22DEEE; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """
        self.buttonStyle_9 = """
        QPushButton {
            background-color: #FFF0D5;
            color: #000000;
            font-family: Arial; 
            font-size: 14px;    
            font-weight: normal;  
            font-style: bold;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #DDD0A2; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """


        # --- Editor for Main window ---
        self.cd_edit = QTextEdit()
        edit_layout.addWidget(self.cd_edit)

        # --- Controls for Editor ---
        bW = 80
        bW2 = 30
        bH = 20
        b_0001 = QPushButton("Open")
        b_0001.setToolTip("Load a text file into the Command editor.")
        b_0001.setFixedSize(bW,bH)
        b_0001.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(b_0001)
        b_0001.clicked.connect(self.open_cd_edit) 

        b_0002 = QPushButton("Append")
        b_0002.setToolTip("Load multiple files into the Command editor.")
        b_0002.setFixedSize(bW,bH)
        b_0002.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(b_0002)
        b_0002.clicked.connect(self.append_cd_edit) 

        b_0003 = QPushButton("Save")
        b_0003.setToolTip("Save Command editor to a text file.")
        b_0003.setFixedSize(bW,bH)
        b_0003.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(b_0003)
        b_0003.clicked.connect(self.save_cd_edit) 

        b_0004 = QPushButton("ƒ")
        b_0004.setToolTip("Switch between proportional and monospace font.")
        b_0004.setFixedSize(bW2,bH)
        b_0004.setStyleSheet(self.buttonStyle_2)
        control_layout.addWidget(b_0004)
        b_0004.clicked.connect(self.toggle_font_family_cd_edit)

        b_0005 = QPushButton("↑")
        b_0005.setToolTip("Increase font size.")
        b_0005.setFixedSize(bW2,bH)
        b_0005.setStyleSheet(self.buttonStyle_2)
        control_layout.addWidget(b_0005)
        b_0005.clicked.connect(self.increase_font_size_cd_edit) 

        b_0006 = QPushButton("↓")
        b_0006.setToolTip("Decrease font size.")
        b_0006.setFixedSize(bW2,bH)
        b_0006.setStyleSheet(self.buttonStyle_2)
        control_layout.addWidget(b_0006)
        b_0006.clicked.connect(self.decrease_font_size_cd_edit) 

        b_0007 = QPushButton("Clear")
        b_0007.setToolTip("Clear the Command editor.")
        b_0007.setFixedSize(bW,bH)
        b_0007.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(b_0007)
        b_0007.clicked.connect(self.cd_edit_clear) 



        
        self.select_project_menu()



        b_0010 = QPushButton("New Project")
        b_0010.setToolTip("New Project.")
        b_0010.setFixedSize(150,20)
        b_0010.setStyleSheet(self.buttonStyle_5)
        self.projects_layout.addWidget(b_0010)
        b_0010.clicked.connect(self.add_new_project) 

        self.new_project = QLineEdit()
        self.new_project.setFixedWidth(150)
        self.projects_layout.addWidget(self.new_project)
        self.projects_layout.addStretch()

        #b_0010 = QPushButton("Manage Projects")
        #b_0010.setToolTip("Select Project.")
        #b_0010.setFixedSize(150,20)
        #b_0010.setStyleSheet(self.buttonStyle_1)
        #self.projects_layout.addWidget(b_0010)
        #b_0010.clicked.connect(self.manage_projects) 


        #b_0004 = QPushButton("ƒ")
        #b_0004.setToolTip("Switch between proportional and monospace font.")
        #b_0004.setFixedSize(bW2,bH)
        #b_0004.setStyleSheet(self.buttonStyle_2)
        #control_layout.addWidget(b_0004)
        #b_0004.clicked.connect(self.toggle_font_family_edit_1)

        #b_0005 = QPushButton("↑")
        #b_0005.setToolTip("Increase font size.")
        #b_0005.setFixedSize(bW2,bH)
        #b_0005.setStyleSheet(self.buttonStyle_2)
        #control_layout.addWidget(b_0005)
        #b_0005.clicked.connect(self.increase_font_size_edit_1) 

        #b_0006 = QPushButton("Launch Training Requirements Form", self)
        #b_0006.setToolTip("Decrease font size.")
        #b_0006.setFixedSize(bW,bH)
        #b_0006.setStyleSheet(self.buttonStyle_5)
        #control_layout.addWidget(b_0006)
        #b_0006.clicked.connect(self.custom_instructions) 
        #self.launch_button = QPushButton("Launch Training Requirements Form", self)
        #self.launch_button.clicked.connect(self.custom_instructions)







        control_layout.addStretch


        # --- Tabs for ADDIE organization ---

        tab_layout = QVBoxLayout()
        tab_widget = QTabWidget(self)
        tab_widget.setMinimumHeight(200)
        tab_widget.setFixedHeight(240)
        tab_layout.addWidget(tab_widget)
        tab_widget.setStyleSheet("QTabWidget { font-size: 18px; }")


        tab_1 = QWidget()
        tab_layout_1 = QHBoxLayout(tab_1)
        tab_widget.addTab(tab_1, f"Analysis")
        tab_layout_1_1v = QVBoxLayout()
        tab_layout_1_1v_1h = QHBoxLayout()
        tab_layout_1.addLayout(tab_layout_1_1v)

        ### $$$ ### --------------------------[ STEP 3: Create the form launch button ]-------------------------- ### $$$ ###
        ###
        ###
        ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###

        tab_layout_1_1v.addStretch()
        b_01_01 = QPushButton("Product Requirements Document (PRD)", self)
        b_01_01.setToolTip("Launch the Product Requirements Document form.")
        b_01_01.setFixedSize(300,30)
        b_01_01.setStyleSheet(self.buttonStyle_8)
        tab_layout_1_1v.addWidget(b_01_01)
        b_01_01.clicked.connect(self.launch_form_b)  # Connect to launch FormB's Training Requirements


        b_01_03 = QPushButton("View PDM Feedback", self)
        b_01_03.setToolTip("Examine Product Manager  Review of the PRD.")
        b_01_03.setFixedSize(145,30)
        b_01_03.setStyleSheet(self.buttonStyle_9)
        tab_layout_1_1v_1h.addWidget(b_01_03)
        # b_01_03.clicked.connect(self.launch_form_b)  # Connect to launch FormB's Training Requirements

        b_01_04 = QPushButton("View TCA Feedback", self)
        b_01_04.setToolTip("Examine Techincal Curriculum Architect Review of the PRD.")
        b_01_04.setFixedSize(145,30)
        b_01_04.setStyleSheet(self.buttonStyle_9)
        tab_layout_1_1v_1h.addWidget(b_01_04)
        # b_01_04.clicked.connect(self.launch_form_b)  # Connect to launch FormB's Training Requirements

        tab_layout_1_1v.addLayout(tab_layout_1_1v_1h)

        tab_layout_1_1v.addStretch()
        b_01_02 = QPushButton("Example Form Interaction", self)
        b_01_02.setToolTip("Launch Basic AI Interaction form.")
        b_01_02.setFixedSize(300,20)
        b_01_02.setStyleSheet(self.buttonStyle_5)
        tab_layout_1_1v.addWidget(b_01_02)
        b_01_02.clicked.connect(self.launch_form_a)  # Connect to launch FormB's Training Requirements

        ### $$$ ### --------------------------[ STEP 3: Create the form launch button ]-------------------------- ### $$$ ###
        ###
        ###
        ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###

        tab_2 = QWidget()
        tab_layout_2 = QHBoxLayout(tab_2)
        tab_widget.addTab(tab_2, f"Design")
        tab_layout_2_1v = QVBoxLayout()
        tab_layout_2_1v_1h = QHBoxLayout()
        tab_layout_2_1v_2h = QHBoxLayout()
        tab_layout_2_1v_3h = QHBoxLayout()
        tab_layout_2.addLayout(tab_layout_2_1v)
        tab_layout_2_1v.addLayout(tab_layout_2_1v_1h)
        tab_layout_2_1v.addLayout(tab_layout_2_1v_2h)
        tab_layout_2_1v.addLayout(tab_layout_2_1v_3h)

        ### $$$ ### --------------------------[ TAB 2 launch buttons ]-------------------------------------------- ### $$$ ###
        ###
        ###
        ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###

        tab_layout_2_1v_1h.addStretch()
        prd_label = QLabel("[PRD] -->  ")
        #prd_label.setStyleSheet(self.buttonStyle_5)
        prd_label.setStyleSheet("""
        QLabel {
            border: 2px solid #3A3AFF;
            background-color: #E6E6E6;
            color: #3A3AFF;
            font-size: 14px;
            padding: 2px;
            border-radius: 4px;
        }
        QLabel:hover {
            background-color: #D4D4D4;
        }
    """)
        tab_layout_2_1v_1h.addWidget(prd_label)
        b_02_01 = QPushButton("Detailed Design Document (DDD)", self)
        b_02_01.setToolTip("Launch the Detailed Design Document form.")
        b_02_01.setFixedSize(300,30)
        b_02_01.setStyleSheet(self.buttonStyle_8)
        tab_layout_2_1v_1h.addWidget(b_02_01)
        b_02_01.clicked.connect(self.launch_form_c)  # Connect to launch FormC's Detailed Desing Document
        tab_layout_2_1v_1h.addStretch()


        tab_layout_2_1v_2h.addStretch()
        b_02_03 = QPushButton("View TCA Feedback", self)
        b_02_03.setToolTip("Examine Techincal Curriculum Architect Review of the DDD.")
        b_02_03.setFixedSize(145,30)
        b_02_03.setStyleSheet(self.buttonStyle_9)
        tab_layout_2_1v_2h.addWidget(b_02_03)
        # b_02_03.clicked.connect(self.launch_form_b)  # Connect to launch FormB's Training Requirements

        b_02_04 = QPushButton("View ID Feedback", self)
        b_02_04.setToolTip("Examine Instructional Designer Review of the DDD.")
        b_02_04.setFixedSize(145,30)
        b_02_04.setStyleSheet(self.buttonStyle_9)
        tab_layout_2_1v_2h.addWidget(b_02_04)
        # b_02_04.clicked.connect(self.launch_form_b)  # Connect to launch FormB's Training Requirements
        tab_layout_2_1v_2h.addStretch()


        tab_layout_2_1v_3h.addStretch()
        mod_label = QLabel("[DDD] + [PRD] -->  ")
        #prd_label.setStyleSheet(self.buttonStyle_5)
        mod_label.setStyleSheet("""
        QLabel {
            border: 2px solid #3A3AFF;
            background-color: #E6E6E6;
            color: #3A3AFF;
            font-size: 14px;
            padding: 2px;
            border-radius: 4px;
        }
        QLabel:hover {
            background-color: #D4D4D4;
        }
    """)
        tab_layout_2_1v_3h.addWidget(mod_label)
        b_02_02 = QPushButton("Prepare for Modular Development", self)
        b_02_02.setToolTip("Launch the modularization form.")
        b_02_02.setFixedSize(300,30)
        b_02_02.setStyleSheet(self.buttonStyle_8)
        tab_layout_2_1v_3h.addWidget(b_02_02)
        b_02_02.clicked.connect(self.launch_form_d)  # Connect to launch FormC's Detailed Desing Document
        tab_layout_2_1v_3h.addStretch()



        ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###

        tab_3 = QWidget()
        tab_layout_3 = QHBoxLayout(tab_3)
        tab_widget.addTab(tab_3, f"Development")

        tab_4 = QWidget()
        tab_layout_4 = QHBoxLayout(tab_4)
        tab_widget.addTab(tab_4, f"Implementation")

        tab_5 = QWidget()
        tab_layout_5 = QHBoxLayout(tab_5)
        # -- tab 5 controls
        #label = QLabel("Tab 5 Controls")
        #tab_layout_5.addWidget(label)
        tab_widget.addTab(tab_5, f"Evaluation")

        tab_6 = QWidget()
        tab_layout_6 = QHBoxLayout(tab_6)
        # -- tab 6 controls
        label = QLabel("")
        tab_layout_6.addWidget(label)
        tab_widget.addTab(tab_6, f"Additional")

        tab_holder.addLayout(tab_layout)

        # Show the window
        self.show()


    ### $$$ ### --------------------------[ STEP 4: Form Launch Method ]-------------------------------------- ### $$$ ###
    ###
    ###
    ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###
    def launch_form_a(self):
        self.form_a.launch_form_interaction()  # Launch Form A

    def launch_form_b(self):
        self.form_b.launch_form_interaction()  # Launch FormB's Training Requirements

    def launch_form_c(self):
        self.form_c.launch_form_interaction()  # Launch FormC's Detailed Design Document

    def launch_form_d(self):
        self.split_outline()  # Split FormC_OUT.txt to /FormD subdirectory
        self.form_d.launch_form_interaction()  # Launch FormD's Modularization to create the summary


    ### $$$ ### --------------------------[ END STEP 4: Form Launch Method ]---------------------------------- ### $$$ ###
    ###
    ###
    ### $$$ ### ---------------------------------------------------------------------------------------------- ### $$$ ###



    def ai_advice1_clear(self):
        self.history1 = ""
        self.text_description.clear()

    # anthropic.claude-3-sonnet-20240229-v1:0
    def ai_action(self,clients,inputs,output_filename):
        self.clients = clients
        self.inputs = inputs
        self.output_filename = output_filename
        # self.history1 = history1
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 3S')
        # Concatenate text from self.edit_1 and self.edit_2
        # input_text = self.text_description.toPlainText() # + " " + self.edit_2.toPlainText()
        input_text = self.inputs
        #temp_input_buffer = "Human: " + input_text # Preserve human input
        # Add history
        #input_text = self.history1 + "\n" + temp_input_buffer # Construct prompt with history

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

        # Clear self.edit_3
        self.cd_edit.clear()

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
                            self.cd_edit.insertPlainText(resp['delta']['text'])
                            QApplication.processEvents()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        
        # Write cd_edit to output_filename
        # Retrieve the text from the QTextEdit
        text_to_save = self.cd_edit.toPlainText()

        # Write the text to the specified file
        try:
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(text_to_save)
            QMessageBox.information(None, "Success", f"Result saved to {output_filename}")
        except IOError as e:
            QMessageBox.critical(None, "Error", f"Failed to save result to {output_filename}: {e}")

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

## ------------------------- PROJECT Methods --------------------------
    def manage_projects(self):
        # Set the initial directory to the /projects directory
        projects_dir = os.path.join(self.startup_location, "projects")
        
        # Open a QFileDialog to allow selection or creation of a new directory
        selected_directory = QFileDialog.getExistingDirectory(
            None, "Select or Create Project Directory", projects_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        # If a directory is selected, update the current project
        if selected_directory:
            self.current_project = selected_directory
            print(f"Current project directory set to: {self.current_project}")
        else:
            print("No directory selected.")


    def select_project_menu(self):
        # Locate all directories in the projects directory
        projects_dir = os.path.join(self.startup_location, "projects")
        
        if not os.path.exists(projects_dir):
            print(f"Directory {projects_dir} does not exist.")
            return
        
        # Get a list of directories in the projects directory
        project_names = [name for name in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, name))]
        
        if not project_names:
            print(f"No projects found in {projects_dir}.")
            return
        
        # Create a QComboBox (pull-down menu)
        self.project_selector = QComboBox()
        self.project_selector.addItems(project_names)
        
        # Add the combo box to the layout
        project_label = QLabel("Current Project: ")
        self.projects_layout.addWidget(project_label)
        self.projects_layout.addWidget(self.project_selector)
        
        # Connect the combo box selection change to a method
        self.project_selector.currentIndexChanged.connect(self.on_project_selected)
    
    def on_project_selected(self, index):
        # Get the selected project name from the combo box
        selected_project = self.project_selector.currentText()
        
        # Update self.current_project to the selected project directory
        projects_dir = os.path.join(self.startup_location, "projects")
        self.current_project = os.path.join(projects_dir, selected_project)
        print(f"Current project directory set to: {self.current_project}")

    def refresh_project_selector(self, new_project_name=None):
        # Clear the current combo box items
        self.project_selector.clear()

        # Re-populate the combo box with the updated list of directories
        projects_dir = os.path.join(self.startup_location, "projects")
        
        if os.path.exists(projects_dir):
            project_names = [name for name in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, name))]
            self.project_selector.addItems(project_names)
            
            # If a new project name is provided, automatically select it
            if new_project_name and new_project_name in project_names:
                index = self.project_selector.findText(new_project_name)
                if index >= 0:
                    self.project_selector.setCurrentIndex(index)
        else:
            # Show a message box if the projects directory doesn't exist
            QMessageBox.critical(None, "Error", f"Directory {projects_dir} does not exist.")

    def add_new_project(self):
        # Get the new project name from the QLineEdit field self.new_project
        new_project_name = self.new_project.text().strip()
        
        if not new_project_name:
            # Show an error message if the project name is empty
            QMessageBox.warning(None, "Warning", "Project name cannot be empty.")
            return

        # Set the path for the new project directory
        projects_dir = os.path.join(self.startup_location, "projects")
        new_project_dir = os.path.join(projects_dir, new_project_name)
        
        # Check if the directory already exists
        if not os.path.exists(new_project_dir):
            os.makedirs(new_project_dir)
            # Show a message box confirming the directory was created
            QMessageBox.information(None, "Success", f"New project directory created: {new_project_dir}")
            
            # Refresh the combo box to reflect the new directory and auto-select the new project
            self.refresh_project_selector(new_project_name)
        else:
            # Show a message box if the directory already exists
            QMessageBox.information(None, "Information", f"Project directory {new_project_dir} already exists.")



## ------------------------ CD_EDIT Methods ----------------------------

#   OPEN cd_edit
#
    def open_cd_edit(self):
        if self.cd_edit:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(None, 'Open File', self.current_project, 'All Files (*)')
            if file_path:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    self.cd_edit.setPlainText(file.read())
        else:
            print("cd_edit is not set.")

#   APPEND CD_EDIT
#
    def append_cd_edit(self):
        # Store the current contents of edit_2
        original_content = self.cd_edit.toPlainText()
        # Add a blank line to separate the original editor contents
        original_content += "\n"
        # Get the file names selected by the user
        file_names, _ = QFileDialog.getOpenFileNames(None, "Select Files", self.current_project, "All Files (*)")

        # Check if any file was selected
        if file_names:
            self.cd_edit.clear()
            # Open each selected file and append its contents to the string
            for file_name in file_names:
                with open(file_name, 'r', encoding='utf-8', errors='ignore') as file:
                    original_content += file.read().strip()  # Append contents of each file
                    original_content += "\n\n"  # Add a blank line between each file's content

            # Store the combined string into cd_Edit
            self.cd_edit.setPlainText(original_content)

#   SAVE CD_EDIT
#

    def save_cd_edit(self):
        if self.cd_edit:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(None, 'Save File', self.current_project, 'Text Files (*.txt);;All Files (*)')
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.cd_edit.toPlainText())
        else:
            print("cd_edit is not set.")


#   CLEAR CD_EDIT
#
    def cd_edit_clear(self):
        self.cd_edit.clear()
        self.default_format = QTextCharFormat()
        self.cd_edit.setCurrentCharFormat(self.default_format)

#   CLEAR CD_EDIT FONT CONTROLS
#
    def increase_font_size_cd_edit(self):
        self.font_size_cd_edit += 2
        self.cd_edit.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_cd_edit, self.font_size_cd_edit))

    def decrease_font_size_cd_edit(self):
        self.font_size_cd_edit -= 2
        if self.font_size_cd_edit < 2:  # Ensure font size doesn't go below 2pt
            self.font_size_cd_edit = 2
        self.cd_edit.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_cd_edit, self.font_size_cd_edit))

    def toggle_font_family_cd_edit(self):
        if self.font_family_cd_edit == "Monospace":
            self.font_family_cd_edit = "Courier"
        else:
            self.font_family_cd_edit = "Monospace"
        self.cd_edit.setStyleSheet("background-color: white; color: black; font-family: {}; font-size: {}pt;".format(self.font_family_cd_edit, self.font_size_cd_edit))


# ---- TEXT Manipulation methods --------------
    def split_outline(self):
        # Step 1: Create the directory FormD in self.current_project if it doesn't exist
        formd_dir = os.path.join(self.current_project, 'FormD')
        if not os.path.exists(formd_dir):
            os.makedirs(formd_dir)

        # Step 2: Open FormC_OUT.txt in read mode
        formc_file = os.path.join(self.current_project, 'FormC_OUT.txt')
        if not os.path.exists(formc_file):
            raise FileNotFoundError(f"{formc_file} does not exist")

        with open(formc_file, 'r') as file:
            content = file.read()

        # Step 3: Split the content by the ||| marker
        parts = content.split('|||')

        # Step 4: Process each part and write it to a separate file in FormD
        for index, part in enumerate(parts):
            # Step 5: Eliminate any blank lines from the beginning and end of the part
            part = part.strip()

            # Step 6: Create a file name with three digits, starting from 001
            filename = f'FormD_OUT_{index + 1:03}.txt'
            filepath = os.path.join(formd_dir, filename)

            # Step 7: Write the cleaned part to the file
            with open(filepath, 'w') as outfile:
                outfile.write(part)
