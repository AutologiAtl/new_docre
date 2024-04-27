# import os
# import pandas as pd

# # Get the current working directory
# path = os.getcwd()

# # Read Transworldtest.xlsx and TruckingLocation.xlsx
# df_1 = pd.read_excel(path + '/Transworldtest.xlsx')
# df_2 = pd.read_excel(path + '/TruckingLocation.xlsx')

# # Get the values from 'Pickup Location' column in df_1
# pickup_locations = df_1['Pickup Location'].tolist()

# # Get the values from 'NameEng' column in df_2
# truck_location_names = df_2['NameEng'].tolist()

# # Filter df_2 based on whether the 'NameEng' exists in df_1's 'Pickup Location' column
# # filtered_df_2 = df_2[df_2['NameEng'].isin(pickup_locations)]
# filtered_df_1 = df_1[df_1['Pickup Location'].isin(truck_location_names)]
# print(filtered_df_1)

# # Now, if you want to get the text from cell A0 of filtered_df_2
# if not filtered_df_1.empty:
#     a0_text = filtered_df_1.iloc[0, 0]  # Assuming A0 refers to the first cell (0-indexed)
#     print("Text from cell A0:", a0_text)




# ##############################################################################################################################################
    
# import pandas as pd
# import json

# # Replace 'your_file.xlsx' with the path to your Excel file
# excel_file = '/Users/foxtrot/Downloads/Autologistics 10 02 2024  12.xlsx'

# # Read the Excel file into a DataFrame
# df = pd.read_excel(excel_file, header=None, skiprows=12)

# # Set row 13 as the column headers
# df.columns = df.iloc[0]

# # Exclude row 13 from the DataFrame
# df = df.drop(index=0)

# # Remove the last row of the DataFrame
# df = df.drop(df.index[-2])

# # Function to extract the second part after splitting by '/'
# def ChassisNo(cell_value):
#     if isinstance(cell_value, str):  # Check if cell value is a string
#         parts = cell_value.split('/')
#         if len(parts) > 1:
#             return parts[1].strip()
#     return None  # Return None if cell value is not a string or doesn't contain '/'

# # Function to extract the desired part from cell value
# def SKU(cell_value):
#     if isinstance(cell_value, str):  # Check if cell value is a string
#         parts = cell_value.split(':')
#         if len(parts) > 1:
#             value_after_colon = parts[-1].strip()  # Take the last part after splitting by ':'
#             if 'BENZ' in value_after_colon:  # Check if 'BENZ' exists in the string
#                 return value_after_colon[value_after_colon.index('BENZ'):]  # Extract substring from 'BENZ' onwards
#             elif '-' in value_after_colon:  # Check if there's a hyphen
#                 return value_after_colon.split('-')[-1].strip()  # Take the value after the last hyphen
#             else:
#                 # Extract the substring after the last space
#                 return value_after_colon.split(':', 2)[-1].strip()  # Take the value after the last colon
#         else:
#             return cell_value.strip()  # If no ':' found, return the original value
#     else:
#         return cell_value  # Return the original value if not a string

# def extract_model(cell_value):
#     if isinstance(cell_value, str):  # Check if cell value is a string
#         if 'BENZ' in cell_value:  # Check if 'BENZ' exists in the string
#             return cell_value  # Return the original value if 'BENZ' is found
#         else:
#             parts = cell_value.split('')  # Split the string by whitespace
#             if len(parts) > 1:
#                 return parts[-1]  # Return the last part after splitting by whitespace
#             else:
#                 return cell_value.strip()  # Return the original value if no whitespace found
#     else:
#         return cell_value  # Return the original value if not a string



# # Replace 'Autologistics' with 'ATL' in the specified column
# df['Drop Location'] = df['Drop Location'].str.replace('Autologistics', 'ATL')

# # Replace Chassis No. cell values after splitting by '/'
# df['Chassis No.'] = df['Stock No. & Chassis No.'].apply(ChassisNo)

