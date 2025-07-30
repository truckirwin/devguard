# ascend_img.py
# Forge Ascend v4.1
# Updated by Tom Stern, 16 DEC 2024
#
#   based on Ascend 1 -- first version January 22 2024 -- by Tom Stern
#
# Required for upscaler:
# pip install PyQt5 numpy scikit-image pillow
#

import os
import sys
import re
import json
import random
import platform
import base64
from datetime import datetime
from pathlib import Path
import webbrowser

import numpy as np
from skimage import io, img_as_float
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageEnhance, ImageQt

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

from PyQt5.QtCore import (
    Qt, QPointF, QLineF, QByteArray, QTimer, QUrl, QEventLoop, pyqtSlot, QBuffer, QIODevice, QRect
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QImage, QPainter, QTextCursor, QFont, QPen, QColor, QPalette, QTransform
)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem, QLabel,
    QTextEdit, QFrame, QRadioButton, QGridLayout, QGroupBox, QInputDialog, QDoubleSpinBox,
    QSlider, QTabWidget, QColorDialog, QMenu
)
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QImage, QPixmap
import base64
from PyQt5.QtWidgets import QGraphicsPixmapItem  # Import QGraphicsPixmapItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QSlider, QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPen

# from graphviz import Digraph
# from graphviz import Source
from PyQt5.QtGui import QImage, QPixmap

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QImageReader, QPixmap

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QByteArray
import tempfile

### -----------------    ImageForge / ImaGen

