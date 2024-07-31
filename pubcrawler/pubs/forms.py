from django import forms

class CoordinateForm(forms.Form):
    start_lat = forms.FloatField(label='Start Latitude', required=True)
    start_lon = forms.FloatField(label='Start Longitude', required=True)
    end_lat = forms.FloatField(label='End Latitude', required=True)
    end_lon = forms.FloatField(label='End Longitude', required=True)

