from django import forms


class LoginForm(forms.Form):
    id = forms.CharField(max_length=50)
    mdp = forms.CharField(max_length=50)