class ImageGen(QMainWindow):
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

    def some_method(self):
        if self.ai_model:
            result = self.ai_model.some_ai_feature()  # Use a feature from AIModelInteraction
            # Do something with result

    def openIMG(self):
        # Set up the main window
        self.setWindowTitle("ImaGen")
        self.setGeometry(100, 100, 800, 600)
        self.resize(1200, 800)

        # Debugging to verify usage of self.clients for access to AWS services including Bedrock
        if self.clients:
            # Debug during development
            # print("Clients are available:", self.clients)
            # print(self.clients)
            pass
        else:
            print("No clients available.")
        # print(self.model_settings)



        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)

        # Create a horizontal layout for the image viewers
        viewer_layout = QHBoxLayout()
        viewer_layout_left = QVBoxLayout()
        viewer_layout_left.setSpacing(2)
        viewer_layout_right = QVBoxLayout()
        viewer_layout_right.setSpacing(2)
        viewer_right_controls = QHBoxLayout()
        viewer_right_controls.setSpacing(2)
        viewer_left_controls = QHBoxLayout()
        viewer_left_controls.setSpacing(2)
        viewer_layout.addLayout(viewer_layout_left)
        viewer_layout.addLayout(viewer_layout_right)

        # Create the left QGraphicsView and QGraphicsScene
        self.left_view = QGraphicsView(self)
        self.left_scene = QGraphicsScene(self)
        self.left_view.setScene(self.left_scene)
        self.left_view.setMinimumHeight(500)

        # SCRIBBLE: Initialize variables for drawing
        self.drawing = False
        self.scribble_enabled = False  # Initially disabled
        self.last_point = QPointF()
        # SCRIBBLE: Set the view to accept mouse events
        self.left_clear_image() # Set defaults
        self.left_view.setMouseTracking(True)
        self.scribble() # Install event handler
        self.save_scribble_as_pixmap() # Save initial image to ensure size is fixed at startup
        self.brush_red = 0
        self.brush_green = 0
        self.brush_blue = 120
        self.brush_pixels = 8

        # Create the right QGraphicsView and QGraphicsScene
        self.right_view = QGraphicsView(self)
        self.right_scene = QGraphicsScene(self)
        self.right_view.setScene(self.right_scene)
        self.right_view.setMinimumHeight(500)

        # Add the QGraphicsViews to the horizontal layout
        viewer_layout_left.addWidget(QLabel("INPUT:"))
        viewer_layout_left.addWidget(self.left_view)
        viewer_layout_right.addWidget(QLabel("OUTPUT:"))
        viewer_layout_right.addWidget(self.right_view)

        # Add the viewer layout to the main layout
        viewer_layout_left.addLayout(viewer_left_controls)
        viewer_layout_right.addLayout(viewer_right_controls)
        main_layout.addLayout(viewer_layout)

        # Global settings 
   


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
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #22DEEE; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """


        # Viewer Control Buttons
        cW = 65
        cH = 20 

        # --- Left Viewer Controls ---

        ctl_01 = QPushButton("Open")
        ctl_01.setToolTip("Load image from file.")
        ctl_01.setFixedSize(cW,cH)
        ctl_01.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_01)
        ctl_01.clicked.connect(self.left_open_image) # load_left

        ctl_02 = QPushButton("Save")
        ctl_02.setToolTip("Save image to file.")
        ctl_02.setFixedSize(cW,cH)
        ctl_02.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_02)
        ctl_02.clicked.connect(self.left_save_image) 

        ctl_03 = QPushButton("Clear")
        ctl_03.setToolTip("Clear left viewer.")
        ctl_03.setFixedSize(cW,cH)
        ctl_03.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_03)
        ctl_03.clicked.connect(self.left_clear_image) 

        ctl_04 = QPushButton("In")
        ctl_04.setToolTip("Zoom in.")
        ctl_04.setFixedSize(cW,cH)
        ctl_04.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_04)
        ctl_04.clicked.connect(self.left_zoom_in) 

        ctl_05 = QPushButton("Out")
        ctl_05.setToolTip("Zoom out.")
        ctl_05.setFixedSize(cW,cH)
        ctl_05.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_05)
        ctl_05.clicked.connect(self.left_zoom_out) 

        ctl_06 = QPushButton("Fit")
        ctl_06.setToolTip("Fits the image to the current window while maintaining the aspect")
        ctl_06.setFixedSize(cW,cH)
        ctl_06.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_06)
        ctl_06.clicked.connect(self.left_zoom_reset) 

        ctl_07 = QPushButton("1:1")
        ctl_07.setToolTip("Shows the image at its actual size with a 1:1 pixel ratio.")
        ctl_07.setFixedSize(cW,cH)
        ctl_07.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_07)
        ctl_07.clicked.connect(self.left_zoom_real_size) 

        ctl_08 = QPushButton("▶")
        ctl_08.setToolTip("Copy from left viewer to right viewer.")
        ctl_08.setFixedSize(cW,cH)
        ctl_08.setStyleSheet(self.buttonStyle_1)
        viewer_left_controls.addWidget(ctl_08)
        ctl_08.clicked.connect(self.copy_to_right_viewer)


        # --- Right Viewer Controls

        ctl_11 = QPushButton("◀")
        ctl_11.setToolTip("Copy from right viewer to left viewer.")
        ctl_11.setFixedSize(cW,cH)
        ctl_11.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_11)
        ctl_11.clicked.connect(self.copy_to_left_viewer) 

        ctl_12 = QPushButton("Open")
        ctl_12.setToolTip("Load image from file.")
        ctl_12.setFixedSize(cW,cH)
        ctl_12.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_12)
        ctl_12.clicked.connect(self.right_open_image) 

        ctl_13 = QPushButton("Save")
        ctl_13.setToolTip("Save image to file.")
        ctl_13.setFixedSize(cW,cH)
        ctl_13.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_13)
        ctl_13.clicked.connect(self.right_save_image) 

        ctl_14 = QPushButton("Clear")
        ctl_14.setToolTip("Clear right viewer.")
        ctl_14.setFixedSize(cW,cH)
        ctl_14.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_14)
        ctl_14.clicked.connect(self.right_clear_image) 

        ctl_15 = QPushButton("In")
        ctl_15.setToolTip("Zoom in.")
        ctl_15.setFixedSize(cW,cH)
        ctl_15.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_15)
        ctl_15.clicked.connect(self.right_zoom_in) 

        ctl_16 = QPushButton("Out")
        ctl_16.setToolTip("Zoom out.")
        ctl_16.setFixedSize(cW,cH)
        ctl_16.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_16)
        ctl_16.clicked.connect(self.right_zoom_out) 

        ctl_17 = QPushButton("Fit")
        ctl_17.setToolTip("Fits the image to the current window while maintaining the aspect")
        ctl_17.setFixedSize(cW,cH)
        ctl_17.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_17)
        ctl_17.clicked.connect(self.right_zoom_reset) 

        ctl_18 = QPushButton("1:1")
        ctl_18.setToolTip("Shows the image at its actual size with a 1:1 pixel ratio.")
        ctl_18.setFixedSize(cW,cH)
        ctl_18.setStyleSheet(self.buttonStyle_1)
        viewer_right_controls.addWidget(ctl_18)
        ctl_18.clicked.connect(self.right_zoom_real_size)



        ## ----------------------------------------------------------------
        ##   Global settings
        # -----------------------------------------------------------------[ Global Settings ]
        #       
        ## Load the current model paraneter settings for Titan Image G1 v2 model as default settings for image generation
        params = self.fetch_parameters('Titan G2')
        Spg = 3
        SpW = 5
        # Define layouts
        gset_h1 = QHBoxLayout()
        gset_h1.addStretch()                  # push controls from the left
        gset_h1.setSpacing(Spg)
        gset_h1_v1 = QVBoxLayout()
        gset_h1_v2 = QVBoxLayout()
        gset_h1_v3 = QVBoxLayout()
        gset_h1_v4 = QVBoxLayout()
        gset_h1_v4_h1 = QHBoxLayout()
        gset_h1_v4_h1_v1 = QVBoxLayout()
        gset_h1_v4_h1_v2 = QVBoxLayout()   
        gset_h1_v5 = QVBoxLayout()
        gset_h1_v6 = QVBoxLayout()
        gset_h1_v6_h1 = QHBoxLayout()
        gset_h1_v6_h2 = QHBoxLayout()
        # Position Layouts
        gset_h1.addLayout(gset_h1_v1)
        gset_h1.addSpacing(SpW)
        gset_h1.addLayout(gset_h1_v2)
        gset_h1.addSpacing(SpW)
        gset_h1.addLayout(gset_h1_v3)
        gset_h1.addSpacing(SpW)
        gset_h1.addLayout(gset_h1_v4)
        gset_h1.addSpacing(SpW)
        gset_h1_v4.addLayout(gset_h1_v4_h1)
        gset_h1_v4_h1.addLayout(gset_h1_v4_h1_v1)
        gset_h1_v4_h1.addLayout(gset_h1_v4_h1_v2)
        gset_h1.addLayout(gset_h1_v5)

        # Add column labels
        gset_h1_v1.addWidget(QLabel("Number"))
        gset_h1_v2.addWidget(QLabel("Quality"))
        gset_h1_v3.addWidget(QLabel("CFG Scale"))
        # gset_h1_v4.addWidget(QLabel("Size"))
        gset_h1_v5.addWidget(QLabel("Seed"))
        gset_h1.addStretch()                 # push controls to the left
        gset_h1_v6.addLayout(gset_h1_v6_h1)        # Save 2x 4x
        gset_h1_v6.addLayout(gset_h1_v6_h2)        # 16 32 48 64
        gset_h1.addLayout(gset_h1_v6)        # push button to the right
        gset_h1.addSpacing(10)               # push button back to the left slightly
        #
        # Add hierarchy to right viewer beneath the controls
        viewer_layout_right.addLayout(gset_h1)
        viewer_layout_right.addSpacing(5)
        gset_left_space = QVBoxLayout()
        ## ---- This is where the save and display storage buttons will go
        #gset_left_space.addSpacing(66)
        #viewer_layout_left.addLayout(gset_left_space)



        # --- Add Settings controls and displays
        #
        gset_number_of_images = params['numberOfImages']                       
        self.ui_gset_number_of_images = QLineEdit(str(gset_number_of_images))  
        self.ui_gset_number_of_images.setFixedWidth(45)
        gset_h1_v1.addWidget(self.ui_gset_number_of_images)
        gset_1_label = QLabel("")
        gset_h1_v1.addWidget(gset_1_label)
        #
        gset_quality = params['quality']                
        self.ui_gset_quality = QLineEdit(gset_quality) 
        self.ui_gset_quality.setFixedWidth(65)
        gset_h1_v2.addWidget(self.ui_gset_quality)
        gset_2_label = QLabel("")
        gset_h1_v2.addWidget(gset_2_label)
        #
        gset_cfg = params['cfgScale']
        self.gset_cfgScale = QDoubleSpinBox(self)
        self.gset_cfgScale.setMaximumWidth(65)
        self.gset_cfgScale.setRange(1.1, 10.0)  # Set range from 1.1 to 10.0
        self.gset_cfgScale.setValue(gset_cfg)  # Set default value to model setting (8.0 is default) 
        self.gset_cfgScale.setSingleStep(0.1)   # Set increment step to 0.1
        gset_h1_v3.addWidget(self.gset_cfgScale)
        gset_3_label = QLabel("")
        gset_h1_v3.addWidget(gset_3_label)
        #
        gset_width = params['width'] 
        self.ui_gset_width = QLineEdit(str(gset_width)) 
        self.ui_gset_width.setFixedWidth(45)
        gset_h1_v4_h1_v1.addWidget(QLabel("Width"))
        gset_h1_v4_h1_v1.addWidget(self.ui_gset_width)
        #
        gset_height = params['height']  
        self.ui_gset_height = QLineEdit(str(gset_height)) 
        self.ui_gset_height.setFixedWidth(45)
        gset_h1_v4_h1_v2.addWidget(QLabel("Height"))
        gset_h1_v4_h1_v2.addWidget(self.ui_gset_height)
        #
        gset_size_button = QPushButton("Select Size", self)
        gset_size_button.setStyleSheet(self.buttonStyle_8)
        gset_size_button.clicked.connect(lambda: self.chooseSize('gset'))
        gset_h1_v4.addWidget(gset_size_button)
        #
        gset_seed = params['seed']  
        self.ui_gset_seed = QLineEdit(str(gset_seed))  
        self.ui_gset_seed.setFixedWidth(100)
        gset_h1_v5.addWidget(self.ui_gset_seed)
        gset_random_button = QPushButton("Random", self)
        gset_random_button.setStyleSheet(self.buttonStyle_8)
        gset_random_button.clicked.connect(lambda: self.randomSeed('gset'))
        gset_h1_v5.addWidget(gset_random_button)
        #


        if self.current_os == 'Windows':
            # Apply a different upscale method on Windows
            gset_upscale_button = QPushButton("Save 2x", self)
            gset_upscale_button.setToolTip("Scales up the right viewer image 2x and saves to a file.")
            gset_upscale_button.setFixedSize(65,20)
            gset_upscale_button.setStyleSheet(self.buttonStyle_1)
            gset_upscale_button.clicked.connect(self.Photo_Upscale_and_Save_Simple) 
            gset_h1_v6_h1.addWidget(gset_upscale_button)
        else:
            # Use the high quality upscale method on other platforms 
            gset_upscale_button = QPushButton("Save 4x", self)
            gset_upscale_button.setToolTip("Scales up the right viewer image 4x and saves to a file.")
            gset_upscale_button.setFixedSize(65,20)
            gset_upscale_button.setStyleSheet(self.buttonStyle_1)
            gset_upscale_button.clicked.connect(self.Photo_Upscale_and_Save) 

            gset_upscale_button2 = QPushButton("Save 2x", self)
            gset_upscale_button2.setToolTip("Scales up the right viewer image 2x and saves to a file.")
            gset_upscale_button2.setFixedSize(65,20)
            gset_upscale_button2.setStyleSheet(self.buttonStyle_1)           
            gset_upscale_button2.clicked.connect(self.Photo_Upscale_and_Save_Simple) 
            gset_h1_v6_h1.addWidget(gset_upscale_button2)
            gset_h1_v6_h1.addWidget(gset_upscale_button)
        
        gset_dnscale_16 = QPushButton("16", self)
        gset_dnscale_16.setToolTip("Scales down the right viewer image icon file.")
        gset_dnscale_16.setFixedSize(30,20)
        gset_dnscale_16.setStyleSheet(self.buttonStyle_1)           
        gset_dnscale_16.clicked.connect(lambda: self.down_scaler(16)) 
        gset_h1_v6_h2.addWidget(gset_dnscale_16)

        gset_dnscale_32 = QPushButton("32", self)
        gset_dnscale_32.setToolTip("Scales down the right viewer image icon file.")
        gset_dnscale_32.setFixedSize(30,20)
        gset_dnscale_32.setStyleSheet(self.buttonStyle_1)           
        gset_dnscale_32.clicked.connect(lambda: self.down_scaler(32)) 
        gset_h1_v6_h2.addWidget(gset_dnscale_32)

        gset_dnscale_48 = QPushButton("48", self)
        gset_dnscale_48.setToolTip("Scales down the right viewer image icon file.")
        gset_dnscale_48.setFixedSize(30,20)
        gset_dnscale_48.setStyleSheet(self.buttonStyle_1)           
        gset_dnscale_48.clicked.connect(lambda: self.down_scaler(48)) 
        gset_h1_v6_h2.addWidget(gset_dnscale_48)

        gset_dnscale_64 = QPushButton("64", self)
        gset_dnscale_64.setToolTip("Scales down the right viewer image icon file.")
        gset_dnscale_64.setFixedSize(30,20)
        gset_dnscale_64.setStyleSheet(self.buttonStyle_1)           
        gset_dnscale_64.clicked.connect(lambda: self.down_scaler(64)) 
        gset_h1_v6_h2.addWidget(gset_dnscale_64)

   
        # -----------------------------------------------------------------[ Global Settings ]
        
        # --- Add Storage controls
        #
        # storage_left_h1
        # storage_right_h1
        #
        stW = 20
        stH = 20
        stB = 7

        storage_left_h1 = QHBoxLayout()
        storage_right_h1 = QHBoxLayout()

        storage_left_above_space= QVBoxLayout()
        storage_left_above_space.addSpacing(stB)
        viewer_layout_left.addLayout(storage_left_above_space)
        monospace_font = QFont("Courier")  # Or "Monospace", depending on the system's available fonts
        viewer_layout_left.addLayout(storage_left_h1)
        storage_left_between_space= QVBoxLayout()
        storage_left_between_space.addSpacing(stB)
        viewer_layout_left.addLayout(storage_left_between_space)
        viewer_layout_left.addLayout(storage_right_h1)

        # Left [0]
        left_st_row = QLabel("INPUT Storage:  ")
        left_st_row.setFont(monospace_font)
        storage_left_h1.addWidget(left_st_row)
        
        storage_left_h1.addWidget(QLabel(" 1: "))
        left_st_1 = QPushButton("▼")
        left_st_1.setToolTip("Stores the image in position 1")
        left_st_1.setFixedSize(stW,stH)
        left_st_1.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_st_1)
        left_st_1.clicked.connect(lambda: self.left_save_image_to_storage(0))

        left_disp_1 = QPushButton("▲")
        left_disp_1.setToolTip("Loads the image from position 1")
        left_disp_1.setFixedSize(stW,stH)
        left_disp_1.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_disp_1)
        left_disp_1.clicked.connect(lambda: self.left_display_image_from_storage(0))

        storage_left_h1.addWidget(QLabel(" 2: "))
        left_st_2 = QPushButton("▼")
        left_st_2.setToolTip("Stores the image in position 2")
        left_st_2.setFixedSize(stW,stH)
        left_st_2.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_st_2)
        left_st_2.clicked.connect(lambda: self.left_save_image_to_storage(1))

        left_disp_2 = QPushButton("▲")
        left_disp_2.setToolTip("Loads the image from position 2")
        left_disp_2.setFixedSize(stW,stH)
        left_disp_2.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_disp_2)
        left_disp_2.clicked.connect(lambda: self.left_display_image_from_storage(1))

        storage_left_h1.addWidget(QLabel(" 3: "))
        left_st_3 = QPushButton("▼")
        left_st_3.setToolTip("Stores the image in position 3")
        left_st_3.setFixedSize(stW,stH)
        left_st_3.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_st_3)
        left_st_3.clicked.connect(lambda: self.left_save_image_to_storage(2))

        left_disp_3 = QPushButton("▲")
        left_disp_3.setToolTip("Loads the image from position 3")
        left_disp_3.setFixedSize(stW,stH)
        left_disp_3.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_disp_3)
        left_disp_3.clicked.connect(lambda: self.left_display_image_from_storage(2))

        storage_left_h1.addWidget(QLabel(" 4: "))
        left_st_4 = QPushButton("▼")
        left_st_4.setToolTip("Stores the image in position 4")
        left_st_4.setFixedSize(stW,stH)
        left_st_4.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_st_4)
        left_st_4.clicked.connect(lambda: self.left_save_image_to_storage(3))

        left_disp_4 = QPushButton("▲")
        left_disp_4.setToolTip("Loads the image from position 4")
        left_disp_4.setFixedSize(stW,stH)
        left_disp_4.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_disp_4)
        left_disp_4.clicked.connect(lambda: self.left_display_image_from_storage(3))

        storage_left_h1.addWidget(QLabel(" 5: "))
        left_st_5 = QPushButton("▼")
        left_st_5.setToolTip("Stores the image in position 5")
        left_st_5.setFixedSize(stW,stH)
        left_st_5.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_st_5)
        left_st_5.clicked.connect(lambda: self.left_save_image_to_storage(4))

        left_disp_5 = QPushButton("▲")
        left_disp_5.setToolTip("Loads the image from position 5")
        left_disp_5.setFixedSize(stW,stH)
        left_disp_5.setStyleSheet(self.buttonStyle_2)
        storage_left_h1.addWidget(left_disp_5)
        left_disp_5.clicked.connect(lambda: self.left_display_image_from_storage(4))                

        # Right [0]
        right_st_row = QLabel("OUTPUT Storage: ")
        right_st_row.setFont(monospace_font)
        storage_right_h1.addWidget(right_st_row)

        storage_right_h1.addWidget(QLabel(" 1: "))
        right_st_1 = QPushButton("▼")
        right_st_1.setToolTip("Stores the image in position 1")
        right_st_1.setFixedSize(stW,stH)
        right_st_1.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_st_1)
        right_st_1.clicked.connect(lambda: self.right_save_image_to_storage(0))

        right_disp_1 = QPushButton("▲")
        right_disp_1.setToolTip("Loads the image from position 1")
        right_disp_1.setFixedSize(stW,stH)
        right_disp_1.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_disp_1)
        right_disp_1.clicked.connect(lambda: self.right_display_image_from_storage(0))

        storage_right_h1.addWidget(QLabel(" 2: "))
        right_st_2 = QPushButton("▼")
        right_st_2.setToolTip("Stores the image in position 2")
        right_st_2.setFixedSize(stW,stH)
        right_st_2.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_st_2)
        right_st_2.clicked.connect(lambda: self.right_save_image_to_storage(1))

        right_disp_2 = QPushButton("▲")
        right_disp_2.setToolTip("Loads the image from position 2")
        right_disp_2.setFixedSize(stW,stH)
        right_disp_2.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_disp_2)
        right_disp_2.clicked.connect(lambda: self.right_display_image_from_storage(1))

        storage_right_h1.addWidget(QLabel(" 3: "))
        right_st_3 = QPushButton("▼")
        right_st_3.setToolTip("Stores the image in position 3")
        right_st_3.setFixedSize(stW,stH)
        right_st_3.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_st_3)
        right_st_3.clicked.connect(lambda: self.right_save_image_to_storage(2))

        right_disp_3 = QPushButton("▲")
        right_disp_3.setToolTip("Loads the image from position 3")
        right_disp_3.setFixedSize(stW,stH)
        right_disp_3.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_disp_3)
        right_disp_3.clicked.connect(lambda: self.right_display_image_from_storage(2))

        storage_right_h1.addWidget(QLabel(" 4: "))
        right_st_4 = QPushButton("▼")
        right_st_4.setToolTip("Stores the image in position 4")
        right_st_4.setFixedSize(stW,stH)
        right_st_4.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_st_4)
        right_st_4.clicked.connect(lambda: self.right_save_image_to_storage(3))

        right_disp_4 = QPushButton("▲")
        right_disp_4.setToolTip("Loads the image from position 4")
        right_disp_4.setFixedSize(stW,stH)
        right_disp_4.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_disp_4)
        right_disp_4.clicked.connect(lambda: self.right_display_image_from_storage(3))

        storage_right_h1.addWidget(QLabel(" 5: "))
        right_st_5 = QPushButton("▼")
        right_st_5.setToolTip("Stores the image in position 5")
        right_st_5.setFixedSize(stW,stH)
        right_st_5.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_st_5)
        right_st_5.clicked.connect(lambda: self.right_save_image_to_storage(4))

        right_disp_5 = QPushButton("▲")
        right_disp_5.setToolTip("Stores the image from position 5")
        right_disp_5.setFixedSize(stW,stH)
        right_disp_5.setStyleSheet(self.buttonStyle_2)
        storage_right_h1.addWidget(right_disp_5)
        right_disp_5.clicked.connect(lambda: self.right_display_image_from_storage(4))

        storage_left_h1.addStretch()
        storage_right_h1.addStretch()
        storage_left_below_space= QVBoxLayout()
        storage_left_below_space.addSpacing(stB)
        viewer_layout_left.addLayout(storage_left_below_space)

        # --- Storage controls

        # scribble brush controls                                 
        scribble_controls_h1 = QHBoxLayout()
        scribble_controls_h2 = QHBoxLayout()
        scribble_controls_h3 = QHBoxLayout()
        storage_left_h1.addLayout(scribble_controls_h1)
        storage_left_h1.addLayout(scribble_controls_h2)
        storage_right_h1.addLayout(scribble_controls_h3)

        brush_color = QPushButton("🎨", self)
        brush_color.setFixedWidth(40)
        brush_color.setStyleSheet(self.buttonStyle_2)
        brush_color.clicked.connect(self.choose_brush_color)  
        scribble_controls_h2.addWidget(brush_color)
        scribble_controls_h2.addSpacing(15)

        brush_up_btn = QPushButton("➕", self)
        brush_up_btn.setFixedWidth(20)
        brush_up_btn.setStyleSheet(self.buttonStyle_2)
        brush_up_btn.clicked.connect(self.brush_up)  
        scribble_controls_h3.addWidget(brush_up_btn)

        brush_dn_btn = QPushButton("➖", self)
        brush_dn_btn.setFixedWidth(20)
        brush_dn_btn.setStyleSheet(self.buttonStyle_2)
        brush_dn_btn.clicked.connect(self.brush_dn)  
        scribble_controls_h3.addWidget(brush_dn_btn)
        scribble_controls_h3.addSpacing(15)

        # Create the radio button
        self.radio_button = QRadioButton("Draw  ", self)
        self.radio_button.setChecked(False)  # Initially checked
        self.radio_button.toggled.connect(self.toggle_scribble)

        # Label to display the current state
        # self.scribble_state_label = QLabel("", self)

        # Layout to arrange widgets
        #layout = QVBoxLayout()
        scribble_controls_h1.addWidget(self.radio_button)
        # scribble_controls_h1.addWidget(self.scribble_state_label)


        # --- Tabs for Specific Tasks ---

        tab_layout = QVBoxLayout()
        tab_widget = QTabWidget(self)
        tab_widget.setMinimumHeight(280)
        tab_layout.addWidget(tab_widget)


        tab_1 = QWidget()
        tab_layout_1 = QHBoxLayout(tab_1)
        tab_widget.addTab(tab_1, f"Image Generation")

        tab_2 = QWidget()
        tab_layout_2 = QHBoxLayout(tab_2)
        tab_widget.addTab(tab_2, f"Color Guided Gen")

        tab_3 = QWidget()
        tab_layout_3 = QHBoxLayout(tab_3)
        tab_widget.addTab(tab_3, f"Image Conditioning")

        tab_4 = QWidget()
        tab_layout_4 = QHBoxLayout(tab_4)
        tab_widget.addTab(tab_4, f"Image Variations")

        tab_5 = QWidget()
        tab_layout_5 = QHBoxLayout(tab_5)
        # -- tab 5 controls
        #label = QLabel("Tab 5 Controls")
        #tab_layout_5.addWidget(label)
        tab_widget.addTab(tab_5, f"Adjustments")

        tab_6 = QWidget()
        tab_layout_6 = QHBoxLayout(tab_6)
        # -- tab 6 controls
        label = QLabel("")
        tab_layout_6.addWidget(label)
        tab_widget.addTab(tab_6, f"Crop Image")


        # {
        #"taskType": "BACKGROUND_REMOVAL",
        #"backgroundRemovalParams": {
        #    "image": "base64-encoded string"
        #}
        #}

        # - XContrast adjustment
        #- XBrightness adjustment
        #- XExposure adjustment
        #- XSharpening
        #- XGaussian blur
        #- XGrayscale conversion
        #- XColor adjustments (hue, saturation, etc.)
        #- Resizing and rescaling
        #- Cropping
        #- Rotation
        #- Flipping (horizontally or vertically)
        #- Drawing shapes, text, and annotations on images
        #- Applying filters (e.g., edge detection, embossing, etc.)
        #- Image enhancement techniques (e.g., histogram equalization, denoising, etc.)
        #- Combining multiple images (e.g., overlaying, blending, etc.)
        #- Converting between different image file formats



        tab_7 = QWidget()
        tab_layout_7 = QHBoxLayout(tab_7)
        # -- tab 7 controls
        #label = QLabel("Tab 7 Controls")
        #tab_layout_7.addWidget(label)
        tab_widget.addTab(tab_7, f"Describe")

        '''
        tab_8 = QWidget()
        tab_layout_8 = QHBoxLayout(tab_8)
        # -- tab 7 controls
        #label = QLabel("Tab 7 Controls")
        #tab_layout_7.addWidget(label)
        tab_widget.addTab(tab_8, f"Graph")
        '''


        '''
        tab_8 = QWidget()
        tab_layout_8 = QHBoxLayout(tab_8)
        # -- tab 8 controls
        label = QLabel("Tab 8 Controls")
        tab_layout_8.addWidget(label)
        tab_widget.addTab(tab_8, f"Background Removal")
        '''
        
        main_layout.addLayout(tab_layout)





        ## -------------------------------------------------------------
 


        ## Load the current model paraneter settings for Titan Image G1 v2 and load as default values in both sides.
        params = self.fetch_parameters('Titan G2')

        ## -------- ImageForge Model Interface ------------------------------------
        u_1h_layout = QHBoxLayout()              # All displays and controls organized left and right.
        u_2v_left_layout = QVBoxLayout()         # Left vertical stack
        u_2v_right_layout = QVBoxLayout()        # right vertical stack
        u_3h_left_layout = QHBoxLayout()         # First row left
        u_3h_left_layout.setSpacing(10)
        u_3h_right_layout = QHBoxLayout()        # First row right
        u_3h_right_layout.setSpacing(10)
        ## -------- ImageForge Model Assembly ------------------------------------
        Sp = 1  # ui vertical spacing within model settings
        Spr = 0 # ui vertical spacing between object rows
        u_1h_layout.addLayout(u_2v_left_layout) 
        # u_2v_left_layout.setSpacing(Spr)
        u_1h_layout.addLayout(u_2v_right_layout) 
        # u_2v_right_layout.setSpacing(Spr)
        u_2v_left_layout.addLayout(u_3h_left_layout)   # This is the left row
        # u_3h_left_layout.setSpacing(Spr)
        u_2v_right_layout.addLayout(u_3h_right_layout) # This is the right row
        # u_3h_right_layout.setSpacing(Spr)

        ###  Tab layouts
        ###
        ## Customize Tab Controls here

        ## TAB 1 -- Image Generation
        ##
        Sp1 = 2
        # tab_layout_1 is the main layout and it is horizontal
        tab_lay_1_v1 = QVBoxLayout() # Left side
        tab_lay_1_v2 = QVBoxLayout() # Middle
        tab_lay_1_v3 = QVBoxLayout() # Right side
        tab_layout_1.addLayout(tab_lay_1_v1)
        tab_layout_1.addLayout(tab_lay_1_v2)
        tab_layout_1.addLayout(tab_lay_1_v3)
        # Build out control layout
        #
        # Create a label for the explanation
        tab1_explanation_label = QLabel("Click [Random] to get a random seed. Titan will produce the same image repeatedly if the seed, prompt, and negative prompt are the same. CFG Scale controls how closely the model adheres to the prompt. [Number] will generate variants which are saved in OUTPUT Storage. inThe current implementation of Stability XL only uses CFG Scale and Seed and produces a fixed size 1024x1024 image. It only uses the prompt and ignores the negative prompt and all other settings.")
        tab1_explanation_label.setWordWrap(True)
        tab1_explanation_label.setFixedWidth(300)  # Set the fixed width here

        # Set the background color of the label
        tab1_palette = tab1_explanation_label.palette()
        tab1_palette.setColor(QPalette.Window, QColor(311, 311, 311))  # Light gray
        tab1_explanation_label.setPalette(tab1_palette)
        tab1_explanation_label.setAutoFillBackground(True)

        # Set the text color of the label
        tab1_explanation_label.setStyleSheet("color: #0000FF;")  # Dark blue

        # Add the label to the layout
        tab_lay_1_v1.addWidget(tab1_explanation_label)

        #
        tab_lay_1_v2.setSpacing(Sp1)
        tab_lay_1_v2.addWidget(QLabel("Prompt"))
        self.tab1_prompt_edit = QTextEdit()
        line_height = self.tab1_prompt_edit.fontMetrics().lineSpacing()
        self.tab1_prompt_edit.setFixedHeight(line_height * 6) 
        tab_lay_1_v2.addWidget(self.tab1_prompt_edit)
        #
        tab_lay_1_v2.addWidget(QLabel("Negative Prompt"))
        self.tab1_neg_prompt_edit = QTextEdit()
        line_height = self.tab1_neg_prompt_edit.fontMetrics().lineSpacing()
        self.tab1_neg_prompt_edit.setFixedHeight(line_height * 3) 
        tab_lay_1_v2.addWidget(self.tab1_neg_prompt_edit)
        #
        # Generate Image using Nova Canvas model
        r_btn_1_1b = QPushButton("Nova Canvas", self)
        r_btn_1_1b.setStyleSheet(self.buttonStyle_1)
        r_btn_1_1b.setFixedSize(130,20)
        r_btn_1_1b.clicked.connect(self.rightNovaCanvas)  
        tab_lay_1_v3.addWidget(r_btn_1_1b)

        # Generate Image using Titan v2 model
        r_btn_1_1 = QPushButton("Titan Image G1 v2", self)
        r_btn_1_1.setStyleSheet(self.buttonStyle_1)
        r_btn_1_1.setFixedSize(130,20)
        r_btn_1_1.clicked.connect(self.rightTitanG2Image)  
        tab_lay_1_v3.addWidget(r_btn_1_1)

        # Generate Image using Titan v1 model
        #
        #  Omitted. v1 produces identical results to v2 with fewer size and variety options.
        #
        #r_btn_1_1 = QPushButton("Generate Image v1", self)
        #r_btn_1_1.setStyleSheet(self.buttonStyle_1)
        #r_btn_1_1.setFixedSize(130,20)
        #r_btn_1_1.clicked.connect(self.rightTitanG2Image)  
        #tab_lay_1_v3.addWidget(r_btn_1_1)

        # Generate Image using Stability XL model
        #
        #  Need to move this to its own tab for additional tailored settings.
        #
        x_btn_1_1 = QPushButton("Stability XL", self)
        x_btn_1_1.setStyleSheet(self.buttonStyle_1)
        x_btn_1_1.setFixedSize(130,20)
        x_btn_1_1.clicked.connect(self.stability_image_gen)  
        tab_lay_1_v3.addWidget(x_btn_1_1)

        x_btn_1_2 = QPushButton("Stability 16x9", self)
        x_btn_1_2.setStyleSheet(self.buttonStyle_1)
        x_btn_1_2.setFixedSize(130,20)
        x_btn_1_2.clicked.connect(self.stability_image_gen_16x9)  
        tab_lay_1_v3.addWidget(x_btn_1_2)
        

        ## TAB 2 -- Image Generation Guided Color
        ##
        Sp1 = 2
        tab_lay_2_v1 = QVBoxLayout() # Left side
        tab_lay_2_v2 = QVBoxLayout() # Middle
        tab_lay_2_v3 = QVBoxLayout() # Right side
        tab_layout_2.addLayout(tab_lay_2_v1)
        tab_layout_2.addLayout(tab_lay_2_v2)
        tab_layout_2.addLayout(tab_lay_2_v3)

        # Build out control layout

        tab_lay_2_v2_h1 = QHBoxLayout()
        tab_lay_2_v2.addLayout(tab_lay_2_v2_h1)
        tab_lay_2_v2_h1.addWidget(QLabel("Hex Colors: "))
        self.ui_tab2_colors = QLineEdit()
        tab_lay_2_v2_h1.addWidget(self.ui_tab2_colors)

        tab2_color_btn = QPushButton("🎨", self)
        tab2_color_btn.setStyleSheet(self.buttonStyle_1)
        tab2_color_btn.clicked.connect(self.tab2ShowColorPopup)  
        tab_lay_2_v2_h1.addWidget(tab2_color_btn)

        tab_lay_2_v2_h1 = QHBoxLayout()
        tab_lay_2_v2.addLayout(tab_lay_2_v2_h1)
        tab_lay_2_v2_h1.setSpacing(Sp1)
        tab_lay_2_v2_h1.addWidget(QLabel("Prompt:    "))
        self.tab2_prompt_edit = QTextEdit()
        line_height = self.tab2_prompt_edit.fontMetrics().lineSpacing()
        self.tab2_prompt_edit.setFixedHeight(line_height * 6) 
        tab_lay_2_v2_h1.addWidget(self.tab2_prompt_edit)
        #
        tab_lay_2_v2_h1 = QHBoxLayout()
        tab_lay_2_v2.addLayout(tab_lay_2_v2_h1)
        tab_lay_2_v2_h1_v1 = QVBoxLayout()
        tab_lay_2_v2_h1.addLayout(tab_lay_2_v2_h1_v1)

        tab_lay_2_v2_h1_v1.addWidget(QLabel("Negative "))
        tab_lay_2_v2_h1_v1.addWidget(QLabel("Prompt:  "))
        self.tab2_neg_prompt_edit = QTextEdit()
        line_height = self.tab2_neg_prompt_edit.fontMetrics().lineSpacing()
        self.tab2_neg_prompt_edit.setFixedHeight(line_height * 3) 
        tab_lay_2_v2_h1.addWidget(self.tab2_neg_prompt_edit)
        #
        # Generate Image using Color Guided Generation with Color Hex Codes
        # Create a label for the explanation
        tab2_explanation_label = QLabel("Color Guided Image Generation requires providing one or more Hex Code colors as dominant colors for the OUTPUT image. The prompt and negative prompt generate the content. [Colors + Ref Image] uses an INPUT image along with the prompts to generate content, while the Hex Code colors determine the output's dominant colors. Its key use is generating images that conforming to specific color palettes or brand colors.")
        tab2_explanation_label.setWordWrap(True)
        tab2_explanation_label.setFixedWidth(300)  # Set the fixed width here

        # Set the background color of the label
        tab2_palette = tab2_explanation_label.palette()
        tab2_palette.setColor(QPalette.Window, QColor(311, 311, 311))  # Light gray
        tab2_explanation_label.setPalette(tab2_palette)
        tab2_explanation_label.setAutoFillBackground(True)

        # Set the text color of the label
        tab2_explanation_label.setStyleSheet("color: #0000FF;")  # Dark blue

        # Add the label to the layout
        tab_lay_2_v1.addWidget(tab2_explanation_label)

        tab_lay_2_v3.setSpacing(3)
        tab_lay_2_v3.addWidget(QLabel(""))
        tab_lay_2_v3.addWidget(QLabel("Hex Code Colors Only"))
        tab2_btn_1_1 = QPushButton("Color Guided Gen", self)
        tab2_btn_1_1.setStyleSheet(self.buttonStyle_1)
        tab2_btn_1_1.setFixedSize(150,20)
        tab2_btn_1_1.clicked.connect(self.ColorG2TitanCOLOR_NOIMAGE)  
        tab_lay_2_v3.addWidget(tab2_btn_1_1)

        # Generate Image using Titan v2 model
        tab_lay_2_v3.addWidget(QLabel(" "))
        tab_lay_2_v3.addWidget(QLabel(""))
        tab_lay_2_v3.addWidget(QLabel("+ Reference Image "))
        tab2_btn_1_1 = QPushButton("Colors + Ref Image", self)
        tab2_btn_1_1.setStyleSheet(self.buttonStyle_1)
        tab2_btn_1_1.setFixedSize(150,20)
        tab2_btn_1_1.clicked.connect(self.ColorG2TitanCOLOR)  
        tab_lay_2_v3.addWidget(tab2_btn_1_1)


        ## TAB 3 -- Image Conditioning
        ##
        Sp3 = 2
        tab_lay_3_v1 = QVBoxLayout() # Left side
        tab_lay_3_v2 = QVBoxLayout() # Middle
        tab_lay_3_v3 = QVBoxLayout() # Right side
        tab_layout_3.addLayout(tab_lay_3_v1)
        tab_layout_3.addLayout(tab_lay_3_v2)
        tab_layout_3.addLayout(tab_lay_3_v3)

        # Build out control layout

        #tab_lay_3_v2_h1 = QHBoxLayout()
        #tab_lay_3_v2.addLayout(tab_lay_2_v2_h1)
        #tab_lay_3_v2_h1.addWidget(QLabel("Hex Colors: "))
        #self.ui_tab2_colors = QLineEdit()
        #tab_lay_3_v2_h1.addWidget(self.ui_tab2_colors)

        #tab2_color_btn = QPushButton("🎨", self)
        #tab2_color_btn.setStyleSheet(self.buttonStyle_1)
        #tab2_color_btn.clicked.connect(self.tab2ShowColorPopup)  
        #tab_lay_2_v2_h1.addWidget(tab2_color_btn)

        tab_lay_3_v2_h1 = QHBoxLayout()
        tab_lay_3_v2.addLayout(tab_lay_3_v2_h1)
        tab_lay_3_v2_h1.setSpacing(Sp3)
        tab_lay_3_v2_h1.addWidget(QLabel("Prompt:    "))
        self.tab3_prompt_edit = QTextEdit()
        line_height = self.tab3_prompt_edit.fontMetrics().lineSpacing()
        self.tab3_prompt_edit.setFixedHeight(line_height * 6) 
        tab_lay_3_v2_h1.addWidget(self.tab3_prompt_edit)
        #
        tab_lay_3_v2_h1 = QHBoxLayout()
        tab_lay_3_v2.addLayout(tab_lay_3_v2_h1)
        tab_lay_3_v2_h1_v1 = QVBoxLayout()
        tab_lay_3_v2_h1.addLayout(tab_lay_3_v2_h1_v1)

        tab_lay_3_v2_h1_v1.addWidget(QLabel("Negative "))
        tab_lay_3_v2_h1_v1.addWidget(QLabel("Prompt:  "))
        self.tab3_neg_prompt_edit = QTextEdit()
        line_height = self.tab3_neg_prompt_edit.fontMetrics().lineSpacing()
        self.tab3_neg_prompt_edit.setFixedHeight(line_height * 3) 
        tab_lay_3_v2_h1.addWidget(self.tab3_neg_prompt_edit)
        #
        # Modify an image using edge detection or object detection
        # Create a label for the explanation
        tab3_explanation_label = QLabel("CANNY conditioning generates images with precise shapes and outlines by applying Canny edge detection to the input image, creating an edge map that guides the generation process - ideal for architectural renderings or product designs. SEGMENTATION conditioning generates images with specific regions or objects by performing semantic segmentation on the input image, creating a mask that defines the regions to be modified, replaced, or preserved - useful for controlled image editing tasks.")
        tab3_explanation_label.setWordWrap(True)
        tab3_explanation_label.setFixedWidth(300)  # Set the fixed width here

        # Set the background color of the label
        tab3_palette = tab3_explanation_label.palette()
        tab3_palette.setColor(QPalette.Window, QColor(311, 311, 311))  # Light gray
        tab3_explanation_label.setPalette(tab3_palette)
        tab3_explanation_label.setAutoFillBackground(True)

        # Set the text color of the label
        tab3_explanation_label.setStyleSheet("color: #0000FF;")  # Dark blue

        # Add the label to the layout
        tab_lay_3_v1.addWidget(tab3_explanation_label)

        tab_lay_3_v3.setSpacing(3)
        tab_lay_3_v3.addWidget(QLabel(""))
        tab_lay_3_v3.addWidget(QLabel("Edge Detection"))
        tab3_btn_1_1 = QPushButton("CANNY", self)
        tab3_btn_1_1.setStyleSheet(self.buttonStyle_1)
        tab3_btn_1_1.setFixedSize(150,20)
        tab3_btn_1_1.clicked.connect(self.ConditionG2TitanCANNY)  ##<< CANNY
        tab_lay_3_v3.addWidget(tab3_btn_1_1)

        # Generate Image using Titan v2 model
        tab_lay_3_v3.addWidget(QLabel(" "))
        tab_lay_3_v3.addWidget(QLabel(""))
        tab_lay_3_v3.addWidget(QLabel("Object Detection"))
        tab3_btn_1_1 = QPushButton("SEGMENTATION", self)
        tab3_btn_1_1.setStyleSheet(self.buttonStyle_1)
        tab3_btn_1_1.setFixedSize(150,20)
        tab3_btn_1_1.clicked.connect(self.ConditionG2TitanSEGMENTATION)   ##<< SEGMENTATION
        tab_lay_3_v3.addWidget(tab3_btn_1_1)


        ## TAB 4 -- Image Variation
        ##
        Sp4 = 2
        tab_lay_4_v1 = QVBoxLayout() # Left side
        tab_lay_4_v2 = QVBoxLayout() # Middle
        tab_lay_4_v3 = QVBoxLayout() # Right side
        tab_layout_4.addLayout(tab_lay_4_v1)
        tab_layout_4.addLayout(tab_lay_4_v2)
        tab_layout_4.addLayout(tab_lay_4_v3)

        # Build out control layout

        tab_lay_4_v2_h1 = QHBoxLayout()
        tab_lay_4_v2.addLayout(tab_lay_4_v2_h1)
        tab_lay_4_v2_h1.addWidget(QLabel("Similarity Strength: "))
        tab4_similarity = 0.7 # Default value
        self.ui_tab4_similarity = QDoubleSpinBox(self)
        self.ui_tab4_similarity.setMaximumWidth(65)
        self.ui_tab4_similarity.setRange(0.2, 1.0)  # Set range from 0.2 to 1.0
        self.ui_tab4_similarity.setValue(tab4_similarity)  # Set default value to model setting (8.0 is default) 
        self.ui_tab4_similarity.setSingleStep(0.1)   # Set increment step to 0.1
        tab_lay_4_v2_h1.addWidget(self.ui_tab4_similarity)
        tab_lay_4_v2_h1.addStretch()

        tab_lay_4_v2_h1 = QHBoxLayout()
        tab_lay_4_v2.addLayout(tab_lay_4_v2_h1)
        tab_lay_4_v2_h1.setSpacing(Sp4)
        tab_lay_4_v2_h1.addWidget(QLabel("Prompt:    "))
        self.tab4_prompt_edit = QTextEdit()
        line_height = self.tab4_prompt_edit.fontMetrics().lineSpacing()
        self.tab4_prompt_edit.setFixedHeight(line_height * 6) 
        tab_lay_4_v2_h1.addWidget(self.tab4_prompt_edit)
        #
        tab_lay_4_v2_h1 = QHBoxLayout()
        tab_lay_4_v2.addLayout(tab_lay_4_v2_h1)
        tab_lay_4_v2_h1_v1 = QVBoxLayout()
        tab_lay_4_v2_h1.addLayout(tab_lay_4_v2_h1_v1)

        tab_lay_4_v2_h1_v1.addWidget(QLabel("Negative "))
        tab_lay_4_v2_h1_v1.addWidget(QLabel("Prompt:  "))
        self.tab4_neg_prompt_edit = QTextEdit()
        line_height = self.tab4_neg_prompt_edit.fontMetrics().lineSpacing()
        self.tab4_neg_prompt_edit.setFixedHeight(line_height * 3) 
        tab_lay_4_v2_h1.addWidget(self.tab4_neg_prompt_edit)
        #
        # Create a variation of an input image
        # Create a label for the explanation
        tab4_explanation_label = QLabel("Image Variation generates an alternate version of an INPUT image. It uses AI to understand the semantic content and intricate relationships within the image producing high-quality, photorealistic changes  while preserving the essential characteristics of the INPUT image. It is used to change backgrounds, modifying colors, add or remove elements, and adjusting lighting conditions. Ignores SEED setting. ")
        tab4_explanation_label.setWordWrap(True)
        tab4_explanation_label.setFixedWidth(300)  # Set the fixed width here

        # Set the background color of the label
        tab4_palette = tab4_explanation_label.palette()
        tab4_palette.setColor(QPalette.Window, QColor(311, 311, 311))  # Light gray
        tab4_explanation_label.setPalette(tab4_palette)
        tab4_explanation_label.setAutoFillBackground(True)

        # Set the text color of the label
        tab4_explanation_label.setStyleSheet("color: #0000FF;")  # Dark blue

        # Add the label to the layout
        tab_lay_4_v1.addWidget(tab4_explanation_label)

        tab_lay_4_v3.setSpacing(3)
        tab_lay_4_v3.addWidget(QLabel(""))
        tab_lay_4_v3.addWidget(QLabel(""))
        tab4_btn_1_1 = QPushButton("Image Variation", self)
        tab4_btn_1_1.setStyleSheet(self.buttonStyle_1)
        tab4_btn_1_1.setFixedSize(150,20)
        tab4_btn_1_1.clicked.connect(self.TitanG2ImageVariation)  
        tab_lay_4_v3.addWidget(tab4_btn_1_1)
    
        tab4_btn_1_2 = QPushButton("Remove Background", self)
        tab4_btn_1_2.setStyleSheet(self.buttonStyle_1)
        tab4_btn_1_2.setFixedSize(150,20)
        tab4_btn_1_2.clicked.connect(self.RemoveBackG2Titan)  
        tab_lay_4_v3.addWidget(tab4_btn_1_2)

        tab_lay_4_v3.addStretch()


        ## TAB 5 -- Photo Editing
        ##
        Sp1 = 2
        tab_lay_5_v1 = QVBoxLayout() # Left side
        tab_lay_5_v2 = QHBoxLayout() # Middle
        tab_lay_5_v2_h1 = QVBoxLayout() # Brightness
        tab_lay_5_v2_h2 = QVBoxLayout() # Contrast  
        tab_lay_5_v2_h3 = QVBoxLayout() # Saturation
        tab_lay_5_v2_h4 = QVBoxLayout() # Red  
        tab_lay_5_v2_h5 = QVBoxLayout() # Green  
        tab_lay_5_v2_h6 = QVBoxLayout() # Blue
        tab_lay_5_v2_h7 = QVBoxLayout() # Alpha 
        tab_lay_5_v2_h8 = QVBoxLayout() # Sharpness 
        tab_lay_5_v2_h9 = QVBoxLayout() # Gaussian Blur 
        tab_lay_5_v2_h10 = QVBoxLayout() # Reset button   
        tab_lay_5_v3 = QVBoxLayout() # Right side
        tab_layout_5.addLayout(tab_lay_5_v1)
        tab_layout_5.addLayout(tab_lay_5_v2)
        tab_layout_5.addLayout(tab_lay_5_v3)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h1)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h2)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h3)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h4)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h5)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h6)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h7)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h8)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h9)
        tab_lay_5_v2.addLayout(tab_lay_5_v2_h10)
    
        # Build out control layout

        # -xContrast adjustment
        #- xBrightness adjustment
        #- xExposure adjustment
        #- xSharpening
        #- xGaussian blur
        #- xGrayscale conversion
        #- xColor adjustments (hue, saturation, etc.)

        #- Resizing and rescaling
        #- Cropping
        #- Rotation
        #- Flipping (horizontally or vertically)
        #- Drawing shapes, text, and annotations on images
        #- Applying filters (e.g., edge detection, embossing, etc.)
        #- Image enhancement techniques (e.g., histogram equalization, denoising, etc.)
        #- Combining multiple images (e.g., overlaying, blending, etc.)
        #- N/A Converting between different image file formats

        #tab_lay_5_v2_h1.addWidget(QLabel("Brightness: "))
        #self.ui_tab5_colors = QLineEdit()
        #tab_lay_5_v2_h1.addWidget(self.ui_tab5_colors)

        #tab5_color_btn = QPushButton("🎨", self)
        #tab5_color_btn.setStyleSheet(self.buttonStyle_1)
        #tab5_color_btn.clicked.connect(self.tab2ShowColorPopup)  
        #tab_lay_5_v2_h1.addWidget(tab5_color_btn)

        tab_lay_5_v2_h1.addWidget(QLabel("Brightness: "))
        photo_brightness = 1.0
        self.photo_bright = QDoubleSpinBox(self)
        self.photo_bright.setMaximumWidth(65)
        self.photo_bright.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_bright.setValue(photo_brightness)  # Set default value to model setting (8.0 is default) 
        self.photo_bright.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h1.addWidget(self.photo_bright)

        self.photo_bright_slider = QSlider()
        self.photo_bright_slider.setRange(1, 30)
        self.photo_bright_slider.setValue(int(self.photo_bright.value()*10 ))
        self.photo_bright_slider.valueChanged.connect(self.sync_bright_slider_to_spinner)
        self.photo_bright.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h1.addWidget(self.photo_bright_slider)
        #photo_bright_label = QLabel("B")
        #tab_lay_5_v2_h1.addWidget(photo_bright_label)

        tab_lay_5_v2_h2.addWidget(QLabel("Contrast: "))
        photo_cont = 1.0
        self.photo_contrast = QDoubleSpinBox(self)
        self.photo_contrast.setMaximumWidth(65)
        self.photo_contrast.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_contrast.setValue(photo_cont)  # Set default value to model setting (8.0 is default) 
        self.photo_contrast.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h2.addWidget(self.photo_contrast)

        self.photo_contrast_slider = QSlider()
        self.photo_contrast_slider.setRange(1, 30)
        self.photo_contrast_slider.setValue(int(self.photo_contrast.value()*10 ))
        self.photo_contrast_slider.valueChanged.connect(self.sync_contrast_slider_to_spinner)
        self.photo_contrast.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h2.addWidget(self.photo_contrast_slider)
        #photo_contrast_label = QLabel("C")
        #tab_lay_5_v2_h2.addWidget(photo_contrast_label)

        tab_lay_5_v2_h3.addWidget(QLabel("Saturation: "))
        photo_sat = 1.0
        self.photo_saturation = QDoubleSpinBox(self)
        self.photo_saturation.setMaximumWidth(65)
        self.photo_saturation.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_saturation.setValue(photo_sat)  # Set default value to model setting (8.0 is default) 
        self.photo_saturation.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h3.addWidget(self.photo_saturation)

        self.photo_saturation_slider = QSlider()
        self.photo_saturation_slider.setRange(1, 30)
        self.photo_saturation_slider.setValue(int(self.photo_bright.value()*10 ))
        self.photo_saturation_slider.valueChanged.connect(self.sync_saturation_slider_to_spinner)
        self.photo_saturation.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h3.addWidget(self.photo_saturation_slider)
        #photo_saturation_label = QLabel("S")
        #tab_lay_5_v2_h3.addWidget(photo_saturation_label)

        #--- RGBA

        # Red=4, Green=5, Blue=6, Apha=7
        tab_lay_5_v2_h4.addWidget(QLabel("[R] Red: "))
        photo_red = 1.0
        self.photo_red = QDoubleSpinBox(self)
        self.photo_red.setMaximumWidth(65)
        self.photo_red.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_red.setValue(photo_red)  # Set default value t
        self.photo_red.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h4.addWidget(self.photo_red)

        self.photo_red_slider = QSlider()
        self.photo_red_slider.setRange(1, 30)
        self.photo_red_slider.setValue(int(self.photo_red.value()*10 ))
        self.photo_red_slider.valueChanged.connect(self.sync_red_slider_to_spinner)
        self.photo_red.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h4.addWidget(self.photo_red_slider)

        tab_lay_5_v2_h5.addWidget(QLabel("[G] Green: "))
        photo_green = 1.0
        self.photo_green = QDoubleSpinBox(self)
        self.photo_green.setMaximumWidth(65)
        self.photo_green.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_green.setValue(photo_green)  # Set default value t
        self.photo_green.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h5.addWidget(self.photo_green)

        self.photo_green_slider = QSlider()
        self.photo_green_slider.setRange(1, 30)
        self.photo_green_slider.setValue(int(self.photo_green.value()*10 ))
        self.photo_green_slider.valueChanged.connect(self.sync_green_slider_to_spinner)
        self.photo_green.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h5.addWidget(self.photo_green_slider)

        tab_lay_5_v2_h6.addWidget(QLabel("[B] Blue: "))
        photo_blue = 1.0
        self.photo_blue = QDoubleSpinBox(self)
        self.photo_blue.setMaximumWidth(65)
        self.photo_blue.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_blue.setValue(photo_blue)  # Set default value t
        self.photo_blue.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h6.addWidget(self.photo_blue)

        self.photo_blue_slider = QSlider()
        self.photo_blue_slider.setRange(1, 30)
        self.photo_blue_slider.setValue(int(self.photo_blue.value()*10 ))
        self.photo_blue_slider.valueChanged.connect(self.sync_blue_slider_to_spinner)
        self.photo_blue.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h6.addWidget(self.photo_blue_slider)

        tab_lay_5_v2_h7.addWidget(QLabel("[A] Alpha: "))
        photo_alpha = 1.0
        self.photo_alpha = QDoubleSpinBox(self)
        self.photo_alpha.setMaximumWidth(65)
        self.photo_alpha.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_alpha.setValue(photo_alpha)  # Set default value t
        self.photo_alpha.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h7.addWidget(self.photo_alpha)

        self.photo_alpha_slider = QSlider()
        self.photo_alpha_slider.setRange(1, 30)
        self.photo_alpha_slider.setValue(int(self.photo_alpha.value()*10 ))
        self.photo_alpha_slider.valueChanged.connect(self.sync_alpha_slider_to_spinner)
        self.photo_alpha.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h7.addWidget(self.photo_alpha_slider)

        #--- RGBA

        tab_lay_5_v2_h8.addWidget(QLabel("Sharpness: "))
        photo_det = 1.0
        self.photo_detail = QDoubleSpinBox(self)
        self.photo_detail.setMaximumWidth(65)
        self.photo_detail.setRange(0.1, 3.0)  # Set range from 1.1 to 10.0
        self.photo_detail.setValue(photo_det)  # Set default value to model setting (8.0 is default) 
        self.photo_detail.setSingleStep(0.01)   # Set increment step to 0.1
        tab_lay_5_v2_h8.addWidget(self.photo_detail)


        self.photo_detail_slider = QSlider()
        self.photo_detail_slider.setRange(1, 30)
        self.photo_detail_slider.setValue(int(self.photo_detail.value()*10 ))
        self.photo_detail_slider.valueChanged.connect(self.sync_detail_slider_to_spinner)
        self.photo_detail.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h8.addWidget(self.photo_detail_slider)
        #photo_detail_label = QLabel("D")
        #tab_lay_5_v2_h4.addWidget(photo_detail_label)

        tab_lay_5_v2_h9.addWidget(QLabel("Blur: "))
        photo_blur_gauss = 0.0
        self.photo_blur = QDoubleSpinBox(self)
        self.photo_blur.setMaximumWidth(65)
        self.photo_blur.setRange(0.0, 10.0)  # Set range from 0.0 to 10.0
        self.photo_blur.setValue(photo_blur_gauss)  # Set default value to model setting (8.0 is default) 
        self.photo_blur.setSingleStep(0.1)   # Set increment step to 0.1
        tab_lay_5_v2_h9.addWidget(self.photo_blur)


        self.photo_blur_slider = QSlider()
        self.photo_blur_slider.setRange(0, 100)
        self.photo_blur_slider.setValue(int(self.photo_detail.value()*10 ))
        self.photo_blur_slider.valueChanged.connect(self.sync_blur_slider_to_spinner)
        self.photo_blur.valueChanged.connect(self.update_image)
        tab_lay_5_v2_h9.addWidget(self.photo_blur_slider)

        ## Live update
        self.photo_bright.valueChanged.connect(self.update_image)
        self.photo_contrast.valueChanged.connect(self.update_image)
        self.photo_saturation.valueChanged.connect(self.update_image)
        self.photo_red.valueChanged.connect(self.update_image)
        self.photo_green.valueChanged.connect(self.update_image)
        self.photo_blue.valueChanged.connect(self.update_image)
        self.photo_alpha.valueChanged.connect(self.update_image)
        self.photo_detail.valueChanged.connect(self.update_image)
        self.photo_blur.valueChanged.connect(self.update_image)
        ## Live update

        tab5_adjust_btn = QPushButton("Reset", self)
        tab5_adjust_btn.setFixedWidth(100)
        tab5_adjust_btn.setStyleSheet(self.buttonStyle_1)
        tab5_adjust_btn.clicked.connect(self.tab5Photo_Reset)  
        tab_lay_5_v2_h10.addWidget(tab5_adjust_btn)


        ## TAB 7 -- Describe image
        ##
        Sp4 = 2
        tab_lay_7_v1 = QVBoxLayout() # Left side
        tab_lay_7_v2 = QVBoxLayout() # Middle
        tab_lay_7_v3 = QVBoxLayout() # Right side
        tab_lay_7_v3_h1 = QHBoxLayout() # chat buttons 1
        tab_lay_7_v3_h2 = QHBoxLayout() # chat buttons 2
        tab_layout_7.addLayout(tab_lay_7_v1)
        tab_layout_7.addLayout(tab_lay_7_v2)
        tab_layout_7.addLayout(tab_lay_7_v3)

        self.text_description = QTextEdit()
        tab_lay_7_v2.addWidget(self.text_description)

        tab7_explanation_label = QLabel("DESCRIBE uses MultiModal Sonnet 3 to provide a text description of the image in the right viewer. You can add additional instructions or information in the text editor. Text chat is provided for Sonnet 3 and Titan Premiere so you can discuss your project without leaving ImaGen.")
        tab7_explanation_label.setWordWrap(True)
        tab7_explanation_label.setFixedWidth(300)  # Set the fixed width here

        # Set the background color of the label
        tab7_palette = tab4_explanation_label.palette()
        tab7_palette.setColor(QPalette.Window, QColor(311, 311, 311))  # Light gray
        tab7_explanation_label.setPalette(tab4_palette)
        tab7_explanation_label.setAutoFillBackground(True)

        # Set the text color of the label
        tab7_explanation_label.setStyleSheet("color: #0000FF;")  # Dark blue

        # Add the label to the layout
        tab_lay_7_v1.addWidget(tab7_explanation_label)


        tab7_btn_3_1 = QPushButton("Describe Right Image", self)
        tab7_btn_3_1.setStyleSheet(self.buttonStyle_1)
        tab7_btn_3_1.setFixedSize(150,20)
        self.describe_mode = 0
        tab7_btn_3_1.clicked.connect(lambda: self.describe_image(self.clients,self.describe_mode,self.text_description))  
        tab_lay_7_v3.addWidget(tab7_btn_3_1)

        tab7_btn_3_2 = QPushButton("Training Description", self)
        tab7_btn_3_2.setStyleSheet(self.buttonStyle_1)
        tab7_btn_3_2.setFixedSize(150,20)
        self.describe_mode = 1
        tab7_btn_3_2.clicked.connect(lambda: self.describe_image(self.clients,self.describe_mode,self.text_description))  
        tab_lay_7_v3.addWidget(tab7_btn_3_2)

        tab7_btn_3_3 = QPushButton("Chat with Sonnet 3", self)
        tab7_btn_3_3.setStyleSheet(self.buttonStyle_1)
        tab7_btn_3_3.setFixedSize(130,20)
        tab7_btn_3_3.clicked.connect(lambda: self.ai_advice1(self.clients,self.history1) )
        tab_lay_7_v3_h1.addWidget(tab7_btn_3_3)
        tab7_btn_3_4 = QPushButton("X", self)
        tab7_btn_3_4.setStyleSheet(self.buttonStyle_1)
        tab7_btn_3_4.setFixedSize(20,20)
        tab7_btn_3_4.clicked.connect(self.ai_advice1_clear )
        tab_lay_7_v3_h1.addWidget(tab7_btn_3_4)
        tab_lay_7_v3.addLayout(tab_lay_7_v3_h1)

        tab7_btn_3_4 = QPushButton("Chat with Titan P", self)
        tab7_btn_3_4.setStyleSheet(self.buttonStyle_1)
        tab7_btn_3_4.setFixedSize(130,20)
        tab7_btn_3_4.clicked.connect(lambda: self.ai_advice2(self.clients,self.history1) )
        tab_lay_7_v3_h2.addWidget(tab7_btn_3_4)
        tab7_btn_3_5 = QPushButton("X", self)
        tab7_btn_3_5.setStyleSheet(self.buttonStyle_1)
        tab7_btn_3_5.setFixedSize(20,20)
        tab7_btn_3_5.clicked.connect(self.ai_advice2_clear )
        tab_lay_7_v3_h2.addWidget(tab7_btn_3_5)
        tab_lay_7_v3.addLayout(tab_lay_7_v3_h2)




        ## TAB 6 -- Crop
        ##
        Sp4 = 2
        self.tab_lay_6_v1 = QVBoxLayout() # Left side
        self.tab_lay_6_v2 = QVBoxLayout() # Middle
        self.tab_lay_6_v3 = QVBoxLayout() # Right side
        #tab_lay_6_v3_h1 = QHBoxLayout() # chat buttons 1
        #tab_lay_6_v3_h2 = QHBoxLayout() # chat buttons 2
        tab_layout_6.addLayout(self.tab_lay_6_v1)
        tab_layout_6.addLayout(self.tab_lay_6_v2)
        tab_layout_6.addLayout(self.tab_lay_6_v3)


        tab6_btn_3_1 = QPushButton("Set Crop Corners", self)
        tab6_btn_3_1.setStyleSheet(self.buttonStyle_1)
        tab6_btn_3_1.setFixedSize(150,20)
        tab6_btn_3_1.clicked.connect(self.start_crop)  
        self.tab_lay_6_v3.addWidget(tab6_btn_3_1)

        tab6_btn_3_2 = QPushButton("Crop Image", self)
        tab6_btn_3_2.setStyleSheet(self.buttonStyle_1)
        tab6_btn_3_2.setFixedSize(150,20)
        tab6_btn_3_2.clicked.connect(self.crop_image)  
        self.tab_lay_6_v3.addWidget(tab6_btn_3_2)

        # Sliders for cropping (created but not yet connected)
        self.left_slider = None
        self.top_slider = None
        self.right_slider = None
        self.bottom_slider = None

        # Placeholder for the bounding rectangle
        self.bounding_rect = None

        # Placeholder for the image pixmap
        self.current_pixmap = None


        ## TAB 8 -- Graph
        ##
        '''
        Sp4 = 2
        self.tab_lay_8_v1 = QVBoxLayout() # Left side
        self.tab_lay_8_v2 = QVBoxLayout() # Middle
        self.tab_lay_8_v3 = QVBoxLayout() # Right side
        #tab_lay_6_v3_h1 = QHBoxLayout() # chat buttons 1
        #tab_lay_6_v3_h2 = QHBoxLayout() # chat buttons 2
        tab_layout_8.addLayout(self.tab_lay_8_v1)
        tab_layout_8.addLayout(self.tab_lay_8_v2)
        tab_layout_8.addLayout(self.tab_lay_8_v3)

        tab8_btn_3_1 = QPushButton("Render Graph", self)
        tab8_btn_3_1.setStyleSheet(self.buttonStyle_1)
        tab8_btn_3_1.setFixedSize(150,20)
        tab8_btn_3_1.clicked.connect(self.render_graph)  
        self.tab_lay_8_v3.addWidget(tab8_btn_3_1)

        tab8_btn_3_2 = QPushButton("Insert Icon", self)
        tab8_btn_3_2.setStyleSheet(self.buttonStyle_1)
        tab8_btn_3_2.setFixedSize(150,20)
        tab8_btn_3_2.clicked.connect(self.insert_icon)  
        self.tab_lay_8_v3.addWidget(tab8_btn_3_2)

        tab8_btn_3_4 = QPushButton("Clear DOT Code", self)
        tab8_btn_3_4.setStyleSheet(self.buttonStyle_1)
        tab8_btn_3_4.setFixedSize(150,20)
        tab8_btn_3_4.clicked.connect(lambda: self.text_graph.clear())  
        self.tab_lay_8_v3.addWidget(tab8_btn_3_4)

        tab8_btn_3_5 = QPushButton("DOT Documentation", self)
        tab8_btn_3_5.setStyleSheet(self.buttonStyle_1)
        tab8_btn_3_5.setFixedSize(150,20)
        tab8_btn_3_5.clicked.connect(self.open_webpage_dotlang)  
        self.tab_lay_8_v3.addWidget(tab8_btn_3_5)


        self.text_graph = QTextEdit()
        self.text_graph.setPlainText("digraph G {\n\n}")
        self.tab_lay_8_v2.addWidget(self.text_graph)
        '''

        # Show the window
        self.show()


    ### -------------------------[ Crop Controls ]--------------------


    def crop_image(self):
        if not self.current_pixmap:
            return

        # Get the current values of the sliders
        left = self.left_slider.value()
        top = self.top_slider.value()
        right = self.right_slider.value()
        bottom = self.bottom_slider.value()

        # Ensure the crop coordinates are within the image bounds
        if left >= right or top >= bottom:
            print("Invalid crop coordinates!")
            return

        # Calculate the crop rectangle
        crop_rect = QRect(left, top, right - left, bottom - top)

        # Crop the image
        cropped_pixmap = self.current_pixmap.copy(crop_rect)

        # Clear the scene and reload the cropped image
        self.right_scene.clear()
        self.right_scene.addPixmap(cropped_pixmap)
        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

        # Update the current_pixmap to the cropped image
        self.current_pixmap = cropped_pixmap

        # Hide or delete the sliders and bounding rectangle
        self.cleanup_after_crop()

    def cleanup_after_crop(self):

        # Safely remove the bounding rectangle from the scene if it exists
        try:
            if self.bounding_rect and self.bounding_rect.scene() is not None:
                self.right_scene.removeItem(self.bounding_rect)
            self.bounding_rect = None
        except RuntimeError:
            self.bounding_rect = None
        # Disable the sliders
        if self.left_slider: 
            self.left_slider.setEnabled(False)
        if self.top_slider:
            self.top_slider.setEnabled(False)
        if self.right_slider:
            self.right_slider.setEnabled(False)
        if self.bottom_slider:
            self.bottom_slider.setEnabled(False)

        # Delete the sliders
        if self.left_slider: 
            self.left_slider.deleteLater()
            self.left_slider = None
        if self.top_slider:
            self.top_slider.deleteLater()
            self.top_slider = None
        if self.right_slider:
            self.right_slider.deleteLater()
            self.right_slider = None
        if self.bottom_slider:
            self.bottom_slider.deleteLater()
            self.bottom_slider = None


    def start_crop(self):
        # Check if the sliders already exist
        if self.left_slider or self.top_slider or self.right_slider or self.bottom_slider:
            return  # Sliders already exist, do nothing
    
        # Ensure the pixmap is set from the currently displayed image in the scene
        for item in self.right_scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                self.current_pixmap = item.pixmap()
                break

        if not self.current_pixmap:
            return  # Exit if no image is found in the scene

        # Get the bounding rectangle from the scene
        scene_rect = self.right_scene.itemsBoundingRect()

        # Set initial bounding rectangle to match the size of the scene
        self.bounding_rect = QGraphicsRectItem(scene_rect)
        self.bounding_rect.setPen(QPen(Qt.red, 2))
        self.right_scene.addItem(self.bounding_rect)

        # Create and configure sliders for cropping
        self.left_slider = self.create_slider(self.tab_lay_6_v2, 0, scene_rect.width(), scene_rect.left())
        self.top_slider = self.create_slider(self.tab_lay_6_v2, 0, scene_rect.height(), scene_rect.top())
        self.right_slider = self.create_slider(self.tab_lay_6_v2, 0, scene_rect.width(), scene_rect.right())
        self.bottom_slider = self.create_slider(self.tab_lay_6_v2, 0, scene_rect.height(), scene_rect.bottom())

        # Connect slider changes to update the bounding rectangle
        self.left_slider.valueChanged.connect(self.update_bounding_rect)
        self.top_slider.valueChanged.connect(self.update_bounding_rect)
        self.right_slider.valueChanged.connect(self.update_bounding_rect)
        self.bottom_slider.valueChanged.connect(self.update_bounding_rect)

    def create_slider(self, layout, min_val, max_val, default_val=0):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(int(min_val), int(max_val))
        slider.setSingleStep(1)
        slider.setValue(int(default_val))

        layout.addWidget(slider)

        return slider

    def update_bounding_rect(self):
        left = self.left_slider.value()
        top = self.top_slider.value()
        right = self.right_slider.value()
        bottom = self.bottom_slider.value()
        self.bounding_rect.setRect(left, top, right - left, bottom - top)



