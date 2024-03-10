import os
import re
import json
import sys
from pprint import pprint 
from collections import defaultdict
from dotenv import load_dotenv
import requests
import fitz  # PyMuPDF

load_dotenv()

#################### CONFIG ####################

NUM_ADDITIONAL_ELEMENTS_TO_LOOK_FOR_CAPTIONS = 7

def get_element_json_from_pdf(file_filename):
    UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
    url = "https://api.upstage.ai/v1/document-ai/layout-analyzer"

    headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
    files = {"document": open(file_filename, "rb")}
    response = requests.post(url, headers=headers, files=files)
    return response.json()

def crop_and_save_image(input_pdf, output_filepath, page, coords):
    """
    # Example usage
    # crop_and_save_image("sample_data/Attention3pg.pdf", "output/attention3pg-1image-output-test.png", 1, [{'x': 808, 'y': 297}, {'x': 1743, 'y': 297}, {'x': 1743, 'y': 1652}, {'x': 808, 'y': 1652}])
    """
    # Open the PDF file
    pdf_document = fitz.open(input_pdf)
    page = pdf_document[page - 1]  # Adjusted to use 0-based index

    # Calculate the rectangle area to crop using the provided coordinates
    x_values = [0.24 * coord['x'] for coord in coords]
    y_values = [0.24 * coord['y'] for coord in coords]
    x0 = min(x_values)
    x1 = max(x_values)
    y0 = min(y_values)
    y1 = max(y_values)

    # Define the rectangle area to crop
    rect = fitz.Rect(x0, y0, x1, y1)

    # Crop the page to the defined rectangle
    pix = page.get_pixmap(clip=rect, dpi=350)

    # Save the cropped image
    pix.save(output_filepath)
    pdf_document.close()
    return output_filepath

############################################################
### Base classes 
class Figure:
    def __init__(self, original_doc_filepath, image_name, image_caption, image_descriptions, page_number, image_coordinates, html, element_id, FigureListObj):
        self.original_doc_filepath = original_doc_filepath
        self.image_name = image_name
        self.image_caption = image_caption
        self.image_descriptions = [image_descriptions] if image_descriptions else []
        self.page_number = page_number
        self.image_coordinates = image_coordinates
        self.html = html
        self.element_id = element_id
        self.FigureListObj = FigureListObj

    def __dict__(self):
        return {
            "original_doc_filepath": self.original_doc_filepath,
            "image_name": self.image_name,
            "image_caption": self.image_caption,
            "image_descriptions": self.image_descriptions,
            "page_number": self.page_number,
            "image_coordinates": self.image_coordinates,
            "html": self.html,
            "element_id": self.element_id
        }

    def create_image_caption(self, caption):
        self.image_caption = caption

    def set_figure_name(self, name):
        # Replace periods with hyphens in the figure name
        name = name.replace(".", "-")
        self.image_name = name

    def add_image_descriptions(self, description):
        self.image_descriptions.append(description)

    def save_image_from_page_coordinates(self, output_filepath):
        success = crop_and_save_image(self.original_doc_filepath, output_filepath, self.page_number, self.image_coordinates)
        return success
        
class FigureList:
    def __init__(self):
        self.figures = []
        self.figure_names = defaultdict(int)  # Tracks the count of each figure name

    def add_figure(self, figure):
        # print(figure.image_name)
        base_name = figure.image_name
        # print(self.figure_names[base_name])
        if self.figure_names[base_name] > 0:
            print(f"Figure name {base_name} already exists")
            # If the figure name already exists, append a number to make it unique 
            figure.set_figure_name(f"{base_name} ({self.figure_names[base_name]})")
        self.figures.append(figure)
        # Increment the count for this base name
        self.figure_names[base_name] += 1

    def get_figure_by_name(self, name):
        for figure in self.figures:
            if figure.image_name == name:
                return figure
        return None

############################################################
### 

