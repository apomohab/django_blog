from django import forms
from .models import Comment


# here the form normally nor for models and database  project
class EmailPostForm(forms.Form):

    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


# forms comment class

# here the forms for model and saved in database , so name is ModelForm ..
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