## ---------------------[ Render Methods ]------------------------------------ ##########$$$$####
    '''
    def render_graph(self):
        # Get the text from the QTextEdit widget
        graph_code = self.text_graph.toPlainText().strip()
        
        # Debugging print statements to check the graph code
        #print("Graph code received:")
        #print(graph_code)
        
        if not graph_code:
            QMessageBox.warning(None, "Error", f"No DOT code graph instructions.")
            return
        
        try:
            # Determine the application's startup directory
            startup_directory = os.getcwd()  # Gets the current working directory
            #print("Startup_Directory:", startup_directory)
            #print("Startup_Directory SYS:", self.startup_location)
            
            # Preprocess the graph_code to resolve image paths
            graph_code = self.preprocess(graph_code, self.startup_location)

            # Define the WABAC folder path
            wabac_directory = os.path.join(startup_directory, 'WABAC')

            # Create the WABAC folder if it doesn't exist
            if not os.path.exists(wabac_directory):
                os.makedirs(wabac_directory)

            # Base file path without extension
            base_file_path = os.path.join(wabac_directory, 'graph')
            
            # Use the graphviz Source class to render the DOT code
            src = Source(graph_code)
            
            # Render the graph to SVG and PNG files
            svg_file_path = src.render(base_file_path, format='svg')
            png_file_path = src.render(base_file_path, format='png')
            
            # Load the rendered PNG image into the right QGraphicsView
            image = QImage(png_file_path)
            #if image.isNull():
            #    print("Failed to load image")
            #else:
            #    print(f"Image loaded: {image.size()}")
            
            pixmap = QPixmap.fromImage(image)
            self.right_scene.clear()  # Clear the scene before adding the new image
            self.right_scene.addPixmap(pixmap)
            self.right_scene.update()

            #print(f"Graph rendered and displayed from {png_file_path}")
            #print(f"SVG saved at: {svg_file_path}")
            #print(f"PNG saved at: {png_file_path}")
        
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error rendering graph: {e}")
            # print(f"Error rendering graph: {e}")

    def preprocess(self, graph_code, startup_location):
        # Regular expression to find image references with .png or .svg extensions
        image_pattern = re.compile(r'image="([^"]+\.(?:png|svg))"')

        # Function to replace the image path with the fully qualified path
        def replace_image_path(match):
            image_path = match.group(1)
            # Determine if the path is relative or absolute
            if os.path.isabs(image_path):
                # If it's already an absolute path, return it unchanged
                return match.group(0)
            else:
                # If it's a relative path (even if it starts with '/'), prepend startup_location and icons
                full_image_path = os.path.join(startup_location, 'icons', image_path.lstrip('/'))
                # Normalize the path to handle both Windows and OSX
                full_image_path = os.path.normpath(full_image_path)
                return f'image="{full_image_path}"'

        # Substitute all image references in the DOT string
        graph_code = image_pattern.sub(replace_image_path, graph_code)
        return graph_code

    def open_webpage_dotlang(self):
        url = "https://graphviz.org/doc/info/lang.html"  # External GraphViz DOT Language Reference
        webbrowser.open(url)
    
    def insert_icon(self):
        # Step 1: Open a file dialog to allow the user to browse the /icons directory
        startup_location = self.startup_location  # Assuming this is defined elsewhere in MyClass
        icon_directory = os.path.join(startup_location, 'icons')
        if not os.path.exists(icon_directory):
            QMessageBox.warning(None, "Error", f"Icons directory not found: {icon_directory}")
            return
        
        # Open file dialog and filter to PNG and SVG files
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select Icon", icon_directory, "Images (*.png *.svg)"
        )
        
        if not file_path:
            return  # User canceled the operation
        
        # Step 2: Display the selected image
        image_reader = QImageReader(file_path)
        if not image_reader.canRead():
            QMessageBox.warning(None, "Error", f"Cannot load image: {file_path}")
            return

        # Step 3: Compute the relative path just below the icons directory
        relative_path = os.path.relpath(file_path, icon_directory)
        normalized_path = os.path.normpath(relative_path)

        # Insert only the file name (relative path below icons directory) into the text editor
        dot_syntax = f'New [image="{normalized_path}"];'
        
        cursor = self.text_graph.textCursor()
        cursor.insertText(dot_syntax)
        '''


    '''
    https://graphviz.org/doc/info/lang.html
EXAMPLE 1

digraph G {
    A -> B;
    A -> C;
    B -> D;
    C -> D;
    D -> A;
    D -> A;
}

digraph G {
    node [shape=none];
    A [image="path/to/your/image.svg"];
    B [image="path/to/another/image.svg"];
    C [label="Regular Node"];
    A -> B;
    B -> C;
}
    '''


