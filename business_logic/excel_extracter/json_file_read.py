# main_class_script.py

from business_logic.excel_extracter.Interasia_excelFormat import INTERASIAExcelWriter
from business_logic.excel_extracter.OOCL_excelFormat import OOCLExcelWriter
from .MSC_excelFormat import MSCExcelWriter
from .ONE_excelFormat import ONEExcelWriter
from .SITC_excelFormat import SITCExcelWriter
from .COSCO_excelFormat import COSCOExcelWriter
import os
import json
from datetime import datetime
import xlwings as xw
from bson.objectid import ObjectId
from pymongo import MongoClient
client = MongoClient('mongodb://admin:UYJjjii8887YHHG@74.226.197.117:27017/')
db = client['docre']
file_name = db['Filename']

class MainClass:

    def processJson(self, data):
        processed_data = {
            'Actual_Shipper': data.get('booking_conformation', {}).get('ActualShipper', '').replace('\n', ' '),
            'Booking_Number': data.get('booking_conformation', {}).get('BookingNumber', ''),
            'Vessel_No': data.get('booking_conformation', {}).get('Vessel_no', '').replace('\n', ' '),
            'Voyage_No': data.get('booking_conformation', {}).get('Voyage_no', '').replace('\n', ' '),
            'Shipping_Comp_Name': data.get('booking_conformation', {}).get('Shipping_comp_name', '').replace('\n', ' '),
            'Place_of_Receipt': data.get('booking_conformation', {}).get('PortOfReceipt', '').replace(',', ', '),
            'Port_of_Discharge': data.get('booking_conformation', {}).get('PortOfDischarge', '').replace(',', ', '),
            'Port_of_Loading': data.get('booking_conformation', {}).get('PortOfLoading', '').replace(',', ', '),
            'Place_of_Delivery': data.get('booking_conformation', {}).get('PlaceOfDelivery', '').replace(',', ', '),
            'B/L_Original': data.get('booking_conformation', {}).get('B/LOriginal', ''),
            'Freight_': data.get('booking_conformation', {}).get('Freight',''),
            'B/LPlaceOfIssue': data.get('booking_conformation', {}).get('B/LPlaceOfIssue',''),
            'shipper': data.get('booking_conformation', {}).get('shipper', ''),
            'consignee': data.get('booking_conformation', {}).get('consignee', ''),
            'notify': data.get('booking_conformation', {}).get('notify', ''),
        }
        return processed_data

    def copy_template_and_populate(self, template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path):
        print("msc running here")
        print("################################################################")
        Actual_Shipper  = processed_data.get('Actual_Shipper', '')
        shipping_comp_name = processed_data.get('Shipping_Comp_Name', '')
        Vessel_No = processed_data.get('Vessel_No', '')
        Freight_ = processed_data.get('Freight_', '')
        print("Actual_Shipper---------->>",Actual_Shipper)
        print("shipping_comp_name---------->>",shipping_comp_name)
        print("Vessel_No---------->>",Vessel_No)
        print("Freight_---------->>",Freight_)
        print("################################################################")
        
        
        if 'Shipping_Comp_Name' in processed_data and 'MSC' in processed_data['Shipping_Comp_Name']:
            print("msc running here 12")
            instance_variable = MSCExcelWriter()
            shipping_comp_name   = processed_data.get('Shipping_Comp_Name', '')
            booking_number       = processed_data.get('Booking_Number', 'UnknownBookingNo')
            vessel_and_voyage_no = processed_data.get('Vessel_No', 'Unknown')
            # template_name = os.path.basename(template_path)
            # os.path.splitext(template_name)
            timestamp = datetime.now().strftime("%Y%m%d")


            for file_path in template_path:
                print("template_name:", file_path)
                timestamp = datetime.now().strftime("%Y%m%d")
                template_name = os.path.basename(file_path)
                new_file_name = f"DR-{shipping_comp_name}-{timestamp}-{vessel_and_voyage_no}-{booking_number}{os.path.splitext(template_name)[1]}"
                
                print("new_file_name:", new_file_name)
                # data2 = {
				# "id": ObjectId(),
				# "filename": new_file_name,
				
			    #  }
                # file_name.insert_one(data2)
            print("Run MSC File")
            try:
                instance_variable.write_to_excel(template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path)
                print('Data written to Excel successfully.')
                return new_file_name
            except FileNotFoundError as e:
                print(f"Error FileNotFoundError : {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        elif processed_data.get('Shipping_Comp_Name', '') == 'ONE':
            instance_variable = ONEExcelWriter()
            print("Run ONE File")
            try:
                new_file_name = instance_variable.write_to_excel(template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path)
                print('Data written to Excel successfully.')
                return new_file_name
            except FileNotFoundError as e:
                print(f"Error FileNotFoundError : {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        elif 'Shipping_Comp_Name' in processed_data and 'SITC' in processed_data['Shipping_Comp_Name']:
            print("msc running here 14")
        # elif processed_data.get('Shipping_Comp_Name', '') == 'SITC CONTAINER LINES CO.,':
            instance_variable = SITCExcelWriter()
            print("Run SITC File")
            try:
                new_file_name = instance_variable.write_to_excel(template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path)
                print('Data written to Excel successfully.')
                return new_file_name
            except FileNotFoundError as e:
                print(f"Error FileNotFoundError : {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        elif 'Shipping_Comp_Name' in processed_data and 'COSCO' in processed_data['Shipping_Comp_Name']:
        # elif processed_data.get('Shipping_Comp_Name', '') == 'SITC CONTAINER LINES CO.,':
            instance_variable = COSCOExcelWriter()
            print("Run COSCO File")
            try:
                new_file_name = instance_variable.write_to_excel(template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path)
                print('Data written to Excel successfully.')
                return new_file_name
            except FileNotFoundError as e:
                print(f"Error FileNotFoundError : {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        elif 'Shipping_Comp_Name' in processed_data and 'IAL' in processed_data['Shipping_Comp_Name']:
            instance_variable = INTERASIAExcelWriter()
            print("Run IAL File")
            try:
                new_file_name = instance_variable.write_to_excel(template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path)
                print('Data written to Excel successfully.')
                return new_file_name
            except FileNotFoundError as e:
                print(f"Error FileNotFoundError : {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        elif 'Shipping_Comp_Name' in processed_data and 'OOCL' in processed_data['Shipping_Comp_Name']:
        # elif processed_data.get('Shipping_Comp_Name', '') == 'SITC CONTAINER LINES CO.,':
            instance_variable = OOCLExcelWriter()
            print("Run OOCL File")
            try:
                new_file_name = instance_variable.write_to_excel(template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path)
                print('Data written to Excel successfully.')
                return new_file_name
            except FileNotFoundError as e:
                print(f"Error FileNotFoundError : {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        else:
            print("ship com",processed_data.get("Shipping_Comp_Name"))
            print("FileNotFound error")
