from django import forms

class nodeInput(forms.Form):
    node1 = forms.CharField(max_length=15, required=False)
    # use setattr ?
    # need to map the names on the POST to variables here for the map
    # major trouble
    # might need to try something else
    # it maps to name property of form
    send_help = forms.CharField(empty_value="default")
