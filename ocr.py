import tkinter as tk
from tkinter import filedialog as fd
import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import pandas as pd
import re


def extract_debit_notes(tesseract_output):
    # Create DataFrame
    df = pd.DataFrame(tesseract_output)
    print(df)

    # Get only words with good confidence
    words = df[(df['level'] == 5)].copy()
    print(words)

    # Sort by position
    words = words.sort_values(['top', 'left'])
    print(words)
    # Group into rows (every ~30 pixels)
    for word in words['text']:
        print(word)

    return df


def image_to_excel():
    # Select file
    root = tk.Tk()
    root.withdraw()
    file_paths = fd.askopenfilenames(
        title="Select image files",
        filetypes=[("Image files", "*.jpeg *.jpg *.png")]
    )
    root.destroy()

    if not file_paths:
        print("No files selected")
        return

    for file_path in file_paths:
        img = cv2.imread(file_path)
        tesseract_output = pytesseract.image_to_data(img, config='--psm 11', output_type=pytesseract.Output.DICT)
        debit_notes = extract_debit_notes(tesseract_output)
        print(debit_notes)


# Run
image_to_excel()