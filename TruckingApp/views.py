import os
import json
import numpy as np
import pandas as pd
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from TruckingApp.forms import ExcelFileForm
from django.shortcuts import redirect, render

path = os.getcwd()
sep = os.path.sep

class FileUploadView(View):
    def get(self, request):
        return render(request, f'trucking{sep}home.html')

    def post(self, request):
        try:
            if request.user.is_authenticated:
                current_user = request.user
                username = current_user.username                
        except:
            return HttpResponse("<h4>Now access the user's properties, such as username or email</h4>")
        form = ExcelFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            company_name = request.POST.get('companyId')
            shippingCompanyName = request.POST.get('shippingCompanyName')
            print(f"company_name \n{company_name} \n{shippingCompanyName}")
            excel_file = request.FILES.get('file')
            
            if excel_file:
                try:
                    print("excel_file",excel_file)
                    df_main = pd.read_excel(excel_file, header=12)
                    df_main = df_main.iloc[0:]
                    df_main.dropna(how='all', inplace=True)
                    df_main.to_string(index=False)

                    # Check if any NaN values exist in the 'Stock No. & Chassis No.' column
                    if df_main['Stock No. & Chassis No.'].isna().any():
                        # Find the index of the first row where the 'Stock No. & Chassis No.' column contains NaN
                        nan_index = df_main[df_main['Stock No. & Chassis No.'].isna()].index.tolist()[0]
                        print("nan_index", nan_index)

                        # Drop rows after encountering NaN in the "Chassis No." column
                        df_main = df_main.iloc[:nan_index]
                    else:
                        print("No NaN values found in the 'Stock No. & Chassis No.' column.")
                except Exception as e:
                    # Use messages framework to display error message
                    messages.error(request, "This Excel file format is not supported! <br>Please upload the supported Excel file.")
                    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
                # Resetting the file read pointer to the beginning
                excel_file.seek(0)
            

                df = pd.read_excel(excel_file.file, header=None, skiprows=12)
                df.columns = df.iloc[0]

                # Exclude row 13 from the DataFrame
                df = df.drop(index=0)
                # Function to extract the second part after splitting by '/'
                def ChassisNo(cell_value):
                    if isinstance(cell_value, str):  # Check if cell value is a string
                        parts = cell_value.split('/')
                        if len(parts) > 1:
                            return parts[1].strip()
                    return None  # Return None if cell value is not a string or doesn't contain '/'

                # Function to extract the desired part from cell value
                def SKU(cell_value):
                    if isinstance(cell_value, str):  # Check if cell value is a string
                        parts = cell_value.split(':')
                        if len(parts) > 1:
                            value_after_colon = parts[-1].strip()  # Take the last part after splitting by ':'
                            if 'BENZ' in value_after_colon:  # Check if 'BENZ' exists in the string
                                return value_after_colon[value_after_colon.index('BENZ'):]  # Extract substring from 'BENZ' onwards
                            # elif '-' in value_after_colon:  # Check if there's a hyphen
                            #     return value_after_colon.split('-')[-1].strip()  # Take the value after the last hyphen
                            else:
                                # Extract the substring after the last space
                                return value_after_colon.split(':', 2)[-1].strip()  # Take the value after the last colon
                        else:
                            return cell_value.strip()  # If no ':' found, return the original value
                    else:
                        return cell_value  # Return the original value if not a string

                def extract_model(cell_value):
                    if isinstance(cell_value, str):
                        if 'BENZ' in cell_value:
                            return cell_value 
                        # else:
                            # parts = cell_value.split('')
                            # if len(parts) > 1:
                            #     return parts[-1]
                            
                        else:
                            return cell_value.strip()
                    else:
                        return cell_value

                df['Drop Location'] = df['Drop Location'].str.replace('Autologistics', 'ATL')

                # Replace Chassis No. cell values after splitting by '/'
                df['Chassis No.'] = df['Stock No. & Chassis No.'].apply(ChassisNo)

                # Replace cell values with the desired part after processing
                df['SKU'] = df['SKU'].apply(SKU)

                # Drop the columns you don't need
                columns_to_drop = ["Stock No. & Chassis No.","Purchase Date", "Supplier/ Purchased Name", "Reg Year", "Forwarder", "NP", "Pickup Schedule Date"]
                df = df.drop(columns=columns_to_drop, errors="ignore")

                # Replace missing values with None
                df = df.where(pd.notnull(df), None)

                # Save DataFrame to Excel
                df.to_excel('Transworldtest_latest.xlsx', index=False)


                locations_to_match_df = pd.read_excel(path + f"{sep}Transworldtest_latest.xlsx")
                models_to_match_df = pd.read_excel(path + f"{sep}VehicleModel.xlsx")
                all_locations_df =pd.read_excel(path + f'{sep}TruckingLocation.xlsx')
                locations_to_match_df['Drop Location'] = locations_to_match_df['Drop Location'].str.upper()

                pickup_location = all_locations_df['Drop Location'].values
                drop_location = all_locations_df['Drop Location'].values
                Locations_ID = all_locations_df['Id'].values
                print('Locations_ID',Locations_ID)


                def split_sku(cell_value):
                    if isinstance(cell_value, str):
                        if 'BENZ' in cell_value:
                            return cell_value
                        
                        elif 'PIXIS' in cell_value:
                            return ' '.join(cell_value.split()[cell_value.split().index('PIXIS'):])
                        
                        else:
                            return cell_value
                    else:
                        return cell_value
                    
                # Perform a left merge to match locations and get their IDs
                merged_df = pd.merge(locations_to_match_df, all_locations_df[['Drop Location','Id']], on='Drop Location', how='left')
                
                # Apply the custom function to the 'SKU' column
                merged_df['SKU'] = merged_df['SKU'].apply(split_sku)

                all_locations_df['Pickup ID'] = all_locations_df['Id']
                yt = all_locations_df[['Drop Location','Pickup ID']]
                merged_df = pd.merge(merged_df, yt, left_on='Pickup Location',right_on='Drop Location', how='left')

                merged_df = merged_df.drop('Drop Location_y',  axis=1, errors="ignore")
                merged_df.rename(columns={'Id': 'DropLocId'}, inplace=True)
                merged_df.rename(columns={'Drop Location_x': 'Drop Location'}, inplace=True)

                models_to_match_df['Model ID'] = models_to_match_df['Id']
                mod_name = models_to_match_df[['ModelNameEng','Model ID']]
                merged_df = pd.merge(merged_df, mod_name, left_on='SKU',right_on='ModelNameEng', how='left')

                if merged_df['Chassis No.'].isna().any():
                    # Find the index of the first row where the 'Chassis No.' column contains NaN
                    nan_index = merged_df[merged_df['Chassis No.'].isna()].index.tolist()[0]
                    print("nan_index", nan_index)

                    # Drop rows after encountering NaN in the "Chassis No." column
                    merged_df = merged_df.iloc[:nan_index]
                    # Keep only the rows before the index where the NaN value was found
                else:
                    print("No NaN values found in the 'Chassis No.' column.")

                # Print the resulting DataFrame
                print("\nMerged DataFrame:")
                print(merged_df)

                merged_df['Pickup ID'] = merged_df['Pickup ID'].fillna(0)
                merged_df['DropLocId'] = merged_df['DropLocId'].fillna(0)
                merged_df['Model ID'] = merged_df['Model ID'].fillna(0)
                merged_df['Lot No.'] = merged_df['Lot No.'].fillna(0)

                # Convert 'Pickup ID' column to integers
                merged_df['Pickup ID'] = pd.to_numeric(merged_df['Pickup ID'], errors='coerce').astype(int)
                merged_df['DropLocId'] = pd.to_numeric(merged_df['DropLocId'], errors='coerce').astype(int)
                merged_df['Model ID'] = pd.to_numeric(merged_df['Model ID'], errors='coerce').astype(int)
                merged_df['Lot No.'] = pd.to_numeric(merged_df['Lot No.'], errors='coerce').astype(int)
                merged_df['Remarks'] = merged_df['Remarks'].astype(str)
                merged_df['Remarks'] = np.where((merged_df['Remarks'] == "0.0") | (merged_df['Remarks'] == "0"), " ", merged_df['Remarks'])

                # Save the merged DataFrame to a new Excel file
                merged_df.to_excel('matched_ids.xlsx', index=False)
                records = merged_df.to_dict(orient='records')

                # Preprocess data to create dictionaries mapping location IDs to pickup and drop locations
                pickup_locations = {}
                drop_locations = {}
                
                for locId, pickup_loc, drop_loc in zip(Locations_ID, pickup_location, drop_location):
                    pickup_locations[locId] = pickup_loc
                    drop_locations[locId] = drop_loc
       
                
                # ----------- JSON PAYLOAD CREATION ------------
                # Initialize an empty list to store payloads
                payload = {
                    "CompanyName": company_name,
                    "ShippingCompanyName": shippingCompanyName,
                    "Vehicles_Details": []
                }

                # Iterate over each row in the DataFrame
                for index, row in merged_df.iterrows():
                    # Construct payload for each row
                    
                    vehicle_details={
                        "pickupLocationId": row["Pickup ID"],
                        "dropLocationId": row["DropLocId"],
                        "chassisNo.": row["Chassis No."],
                        "posNo.": row["POS No."],
                        "lotNo.": row["Lot No."],
                        "vehicleModelId": row["Model ID"],
                        "remarks": row["Remarks"]
                    }
                    
                    payload["Vehicles_Details"].append(vehicle_details)

                # Convert payloads dictionary to JSON string
                json_payload_string = json.dumps(payload, indent=2)

                # Write JSON string to a file
                with open('TRUCKING_CODE.json', 'w') as json_file:
                    json_file.write(json_payload_string)

                print("JSON file created successfully.")

                # Save DataFrame to Excel
                df.to_excel('Transworldtest_latest.xlsx', index=False)

                return render(request, f'trucking{sep}excelFrontend.html', {'data': df_main.to_html(),'records': records,'username':username, 'ShippingCompanyName':shippingCompanyName, 'company_name': company_name, 'pickup_locations':pickup_locations})
        else:
            return HttpResponse("No file uploaded or invalid request method!")        