## ---------------------[ Describe Methods ]------------------------------------ #

    def describe_image(self, clients, describe_mode, text_description):
        self.clients = clients
        self.mode = describe_mode
        self.text_description = text_description
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 3S')
        if self.mode == 0:
            input_text = "Describe the accompanying image."
            input_text = input_text + "\nADDITIONAL INSTRUCTIONS: \n" + self.text_description.toPlainText()
        if self.mode ==1:
            #input_text = "Describe the image and begin your response with the words COPYRIGHT 2024 "
            input_text = """Your job is to write content to describe a slide from a class to individuals with accessibility needs. I will provide you with an image of the slide and ADDITIONAL_INFORMATION.

Follow these INSTRUCTIONS:
1. Analyze the image. If the image is a title slide or a section title slide, say so. And keep the description brief, factual, and direct.
2. If the image contains only text information such as bullet points and the visual elements are not substantial, focus on communicating the key concepts.
3. If the image contains essential visual information, describe the image using the following VISUAL_GUIDELINES. Then summarize the key concepts and essential information in a clear and complete paragraph.
4. Omit any introductory paragraph identifying the team and its purpose. Omit any final paragraph of goodwill that has no technical communication value.

VISUAL_GUIDELINES:
Combine these 7 methods to write a paragraph that describes the image in a clear, understandable, direct, and factual way. Do not identify the methods used. Do not list copyright information in your description. Ensure that the final paragraph is complete and easily understood.

1. Hierarchical Structure Description: Decompose the image into major sections and describe the hierarchy and relationships between them. Clearly indicate different levels of information.
2. Sequential Description: Describe the elements in the order they would be encountered or read, providing a logical flow that simulates visually scanning the slide.
3. Positional Context: Indicate the relative positions of elements using terms like "above," "below," "to the left of," and "to the right of." To help build a mental map of the layout.
4. Data Summaries and Insights: Provide a summary of the key data points for charts or graphs. Include trends, insights, and main takeaways conveyed.
5. Detailed Descriptions of Visual Elements: Describe each visual element in detail such as content, colors, shapes, and significant features.
6. Use of Lists: Organize information into bullet points or numbered lists where appropriate to enhance clarity and readability.
7. Explicitly Describe Actions or Processes: If the slide includes steps in a process, describe each step in detail, including any conditions or outcomes."""

        input_text = input_text + "\nADDITIONAL_INFORMATION: \n" + self.text_description.toPlainText()

        while input_text.startswith("\n"):
            input_text = input_text[1:]

        # Prepare base64 version of the image contained in the right QGraphicsView


        # Assuming `self.right_view` is a QGraphicsView and has a scene with the image
        if self.right_view and self.right_view.scene():
            # Extract the QImage from the QGraphicsScene
            scene = self.right_view.scene()
            if scene.items():
                # Get the first item assuming it's the image
                pixmap_item = scene.items()[0]
                if isinstance(pixmap_item, QGraphicsPixmapItem):
                    qimage = pixmap_item.pixmap().toImage()

                    # Convert QImage to QByteArray
                    byte_array = QByteArray()
                    buffer = QBuffer(byte_array)
                    buffer.open(QIODevice.WriteOnly)
                    qimage.save(buffer, "JPEG")  # Save as JPEG in the buffer

                    # Convert QByteArray to base64 string
                    img_base64 = base64.b64encode(byte_array.data()).decode('utf-8')
                else:
                    QMessageBox.warning(None, "Error", "The scene does not contain a QGraphicsPixmapItem.")
                    return
            else:
                QMessageBox.warning(None, "Error", "The scene is empty.")
                return
        else:
            QMessageBox.warning(None, "Error", "Right view or scene is not initialized.")
            return

        modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
        assistant_text = ""
        body = json.dumps({
            "messages": [{"role": "user", "content": [
                         {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_base64}},
                         {"type": "text", "text": input_text}]}],
            "max_tokens": params['maxT'],
            "temperature": params['temp'],
            "top_p": params['topP'],
            "anthropic_version": "bedrock-2023-05-31"
        })

        # Clear self.edit_3
        self.text_description.clear()

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
                            self.text_description.insertPlainText(resp['delta']['text'])
                            QApplication.processEvents()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")


    def ai_advice1_clear(self):
        self.history1 = ""
        self.text_description.clear()

    # anthropic.claude-3-sonnet-20240229-v1:0
    def ai_advice1(self,clients,history1):
        self.clients = clients
        self.history1 = history1
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Claude 3S')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.text_description.toPlainText() # + " " + self.edit_2.toPlainText()
        temp_input_buffer = "Human: " + input_text # Preserve human input
        # Add history
        input_text = self.history1 + "\n" + temp_input_buffer # Construct prompt with history

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
        self.text_description.clear()

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
                            self.text_description.insertPlainText(resp['delta']['text'])
                            QApplication.processEvents()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        
        self.text_description.insertPlainText("\n\n")
        temp_response_buffer = "AI: "+ self.text_description.toPlainText()
        self.history1 = self.history1 + "\n" + temp_input_buffer + "\n" + temp_response_buffer

    def ai_advice2_clear(self):
        self.history2 = ""
        self.text_description.clear()

    # amazon.titan-text-premier-v1:0
    def ai_advice2(self,clients,history2):
        self.clients = clients
        self.history2 = history2
        if 'bedrun' not in self.clients:
            QMessageBox.warning(None, 'Warning', 'Credentials Issue. Could not use Bedrock.')
            return
        # Get the model settings
        params = self.fetch_parameters('Titan P')
        # Concatenate text from self.edit_1 and self.edit_2
        input_text = self.text_description.toPlainText() # + " " + self.edit_2.toPlainText()
        temp_input_buffer = "Human: " + input_text # Preserve human input
        # Add history
        input_text = self.history2 + "\n" + temp_input_buffer # Construct prompt with history

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
        self.text_description.clear()

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
                        self.text_description.insertPlainText(output_text) 
                        QApplication.processEvents() 
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking model: {str(e)}")
        
        self.text_description.insertPlainText("\n\n")
        temp_response_buffer = "AI: "+ self.text_description.toPlainText()
        self.history2 = self.history2 + "\n" + temp_input_buffer + "\n" + temp_response_buffer






