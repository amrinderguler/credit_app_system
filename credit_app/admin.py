from django.contrib import admin

# Register your models here.
from .models import Customer,Loan

from import_export.admin import ImportExportModelAdmin
from  import_export import resources

class CustomerResources(resources.ModelResource):
    class Meta:
        model=Customer
        import_id_fields = ['customer_id']
        
class LoanResources(resources.ModelResource):
    class Meta:
        model=Loan
        import_id_fields = ['loan_id']
        
@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResources
     
    list_display = ['customer_id','first_name']
    
@admin.register(Loan)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class = LoanResources
     
    list_display = ['customer_id']
    

