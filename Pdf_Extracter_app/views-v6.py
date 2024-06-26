import os
import json
import re
import shutil
import pandas as pd
from django.views import View
from .models import UploadedFile
from .forms import FileUploadForm,LoginForm
from django.contrib.auth.views import LogoutView
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from business_logic.source_code.main import Main_Class
from business_logic.excel_extracter.excel_extr_atl import ExcelProcessor
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from business_logic.source_code.PDFExtractor import PDFExtractor
from business_logic.excel_extracter.json_file_read import MainClass
from django.http import JsonResponse, HttpResponseBadRequest, StreamingHttpResponse

# file separator added instead of hard coding '/' or '\'
sep = os.path.sep
path = os.getcwd()

class LoginView(View):
    template_name = f'registration{sep}login.html'  # Your login template

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('file_upload')  # Redirect to a success page if the user is already authenticated
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form, 'error_message': None})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('file_upload')  # Redirect to a success page
            else:
                # Authentication failed
                return render(request, self.template_name, {'form': form, 'error_message': 'Invalid username or password'})
        else:
            # Form is not valid
            return render(request, self.template_name, {'form': form, 'error_message': 'Invalid form data'})

class LogoutView(LogoutView):
    next_page = '/'  # Redirect to home page after logout

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return redirect('login')  # Redirect to the login page after logout


@method_decorator(login_required(login_url='login'), name='dispatch')
class FileUploadView(LoginRequiredMixin, View):
    
    template_name = f'fileupload{sep}home.html'
    
    def get(self, request):
        form = FileUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form:
            icm = request.POST.get('form-select')
            icm1 = request.POST.get('form-select-sm')
            file1 = request.FILES.get('file1')
            file2 = request.FILES.get('file2')
            # file3 = request.FILES.get('file3')

            excel_All_files_paths = []
            excel_download_path = os.path.join(path, f'business_logic','media')
            os.makedirs(excel_download_path, exist_ok=True)
            
            for file in request.FILES.getlist('file3'):
                excelfile_path = os.path.join(excel_download_path, file.name)
                excel_All_files_paths.append(excelfile_path)
                with open(excelfile_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                        
            # return HttpResponse('Files uploaded successfully!')

            print("multipe files",'\n',excel_All_files_paths)

            request.session['icm'] = icm
            request.session['icm1'] = icm1
            request.session['file1'] = file1.name if file1 else None
            request.session['file2'] = file2.name if file2 else None
            

            main = Main_Class(icm, icm1, [file1,file2])
            main.main_function()
            df1=main.df
            
            # instance_var1 = ExcelProcessor()
            # df3 =  instance_var1.process_all_excel_files(excel_download_path)
            # instance_var1.copy_and_format_data(excelfile_path)
            # instance_var1.find_and_print_values('B/L ISSUE BY :', 'CONSIGNEE :', 'NOTIFY PARTY :')
            # instance_var1.extract_table_from_excel(excelfile_path)
            df1_dict = df1.to_dict(orient='records')
            # df3_dict = df3.to_dict(orient='records')


            # print("DATAFRAME 3",df3)
            # Convert to JSON strings
            df1_json = json.dumps(df1_dict)
            # df3_json = json.dumps(df3_dict)

            # Store the JSON strings in the session
            request.session['df1'] = df1_json
            # request.session['df3'] = df3_json
            request.session['excel_download_path'] = excel_download_path
            request.session['excelfile_path'] = excelfile_path

            return redirect('view_files')
        else:
            return HttpResponseBadRequest("Form data is not valid.")

       
class FileListView(View):
    template_name = f'fileupload{sep}list_view.html'

    def get(self, request, *args, **kwargs):
        # Your view logic goes here
        context = {
            'message': 'Hello, Coming Soon!'
        }
        return render(request, self.template_name, context)

class ViewFilesView(View):
    template_name = f'fileupload{sep}outputedit.html'

    def get(self, request):
        icm = request.session.get('icm')   
        icm1 = request.session.get('icm1')
        booking_conformation_pdf = request.session.get('file2')
        download_pdf_path = os.path.join(path, 'business_logic','media')
        booking_conformation_pdf_path = os.path.join(download_pdf_path, booking_conformation_pdf)

        print("booking_conformation_pdf",booking_conformation_pdf_path)
        
        df1_json = request.session.get('df1', '{}')
        # df3_json = request.session.get('df3', '{}')
        

        # Convert JSON strings to dictionaries
        df1_dict = json.loads(df1_json)
        # df3_dict = json.loads(df3_json)
        # df3_dict = json.loads(df3_json)

        
        # Convert dictionaries to DataFrames
        df1 = pd.DataFrame(df1_dict)
        # df3 = pd.DataFrame(df3_dict)

        obj = PDFExtractor(icm, icm1,booking_conformation_pdf_path)
        obj.extract_pdf_coordinates()
        df2_ = obj.df

        print('909090909099()())90909()()(()(9(()(()90990(0(0)9)))))',df2_)

        shipping_comp_name = df2_.loc[df2_['Label'] == 'Shipping Comp Name', 'Content'].iloc[0]

        print("Shipping Comp Name:", shipping_comp_name)
        request.session['shipping_comp_name'] = shipping_comp_name

        excel_download_path = request.session.get('excel_download_path')
        excelfile_path = request.session.get('excelfile_path')

        instance_var1 = ExcelProcessor()
        df3 =  instance_var1.process_all_excel_files(excel_download_path)
        instance_var1.copy_and_format_data(excelfile_path,shipping_comp_name)
        instance_var1.find_and_print_values('B/L ISSUE BY :', 'CONSIGNEE :', 'NOTIFY PARTY :')
        instance_var1.extract_table_from_excel(excelfile_path)
        

        # image_path = os.path.join(path +f"{sep}Pdf_Extracter_app{sep}static{sep}images")
        image_paths = [            
            os.path.join(path + f"{sep}Pdf_Extracter_app{sep}static{sep}images{sep}page_3.png"),            
            os.path.join(path + f"{sep}Pdf_Extracter_app{sep}static{sep}images{sep}page_4.png"),            
            os.path.join(path + f"{sep}Pdf_Extracter_app{sep}static{sep}images{sep}page_5.png"),
            os.path.join(path + f"{sep}Pdf_Extracter_app{sep}static{sep}images{sep}page_6.png"),
            os.path.join(path + f"{sep}Pdf_Extracter_app{sep}static{sep}images{sep}page_7.png"),
            # Add more paths if needed
        ]

        df1 = df1.to_dict(orient='records')
        df2 = df2_.to_dict(orient='records')
        df3 = df3.to_dict(orient='records')

         # Extract column names from the first row of your_data
        columns = list(df3[0].keys()) if df3 else []


        print("Dataframe 3",'\n', df3)

        new_list = []
        for index, item in enumerate(df1, start=1):
            new_dict = {'masho' + str(index): {
                'Registration no': item['Registration_no'],
                'Registration date': item['Registration_date'],
                'First registration date': item['First_registration_date'],
                'makers_serial_no': item['Makers_serial_no'],
                'trade_maker_vehicle': item['Trade_maker_vehicle'],
                'engine_model': item['Engine_model'],
                'name_address': item['Name_address'],
                'use': item['use'],
                'purpose': item['purpose'],
                'type_of_body': item['type_of_body'],
                'fixed_no': item['fixed_no'],
                'maxim_carry': item['maxim_carry'],
                'weight': item['weight'],
                'gweight': item['gweight'],
                'engine_capacity': item['engine_capacity'],
                'fuel': item['fuel'],
                'length': item['length'],
                'width': item['width'],
                'height': item['height'],
                'export_schedule_day': item['export_schedule_day'],
                'mileage': item['mileage'],
            }}
            new_list.append(new_dict)

        # Remove dictionaries with 'masho' as nan
        filtered_data = [{key: value} for key, value in new_list[0].items() if value is not None]
        filtered_data = [entry for entry in new_list if all(value is not None for value in entry.values())]

        df1_html = filtered_data
        df1_html = json.dumps(df1_html)

        return render(request, self.template_name, {'image_paths': image_paths, 'df1_html': df1_html,
                                                    'df2_html': df2, 'df3_html': df3, 'columns':columns,
                                                    'icm':icm, 'icm1':icm1, 'shipping_comp_name': shipping_comp_name
                                                    })
    

@method_decorator(csrf_exempt, name='dispatch')
class AjaxSaveView(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Assuming the data is sent as JSON
                data = json.loads(request.body)

                print('Received data:', data)
                request.session['data'] = data
                # print('Session data set:', request.session['data'])
                
                response_data = {'status': 'success', 'message': 'Data saved successfully'}
                return JsonResponse(response_data)
            except json.JSONDecodeError as e:
                response_data = {'status': 'error', 'message': 'Invalid JSON data'}
                return JsonResponse(response_data, status=400)
        else:
            response_data = {'status': 'error', 'message': 'Invalid request'}
            return JsonResponse(response_data, status=400)

        
class MscExcelView(View):
    template_name = f'fileupload{sep}excel_file.html'

    def get(self, request, *args, **kwargs):

        try:
            json_dict = request.session.get('data')
            print("######################################")
            print(json_dict)
            if json_dict is not None:
                payload_dict = json_dict.get('payload', {})
            else:
                print("json_dict is None. Unable to retrieve payload.")

            json_data = json.dumps(payload_dict)
            json_data_dict = json.loads(json_data)
        except json.JSONDecodeError:
            return redirect('view_files')
        
        print("json_data_dict---------------->>>",json_data_dict)
        downloded_excel_path = request.session.get('excel_download_path')
        uploaded_excel_path = request.session.get('excelfile_path')

        shipping_comp_name = request.session.get('shipping_comp_name')
        template_folder = path + f"{sep}business_logic{sep}excel_extracter{sep}Templates"
        excel_file_keyword = shipping_comp_name

        # Get a list of all files in the Templates folder
        template_files = os.listdir(template_folder)

        # List to store matching file paths
        matching_file_paths = []
        template_excel_path_ = []

        # Iterate through each file in the Templates folder
        # Iterate through each file in the Templates folder
        for file in template_files:
            target_prefix = excel_file_keyword.lower()[:3]  # Extract the first 3-4 letters and convert to lowercase
            if target_prefix in file.lower() and file.lower().endswith(".xlsx"):
                # Matching Excel file found
                matching_file_path = os.path.join(template_folder, file)
                matching_file_paths.append(matching_file_path)


        # Print the list of matching file paths
        if matching_file_paths:
            print(f"Matching Excel files found:")
            for temp_pass in matching_file_paths:
                template_excel_path_.append(temp_pass)
                print(temp_pass)
        else:
            print(f"No Excel files found in '{template_folder}' with '{excel_file_keyword}' in their names.")

        # template_excel_path = path + f"{sep}business_logic{sep}excel_extracter{sep}MSC DURBAN TEMPLATE.xlsx"
        template_excel_path = template_excel_path_
        output_folder_path = path + f"{sep}business_logic{sep}excel_extracter{sep}Excel_output_files"

        # Access the 'payload' key
        instance_var = MainClass()
        processed_data = instance_var.processJson(json_data_dict)

        # Ensure the output folder exists
        os.makedirs(output_folder_path, exist_ok=True)

        # Call the copy_template_and_populate method and capture the returned new_file_name
        new_file_name = instance_var.copy_template_and_populate(template_excel_path, output_folder_path, processed_data,downloded_excel_path,uploaded_excel_path)
        request.session['new_file_name'] = new_file_name

        return render(request, self.template_name, {'message': 'Docre created successfully','new_file_name':new_file_name})
    
class ExcelDownloadView(View):
    template_name = f'fileupload{sep}excel_file.html'

    def get(self, request, *args, **kwargs):

        new_file_name = request.session.get('new_file_name')

        excel_file_path = path + f'{sep}business_logic{sep}excel_extracter{sep}Excel_output_files'
        excel_file_path = f"{excel_file_path}{sep}{new_file_name}"
        print("excel_file_path",excel_file_path)
        print("new_file_name",new_file_name)

        if os.path.exists(excel_file_path):
            excel_file_name = os.path.basename(excel_file_path)
            response = StreamingHttpResponse(self.file_iterator(excel_file_path))
            response['Content-Disposition'] = f'attachment; filename="{excel_file_name}"'
            return response
        else:
            return render(request, self.template_name, {'file_not_found': True})

    def file_iterator(self, file_path, chunk_size=8192):
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    

    def move_files(self,filename,mediador):
        
        try:
            pattern = r'-(\d+)\.xlsx$'
            # Use re.search to find the match in the filename
            match = re.search(pattern, filename)

            if match:
                booking_number = match.group(1)
                print("Booking Number:move ", booking_number)
            else:
                print("Booking number not found in the filename.")

            booking_number = booking_number
            old_name = 'uploads'
            mediator = mediador
            source_folder = path + f'{sep}media'
            destination_folder = path + f'{sep}business_logic{sep}UPLOAD_Files'
            destination_folder = f'{destination_folder}{sep}{mediator}{sep}{booking_number}'
            # Create destination folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)

            # Move each file from the source folder to the destination folder
            for filename in os.listdir(source_folder):
                source_file = os.path.join(source_folder, filename)
                destination_file = os.path.join(destination_folder, filename)
                shutil.move(source_file, destination_file)

            

            if os.path.exists(old_name):
                # Rename the folder
                os.rename(old_name, booking_number)
                print(f"Folder '{old_name}' has been renamed to '{booking_number}'.")
            else:
                print(f"Folder '{old_name}' does not exist or is not a directory.")

            print(f"All files from '{source_folder}' moved to '{destination_folder}' successfully!")
        except Exception as e:
            print(f"Error moving files: {e}")