## ---------------------[ Image Viewer Control Methods ] ------------------------

    ## --- Photo editor live synch dual control methods ---
    def sync_bright_slider_to_spinner(self, value):
        self.photo_bright.setValue(value / 10.0)

    def sync_contrast_slider_to_spinner(self, value):
        self.photo_contrast.setValue(value / 10.0)

    def sync_saturation_slider_to_spinner(self, value):
        self.photo_saturation.setValue(value / 10.0)

    def sync_red_slider_to_spinner(self, value):
        self.photo_red.setValue(value / 10.0)

    def sync_green_slider_to_spinner(self, value):
        self.photo_green.setValue(value / 10.0)

    def sync_blue_slider_to_spinner(self, value):
        self.photo_blue.setValue(value / 10.0)

    def sync_alpha_slider_to_spinner(self, value):
        self.photo_alpha.setValue(value / 10.0)

    def sync_detail_slider_to_spinner(self, value):
        self.photo_detail.setValue(value / 10.0)

    def sync_blur_slider_to_spinner(self, value):
        self.photo_blur.setValue(value / 10.0)


    # --- PHOTO EDITOR METHODS ---

    def tab5Photo_Reset(self):
        self.photo_saturation_slider.setValue(10)
        self.photo_bright_slider.setValue(10)
        self.photo_red_slider.setValue(10)
        self.photo_green_slider.setValue(10)
        self.photo_blue_slider.setValue(10)
        self.photo_alpha_slider.setValue(10)
        self.photo_contrast_slider.setValue(10)
        self.photo_detail_slider.setValue(10)
        self.photo_blur_slider.setValue(0)

        self.photo_bright.setValue(1.0)
        self.photo_contrast.setValue(1.0)
        self.photo_saturation.setValue(1.0)
        self.photo_red.setValue(1.0)
        self.photo_green.setValue(1.0)
        self.photo_blue.setValue(1.0)
        self.photo_alpha.setValue(1.0)
        self.photo_detail.setValue(1.0)
        self.photo_blur.setValue(0.0)



    ## Live update
    @pyqtSlot()
    def update_image(self):
        # Check if the left_view contains an image
        has_image = False
        for item in self.left_scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                has_image = True
                break
        if not has_image:
            QMessageBox.warning(None, "Warning", "The input image view is empty. Please load an image before proceeding.")
            return
        
        # Extract the image from the left QGraphicsView
        pixmap = self.left_scene.items()[0].pixmap()
        image = pixmap.toImage()
        # Convert QImage to PIL Image
        # Ensure the QImage is in the correct format
        image = image.convertToFormat(QImage.Format_RGBA8888)
        # Get the size of the QImage
        width = image.width()
        height = image.height()
        # Get the raw pixel data from the QImage
        ## ptr = image.bits()
        ## ptr.setsize(image.byteCount())
        # Create a PIL Image from the raw data
        ## pil_image = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

        if not image.isNull():
            ptr = image.bits()
            ptr.setsize(image.byteCount())
            pil_image = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        else:
            QMessageBox.warning(None, "Warning", "The input image view is invalid. Please load an image before proceeding.")
            return


        # Adjust the brightness
        brightness_value = self.photo_bright.value()
        enhancer = ImageEnhance.Brightness(pil_image)
        enhanced_image = enhancer.enhance(brightness_value)

        # Adjust the contrast
        contrast_value = self.photo_contrast.value()
        enhancer = ImageEnhance.Contrast(enhanced_image)
        enhanced_image = enhancer.enhance(contrast_value)

        # Adjust the saturation
        saturation_value = self.photo_saturation.value()
        enhancer = ImageEnhance.Color(enhanced_image)  # Use the already enhanced image
        enhanced_image = enhancer.enhance(saturation_value)

        ## RGBA controls

        # Split the image into R, G, B, A channels
        photo_red = self.photo_red.value()
        photo_green = self.photo_green.value()
        photo_blue = self.photo_blue.value()
        photo_alpha = self.photo_alpha.value()

        r, g, b, *alpha = enhanced_image.split()  # The *alpha syntax provides empty list if no alpha channel
        # If there's no alpha channel, create one
        if not alpha:
            a = Image.new("L", r.size, 255)  # Create a fully opaque alpha channel (255)
        else:
            a = alpha[0]  # Use the existing alpha channel

        enhancer = ImageEnhance.Brightness(r)
        r_enhanced = enhancer.enhance(photo_red)  # Adjust the brightness of the Red channel
        enhancer = ImageEnhance.Brightness(g)
        g_enhanced = enhancer.enhance(photo_green)  # Adjust the brightness of the Green channel
        enhancer = ImageEnhance.Brightness(b)
        b_enhanced = enhancer.enhance(photo_blue)  # Adjust the brightness of the Red channel
        enhancer = ImageEnhance.Brightness(a)
        a_enhanced = enhancer.enhance(photo_alpha)  # Adjust the brightness of the Red channel
        enhanced_image = Image.merge("RGBA", (r_enhanced, g_enhanced, b_enhanced, a_enhanced))
        ##

        # Adjust the detail
        detail_value = self.photo_detail.value()
        enhancer = ImageEnhance.Sharpness(enhanced_image)  # Use the already enhanced image
        enhanced_image = enhancer.enhance(detail_value)

        
        blur_value = self.photo_blur.value()


        # Convert PIL.Image to QImage
        enhanced_image = enhanced_image.convert("RGBA")  # Ensure the image is in RGBA mode
        data = enhanced_image.tobytes("raw", "RGBA")
        qimage = QImage(data, enhanced_image.width, enhanced_image.height, QImage.Format_RGBA8888)

        # Now 'qimage' is a QImage object, and you can proceed with further processing if needed
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())

        # Convert QImage back to PIL.Image if further processing in PIL is required
        pil_image = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

        # Apply blur
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=blur_value))

        # Convert back to QImage
        enhanced_image = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(enhanced_image)

        # Display the adjusted image in the right QGraphicsView
        self.right_scene.clear()
        self.right_scene.addPixmap(pixmap)
        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)





    # --- Upscale and Save Right Scene
    def Photo_Upscale_and_Save(self):
        try:
            # Extract the image from the right QGraphicsView
            pixmap = self.right_scene.items()[0].pixmap()
            image = pixmap.toImage()

            # Convert QImage to NumPy array
            img = self.qimage_to_numpy(image)

            # Ask the user to select an output file
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            outputFile, _ = QFileDialog.getSaveFileName(None, "Select Output File Name", "", "PNG Files (*.png);;All Files (*)", options=options)
            if not outputFile:
                QMessageBox.warning(None, "Error", "No output file selected.")
                return

            # Upscale the image
            scale_factor = 4
            img = img_as_float(img)

            # Check if the image is grayscale or color
            if len(img.shape) == 2:  # Grayscale image
                pil_img = Image.fromarray((img * 255).astype(np.uint8))
                new_size = (int(img.shape[1] * scale_factor), int(img.shape[0] * scale_factor))
                upscaled_img = pil_img.resize(new_size, Image.LANCZOS)
                hr_img = np.array(upscaled_img) / 255.0
            else:  # Color image, handle each channel separately
                upscaled = np.zeros((img.shape[0] * scale_factor, img.shape[1] * scale_factor, img.shape[2]))

                for channel in range(img.shape[2]):
                    pil_img = Image.fromarray((img[..., channel] * 255).astype(np.uint8))
                    new_size = (int(img.shape[1] * scale_factor), int(img.shape[0] * scale_factor))
                    upscaled_channel = pil_img.resize(new_size, Image.LANCZOS)
                    upscaled[..., channel] = np.array(upscaled_channel) / 255.0

                hr_img = upscaled

            # Convert the upscaled floating point image to uint8 format
            hr_img_uint8 = (hr_img * 255).astype(np.uint8)

            # Convert the NumPy array back to a PIL image
            pil_img = Image.fromarray(hr_img_uint8)

            # Apply sharpening
            enhancer = ImageEnhance.Sharpness(pil_img)
            sharpened_img = enhancer.enhance(1.5)  # Adjust the factor as needed

            # Apply unsharp mask
            sharpened_img = sharpened_img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

            # Save the final image
            sharpened_img.save(outputFile)

            QMessageBox.information(None, "Success", f"Image successfully upscaled and saved to {outputFile}")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def qimage_to_numpy(self, qimage: QImage):
        """Convert a QImage object to a NumPy array, handling the stride correctly."""
        qimage = qimage.convertToFormat(QImage.Format_RGB888)
        width = qimage.width()
        height = qimage.height()
        stride = qimage.bytesPerLine()  # Get the number of bytes per line (stride)

        ptr = qimage.bits()
        ptr.setsize(height * stride)  # Adjust size based on stride

        # Convert the raw data into a NumPy array with the full stride
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, stride))

        # Extract only the relevant part of each row (the image width)
        arr = arr[:, :width * 3]  # Remove the padding bytes

        # Reshape to get the final image with 3 color channels
        arr = arr.reshape((height, width, 3))

        return arr
    # --- Upscale and Save Right Scene

    # --- Simple Upscaler for Windows and platforms with less sophisticated memory managment methods
    def Photo_Upscale_and_Save_Simple(self):
        try:
            # Extract the image from the right QGraphicsView
            pixmap = self.right_scene.items()[0].pixmap()
            image = pixmap.toImage()

            # Determine the format of the image
            if image.format() in (QImage.Format_ARGB32, QImage.Format_RGBA8888):
                has_alpha = True
            else:
                has_alpha = False

            # Extract the width and height of the image
            width = image.width()
            height = image.height()

            # Create a new QImage with doubled size
            new_width = width * 2
            new_height = height * 2

            if has_alpha:
                upscaled_image = QImage(new_width, new_height, QImage.Format_ARGB32)
            else:
                upscaled_image = QImage(new_width, new_height, QImage.Format_RGB32)


            if upscaled_image.isNull():
                print("Error: upscaled_image is not valid")
            else:
                painter = QPainter(upscaled_image)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                painter.drawImage(QRect(0, 0, new_width, new_height), image)
                painter.end()


            # Ask the user to select an output file
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            outputFile, _ = QFileDialog.getSaveFileName(None, "Select Output File Name", "", "PNG Files (*.png);;All Files (*)", options=options)
            if not outputFile:
                QMessageBox.warning(None, "Error", "No output file selected.")
                return

            # Save the upscaled image
            upscaled_image.save(outputFile)

            QMessageBox.information(None, "Success", f"Image successfully upscaled and saved to {outputFile}")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")


    # -------------- Simple upscaler

    ## -------------- DownScaler for ICONs
    def down_scaler(self, down_size):
        try:
            # Extract the image from the right QGraphicsView
            pixmap = self.right_scene.items()[0].pixmap()
            image = pixmap.toImage()

            # Determine the format of the image
            if image.format() in (QImage.Format_ARGB32, QImage.Format_RGBA8888):
                has_alpha = True
            else:
                has_alpha = False

            # Calculate the scale factor based on the desired down_size
            scale_factor = down_size / max(image.width(), image.height())

            # Calculate the new dimensions while preserving the aspect ratio
            new_width = int(image.width() * scale_factor)
            new_height = int(image.height() * scale_factor)

            # Create a new QImage with the downscaled size
            if has_alpha:
                downscaled_image = QImage(new_width, new_height, QImage.Format_ARGB32)
            else:
                downscaled_image = QImage(new_width, new_height, QImage.Format_RGB32)

            if downscaled_image.isNull():
                print("Error: downscaled_image is not valid")
            else:
                # Use QPainter to scale the image down
                painter = QPainter(downscaled_image)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                painter.drawImage(QRect(0, 0, new_width, new_height), image)
                painter.end()

            # Ask the user to select an output file
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            outputFile, _ = QFileDialog.getSaveFileName(None, "Select Output File Name", "", "PNG Files (*.png);;All Files (*)", options=options)
            if not outputFile:
                QMessageBox.warning(None, "Error", "No output file selected.")
                return

            # Save the downscaled image
            downscaled_image.save(outputFile)

            QMessageBox.information(None, "Success", f"Image successfully downscaled and saved to {outputFile}")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
    ## -------------- DownScaler for ICONs



    def scribble(self):
        # Install event filter to capture events in the QGraphicsView
        self.left_view.viewport().installEventFilter(self)

    def choose_brush_color(self):
        # Open the color dialog and get the selected color
        color = QColorDialog.getColor()

        if color.isValid():
            # Set the brush color components
            self.brush_red = color.red()
            self.brush_green = color.green()
            self.brush_blue = color.blue()

    def brush_up(self):
        """Increase the brush size by 1."""
        self.brush_pixels += 1
        print(f"Brush size increased to: {self.brush_pixels}")

    def brush_dn(self):
        """Decrease the brush size by 1, but not below 1."""
        if self.brush_pixels > 1:
            self.brush_pixels -= 1


    

    # --- SCRIBBLE Left Scene

    def eventFilter(self, obj, event):
        if obj == self.left_view.viewport() and self.scribble_enabled:
            if event.type() == event.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.drawing = True
                    # Convert to scene coordinates
                    self.last_point = self.left_view.mapToScene(event.pos())
                    return True
            elif event.type() == event.MouseMove:
                if self.drawing:
                    # Convert to scene coordinates
                    current_point = self.left_view.mapToScene(event.pos())
                    line = QLineF(self.last_point, current_point)
                    pen = QPen(QColor(self.brush_red, self.brush_green, self.brush_blue), self.brush_pixels)  # Using brush colors and size
                    self.left_scene.addLine(line, pen)
                    self.last_point = current_point
                    return True
            elif event.type() == event.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self.drawing = False
                    # Save the current drawing as a pixmap every time the user releases the mouse
                    self.save_scribble_as_pixmap()
                    return True
        return False
    
    def toggle_scribble(self):
        """Toggle the scribble feature on or off."""
        self.scribble_enabled = self.radio_button.isChecked()
        if self.scribble_enabled:
            # Check if there's an image in the background and use its size
            pixmap_item = next((item for item in self.left_scene.items() if isinstance(item, QGraphicsPixmapItem)), None)
            if pixmap_item:
                # Use the size of the existing pixmap item
                pixmap_rect = pixmap_item.boundingRect()
                #print("DEBUG-001: ", pixmap_rect)
                self.left_scene.setSceneRect(pixmap_rect)
            else:
                # Clear the left scene if no image is found before adding the new image
                self.left_scene.clear()
                # Set the scene rectangle to a default size (e.g., 512x512)
                default_size = 512
                #print("DEBUG-002: ", default_size)
                self.left_scene.setSceneRect(0, 0, default_size, default_size)

            self.left_view.resetTransform()  # Reset any transformations (e.g., zoom)

    def save_scribble_as_pixmap(self):
        # Find the original background image, if it exists
        original_pixmap_item = next((item for item in self.left_scene.items() if isinstance(item, QGraphicsPixmapItem)), None)
        if original_pixmap_item:
            original_rect = original_pixmap_item.boundingRect()
            #print("DEBUG-004: Original image size:", original_rect.width(), original_rect.height())
            final_width = int(original_rect.width())
            final_height = int(original_rect.height())
        else:
            # Fallback to current scene size if no original image is found
            rect = self.left_scene.sceneRect()
            final_width = int(rect.width())
            final_height = int(rect.height())
            #print("DEBUG-003 (W,H): ", rect.width(), rect.height())

        # Create a QImage with the scene size, explicitly setting the format to RGB without alpha
        image = QImage(final_width, final_height, QImage.Format_RGB32)
        image.fill(Qt.white)  # Fill with a white background

        # Use a QPainter to render the scene onto the QImage
        #painter = QPainter(image)
        #self.left_scene.render(painter)
        #painter.end()
        if image.isNull():
            # print("Error: image is not valid") ## Testing on load during debug development
            pass
        else:
            painter = QPainter(image)
            self.left_scene.render(painter)
            painter.end()


        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(image)

        # Clear the scene
        self.left_scene.clear()

        # Restore the original scene rectangle size (should match the background image size)
        self.left_scene.setSceneRect(0, 0, final_width, final_height)
        self.left_view.resetTransform()  # Reset any transformations (e.g., zoom)

        # Add the QPixmap as an item to the scene
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.left_scene.addItem(pixmap_item)

        # Optionally, you can adjust the view to fit the new pixmap
        self.left_view.fitInView(pixmap_item, Qt.KeepAspectRatio)

        return pixmap    
    
    ## AutoScribble    


    # --- LEFT IMAGE VIEWER METHODS ---
    #
    def left_open_image(self):
        # Open a file dialog to select an image file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp *.gif)")
        if file_name:
            # Load the image and display it in the left QGraphicsView
            pixmap = QPixmap(file_name)
            self.left_scene.clear()  # Clear the scene before adding the new image
            self.left_scene.addPixmap(pixmap)

            # Optional: Set the scene rectangle and transformation to avoid cropping
            self.left_view.setSceneRect(self.left_scene.itemsBoundingRect())
            self.left_view.setTransform(QTransform())  # Reset any previous transformation

            # Fit the image in the view
            self.left_view.fitInView(self.left_scene.itemsBoundingRect(), Qt.KeepAspectRatio)


    def left_save_image(self):
        # Open a file dialog to choose the save location and file name
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image File", "", "Images (*.png *.jpg *.bmp *.gif)")
        if file_name:
            # Check if there's an item in the scene to save
            if not self.left_scene.items():
                print("No image to save.")
                return

            # Create a QPixmap of the same size as the scene's bounding rectangle
            rect = self.left_scene.itemsBoundingRect()
            image = QPixmap(int(rect.width()), int(rect.height()))
            image.fill(Qt.white)  # Optional: fill the background with white

            # Render the scene to the pixmap
            painter = QPainter(image)
            self.left_scene.render(painter, target=rect, source=rect)
            painter.end()

            # Save the pixmap to the selected file
            image.save(file_name)

    def left_clear_image(self):
        # Clear the scene and reset the view
        self.left_scene.clear()
        # Set the scene rectangle to a default size (e.g., 512x512)
        #default_size = 512
        #self.left_scene.setSceneRect(0, 0, default_size, default_size)
        #self.left_view.resetTransform()  # Reset any transformations (e.g., zoom)

    def left_zoom_in(self):
        # Zoom in by scaling the view
        self.left_view.scale(1.25, 1.25)  # Scale by 125% (1.25 times)

    def left_zoom_out(self):
        # Zoom out by scaling the view
        self.left_view.scale(0.8, 0.8)  # Scale by 80% (0.8 times)

    def left_zoom_real_size(self):
        # Zoom out by scaling the view
        self.left_view.resetTransform()

    def left_zoom_reset(self):
        # Fit the image in the view while maintaining the aspect ratio
        self.left_view.fitInView(self.left_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def copy_to_right_viewer(self):
        # Check if there's an item in the left scene
        if self.left_scene.items():
            # Get the first item in the left scene (assuming it's the image)
            left_item = self.left_scene.items()[0]

            if isinstance(left_item, QGraphicsPixmapItem):  # Ensure the item is a pixmap
                pixmap = left_item.pixmap()

                # Clear the right scene before adding the new image
                self.right_scene.clear()
                self.right_scene.addPixmap(pixmap)

                # Optionally, fit the image to the right view
                self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        else:
            print("No image found in the left viewer.")

    ## -------- Left Storage methods ------ ###
    ##
    def left_save_image_to_storage(self, storage_index):
        # Grab the image from the left scene
        if self.left_scene.items():  # Check if there are any items in the scene
            image = QImage(self.left_scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
            painter = QPainter(image)
            self.left_scene.render(painter)
            painter.end()

            pixmap = QPixmap.fromImage(image)
            self.left_image_storage[storage_index] = pixmap  # Store the QPixmap in the specified storage area


    def left_display_image_from_storage(self, storage_index):
        if self.left_image_storage[storage_index] is not None:
                self.left_scene.clear()                                            # Clear the existing scene
                self.left_scene.addPixmap(self.left_image_storage[storage_index])  # Display the image



    # --- RIGHT IMAGE VIEWER METHODS ---

    def right_open_image(self):
        # Open a file dialog to select an image file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp *.gif)")
        if file_name:
            # Load the image and display it in the left QGraphicsView
            pixmap = QPixmap(file_name)
            self.right_scene.clear()  # Clear the scene before adding the new image
            self.right_scene.addPixmap(pixmap)
            self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)  # Fit the image in the view

    def right_save_image(self):
        # Open a file dialog to choose the save location and file name
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image File", "", "Images (*.png *.jpg *.bmp *.gif)")
        if file_name:
            # Check if there's an item in the scene to save
            if not self.right_scene.items():
                print("No image to save.")
                return

            # Create a QPixmap of the same size as the scene's bounding rectangle
            rect = self.right_scene.itemsBoundingRect()
            image = QPixmap(int(rect.width()), int(rect.height()))
            image.fill(Qt.white)  # Optional: fill the background with white

            # Render the scene to the pixmap
            painter = QPainter(image)
            self.right_scene.render(painter, target=rect, source=rect)
            painter.end()

            # Save the pixmap to the selected file
            image.save(file_name)

    def right_clear_image(self):
        # Clear the scene and reset the view
        self.right_scene.clear()
        self.right_view.resetTransform()  # Reset any transformations (e.g., zoom)

    def right_zoom_in(self):
        # Zoom in by scaling the view
        self.right_view.scale(1.25, 1.25)  # Scale by 125% (1.25 times)

    def right_zoom_out(self):
        # Zoom out by scaling the view
        self.right_view.scale(0.8, 0.8)  # Scale by 80% (0.8 times)

    def right_zoom_real_size(self):
        # Zoom out by scaling the view
        self.right_view.resetTransform()

    def right_zoom_reset(self):
        # Fit the image in the view while maintaining the aspect ratio
        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def copy_to_left_viewer(self):
        # Check if there's an item in the left scene
        if self.right_scene.items():
            # Get the first item in the left scene (assuming it's the image)
            right_item = self.right_scene.items()[0]

            if isinstance(right_item, QGraphicsPixmapItem):  # Ensure the item is a pixmap
                pixmap = right_item.pixmap()

                # Clear the left scene before adding the new image
                self.left_scene.clear()

                ###n
                self.left_view.setSceneRect(self.right_view.sceneRect())  # Set the scene rectangle
                self.left_view.setTransform(self.right_view.transform())  # Copy the transformation

                self.left_scene.addPixmap(pixmap)

                # Fit the image to the right view
                self.left_view.fitInView(self.left_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        else:
            print("No image found in the left viewer.")

    ## -------- Right Storage methods ---------- ###
    ##


    def right_save_image_to_storage(self, storage_index):
        # Grab the image from the right scene
        if self.right_scene.items():  # Check if there are any items in the scene
            image = QImage(self.right_scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
            painter = QPainter(image)
            self.right_scene.render(painter)
            painter.end()

            pixmap = QPixmap.fromImage(image)
            self.right_image_storage[storage_index] = pixmap  # Store the QPixmap in the specified storage area

    def right_display_image_from_storage(self, storage_index):
        if self.right_image_storage[storage_index] is not None:
            self.right_scene.clear()
            self.right_scene.addPixmap(self.right_image_storage[storage_index])



## ---------------------[ General Methods ] ------------------------

    # ---------------[ Choose Size ]------------------
    #
    def chooseSize(self, side):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Valid Titan Image Size")
        dialog.resize(450, 850) 
        
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setRowCount(25)  
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Width", "Height", "Aspect Ratio", "Price Equivalent"])

        data = [
            [1024, 1024, "1:1", "1024 x 1024"],
            [768, 768, "1:1", "512 x 512"],
            [512, 512, "1:1", "512 x 512"],
            [768, 1152, "2:3", "1024 x 1024"],
            [384, 576, "2:3", "512 x 512"],
            [1152, 768, "3:2", "1024 x 1024"],
            [576, 384, "3:2", "512 x 512"],
            [768, 1280, "3:5", "1024 x 1024"],
            [384, 640, "3:5", "512 x 512"],
            [1280, 768, "5:3", "1024 x 1024"],
            [640, 384, "5:3", "512 x 512"],
            [896, 1152, "7:9", "1024 x 1024"],
            [448, 576, "7:9", "512 x 512"],
            [1152, 896, "9:7", "1024 x 1024"],
            [576, 448, "9:7", "512 x 512"],
            [768, 1408, "6:11", "1024 x 1024"],
            [384, 704, "6:11", "512 x 512"],
            [1408, 768, "11:6", "1024 x 1024"],
            [704, 384, "11:6", "512 x 512"],
            [640, 1408, "5:11", "1024 x 1024"],
            [320, 704, "5:11", "512 x 512"],
            [1408, 640, "11:5", "1024 x 1024"],
            [704, 320, "11:5", "512 x 512"],
            [1152, 640, "9:5", "1024 x 1024"],
            [1173, 640, "16:9", "1024 x 1024"],
        ]

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)

        layout.addWidget(table)

        # Add a button to confirm selection
        button = QPushButton("Select", dialog)
        button.clicked.connect(lambda: self.setSize(table, dialog, side))
        layout.addWidget(button)

        dialog.setLayout(layout)
        dialog.exec_()

    def setSize(self, table, dialog, side):
        selected_items = table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            width = int(table.item(selected_row, 0).text())
            height = int(table.item(selected_row, 1).text())

            if side == 'left':
                self.ui_left_width.setText(str(width))
                self.ui_left_height.setText(str(height))
            elif side == 'gset':
                self.ui_gset_width.setText(str(width))
                self.ui_gset_height.setText(str(height))

        dialog.accept()

    # ---------------[ Set random number for seed ]------------------
    #
    def randomSeed(self, side):
        # Generate a random value in the desired range
        seed = random.randint(0, 2147483646)

        # Determine whether to set the left or right seed
        if side == 'left':
            self.left_seed = seed
            self.ui_left_seed.setText(str(self.left_seed))
        elif side == 'gset':
            self.gset_seed = seed
            self.ui_gset_seed.setText(str(self.gset_seed))



## ---------------------[ MODEL INVOCATION ] ------------------------

## ---------------------- NOVA CANVAS ------------------
    def rightNovaCanvas(self):
        # The following values come from Tab 1, Image Generation
        G2input_text = self.tab1_prompt_edit.toPlainText()
        G2neg_input_text = self.tab1_neg_prompt_edit.toPlainText()
        # The following values come from the global settings
        G2number_of_images = int(self.ui_gset_number_of_images.text())
        G2quality = self.ui_gset_quality.text().strip().lower()
        G2cfg_scale = float(self.gset_cfgScale.text())
        G2width = int(self.ui_gset_width.text())
        G2height = int(self.ui_gset_height.text())
        G2seed = int(self.ui_gset_seed.text())

        # The model only suppots specific sizes that must be betwee 256 and 1405 
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html

        while G2input_text.startswith("\n"):
            G2input_text = G2input_text[1:]
        
        modelId = 'amazon.nova-canvas-v1:0'

        body = json.dumps(
        {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": G2input_text,"negativeText": G2neg_input_text},
        "imageGenerationConfig": {
            "numberOfImages": G2number_of_images,
            "quality": G2quality,
            "cfgScale": G2cfg_scale,
            "height": G2height,
            "width": G2width,
            "seed": G2seed,
        }, } )

        if(len(G2neg_input_text)<4):
            body = json.dumps(
            {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": G2input_text},
            "imageGenerationConfig": {
                "numberOfImages": G2number_of_images,
                "quality": G2quality,
                "cfgScale": G2cfg_scale,
                "height": G2height,
                "width": G2width,
                "seed": G2seed,
            }, } )

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap        



        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Nova Canvas model: {str(e)}")

## ---------------------- NOVA CANVAS ------------------

## ---------------------- TITAN IMAGE G1 v2 ------------------------
##
##  Invoked from tab 1
##
    def rightTitanG2Image(self):
        # The following values come from Tab 1, Image Generation
        G2input_text = self.tab1_prompt_edit.toPlainText()
        G2neg_input_text = self.tab1_neg_prompt_edit.toPlainText()
        # The following values come from the global settings
        G2number_of_images = int(self.ui_gset_number_of_images.text())
        G2quality = self.ui_gset_quality.text().strip().lower()
        G2cfg_scale = float(self.gset_cfgScale.text())
        G2width = int(self.ui_gset_width.text())
        G2height = int(self.ui_gset_height.text())
        G2seed = int(self.ui_gset_seed.text())

        # The model only suppots specific sizes that must be betwee 256 and 1405 
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html

        while G2input_text.startswith("\n"):
            G2input_text = G2input_text[1:]
        
        modelId = 'amazon.titan-image-generator-v2:0'

        body = json.dumps(
        {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": G2input_text,"negativeText": G2neg_input_text},
        "imageGenerationConfig": {
            "numberOfImages": G2number_of_images,
            "quality": G2quality,
            "cfgScale": G2cfg_scale,
            "height": G2height,
            "width": G2width,
            "seed": G2seed,
        }, } )

        if(len(G2neg_input_text)<4):
            body = json.dumps(
            {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": G2input_text},
            "imageGenerationConfig": {
                "numberOfImages": G2number_of_images,
                "quality": G2quality,
                "cfgScale": G2cfg_scale,
                "height": G2height,
                "width": G2width,
                "seed": G2seed,
            }, } )

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap        



        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G2 model: {str(e)}")
# ------------------------------

# ------ TITAN IMAGE GENERATOR v1
# modelId = 'amazon.titan-image-generator-v1'
#
    def rightTitanG1Image(self):
        # The following values come from Tab 1, Image Generation
        G2input_text = self.tab1_prompt_edit.toPlainText()
        G2neg_input_text = self.tab1_neg_prompt_edit.toPlainText()
        # The following values come from the global settings
        G2number_of_images = int(self.ui_gset_number_of_images.text())
        G2quality = self.ui_gset_quality.text().strip().lower()
        G2cfg_scale = float(self.gset_cfgScale.text())
        G2width = int(self.ui_gset_width.text())
        G2height = int(self.ui_gset_height.text())
        G2seed = int(self.ui_gset_seed.text())

        # The model only suppots specific sizes that must be betwee 256 and 1405 
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html

        while G2input_text.startswith("\n"):
            G2input_text = G2input_text[1:]
        
        modelId = 'amazon.titan-image-generator-v1'

        body = json.dumps(
        {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": G2input_text,"negativeText": G2neg_input_text},
        "imageGenerationConfig": {
            "numberOfImages": G2number_of_images,
            "quality": G2quality,
            "cfgScale": G2cfg_scale,
            "height": G2height,
            "width": G2width,
            "seed": G2seed,
        }, } )

        if(len(G2neg_input_text)<4):
            body = json.dumps(
            {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": G2input_text},
            "imageGenerationConfig": {
                "numberOfImages": G2number_of_images,
                "quality": G2quality,
                "cfgScale": G2cfg_scale,
                "height": G2height,
                "width": G2width,
                "seed": G2seed,
            }, } )

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]
        
            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G2 model: {str(e)}")
# ------------------------------

    ## ------------------ RIGHT Reference Color Guided Image Generator
    def ColorG2TitanCOLOR(self):
        G3input_text = self.tab2_prompt_edit.toPlainText()
        G3neg_input_text = self.tab2_neg_prompt_edit.toPlainText()
        G3number_of_images = int(self.ui_gset_number_of_images.text())
        G3quality = self.ui_gset_quality.text().strip().lower()
        G3cfg_scale = float(self.gset_cfgScale.text())
        G3width = int(self.ui_gset_width.text())
        G3height = int(self.ui_gset_height.text())
        G3seed = int(self.ui_gset_seed.text())
        # G3control_mode = "COLOR_GUIDED_GENERATION" 
        # G3color = self.ui_tab2_colors.text()
        G3color = self.process_colors_tab2() # Hex code colors are on the left. And the reference image is on the left.
        # print("G3color",G3color)

        while G3input_text.startswith("\n"):
            G3input_text = G3input_text[1:]

        modelId = 'amazon.titan-image-generator-v2:0'

        # Extract the image from the left QGraphicsView or set G3input_image to None if there is no image in the left view
        items = self.left_scene.items() 
        if items:
            pixmap = self.left_scene.items()[0].pixmap()  # Assuming there's only one item in the scene and the reference image is on the left
            image = pixmap.toImage()
            # Convert the QImage to a byte array
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            image.save(buffer, "PNG")
            G3input_image = buffer.data().toBase64().data().decode('utf8')
        else:
            G3input_image = None

        # 1. Whether there is negative text present or not
        # 2. Whether there is a reference image in left or not
        # 3. Whether there are hex codes present or not.
        # Flags
        flagNeg = 0 if len(G3neg_input_text) < 3 else 1
        flagHex = 0 if not G3color else 1
        flagImg = 0 if G3input_image is None else 1

        body_dict = {
            "taskType": "COLOR_GUIDED_GENERATION",
            "colorGuidedGenerationParams": {},
            "imageGenerationConfig": {
                "numberOfImages": G3number_of_images,
                "quality": G3quality,
                "cfgScale": G3cfg_scale,
                "height": G3height,
                "width": G3width,
                "seed": G3seed
            }
        }
        # Always include text
        body_dict["colorGuidedGenerationParams"]["text"] = G3input_text
        # Conditionally add negativeText if flagNeg is set
        if flagNeg:
            body_dict["colorGuidedGenerationParams"]["negativeText"] = G3neg_input_text
        # Conditionally add colors if flagHex is set
        if flagHex:
            body_dict["colorGuidedGenerationParams"]["colors"] = G3color
        # Conditionally add referenceImage if flagImg is set
        if flagImg:
            body_dict["colorGuidedGenerationParams"]["referenceImage"] = G3input_image
        # Convert the dictionary to a JSON string
        body = json.dumps(body_dict)

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap


        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")


    ## ------------------ Color Guided Image Generator WITHOUT Reference image
    def ColorG2TitanCOLOR_NOIMAGE(self):
        G3input_text = self.tab2_prompt_edit.toPlainText()
        G3neg_input_text = self.tab2_neg_prompt_edit.toPlainText()
        G3number_of_images = int(self.ui_gset_number_of_images.text())
        G3quality = self.ui_gset_quality.text().strip().lower()
        G3cfg_scale = float(self.gset_cfgScale.text())
        G3width = int(self.ui_gset_width.text())
        G3height = int(self.ui_gset_height.text())
        G3seed = int(self.ui_gset_seed.text())
        # G3control_mode = "COLOR_GUIDED_GENERATION" 
        # G3color = self.ui_tab2_colors.text()
        G3color = self.process_colors_tab2() # Hex code colors are on the left. And the reference image is on the left.
        # print("G3color",G3color)

        while G3input_text.startswith("\n"):
            G3input_text = G3input_text[1:]

        modelId = 'amazon.titan-image-generator-v2:0'

        # Extract the image from the left QGraphicsView or set G3input_image to None if there is no image in the left view
        items = self.left_scene.items() 
        if items:
            pixmap = self.left_scene.items()[0].pixmap()  # Assuming there's only one item in the scene and the reference image is on the left
            image = pixmap.toImage()
            # Convert the QImage to a byte array
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            image.save(buffer, "PNG")
            G3input_image = buffer.data().toBase64().data().decode('utf8')
        else:
            G3input_image = None

        # 1. Whether there is negative text present or not
        # 2. Whether there is a reference image in left or not
        # 3. Whether there are hex codes present or not.
        # Flags
        flagNeg = 0 if len(G3neg_input_text) < 3 else 1
        flagHex = 0 if not G3color else 1
        flagImg = 0 # Setting it to have NO reference image

        body_dict = {
            "taskType": "COLOR_GUIDED_GENERATION",
            "colorGuidedGenerationParams": {},
            "imageGenerationConfig": {
                "numberOfImages": G3number_of_images,
                "quality": G3quality,
                "cfgScale": G3cfg_scale,
                "height": G3height,
                "width": G3width,
                "seed": G3seed
            }
        }
        # Always include text
        body_dict["colorGuidedGenerationParams"]["text"] = G3input_text
        # Conditionally add negativeText if flagNeg is set
        if flagNeg:
            body_dict["colorGuidedGenerationParams"]["negativeText"] = G3neg_input_text
        # Conditionally add colors if flagHex is set
        if flagHex:
            body_dict["colorGuidedGenerationParams"]["colors"] = G3color
        # Conditionally add referenceImage if flagImg is set
        if flagImg:
            body_dict["colorGuidedGenerationParams"]["referenceImage"] = G3input_image
        # Convert the dictionary to a JSON string
        body = json.dumps(body_dict)

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")




    def process_colors_tab2(self):
        # Get the text from the QLineEdit widget
        color_text = self.ui_tab2_colors.text().strip()

        # If the color_text is empty, return an empty list
        if not color_text:
            return []

        # Split the input text by spaces, commas, or semicolons
        raw_colors = re.split(r'[ ,;]+', color_text)

        # Process each color: ensure it starts with a '#' and has exactly 6 hex digits
        valid_colors = []
        for color in raw_colors:
            # Strip any leading or trailing whitespace
            color = color.strip()
            
            # Ensure the color has 6 hex digits
            if len(color) == 6 and all(c in "0123456789ABCDEFabcdef" for c in color):
                color = '#' + color  # Add '#' if it's not present
            elif len(color) == 7 and color.startswith('#') and all(c in "0123456789ABCDEFabcdef" for c in color[1:]):
                pass  # The color is already valid with '#'
            else:
                continue  # Skip invalid entries

            valid_colors.append(color)

        return valid_colors  # Return as a list


# Stable Diffusion XL | stability.stable-diffusion-xl |
# stability.stable-diffusion-xl-v1
    def stability_image_gen(self):
        G2input_text = self.tab1_prompt_edit.toPlainText()
        G2cfg_scale = float(self.gset_cfgScale.text())
        G2seed = int(self.ui_gset_seed.text())

        while G2input_text.startswith("\n"):
            G2input_text = G2input_text[1:]
        
        modelId = 'stability.stable-diffusion-xl-v1'

        body = json.dumps({
            "text_prompts": [{"text": G2input_text}], 
            "seed": G2seed,
            "cfg_scale": G2cfg_scale,
            "steps": 30,   # Default is 30
            })
        
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-1-0-text-image.html
        #
        # Size: 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640, 640x1536, 768x1344, 832x1216, 896x1152.

        #1024x1024 = 1:1 (Square)
        #1152x896 = 1.285:1 (Close to 5:4)
        #1216x832 = 1.462:1  
        #1344x768 = 1.75:1 (Close to 16:9)
        #1536x640 = 2.4:1
        #640x1536 = 1:2.4
        #768x1344 = 1:1.75 (Close to 16:9)  
        #832x1216 = 1:1.462
        #896x1152 = 1:1.285 (Close to 5:4)


        #    "height": int,
        #    "width": int,
        #    "cfg_scale": float, >> Is an integer between 0 and 35, default 7
        #    "clip_guidance_preset": string,
        #    "sampler": string, >>> Automatically selected for you : DDIM, DDPM, K_DPMPP_2M, K_DPMPP_2S_ANCESTRAL, K_DPM_2, K_DPM_2_ANCESTRAL, K_EULER, K_EULER_ANCESTRAL, K_HEUN K_LMS.
        #    "samples", >>> Bedrock only currently supports a sample of 1
        #    "seed": int,  >>> 0 to 4294967295
        #    "steps": int, >>> 10 to 150 default 30
        #    "style_preset": string,
        #  3d-model, analog-film, anime, cinematic, comic-book, digital-art, enhance, fantasy-art, isometric, line-art, low-poly, modeling-compound, neon-punk, origami, photographic, pixel-art, tile-texture
        #  This list changes...
        #  Currently 160 styles:
        # Stability AI styles
        '''
		3D Model
		Analog Film
		Anime
		Cinematic
		Comic Book
		Craft Clay
		Digital Art
		Enhance
		Fantasy Art
		Isometric
		Line Art
		Lowpoly
		Neonpunk
		Origami
		Photographic
		Pixel Art
		Texture
		TWRI styles
		Ads Advertising
		Ads Automotive
		Ads Corporate
		Ads Fashion Editorial
		Ads Food Photography
		Ads Gourmet Food Photography
		Ads Luxury
		Ads Real Estate
		Ads Retail
		Artstyle Abstract
		Artstyle Abstract Expressionism
		Artstyle Art Deco
		Artstyle Art Nouveau
		Artstyle Constructivist
		Artstyle Cubist
		Artstyle Expressionist
		Artstyle Graffiti
		Artstyle Hyperrealism
		Artstyle Impressionist
		Artstyle Pointillism
		Artstyle Pop Art
		Artstyle Psychedelic
		Artstyle Renaissance
		Artstyle Steampunk
		Artstyle Surrealist
		Artstyle Typography
		Artstyle Watercolor
		Futuristic Biomechanical
		Futuristic Biomechanical Cyberpunk
		Futuristic Cybernetic
		Futuristic Cybernetic Robot
		Futuristic Cyberpunk Cityscape
		Futuristic Futuristic
		Futuristic Retro Cyberpunk
		Futuristic Retro Futurism
		Futuristic Sci Fi
		Futuristic Vaporwave
		Game Bubble Bobble
		Game Cyberpunk Game
		Game Fighting Game
		Game Gta
		Game Mario
		Game Minecraft
		Game Pokemon
		Game Retro Arcade
		Game Retro Game
		Game RPG Fantasy Game
		Game Strategy Game
		Game Streetfighter
		Game Zelda
		Misc Architectural
		Misc Disco
		Misc Dreamscape
		Misc Dystopian
		Misc Fairy Tale
		Misc Gothic
		Misc Grunge
		Misc Horror
		Misc Kawaii
		Misc Lovecraftian
		Misc Macabre
		Misc Manga
		Misc Metropolis
		Misc Minimalist
		Misc Monochrome
		Misc Nautical
		Misc Space
		Misc Stained Glass
		Misc Techwear Fashion
		Misc Tribal
		Misc Zentangle
		Papercraft Collage
		Papercraft Flat Papercut
		Papercraft Kirigami
		Papercraft Paper Mache
		Papercraft Paper Quilling
		Papercraft Papercut Collage
		Papercraft Papercut Shadow Box
		Papercraft Stacked Papercut
		Papercraft Thick Layered Papercut
		Photo Alien
		Photo Film Noir
		Photo Glamour
		Photo Hdr
		Photo Iphone Photographic
		Photo Long Exposure
		Photo Neon Noir
		Photo Silhouette
		Photo Tilt Shift
        '''
        #    "extras" :JSON object



        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            #base64_image_data = response_body["images"][0]
            base64_image_data = response_body["artifacts"][0]["base64"]

            # Convert base64 image to QImage and then to QPixmap
            image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            pixmap = QPixmap.fromImage(image)
            self.right_scene.clear()  # Clear the previous image
            self.right_scene.addPixmap(pixmap)
            self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Stability XL model: {str(e)}")


# ------------------------------


# Stable Diffusion XL | stability.stable-diffusion-xl |
# stability.stable-diffusion-xl-v1
    def stability_image_gen_16x9(self):
        G2input_text = self.tab1_prompt_edit.toPlainText()
        G2cfg_scale = float(self.gset_cfgScale.text())
        G2seed = int(self.ui_gset_seed.text())

        while G2input_text.startswith("\n"):
            G2input_text = G2input_text[1:]
        
        modelId = 'stability.stable-diffusion-xl-v1'

        body = json.dumps({
            "text_prompts": [{"text": G2input_text}], 
            "height": 768,
            "width": 1344,
            "seed": G2seed,
            "cfg_scale": G2cfg_scale,
            "steps": 30,   # Default is 30
            })
        
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-1-0-text-image.html
        #
        # Size: 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640, 640x1536, 768x1344, 832x1216, 896x1152.

        #1024x1024 = 1:1 (Square)
        #1152x896 = 1.285:1 (Close to 5:4)
        #1216x832 = 1.462:1  
        #1344x768 = 1.75:1 (Close to 16:9)
        #1536x640 = 2.4:1
        #640x1536 = 1:2.4
        #768x1344 = 1:1.75 (Close to 16:9)  
        #832x1216 = 1:1.462
        #896x1152 = 1:1.285 (Close to 5:4)

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            #base64_image_data = response_body["images"][0]
            base64_image_data = response_body["artifacts"][0]["base64"]

            # Convert base64 image to QImage and then to QPixmap
            image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            pixmap = QPixmap.fromImage(image)
            self.right_scene.clear()  # Clear the previous image
            self.right_scene.addPixmap(pixmap)
            self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Stability XL model: {str(e)}")


# ------------------------------





# ------------------------------ Model Invocation, Titan G3 Left Side with Conditioning
    
    def ConditionG2TitanCANNY(self):
        G3control_mode = "CANNY_EDGE" 

        G3input_text = self.tab3_prompt_edit.toPlainText()
        G3neg_input_text = self.tab3_neg_prompt_edit.toPlainText()
        G3number_of_images = int(self.ui_gset_number_of_images.text())
        G3quality = self.ui_gset_quality.text().strip().lower()
        G3cfg_scale = float(self.gset_cfgScale.text())
        G3width = int(self.ui_gset_width.text())
        G3height = int(self.ui_gset_height.text())
        G3seed = int(self.ui_gset_seed.text())



        while G3input_text.startswith("\n"):
            G3input_text = G3input_text[1:]

        modelId = 'amazon.titan-image-generator-v2:0'

        # Read image from file and encode it as base64 string
        # with open(G3condition_image_path, "rb") as image_file:
        #    G3input_image = base64.b64encode(image_file.read()).decode('utf8')

        # Extract the image from the left QGraphicsView
        pixmap = self.left_scene.items()[0].pixmap()  # Assuming there's only one item in the scene
        image = pixmap.toImage()

        # Convert the QImage to a byte array
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        G3input_image = buffer.data().toBase64().data().decode('utf8')

        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": G3input_text,
                "negativeText": G3neg_input_text,
                "conditionImage": G3input_image,
                "controlMode": G3control_mode,
            },
            "imageGenerationConfig": {
                "numberOfImages": G3number_of_images,
                "quality": G3quality,
                "cfgScale": G3cfg_scale,
                "height": G3height,
                "width": G3width,
                "seed": G3seed
            }
        })

        if(len(G3neg_input_text)<4):
            body = json.dumps({
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": G3input_text,
                    "conditionImage": G3input_image,
                    "controlMode": G3control_mode,
                },
                "imageGenerationConfig": {
                    "numberOfImages": G3number_of_images,
                    "quality": G3quality,
                    "cfgScale": G3cfg_scale,
                    "height": G3height,
                    "width": G3width,
                    "seed": G3seed
                }
            })

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")



    def ConditionG2TitanSEGMENTATION(self):
        G3control_mode = "SEGMENTATION"  

        G3input_text = self.tab3_prompt_edit.toPlainText()
        G3neg_input_text = self.tab3_neg_prompt_edit.toPlainText()
        G3number_of_images = int(self.ui_gset_number_of_images.text())
        G3quality = self.ui_gset_quality.text().strip().lower()
        G3cfg_scale = float(self.gset_cfgScale.text())
        G3width = int(self.ui_gset_width.text())
        G3height = int(self.ui_gset_height.text())
        G3seed = int(self.ui_gset_seed.text())

        while G3input_text.startswith("\n"):
            G3input_text = G3input_text[1:]

        modelId = 'amazon.titan-image-generator-v2:0'

        # Read image from file and encode it as base64 string
        # with open(G3condition_image_path, "rb") as image_file:
        #    G3input_image = base64.b64encode(image_file.read()).decode('utf8')

        # Extract the image from the left QGraphicsView
        pixmap = self.left_scene.items()[0].pixmap()  # Assuming there's only one item in the scene
        image = pixmap.toImage()

        # Convert the QImage to a byte array
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        G3input_image = buffer.data().toBase64().data().decode('utf8')

        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": G3input_text,
                "negativeText": G3neg_input_text,
                "conditionImage": G3input_image,
                "controlMode": G3control_mode,
            },
            "imageGenerationConfig": {
                "numberOfImages": G3number_of_images,
                "quality": G3quality,
                "cfgScale": G3cfg_scale,
                "height": G3height,
                "width": G3width,
                "seed": G3seed
            }
        })

        if(len(G3neg_input_text)<4):
            body = json.dumps({
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": G3input_text,
                    "conditionImage": G3input_image,
                    "controlMode": G3control_mode,
                },
                "imageGenerationConfig": {
                    "numberOfImages": G3number_of_images,
                    "quality": G3quality,
                    "cfgScale": G3cfg_scale,
                    "height": G3height,
                    "width": G3width,
                    "seed": G3seed
                }
            })

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap


        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")


    ## ---------- Image Variation
    def TitanG2ImageVariation(self):
        G3control_mode = "IMAGE_VARIATION"  

        G3input_text = self.tab4_prompt_edit.toPlainText()
        G3neg_input_text = self.tab4_neg_prompt_edit.toPlainText()
        G3number_of_images = int(self.ui_gset_number_of_images.text())
        G3quality = self.ui_gset_quality.text().strip().lower()
        G3cfg_scale = float(self.gset_cfgScale.text())
        G3width = int(self.ui_gset_width.text())
        G3height = int(self.ui_gset_height.text())
        G3seed = int(self.ui_gset_seed.text())

        G3similarity_strength = float(self.ui_tab4_similarity.text())

        while G3input_text.startswith("\n"):
            G3input_text = G3input_text[1:]

        modelId = 'amazon.titan-image-generator-v2:0'

        # Read image from file and encode it as base64 string
        # with open(G3condition_image_path, "rb") as image_file:
        #    G3input_image = base64.b64encode(image_file.read()).decode('utf8')

        # Extract the image from the left QGraphicsView
        pixmap = self.left_scene.items()[0].pixmap()  # Assuming there's only one item in the scene
        image = pixmap.toImage()

        # Convert the QImage to a byte array
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        G3input_image = buffer.data().toBase64().data().decode('utf8')

        body = json.dumps({
            "taskType": "IMAGE_VARIATION",
            "imageVariationParams": {
                "text": G3input_text,
                "negativeText": G3neg_input_text,
                "images": [G3input_image],
                "similarityStrength": G3similarity_strength,
            },
            "imageGenerationConfig": {
                "numberOfImages": G3number_of_images,
                "cfgScale": G3cfg_scale,
                "height": G3height,
                "width": G3width,
                #"seed": G3seed
            }
        })

        if(len(G3neg_input_text)<4):
            body = json.dumps({
                "taskType": "IMAGE_VARIATION",
                "imageVariationParams": {
                    "text": G3input_text,
                    "images": [G3input_image],
                    "similarityStrength": G3similarity_strength,
                },
                "imageGenerationConfig": {
                    "numberOfImages": G3number_of_images,
                    "cfgScale": G3cfg_scale,
                    "height": G3height,
                    "width": G3width,
                    #"seed": G3seed
                }
            })

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")
    ## ---------- Image Variation

    ## ---------- Background Removal
    def RemoveBackG2Titan(self):
        G3control_mode = "BACKGROUND_REMOVAL" 

        G3input_text = self.tab3_prompt_edit.toPlainText()

        while G3input_text.startswith("\n"):
            G3input_text = G3input_text[1:]

        modelId = 'amazon.titan-image-generator-v2:0'

        if not self.left_scene.items():  # Check if the scene is empty
            QMessageBox.warning(None, "Warning", "The input image view is empty. Please load an image before proceeding.")
            return

        # Extract the image from the left QGraphicsView
        pixmap = self.left_scene.items()[0].pixmap()  # Assuming there's only one item in the scene
        image = pixmap.toImage()

        # Convert the QImage to a byte array
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        G3input_image = buffer.data().toBase64().data().decode('utf8')

        body = json.dumps({
            "taskType": "BACKGROUND_REMOVAL",
            "backgroundRemovalParams": {
                "image": G3input_image,
            }
        })

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")



        '''
        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            pixmap = QPixmap.fromImage(image)
            self.right_scene.clear()  # Clear the previous image
            self.right_scene.addPixmap(pixmap)
            self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")
        '''

    ## ------------------ RIGHT Reference Color Generator
    def ColorGen(self):
        G3input_text = self.right_prompt_edit.toPlainText()
        G3neg_input_text = self.right_neg_prompt_edit.toPlainText()
        G3number_of_images = int(self.ui_right_number_of_images.text())
        G3quality = self.ui_right_quality.text().strip().lower()
        G3cfg_scale = float(self.right_cfgScale.text())
        G3width = int(self.ui_right_width.text())
        G3height = int(self.ui_right_height.text())
        G3seed = int(self.ui_right_seed.text())
        # G3control_mode = "COLOR_GUIDED_GENERATION" 
        # G3color = self.ui_left_colors.text()
        G3color = self.process_colors_right() # Hex code colors are on the left. And the reference image is on the left.
        # print("G3color",G3color)

        while G3input_text.startswith("\n"):
            G3input_text = G3input_text[1:]

        modelId = 'amazon.titan-image-generator-v2:0'

        # Hex Color does not use a source image for colors
        G3input_image = None

        # 1. Whether there is negative text present or not
        # 2. Whether there is a reference image in left or not
        # 3. Whether there are hex codes present or not.
        # Flags
        flagNeg = 0 if len(G3neg_input_text) < 3 else 1
        flagHex = 0 if not G3color else 1
        flagImg = 0 if G3input_image is None else 1

        print("flagNeg",flagNeg)
        print("G3color",type(G3color),G3color)
        print("flagHex",flagHex)
        print("flagImg",flagImg)
        print("\n\n")
        
        body_dict = {
            "taskType": "COLOR_GUIDED_GENERATION",
            "colorGuidedGenerationParams": {},
            "imageGenerationConfig": {
                "numberOfImages": G3number_of_images,
                "quality": G3quality,
                "cfgScale": G3cfg_scale,
                "height": G3height,
                "width": G3width,
                "seed": G3seed
            }
        }
        # Always include text
        body_dict["colorGuidedGenerationParams"]["text"] = G3input_text
        # Conditionally add negativeText if flagNeg is set
        if flagNeg:
            body_dict["colorGuidedGenerationParams"]["negativeText"] = G3neg_input_text
        # Conditionally add colors if flagHex is set
        if flagHex:
            body_dict["colorGuidedGenerationParams"]["colors"] = G3color
        # Conditionally add referenceImage if flagImg is set
        if flagImg:
            body_dict["colorGuidedGenerationParams"]["referenceImage"] = G3input_image
        # Convert the dictionary to a JSON string
        body = json.dumps(body_dict)

        accept = 'application/json'
        contentType = 'application/json'

        try:
            # Call the Bedrock API
            response = self.clients['bedrun'].invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response["body"].read())
            base64_image_data = response_body["images"][0]

            # Convert base64 image to QImage and then to QPixmap
            #image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            #pixmap = QPixmap.fromImage(image)
            #self.right_scene.clear()  # Clear the previous image
            #self.right_scene.addPixmap(pixmap)
            #self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

            # Process the images returned from the Bedrock API
            for i in range(5):  # Loop over the possible images (0-4)
                if i < len(response_body["images"]):  # Check if the image exists
                    base64_image_data = response_body["images"][i]

                    # Convert base64 image to QImage and then to QPixmap
                    image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
                    pixmap = QPixmap.fromImage(image)

                    if i == 0:
                        # Display the first image [0] in the viewer
                        self.right_scene.clear()  # Clear the previous image
                        self.right_scene.addPixmap(pixmap)
                        self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.right_image_storage[i] = pixmap
                    else:
                        # Store additional images [1] through [4] in storage
                        self.right_image_storage[i] = pixmap

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G3 model: {str(e)}")


    # -----------------------[ Right Color Palette ]---------------
    #

    def tab2ShowColorPopup(self):
        # Creating a placeholder for selected colors
        selected_colors = []

        # Function to handle color selection
        def select_color():
            color = QColorDialog.getColor()
            if color.isValid():
                hex_color = color.name()  # Automatically includes the '#'
                selected_colors.append(hex_color)
                print(f'Selected color: {hex_color}')  # For debugging/visibility

        # Directly open the color dialog without showing a menu
        select_color()

        # Join the selected colors with spaces and append them to the existing text
        selected_colors_string = ' '.join(selected_colors)
        current_text = self.ui_tab2_colors.text().strip()

        if current_text:
            # Append selected colors to the existing text
            new_text = f"{current_text} {selected_colors_string}"
        else:
            # If the QLineEdit is empty, just use the selected colors
            new_text = selected_colors_string

        # Set the updated text back to the QLineEdit
        self.ui_tab2_colors.setText(new_text)

        print(f'Updated Colors in QLineEdit: {new_text}')  # For debugging/visibility

        return new_text

    # -----------------------[ Left Color Palette ]---------------
    #

    def leftShowColorPopup(self):
        # Creating a placeholder for selected colors
        selected_colors = []

        # Function to handle color selection
        def select_color():
            color = QColorDialog.getColor()
            if color.isValid():
                hex_color = color.name()  # Automatically includes the '#'
                selected_colors.append(hex_color)
                print(f'Selected color: {hex_color}')  # For debugging/visibility

        # Directly open the color dialog without showing a menu
        select_color()

        # Join the selected colors with spaces and append them to the existing text
        selected_colors_string = ' '.join(selected_colors)
        current_text = self.ui_left_colors.text().strip()

        if current_text:
            # Append selected colors to the existing text
            new_text = f"{current_text} {selected_colors_string}"
        else:
            # If the QLineEdit is empty, just use the selected colors
            new_text = selected_colors_string

        # Set the updated text back to the QLineEdit
        self.ui_left_colors.setText(new_text)

        print(f'Updated Colors in QLineEdit: {new_text}')  # For debugging/visibility

        return new_text
    

    def process_colors_left(self):
        # Get the text from the QLineEdit widget
        color_text = self.ui_left_colors.text().strip()

        # If the color_text is empty, return an empty list
        if not color_text:
            return []

        # Split the input text by spaces, commas, or semicolons
        raw_colors = re.split(r'[ ,;]+', color_text)

        # Process each color: ensure it starts with a '#' and has exactly 6 hex digits
        valid_colors = []
        for color in raw_colors:
            # Strip any leading or trailing whitespace
            color = color.strip()
            
            # Ensure the color has 6 hex digits
            if len(color) == 6 and all(c in "0123456789ABCDEFabcdef" for c in color):
                color = '#' + color  # Add '#' if it's not present
            elif len(color) == 7 and color.startswith('#') and all(c in "0123456789ABCDEFabcdef" for c in color[1:]):
                pass  # The color is already valid with '#'
            else:
                continue  # Skip invalid entries

            valid_colors.append(color)

        return valid_colors  # Return as a list

    '''
    def process_colors_right(self):
        # Get the text from the QLineEdit widget
        color_text = self.ui_right_colors.text().strip()

        # If the color_text is empty, return an empty list
        if not color_text:
            return []

        # Split the input text by spaces, commas, or semicolons
        raw_colors = re.split(r'[ ,;]+', color_text)

        # Process each color: ensure it starts with a '#' and has exactly 6 hex digits
        valid_colors = []
        for color in raw_colors:
            # Strip any leading or trailing whitespace
            color = color.strip()
            
            # Ensure the color has 6 hex digits
            if len(color) == 6 and all(c in "0123456789ABCDEFabcdef" for c in color):
                color = '#' + color  # Add '#' if it's not present
            elif len(color) == 7 and color.startswith('#') and all(c in "0123456789ABCDEFabcdef" for c in color[1:]):
                pass  # The color is already valid with '#'
            else:
                continue  # Skip invalid entries

            valid_colors.append(color)

        return valid_colors  # Return as a list
        '''