# # Replace cell values with the desired part after processing
# df['SKU'] = df['SKU'].apply(SKU)

# # Drop the columns you don't need
# columns_to_drop = ["Stock No. & Chassis No.","Purchase Date", "Supplier/ Purchased Name", "Reg Year", "Forwarder", "NP", "Pickup Schedule Date"]
# df = df.drop(columns=columns_to_drop, errors="ignore")

# # Replace missing values with None
# df = df.where(pd.notnull(df), None)

# # Save DataFrame to Excel
# df.to_excel('Transworldtest_latest.xlsx', index=False)



# # -------- VLOOKUP APPLIED HERE ---------

# # Read the first Excel file with all locations and IDs
# all_locations_df = pd.read_excel('/Users/foxtrot/Downloads/TruckingLocation.xlsx')

# # Read the second Excel file with the locations you have
# locations_to_match_df = pd.read_excel('Transworldtest_latest.xlsx')
# locations_to_match_df['Drop Location'] = locations_to_match_df['Drop Location'].str.upper()

# # Print unique values in the 'Drop Location' column of each DataFrame
# print("Unique values in all_locations_df:")
# print(all_locations_df['Drop Location'].unique())
# print("\nUnique values in locations_to_match_df:")
# print(locations_to_match_df['Drop Location'])

# # Perform a left merge to match locations and get their IDs
# merged_df = pd.merge(locations_to_match_df, all_locations_df[['Drop Location','Id']], on='Drop Location', how='left')

# all_locations_df['Pickup ID'] = all_locations_df['Id']
# yt = all_locations_df[['Drop Location','Pickup ID']]
# merged_df = pd.merge(merged_df, yt, left_on='Pickup Location',right_on='Drop Location', how='left')


# merged_df = merged_df.drop('Drop Location_y',  axis=1, errors="ignore")
# merged_df.rename(columns={'Id': 'DropLocId'}, inplace=True)
# merged_df.rename(columns={'Drop Location_x': 'Drop Location'}, inplace=True)

# # Print the resulting DataFrame
# print("\nMerged DataFrame:")
# print(merged_df)

# # Save the merged DataFrame to a new Excel file
# merged_df.to_excel('matched_ids.xlsx', index=False)



# # ----------- JSON PAYLOAD CREATION ------------
# # Initialize an empty list to store payloads
# payloads = []

# # Iterate over each row in the DataFrame
# for index, row in merged_df.iterrows():
#     # Construct payload for each row
#     payload = {
#         "pickupLocationId": row["Pickup ID"],
#         "dropLocationId": row["DropLocId"],
#         "chassisNo.": row["Chassis No."],
#         "posNo.": row["POS No."],
#         "lotNo.": row["Lot No."],
#         "vehicleModelId": row["SKU"],
#         "remarks": row["Remarks"]
#     }
#     # Append payload to the list
#     payloads.append(payload)

# # Wrap payloads with key 'payload'
# json_payload = {'payload': payloads}

# # Convert payloads dictionary to JSON string
# json_payload_string = json.dumps(json_payload, indent=2)

# # Write JSON string to a file
# with open('TRUCKING_CODE.json', 'w') as json_file:
#     json_file.write(json_payload_string)

# print("JSON file created successfully.")

import requests
import json

url = "https://atlapis.azurewebsites.net/api/addExistingStock"

payload = json.dumps({
  "CompanyName": "107",
  "ShippingCompanyName": "28",
  "VehiclesDetails": [
    {
      "pickupLocationId": 544,
      "dropLocationId": 595,
      "chassisNo": "LVK-qwq",
      "posNo": "P5557",
      "lotNo": "rahul",
      "vehicleModelId": 5977,
      "remarks": "noremark"
    }
  ]
})
headers = {
  'x-functions-key': '7pYEofgTo7FyBN4VkYCp0GOh1x7NPoGV8FJQotmpU2vOAzFuYhxp1w==',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
