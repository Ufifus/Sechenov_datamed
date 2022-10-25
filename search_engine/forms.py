from django import forms
from datetime import date
from .models import Source
from django.forms.widgets import Select


def list_years(year_begin):
    corrent_year = date.today().year
    YEAR_CHOICES = []
    for i, year in enumerate(range(year_begin, corrent_year)):
        YEAR_CHOICES.append((str(i), str(year)))
    return YEAR_CHOICES

YEAR_CHOICES = list_years(1990)


class AddSearchForm(forms.Form):
    user_query = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите запрос...'
            }
        ),
        required=True
    )

    query_begin = forms.DateField(required=True,
                                  widget=forms.TextInput(
                                      attrs={
                                          'class': 'date-control',
                                          'placeholder': 'Введите запрос...'
                                      }
                                  ),
                                  initial=date.today(),
                                  localize=True)

    query_end = forms.DateField(required=True,
                                widget=forms.TextInput(
                                    attrs={
                                        'class': 'date-control',
                                        'placeholder': 'Введите запрос...'
                                    }
                                ),
                                initial=date.today(),
                                localize=True)

    query_source = forms.ModelChoiceField(Source.objects.all(), widget=Select, initial='PubMed')


class AddLocalSearch(forms.Form):
    user_query = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите запрос...'
            }
        )
    )
    
    
class AddSourceSearch(forms.Form):
    user_query = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите запрос...'
            }
        ),
        required=True
    )

    query_begin = forms.DateField(required=True,
                                  widget=forms.TextInput(
                                      attrs={
                                          'class': 'date-control',
                                          'placeholder': 'Введите запрос...'
                                      }
                                  ),
                                  initial=date.today(),
                                  localize=True)

    query_end = forms.DateField(required=True,
                                widget=forms.TextInput(
                                    attrs={
                                        'class': 'date-control',
                                        'placeholder': 'Введите запрос...'
                                    }
                                ),
                                initial=date.today(),
                                localize=True)
