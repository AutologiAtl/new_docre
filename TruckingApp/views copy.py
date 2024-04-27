from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
import pandas as pd
import numpy as np
import json
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from TruckingApp.forms import ExcelFileForm
import os
sep = os.path.sep
path = os.getcwd()

@method_decorator(login_required(login_url='login'), name='dispatch')
class FileUploadView(View):
    def get(self, request):
        return render(request, f'trucking{sep}home.html')

    def post(self, request):
        form = ExcelFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            company_name = request.POST.get('companyId')
            shippingCompanyName = request.POST.get('shippingCompanyName')
            print(f"company_name \n{company_name} \n{shippingCompanyName}")
            excel_file = request.FILES.get('file')
            if excel_file:
                df_main = pd.read_excel(excel_file, header=12)
                df_main = df_main.iloc[0:]
                df_main.dropna(how='all', inplace=True)
                df_main.to_string(index=False)
                # Find the index of the first occurrence of NaN in the "Chassis No." column
                nan_index = df_main[df_main['Stock No. & Chassis No.'].isna()].index.tolist()[0]

                # Drop rows after encountering NaN in the "Chassis No." column
                df_main = df_main.iloc[:nan_index]
                # Process the file directly without saving
                # df_main = pd.read_excel(excel_file, header=12)
                # df_main = df_main.iloc[0:]
                # df_main.dropna(how='all', inplace=True)
                # df_main = df_main.iloc[:-1]
                # df_main.reset_index(drop=False, inplace=False)
                # df_main.to_string(index=False)

                print(f"hhjhjjjjhj \n{df_main}")

                
                # Resetting the file read pointer to the beginning
                excel_file.seek(0)
            

                df = pd.read_excel(excel_file.file, header=None, skiprows=12)

                print(df)
                # Set row 13 as the column headers
                df.columns = df.iloc[0]

                # Exclude row 13 from the DataFrame
                df = df.drop(index=0)

                # Remove the last row of the DataFrame
                # df = df.drop(df.index[-36])

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
                            elif '-' in value_after_colon:  # Check if there's a hyphen
                                return value_after_colon.split('-')[-1].strip()  # Take the value after the last hyphen
                            else:
                                # Extract the substring after the last space
                                return value_after_colon.split(':', 2)[-1].strip()  # Take the value after the last colon
                        else:
                            return cell_value.strip()  # If no ':' found, return the original value
                    else:
                        return cell_value  # Return the original value if not a string

                def extract_model(cell_value):
                    if isinstance(cell_value, str):  # Check if cell value is a string
                        if 'BENZ' in cell_value:  # Check if 'BENZ' exists in the string
                            return cell_value  # Return the original value if 'BENZ' is found
                        else:
                            parts = cell_value.split('')  # Split the string by whitespace
                            if len(parts) > 1:
                                return parts[-1]  # Return the last part after splitting by whitespace
                            else:
                                return cell_value.strip()  # Return the original value if no whitespace found
                    else:
                        return cell_value  # Return the original value if not a string

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
                all_locations_df =pd.read_excel(path + f'{sep}TruckingLocation.xlsx')
                locations_to_match_df['Drop Location'] = locations_to_match_df['Drop Location'].str.upper()

                # Print unique values in the 'Drop Location' column of each DataFrame
                print("Unique values in all_locations_df:")
                print(all_locations_df['Drop Location'].unique())
                print("\nUnique values in locations_to_match_df:")
                print(locations_to_match_df['Drop Location'])

                pickup_location = all_locations_df['Drop Location'].values
                drop_location   = all_locations_df['Drop Location'].values

                def split_sku(cell_value):
                    if isinstance(cell_value, str):
                        if 'BENZ' in cell_value:
                            return cell_value
                        
                        elif 'PIXIS' in cell_value:
                            return ' '.join(cell_value.split()[cell_value.split().index('PIXIS'):])
                        
                        else:
                            return cell_value.split()[-1]
                    else:
                        return cell_value

                # Perform a left merge to match locations and get their IDs
                merged_df = pd.merge(locations_to_match_df, all_locations_df[['Drop Location','Id']], on='Drop Location', how='left')

                all_locations_df['Pickup ID'] = all_locations_df['Id']
                yt = all_locations_df[['Drop Location','Pickup ID']]
                merged_df = pd.merge(merged_df, yt, left_on='Pickup Location',right_on='Drop Location', how='left')


                merged_df = merged_df.drop('Drop Location_y',  axis=1, errors="ignore")
                merged_df.rename(columns={'Id': 'DropLocId'}, inplace=True)
                merged_df.rename(columns={'Drop Location_x': 'Drop Location'}, inplace=True)
                # Assuming 'df' is your DataFrame
                # merged_df = merged_df.iloc[:-3]
                # merged_df.reset_index(drop=True, inplace=True)
                # Find the index of the first occurrence of NaN in the "Chassis No." column
                nan_index = merged_df[merged_df['Chassis No.'].isna()].index.tolist()[0]

                # Drop rows after encountering NaN in the "Chassis No." column
                merged_df = merged_df.iloc[:nan_index]

                # Print the resulting DataFrame
                print("\nMerged DataFrame:")
                print(merged_df)

                # Save the merged DataFrame to a new Excel file
                merged_df.to_excel('matched_ids.xlsx', index=False)
                records = merged_df.to_dict(orient='records')

                # ----------- JSON PAYLOAD CREATION ------------
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
                        "vehicleModelId": row["SKU"],
                        "remarks": row["Remarks"]
                    }
                    
                    payload["Vehicles_Details"].append(vehicle_details)
                
                context = {
                    'pickup_location': ', '.join(pickup_location.tolist()), 
                    'drop_location': ', '.join(drop_location.tolist())
                }

                # Convert payloads dictionary to JSON string
                json_payload_string = json.dumps(payload, indent=2)

                # Write JSON string to a file
                with open('TRUCKING_CODE.json', 'w') as json_file:
                    json_file.write(json_payload_string)

                print("JSON file created successfully.")

                


                # Save DataFrame to Excel
                df.to_excel('Transworldtest_latest.xlsx', index=False)

                return render(request, f'trucking{sep}excelFrontend.html', {'data': df_main.to_html(),'company_name': company_name, 'records': records,'pickup_location':pickup_location,'drop_location':drop_location})

        else:
            # If no file was uploaded or the request method is not POST, return an error message
            return HttpResponse("No file uploaded or invalid request method!")
        
