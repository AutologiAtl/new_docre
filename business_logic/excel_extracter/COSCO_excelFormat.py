import os
import shutil
import traceback
import xlwings as xw
from openpyxl import load_workbook
import os 
from datetime import datetime
import traceback
from .excel_extr_atl import ExcelProcessor

path = os.getcwd()
class COSCOExcelWriter:

    def calling_to_excel(self,processed_data, downloded_excel_path, uploaded_excel_path):
        try:
            consignee_from_pdf = processed_data.get('consignee', '')
            Notify_party_from_pdf = processed_data.get('notify', '')
            bl_issue_from_pdf = processed_data.get('B/LPlaceOfIssue', '')

            excel_processor = ExcelProcessor()
            self.df = excel_processor.process_all_excel_files(downloded_excel_path)
            excel_processor.copy_and_format_data(uploaded_excel_path)
            BL_ISSUE_BY_values_h31, final_values = excel_processor.find_and_print_values('B/L ISSUE BY :', 'CONSIGNEE :', 'NOTIFY PARTY :')
            excel_processor.extract_table_from_excel(uploaded_excel_path)

            consignee_from_excel = final_values[0] if len(final_values) > 0 else None
            Notify_party_from_excel = final_values[1] if len(final_values) > 0 else None
            bl_issue_from_excel = BL_ISSUE_BY_values_h31[0] if len(BL_ISSUE_BY_values_h31) > 0 else None

            if 'ACTUAL NAMEADDRESSTEL' in consignee_from_pdf and 'SAME AS CONSIGNEE' in Notify_party_from_pdf:
                print(f"This condition is applied when the PDF document lacks shipper details and requires extraction from the Excel invoice sheet.-- {consignee_from_pdf} -- {Notify_party_from_pdf}")
                consignee = consignee_from_excel
                Notify_party = Notify_party_from_excel
                bl_issue = bl_issue_from_excel
                print('consignee',consignee)
                print(Notify_party)
                print('bl_issue',bl_issue)
                return consignee, Notify_party, bl_issue
            else:
                print(f"This condition applied when the docre pdf haveing the shiper details- {consignee_from_pdf} -- {Notify_party_from_pdf} -- {bl_issue_from_pdf}")  
                consignee = consignee_from_pdf
                Notify_party = Notify_party_from_pdf
                bl_issue = bl_issue_from_pdf

                return consignee, Notify_party, bl_issue

        except Exception as e:
            print(f"Error Exception in msc_excelfile: {e}")
            traceback.print_exc()
            return None, None, None
        
    def write_to_excel(self, template_path, output_folder, processed_data,downloded_excel_path,uploaded_excel_path):
        
        try:
            if template_path:
                template_path = template_path[0]
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@",template_path)
            consignee, Notify_party, bl_issue = self.calling_to_excel(processed_data, downloded_excel_path,uploaded_excel_path)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(consignee)
            print(Notify_party)
            print('bl_issue',bl_issue)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            # Extract relevant information from the processed data
            shipping_comp_name = processed_data.get('Shipping_Comp_Name', '')
            booking_number = processed_data.get('Booking_Number', 'UnknownBookingNo')
            vessel_and_voyage_no = processed_data.get('Vessel_No', 'Unknown')

            # Generate a timestamp
            timestamp = datetime.now().strftime("%Y%m%d")
            print('temp---------->>',template_path)
            template_name = os.path.basename(template_path)
            booking_number = booking_number or 'UnknownBookingNo'
            new_file_name = f"DR-{shipping_comp_name}-{timestamp}-{vessel_and_voyage_no}-{booking_number}{os.path.splitext(template_name)[1]}"
            new_file_path = os.path.join(output_folder, new_file_name)

            # Copy template to the output folder with the new name
            shutil.copy(template_path, new_file_path)
            app = xw.App(visible=False)
            workbook = app.books.open(new_file_path)

            # Merge and center cells A5 to J9
            workbook.sheets[0].range('A4:D10').merge()
            # Write Actual Shipper details with wrap text
            actual_shipper_text = processed_data['Actual_Shipper']
            workbook.sheets[0].range('A4').value = actual_shipper_text
            # workbook.sheets[0].range('A5').api.WrapText = True

            # Merge and center cells A11 to J16
            workbook.sheets[0].range('A12:D17').merge()
            workbook.sheets[0].range('A12').value = consignee
            workbook.sheets[0].range('A12').api.WrapText = True

            # Merge and center cells J11 to J16
            workbook.sheets[0].range('A19:D24').merge()
            workbook.sheets[0].range('A19').value = Notify_party
            workbook.sheets[0].range('A19').api.WrapText = True

            # Merge and center cells H31
            workbook.sheets[0].range('E65:G66').merge()
            workbook.sheets[0].range('E65').value = bl_issue

            # Write Booking Number to cell K10
            workbook.sheets[0].range('F3').value = processed_data['Booking_Number']
            workbook.sheets[0].range('F5').value = processed_data['B/L_Original']
            workbook.sheets[0].range('A28').value = processed_data['Vessel_No'] +' '+ processed_data['Voyage_No']
            workbook.sheets[0].range('C28').value = processed_data['Port_of_Loading']
            workbook.sheets[0].range('C26').value = processed_data['Place_of_Receipt']
            workbook.sheets[0].range('A30').value = processed_data['Port_of_Discharge']
            workbook.sheets[0].range('C30').value = processed_data['Place_of_Delivery']
            workbook.sheets[0].range('D56').value = "Freight: "+ processed_data['Freight_']
            # workbook.sheets[0].range('P67').value = processed_data['B/L_Payble_At']

            self.write_sheet_2(workbook)
            workbook.save()

            print(f"File created: {new_file_path}")
            print(f"Invoice df: {self.df}")
            return new_file_name 

        except Exception as e:
            print(f"Error Exception in msc excelfile: {e}")
            traceback.print_exc()
            return None
        finally:
            workbook.close()
            app.quit()

    def write_sheet_2(self, workbook):

        #################### default df write into the excel sheet 1 ##################################################
        columns = list(self.df.columns) if not self.df.empty else []

        # Write column names in the first row
        for j, col in enumerate(columns):
            workbook.sheets[1].range(10, j+1).value = col

        # Write values horizontally for each row
        for i, row in self.df.iterrows():
            for j, col in enumerate(columns):
                workbook.sheets[1].range(i+12, j+1).value = row[col]

        last_row = workbook.sheets[1].range("A" + str(workbook.sheets[1].cells.last_cell.row)).end('up').row + 1  # Assuming the data starts from row 11

        last_row = last_row + 2
        print("last row >>>>>",last_row)


        # Merge cells A to E and write text
        workbook.sheets[1].range(f'A{last_row}:E{last_row}').merge()
        workbook.sheets[1].range(f'A{last_row}').value = "TOTAL WEIGHT AND M3"

        
        sum_formula = f'=SUM(G11:G{last_row - 1})'
        print('sum_formula',sum_formula)
        workbook.sheets[1].range(f'G{last_row}').formula = sum_formula
        workbook.sheets[1].range(f'G{last_row + 1}').value = "KG"
            

        # Sum values in column F
        sum_formula = f'=SUM(J11:J{last_row - 1})'
        workbook.sheets[1].range(f'J{last_row}').formula = sum_formula
        workbook.sheets[1].range(f'J{last_row +1}').value = "M3"

            