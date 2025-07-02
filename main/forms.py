from django import forms

class AddSongTextbox(forms.Form):
    name = forms.CharField(max_length=100, label="Enter a new song name:", required=False)
    
class NewSchedule(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
