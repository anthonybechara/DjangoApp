from django import forms
from django.contrib.auth import get_user_model


class CreateChatRoomForm(forms.Form):
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(CreateChatRoomForm, self).__init__(*args, **kwargs)
        if current_user:
            self.fields['participants'].queryset = get_user_model().objects.exclude(id=current_user.id)

    participants = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        label='Select Users to Chat With',
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )

