from django.shortcuts import render
from django.views import View
from .forms import ExcelFileForm

class FileUploadView(View):
    def get(self, request):
        form = ExcelFileForm()
        return render(request, 'base.html', {'form': form})

    def post(self, request):
        form = ExcelFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.save()
            return render(request, 'excelFrontend.html', {'data': excel_file})
        else:
            return render(request, 'base.html', {'form': form})
