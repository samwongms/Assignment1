from django.contrib import admin
from .models import Listing,Subject 
from django.forms import NumberInput
from django.db import models
from django import forms
from taggit.forms import TagWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
class ListingAdminForm(forms.ModelForm):
    professionals = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Professionals', is_stacked=False, attrs={'rows' : '5'}), required=False, label="Select Professionals"
    )
    class Meta:
        model = Listing
        fields = '__all__'
        widgets = {
            'services': TagWidget(),  # Use Taggit's widget for tags
        }
class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    list_display = 'id', 'title','district', 'is_published','rooms', 'doctor', 'tag_list', 'display_professionals'
    list_display_links = 'id', 'title'
    list_filter = ("doctor", 'services')
    list_editable = ("is_published","rooms")
    search_fields = ("title",  "district", "doctor__name", "services__name", "professionals__name")
    list_per_page = 25
    ordering=['-id']
    #  prepopulated_fields = {"title" : ('title',)}
    formfield_overrides = {
        models.IntegerField: {
            'widget': NumberInput(attrs={'size': '10'})
        },
    }
    show_facets = admin.ShowFacets.ALWAYS
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('services', 'professionals')
    def display_professionals(self, obj):
        return ", ".join([subject.name for subject in obj.professionals.all()]) or 'None'
    display_professionals.short_description = "Professionals"

class SubjectAdmin(admin.ModelAdmin):
    list_display = 'name', 
    search_fields = ("name",)
       
admin.site.register(Listing, ListingAdmin)
admin.site.register(Subject,SubjectAdmin)