def process_figures(pdf_filepath, response_json):
    """
    Process the figures from the response JSON and return a FigureList object 
    """
    OUTPUT_DIR = "output_figures"
    figure_list = FigureList()

    for i, element in enumerate(response_json["elements"]):
        if element["category"] == "figure":
            this_figure = Figure(original_doc_filepath=pdf_filepath, image_name=None, image_caption=None, image_descriptions=element["text"], page_number=element["page"], image_coordinates=element.get("bounding_box"), html=element["html"], element_id=element["id"], FigureListObj=figure_list)

            print("\n=================================")
            print(response_json["elements"][i]["id"])

            # Look for the next caption or paragraph after all 'figure' elements
            for j in range(i+1, min(i+NUM_ADDITIONAL_ELEMENTS_TO_LOOK_FOR_CAPTIONS, len(response_json["elements"]))):
                next_element = response_json["elements"][j]
                print(f'\n next element {j} \n {next_element["text"]}\n')

                if next_element["category"] in ["caption", "paragraph"] and next_element["text"] not in ["", " ", None]:
                    this_figure.create_image_caption(next_element["text"])
                    match = re.search(r'(?i)(Figure|Fig\.?)\s*(\d+(?:[.-]\d+)*)', next_element["text"])
                    if match:
                        this_figure.set_figure_name(f"{match.group(1)} {match.group(2)}")
                        print("set figure name to", f"{match.group(1)} {match.group(2)}")
                    break  # Stop after finding the first caption or paragraph

            if not this_figure.image_name:  # Ensure we have a valid figure name before adding
                this_figure.set_figure_name(f"Element {element['id']}")
            figure_list.add_figure(this_figure)
            
            # Now save the image with the potentially updated unique name # nvm we save it later in process_pdf 
            # this_figure.save_image_from_page_coordinates(output_filepath=f"{OUTPUT_DIR}/{this_figure.image_name}.png")

    # Process descriptions for all figures by going through the rest of the text
    for element in response_json["elements"]:
        if "Figure" in element["text"] or "Fig" in element["text"]:
            match = re.search(r'(Figure|Fig)\s?(\d+(\.\d+)?)', element["text"])
            if match:
                figure_name = f"{match.group(1)} {match.group(2)}"
                existing_figure = next((fig for fig in figure_list.figures if fig.image_name == figure_name), None)
                if existing_figure:
                    existing_figure.add_image_descriptions(element["text"])

    return figure_list

# # Example usage
# file_filename = "sample_data/Attention.pdf"
# figure_list = process_figures(file_filename, response_json)

# # Save figure list as a JSON
# import json
# figure_list_dict = [figure.__dict__() for figure in figure_list.figures]
# with open("output_figures/FigureList.json", "w") as json_file:
#     json.dump(figure_list_dict, json_file, indent=4)

# for figure in figure_list.figures:
#     print(f"Figure Name: {figure.image_name}, Caption: {figure.image_caption}")

############################################################
## Process the PDF and save the figures
def process_json_from_pdf(pdf_filepath, response_json, OUTPUT_DIR="output_figures"):
    """
    Process the PDF and save the figures in the output directory
    """
    # Assuming `process_figures` function is defined elsewhere in your code
    # and it returns a FigureList object after processing the PDF file.
    
    # Extract PDF name without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_filepath))[0]
    
    # Define output directories
    diagrams_dir = os.path.join(pdf_name, "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)  # Create directories if they don't exist

    os.makedirs(os.path.join(OUTPUT_DIR, diagrams_dir), exist_ok=True)  # Create directories if they don't exist

    # Process the figures using the existing logic
    figure_list = process_figures(pdf_filepath, response_json)

    # Save each figure image
    for figure in figure_list.figures:
        output_filepath = os.path.join(OUTPUT_DIR, diagrams_dir, f"{figure.image_name}.png")
        figure.save_image_from_page_coordinates(output_filepath)

    # Save the figure list as a JSON file
    figure_list_dict = [figure.__dict__() for figure in figure_list.figures]
    json_filepath = os.path.join(OUTPUT_DIR, pdf_name, f"{pdf_name}_figure_list.json") 
    with open(json_filepath, "w") as json_file:
        json.dump(figure_list_dict, json_file, indent=4)

    print(f"Processed PDF '{pdf_filepath}'. Results saved in '{OUTPUT_DIR}/{pdf_name}/' directory.")

############################################################
## Main function

def process_full_pdf(pdf_filepath, OUTPUT_DIR="output_figures"):
    """
    Process the full PDF and save the figures in the output directory
    """
    # Extract the images and texts from the PDF 
    response_json = get_element_json_from_pdf(pdf_filepath)
    results = process_json_from_pdf(pdf_filepath, response_json, OUTPUT_DIR=OUTPUT_DIR)
    return results

############################################################
if __name__ == "__main__":
    input_path = sys.argv[1]

    ## Directory 
    if os.path.isdir(input_path):
        for filename in os.listdir(input_path):
            if filename.endswith(".pdf"):
                pdf_filepath = os.path.join(input_path, filename)
                print(f"Processing {pdf_filepath}...")
                process_full_pdf(pdf_filepath)

    ## Single file
    elif os.path.isfile(input_path) and input_path.endswith(".pdf"):
        process_full_pdf(input_path)

    ## Invalid 
    else:
        print("The provided path is not a PDF file or a directory containing PDF files.")
        sys.exit(1)