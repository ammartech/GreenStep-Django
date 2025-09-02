from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Activity, EmissionFactor

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['emission_factor', 'quantity', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
                'step': '0.1',
                'placeholder': 'Enter amount'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Optional notes about this activity'
            }),
            'emission_factor': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group emission factors by category for better UX
        self.fields['emission_factor'].queryset = EmissionFactor.objects.all()
        self.fields['emission_factor'].empty_label = "Select an activity"

        # Add helpful labels
        self.fields['quantity'].help_text = "Amount will depend on the activity selected"
        self.fields['emission_factor'].help_text = "Choose the activity that best matches what you did"

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'your.email@example.com'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your first name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your last name'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-input'})

        # Update placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a strong password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
