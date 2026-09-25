from django import forms

from .models import SequenciaFasta


class UploadFastaForm(forms.ModelForm):
    class Meta:
        model = SequenciaFasta
        fields = ['arquivo']
