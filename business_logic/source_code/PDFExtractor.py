import io
import os
import sys
import json
import fitz
import pandas as pd
import pdfplumber
from PIL import Image 
import pytesseract

# from google.cloud import vision
# from google.cloud.vision_v1 import types
import traceback

import os
sep = os.path.sep
path = os.getcwd()
class PDFExtractor:    

    def __init__(self, cl_name,booking_Customer_name,booking_conformation_pdf_path=None):
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path +"/business_logic/source_code/json_files/token/VisionAPI_ServiceAccountToken.json"
        # self.client = vision.ImageAnnotatorClient()
        self.cl_name = cl_name
        self.booking_Customer_name = booking_Customer_name
        self.booking_conformation_pdf = booking_conformation_pdf_path
        self.path = os.getcwd()

    
    # --------- FOR TABLE DATA EXTRACTION --------- WORKING !!!!!!
    def extract_pdf_coordinates(self):
        self.path = os.getcwd()
        if self.booking_conformation_pdf is not None:
            json_config_path = os.path.join(self.path,'business_logic', 'source_code', 'json_files', f'{self.booking_Customer_name}.json')
            json_config = json.load(open(json_config_path))
            booking_conformation_pdf = os.path.basename(self.booking_conformation_pdf)
            
            json_config['pdf_files'][0]['file_name'] = booking_conformation_pdf

            for pdf_info in json_config["pdf_files"]:
                print("MMMMMMMMMMMMpdf_infoMMMMMMMMMMMMM",pdf_info)
                pdf_file = pdf_info["file_name"]
                pdf_file_path = os.path.join(self.path, 'media','uploads', pdf_file)

                try:
                    labels = []
                    contents = []
                    try:
                        with pdfplumber.open(pdf_file_path) as pdf:
                            for area in pdf_info["coordinates"]:
                                label = area["label"]
                                x0, y0, x1, y1 = area["x0"], area["y0"], area["x1"], area["y1"]

                                if x0 < 0 or y0 < 0 or x1 > pdf.pages[0].width or y1 > pdf.pages[0].height:
                                    print(f"Error: Coordinates for '{label}' exceed page dimensions in {pdf_file}.")
                                    continue

                                content = pdf.pages[0].crop((x0, y0, x1, y1)).extract_text()
                                
                                labels.append(label)
                                contents.append(content)
                    except Exception as err:
                        print("No PDf Found in pdfextracter", err)
                        print("let's try it again")
                        with pdfplumber.open(pdf_file_path) as pdf:
                            for area in pdf_info["coordinates"]:
                                label = area["label"]
                                x0, y0, x1, y1 = area["x0"], area["y0"], area["x1"], area["y1"]

                                if x0 < 0 or y0 < 0 or x1 > pdf.pages[0].width or y1 > pdf.pages[0].height:
                                    print(f"Error: Coordinates for '{label}' exceed page dimensions in {pdf_file}.")
                                    continue

                                content = pdf.pages[0].crop((x0, y0, x1, y1)).extract_text()
                                
                                labels.append(label)
                                contents.append(content)

                    self.df = pd.DataFrame({"Label": labels, "Content": contents})

                except FileNotFoundError as e:
                    print(f"Error: PDF file '{pdf_file}' not found, please check whether the file is in the same file directory.")
                    traceback.print_exc()

                except Exception as e:
                    print(f"Error processing PDF '{pdf_file}': {str(e)}")
                    traceback.print_exc()
        else:
            print(f"No PDF file processing : {str(e)}")
            traceback.print_exc()
            pass



    def pdf_to_images(self):
        # Open the PDF file
        try:
            pdf_document = fitz.open(self.PDF_FILE_PATH)
        except Exception as e:
            print(f"Error:{e}")

        a =[]
        b = []
        # Iterate through each page
        for page_number in range(pdf_document.page_count):
            # Get the page using pdfplumber
            pdf_page = pdf_document[page_number]

            # Get the pixel dimensions (DPI) of the page
            dpi = 600  # You can adjust this value based on your requirements

            # Get the image data using fitz
            pixmap = pdf_page.get_pixmap(matrix=fitz.Matrix(dpi / 255, dpi / 255))

            # Convert the image data to a Pillow Image
            pil_image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

            # Resize the image to 1901x1469
            resized_image = pil_image.resize((1901, 1469))
            a.append(resized_image)

            # Save the image to the specified folder
            image_file_name = path +f"{sep}static{sep}images"
            image_filename = f"{image_file_name}{sep}page_{page_number + 1}.png"
            # print("image_filename :- ",image_filename)
            pil_image.save(image_filename)
            # # Open the image from the file path
            # original_image = Image.open(image_filename)
            
            b.append(image_filename)
            # print(f"Page {page_number + 1} converted and saved as {image_filename}")

        # Close the PDF document
        pdf_document.close()
        return a,b


    def image_crop(self, file_name):
        # Open the image file
        im = Image.open(file_name)
        # Use pytesseract to perform OCR
        extracted_text = pytesseract.image_to_string(im, lang='eng+jpn')  # Adjust the language parameter as needed
        # Assuming the extracted text contains the bounding box coordinates (e.g., "left, upper, right, down")
        # You need to parse the extracted text to get these coordinates
        # Example parsing logic (replace with your actual parsing logic)
        coordinates = extracted_text.split(',')
        left, upper, right, down = map(int, coordinates)

        # Crop the image
        im_cropped = im.crop((left, upper, right, down))

        # Resize the cropped image
        size = (1901, 1469)
        im_resized = im_cropped.resize(size)

        # Return the resized image
        return im_resized

    @staticmethod
    def crop_image(left, top, right, bottom, image_path):

        # Open the image from the file path
        original_image = Image.open(image_path)        
        # Define the coordinates for cropping
        coordinates = (left, top, right, bottom)
        # Crop the image
        cropped_image = original_image.crop(coordinates)
        # cropped_image.save('cropped_image.png')
        return cropped_image


    def extract_text_from_image(image_path):
        try:
            # Open the image using PIL (Python Imaging Library)
            with Image.open(image_path) as img:
                # Use pytesseract to perform OCR on the image
                extracted_text = pytesseract.image_to_string(img, lang='eng+jpn')
                print("Text Extracting.......")
                # print("Extracted Text:", extracted_text)
                return extracted_text
        except Exception as e:
            print(f"Error: {e}")
            return None