## --------------------- Image Conditioning -------------------------
##
##
#	"taskType": "TEXT_IMAGE",#
#	"textToImageParams": {
# 		"text": "a cartoon deer in a fairy world.",
#        "conditionImage": input_image, # Optional
#        "controlMode": "CANNY_EDGE" # Optional: CANNY_EDGE | SEGMENTATION
#        "controlStrength": 0.7 # Optional: weight given to the condition image. Default: 0.7
#     }


    '''
    def rightTitanG1Image(self):
        params = self.fetch_parameters('Titan G2')
        input_text = "A bunny."
        #input_text = self.process_comments(input_text)
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

            # Convert base64 image to QImage and then to QPixmap
            image = QImage.fromData(QByteArray.fromBase64(base64_image_data.encode()))
            pixmap = QPixmap.fromImage(image)
            self.right_scene.clear()  # Clear the previous image
            self.right_scene.addPixmap(pixmap)
            self.right_view.fitInView(self.right_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error invoking Titan G2 model: {str(e)}")

    def rightStabilityImage(self):
        pass

    '''

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

####################################### ###################### ###################### ######################
## ----------------------------- Titan G2 Image Manipulation Tool

'''
    ### -----------------    
class G2ImgTool:
    def __init__(self):
        # Create the main window
        self.window = QMainWindow()
        self.window.setWindowTitle("Ascend GenAI Image Forge")
        self.window.resize(1200, 600)

        # Create the central widget
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)

        # Create the main layout
        self.main_layout = QVBoxLayout(central_widget)

        # Create a horizontal layout for the image views
        self.image_layout = QHBoxLayout()
        self.control_layout = QHBoxLayout()  # The first row horizontal buttons 
        self.button_layout = QHBoxLayout()
        self.control_b_layout = QHBoxLayout()  # The last row horizontal buttons 

        # Create the two image views (left and right)
        self.left_image_view = QGraphicsView()
        self.right_image_view = QGraphicsView()

        # Create scenes for each image view
        self.left_scene = QGraphicsScene()
        self.right_scene = QGraphicsScene()

        # Assign the scenes to the image views
        self.left_image_view.setScene(self.left_scene)
        self.right_image_view.setScene(self.right_scene)

        # Add the image views to the horizontal layout
        self.image_layout.addWidget(self.left_image_view)
        self.image_layout.addWidget(self.right_image_view)

        # Add the image layout to the main layout
        self.main_layout.addLayout(self.image_layout)
        self.main_layout.addLayout(self.control_layout)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.control_b_layout)

        # Example button
        ctl_01 = QPushButton("Open")
        ctl_01.setToolTip("Load an image into the left view.")
        ctl_01.setFixedSize(100, 30)  # Example size
        ctl_01.setStyleSheet("background-color: #D3D3D3;")  # Example style
        self.control_layout.addWidget(ctl_01)
        ctl_01.clicked.connect(self.load_left)  # Connect button to method

    def load_left(self):
        # Example of adding an image to the left scene
        pixmap = QPixmap('path/to/your/image.png')  # Replace with actual image path
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.left_scene.addItem(pixmap_item)
        self.left_image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)

    def show(self):
        self.window.show()


    ### -----------------    
    
    def XYG2ImgTool(self,clients):
        # Create the main window
        self.window = QMainWindow()
        self.window.setWindowTitle("Ascend GenAI Image Forge")
        self.window.resize(1200, 600)
        # Create the central widget
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        # Create the main layout
        main_layout = QVBoxLayout(central_widget)
        # Create a horizontal layout for the image views
        image_layout = QHBoxLayout()
        control_layout = QHBoxLayout() # The first row horizontal buttons 
        button_layout = QHBoxLayout()
        control_b_layout = QHBoxLayout() # The last row horizontal buttons 

        # Create the two image views (left and right)
        left_image_view = QGraphicsView()
        right_image_view = QGraphicsView()
        # Add the image views to the horizontal layout
        #image_layout.addWidget(self.left_image_view)
        #image_layout.addWidget(self.right_image_view)

        # Create scenes for each image view
        left_scene = QGraphicsScene()
        right_scene = QGraphicsScene()
    
        # Assign the scenes to the image views
        left_image_view.setScene(left_scene)
        right_image_view.setScene(right_scene)
    
        # Add the image views to the horizontal layout
        image_layout.addWidget(left_image_view)
        image_layout.addWidget(right_image_view)


        # Add the image layout to the main layout
        main_layout.addLayout(image_layout)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(control_b_layout)
 
        vSpace = 2
        button_layout_1 = QVBoxLayout()  
        button_layout_1.setSpacing(vSpace)
        button_layout_2 = QVBoxLayout()
        button_layout_2.setSpacing(vSpace)
        button_layout_3 = QVBoxLayout()
        button_layout_3.setSpacing(vSpace)
        button_layout_4 = QVBoxLayout()
        button_layout_4.setSpacing(vSpace)
        button_layout_5 = QVBoxLayout()
        button_layout_5.setSpacing(vSpace)
        button_layout_6 = QVBoxLayout()
        button_layout_6.setSpacing(vSpace)
        button_layout.setSpacing(vSpace)

        button_layout.addLayout(button_layout_1)
        button_layout.addLayout(button_layout_2)
        button_layout.addLayout(button_layout_3)
        button_layout.addLayout(button_layout_4)
        button_layout.addLayout(button_layout_5)
        button_layout.addLayout(button_layout_6)

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
            font-size: 12px;    
            font-weight: normal;  
            font-style: normal;  
            border: 2px solid #222222;
            border-radius: 5px;
            }
            QPushButton:hover { background-color: #22DEEE; }
            QPushButton:pressed { background-color: #000000; color: #FFFFFF; }
        """



       # Control Buttons
        cW = 85
        cH = 20 

        ctl_01 = QPushButton("Open")
        ctl_01.setToolTip("Increase font size.")
        ctl_01.setFixedSize(cW,cH)
        ctl_01.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_01)
        ctl_01.clicked.connect(self.load_left) # load_left

        ctl_02 = QPushButton("Save")
        ctl_02.setToolTip("Increase font size.")
        ctl_02.setFixedSize(cW,cH)
        ctl_02.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_02)
        #ctl_02.clicked.connect(self.some_method) 

        ctl_03 = QPushButton("Clear")
        ctl_03.setToolTip("Increase font size.")
        ctl_03.setFixedSize(cW,cH)
        ctl_03.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_03)
        #ctl_03.clicked.connect(self.some_method) 

        ctl_04 = QPushButton(" ")
        ctl_04.setToolTip("Increase font size.")
        ctl_04.setFixedSize(cW,cH)
        ctl_04.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_04)
        #ctl_04.clicked.connect(self.some_method) 

        ctl_05 = QPushButton("Open")
        ctl_05.setToolTip("Increase font size.")
        ctl_05.setFixedSize(cW,cH)
        ctl_05.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_05)
        #ctl_05.clicked.connect(self.some_method) 

        ctl_06 = QPushButton("Save")
        ctl_06.setToolTip("Increase font size.")
        ctl_06.setFixedSize(cW,cH)
        ctl_06.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_06)
        #ctl_06.clicked.connect(self.some_method) 

        ctl_07 = QPushButton("Clear")
        ctl_07.setToolTip("Increase font size.")
        ctl_07.setFixedSize(cW,cH)
        ctl_07.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_07)
        #ctl_07.clicked.connect(self.some_method) 

        ctl_08 = QPushButton(" ")
        ctl_08.setToolTip("Increase font size.")
        ctl_08.setFixedSize(cW,cH)
        ctl_08.setStyleSheet(self.buttonStyle_1)
        control_layout.addWidget(ctl_08)
        #ctl_08.clicked.connect(self.some_method) 

        # Feature Buttons [6 columns (first digit)] x [6 rows (second digit)]
        # Control Buttons
        bW = 85
        bH = 20


        ## Button Layout 1 
        #
        btn_11 = QPushButton("Feature 1-1")
        btn_11.setToolTip("Increase font size.")
        btn_11.setFixedSize(bW,bH)
        btn_11.setStyleSheet(self.buttonStyle_5)
        button_layout_1.addWidget(btn_11)
        #btn_11.clicked.connect(self.some_method)

        btn_12 = QPushButton("Feature 1-2")
        btn_12.setToolTip("Increase font size.")
        btn_12.setFixedSize(bW,bH)
        btn_12.setStyleSheet(self.buttonStyle_5)
        button_layout_1.addWidget(btn_12)
        #btn_12.clicked.connect(self.some_method)

        btn_13 = QPushButton("Feature 1-3")
        btn_13.setToolTip("Increase font size.")
        btn_13.setFixedSize(bW,bH)
        btn_13.setStyleSheet(self.buttonStyle_5)
        button_layout_1.addWidget(btn_13)
        #btn_13.clicked.connect(self.some_method)

        btn_14 = QPushButton("Feature 1-4")
        btn_14.setToolTip("Increase font size.")
        btn_14.setFixedSize(bW,bH)
        btn_14.setStyleSheet(self.buttonStyle_5)
        button_layout_1.addWidget(btn_14)
        #btn_14.clicked.connect(self.some_method)

        btn_15 = QPushButton("Feature 1-5")
        btn_15.setToolTip("Increase font size.")
        btn_15.setFixedSize(bW,bH)
        btn_15.setStyleSheet(self.buttonStyle_5)
        button_layout_1.addWidget(btn_15)
        #btn_15.clicked.connect(self.some_method)

        btn_16 = QPushButton("Feature 1-6")
        btn_16.setToolTip("Increase font size.")
        btn_16.setFixedSize(bW,bH)
        btn_16.setStyleSheet(self.buttonStyle_5)
        button_layout_1.addWidget(btn_16)
        #btn1_16.clicked.connect(self.some_method)

        ## Button Layout 2 
        #
        btn_21 = QPushButton("Feature 2-1")
        btn_21.setToolTip("Increase font size.")
        btn_21.setFixedSize(bW,bH)
        btn_21.setStyleSheet(self.buttonStyle_5)
        button_layout_2.addWidget(btn_21)
        #btn_21.clicked.connect(self.some_method)

        btn_22 = QPushButton("Feature 2-2")
        btn_22.setToolTip("Increase font size.")
        btn_22.setFixedSize(bW,bH)
        btn_22.setStyleSheet(self.buttonStyle_5)
        button_layout_2.addWidget(btn_22)
        #btn_22.clicked.connect(self.some_method)

        btn_23 = QPushButton("Feature 2-3")
        btn_23.setToolTip("Increase font size.")
        btn_23.setFixedSize(bW,bH)
        btn_23.setStyleSheet(self.buttonStyle_5)
        button_layout_2.addWidget(btn_23)
        #btn_23.clicked.connect(self.some_method)

        btn_24 = QPushButton("Feature 2-4")
        btn_24.setToolTip("Increase font size.")
        btn_24.setFixedSize(bW,bH)
        btn_24.setStyleSheet(self.buttonStyle_5)
        button_layout_2.addWidget(btn_24)
        #btn_24.clicked.connect(self.some_method)

        btn_25 = QPushButton("Feature 2-5")
        btn_25.setToolTip("Increase font size.")
        btn_25.setFixedSize(bW,bH)
        btn_25.setStyleSheet(self.buttonStyle_5)
        button_layout_2.addWidget(btn_25)
        #btn_25.clicked.connect(self.some_method)

        btn_26 = QPushButton("Feature 2-6")
        btn_26.setToolTip("Increase font size.")
        btn_26.setFixedSize(bW,bH)
        btn_26.setStyleSheet(self.buttonStyle_5)
        button_layout_2.addWidget(btn_26)
        #btn_26.clicked.connect(self.some_method)

        ## Button Layout 3 
        #
        btn_31 = QPushButton("Feature 3-1")
        btn_31.setToolTip("Increase font size.")
        btn_31.setFixedSize(bW,bH)
        btn_31.setStyleSheet(self.buttonStyle_5)
        button_layout_3.addWidget(btn_31)
        #btn_31.clicked.connect(self.some_method)

        btn_32 = QPushButton("Feature 3-2")
        btn_32.setToolTip("Increase font size.")
        btn_32.setFixedSize(bW,bH)
        btn_32.setStyleSheet(self.buttonStyle_5)
        button_layout_3.addWidget(btn_32)
        #btn_32.clicked.connect(self.some_method)

        btn_33 = QPushButton("Feature 3-3")
        btn_33.setToolTip("Increase font size.")
        btn_33.setFixedSize(bW,bH)
        btn_33.setStyleSheet(self.buttonStyle_5)
        button_layout_3.addWidget(btn_33)
        #btn_33.clicked.connect(self.some_method)

        btn_34 = QPushButton("Feature 3-4")
        btn_34.setToolTip("Increase font size.")
        btn_34.setFixedSize(bW,bH)
        btn_34.setStyleSheet(self.buttonStyle_5)
        button_layout_3.addWidget(btn_34)
        #btn_34.clicked.connect(self.some_method)

        btn_35 = QPushButton("Feature 3-5")
        btn_35.setToolTip("Increase font size.")
        btn_35.setFixedSize(bW,bH)
        btn_35.setStyleSheet(self.buttonStyle_5)
        button_layout_3.addWidget(btn_35)
        #btn_35.clicked.connect(self.some_method)

        btn_36 = QPushButton("Feature 3-6")
        btn_36.setToolTip("Increase font size.")
        btn_36.setFixedSize(bW,bH)
        btn_36.setStyleSheet(self.buttonStyle_5)
        button_layout_3.addWidget(btn_36)
        #btn_36.clicked.connect(self.some_method)

        ## Button Layout 4 
        #
        btn_41 = QPushButton("Feature 4-1")
        btn_41.setToolTip("Increase font size.")
        btn_41.setFixedSize(bW,bH)
        btn_41.setStyleSheet(self.buttonStyle_5)
        button_layout_4.addWidget(btn_41)
        #btn_41.clicked.connect(self.some_method)

        btn_42 = QPushButton("Feature 4-2")
        btn_42.setToolTip("Increase font size.")
        btn_42.setFixedSize(bW,bH)
        btn_42.setStyleSheet(self.buttonStyle_5)
        button_layout_4.addWidget(btn_42)
        #btn_42.clicked.connect(self.some_method)

        btn_43 = QPushButton("Feature 4-3")
        btn_43.setToolTip("Increase font size.")
        btn_43.setFixedSize(bW,bH)
        btn_43.setStyleSheet(self.buttonStyle_5)
        button_layout_4.addWidget(btn_43)
        #btn_43.clicked.connect(self.some_method)

        btn_44 = QPushButton("Feature 4-4")
        btn_44.setToolTip("Increase font size.")
        btn_44.setFixedSize(bW,bH)
        btn_44.setStyleSheet(self.buttonStyle_5)
        button_layout_4.addWidget(btn_44)
        #btn_44.clicked.connect(self.some_method)

        btn_45 = QPushButton("Feature 4-5")
        btn_45.setToolTip("Increase font size.")
        btn_45.setFixedSize(bW,bH)
        btn_45.setStyleSheet(self.buttonStyle_5)
        button_layout_4.addWidget(btn_45)
        #btn_45.clicked.connect(self.some_method)

        btn_46 = QPushButton("Feature 4-6")
        btn_46.setToolTip("Increase font size.")
        btn_46.setFixedSize(bW,bH)
        btn_46.setStyleSheet(self.buttonStyle_5)
        button_layout_4.addWidget(btn_46)
        #btn_46.clicked.connect(self.some_method)

        ## Button Layout 5 
        #
        btn_51 = QPushButton("Feature 5-1")
        btn_51.setToolTip("Increase font size.")
        btn_51.setFixedSize(bW,bH)
        btn_51.setStyleSheet(self.buttonStyle_5)
        button_layout_5.addWidget(btn_51)
        #btn_51.clicked.connect(self.some_method)

        btn_52 = QPushButton("Feature 5-2")
        btn_52.setToolTip("Increase font size.")
        btn_52.setFixedSize(bW,bH)
        btn_52.setStyleSheet(self.buttonStyle_5)
        button_layout_5.addWidget(btn_52)
        #btn_52.clicked.connect(self.some_method)

        btn_53 = QPushButton("Feature 5-3")
        btn_53.setToolTip("Increase font size.")
        btn_53.setFixedSize(bW,bH)
        btn_53.setStyleSheet(self.buttonStyle_5)
        button_layout_5.addWidget(btn_53)
        #btn_53.clicked.connect(self.some_method)

        btn_54 = QPushButton("Feature 5-4")
        btn_54.setToolTip("Increase font size.")
        btn_54.setFixedSize(bW,bH)
        btn_54.setStyleSheet(self.buttonStyle_5)
        button_layout_5.addWidget(btn_54)
        #btn_54.clicked.connect(self.some_method)

        btn_55 = QPushButton("Feature 5-5")
        btn_55.setToolTip("Increase font size.")
        btn_55.setFixedSize(bW,bH)
        btn_55.setStyleSheet(self.buttonStyle_5)
        button_layout_5.addWidget(btn_55)
        #btn_55.clicked.connect(self.some_method)

        btn_56 = QPushButton("Feature 5-6")
        btn_56.setToolTip("Increase font size.")
        btn_56.setFixedSize(bW,bH)
        btn_56.setStyleSheet(self.buttonStyle_5)
        button_layout_5.addWidget(btn_56)
        #btn_56.clicked.connect(self.some_method)

        ## Button Layout 6 
        #
        btn_61 = QPushButton("Feature 6-1")
        btn_61.setToolTip("Increase font size.")
        btn_61.setFixedSize(bW,bH)
        btn_61.setStyleSheet(self.buttonStyle_5)
        button_layout_6.addWidget(btn_61)
        #btn_61.clicked.connect(self.some_method)

        btn_62 = QPushButton("Feature 6-2")
        btn_62.setToolTip("Increase font size.")
        btn_62.setFixedSize(bW,bH)
        btn_62.setStyleSheet(self.buttonStyle_5)
        button_layout_6.addWidget(btn_62)
        #btn_62.clicked.connect(self.some_method)

        btn_63 = QPushButton("Feature 6-3")
        btn_63.setToolTip("Increase font size.")
        btn_63.setFixedSize(bW,bH)
        btn_63.setStyleSheet(self.buttonStyle_5)
        button_layout_6.addWidget(btn_63)
        #btn_63.clicked.connect(self.some_method)

        btn_64 = QPushButton("Feature 6-4")
        btn_64.setToolTip("Increase font size.")
        btn_64.setFixedSize(bW,bH)
        btn_64.setStyleSheet(self.buttonStyle_5)
        button_layout_6.addWidget(btn_64)
        #btn_64.clicked.connect(self.some_method)

        btn_65 = QPushButton("Feature 6-5")
        btn_65.setToolTip("Increase font size.")
        btn_65.setFixedSize(bW,bH)
        btn_65.setStyleSheet(self.buttonStyle_5)
        button_layout_6.addWidget(btn_65)
        #btn_65.clicked.connect(self.some_method)

        btn_66 = QPushButton("Feature 6-6")
        btn_66.setToolTip("Increase font size.")
        btn_66.setFixedSize(bW,bH)
        btn_66.setStyleSheet(self.buttonStyle_5)
        button_layout_6.addWidget(btn_66)
        #btn_66.clicked.connect(self.some_method)

# Control Bottom Buttons
        cW = 85
        cH = 20

        ctlb_01 = QPushButton("Control 1")
        ctlb_01.setToolTip("Increase font size.")
        ctlb_01.setFixedSize(cW,cH)
        ctlb_01.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_01)
        #ctlb_01.clicked.connect(self.some_method) 

        ctlb_02 = QPushButton("Control 2")
        ctlb_02.setToolTip("Increase font size.")
        ctlb_02.setFixedSize(cW,cH)
        ctlb_02.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_02)
        #ctl_02.clicked.connect(self.some_method) 

        ctlb_03 = QPushButton("Control 3")
        ctlb_03.setToolTip("Increase font size.")
        ctlb_03.setFixedSize(cW,cH)
        ctlb_03.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_03)
        #ctl_03.clicked.connect(self.some_method) 

        ctlb_04 = QPushButton("Control 4")
        ctlb_04.setToolTip("Increase font size.")
        ctlb_04.setFixedSize(cW,cH)
        ctlb_04.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_04)
        #ctlb_04.clicked.connect(self.some_method) 

        ctlb_05 = QPushButton("Control 5")
        ctlb_05.setToolTip("Increase font size.")
        ctlb_05.setFixedSize(cW,cH)
        ctlb_05.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_05)
        #ctlb_05.clicked.connect(self.some_method) 

        ctlb_06 = QPushButton("Control 6")
        ctlb_06.setToolTip("Increase font size.")
        ctlb_06.setFixedSize(cW,cH)
        ctlb_06.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_06)
        #ctlb_06.clicked.connect(self.some_method) 

        ctlb_07 = QPushButton("Submit")
        ctlb_07.setToolTip("Increase font size.")
        ctlb_07.setFixedSize(cW,cH)
        ctlb_07.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_07)
        #ctl_07.clicked.connect(self.some_method) 

        ctlb_08 = QPushButton("Done")
        ctlb_08.setToolTip("Increase font size.")
        ctlb_08.setFixedSize(cW,cH)
        ctlb_08.setStyleSheet(self.buttonStyle_1)
        control_b_layout.addWidget(ctlb_08)
        ctlb_08.clicked.connect(self.window.close) 

        # Connect the Done button to close the window
        #done_button.clicked.connect(self.window.close)

        # Show the window
        self.window.show()

        ## --- image methods

        def load_left(self):   
            # Example of adding an image to the left scene
            pixmap = QPixmap('path/to/your/image.png')
            pixmap_item = QGraphicsPixmapItem(pixmap)
            left_scene.addItem(pixmap_item)
    
    # Fit the image to the view
    left_image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)
    
    def XXG2ImgTool(self,clients):
        pass 
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
##
            
'''