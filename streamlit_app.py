import os
import json
import streamlit as st
from PIL import Image

import glob  # Import glob module

st.set_page_config(
    layout="wide"
    )

# Set the path to the output_figures directory
output_figures_path = "output_figures"

# Get a list of book folders
book_folders = [folder for folder in os.listdir(output_figures_path) if os.path.isdir(os.path.join(output_figures_path, folder))]

# Sort the book folders alphabetically
book_folders.sort()

# Iterate over each book folder
for book_folder in book_folders:
    # Create a top-level header for the book

    try: 
        st.markdown(f"## {book_folder}")
        
        # Load the JSON file for the current book
        json_file = os.path.join(output_figures_path, book_folder, f"{book_folder}_figure_list.json")
        try:
            with open(json_file, "r") as file:
                figure_list = json.load(file)
        except FileNotFoundError:
            # If the specific JSON file is not found, load any JSON file in the folder
            json_files = glob.glob(os.path.join(output_figures_path, book_folder, "*.json"))
            if json_files:  # Check if there is at least one JSON file
                with open(json_files[0], "r") as file:  # Open the first JSON file found
                    figure_list = json.load(file)
            else:
                st.error(f"No JSON files found in {book_folder}.")
                continue  # Skip this iteration if no JSON files are found
        
        # Create 5 columns for displaying the images
        cols = st.columns(4)
        
        # Iterate over each figure in the JSON file
        for i, figure in enumerate(figure_list):
            # Get the image file path
            try: 
                image_file = os.path.join(output_figures_path, book_folder, "diagrams", figure["image_name"] + ".png")
                
                # Open the image using PIL
                image = Image.open(image_file)
                
                # Display the image in the corresponding column
                cols[i % 5].image(image, caption=figure["image_name"], use_column_width=True)
                
                # Display the image caption and descriptions
                cols[i % 5].write(figure["image_caption"])
                cols[i % 5].write(figure["image_descriptions"])
            except FileNotFoundError:
                print(f"Image file not found: {figure['image_name']}.")
                continue

    except Exception as e:
        print(f"An error occurred while processing {book_folder}: {e}")
        continue
