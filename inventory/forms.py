from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import BorrowRequest, Item, Message


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Lưu", css_class="btn btn-primary"))

    class Meta:
        model = Item
        fields = ["name", "category", "description", "is_available", "image"]


class LoanRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Gửi yêu cầu", css_class="btn btn-primary"))

    class Meta:
        model = BorrowRequest
        fields = ["start_date", "end_date", "note"]
        widgets = {
            # DatePicker: flatpickr is initialized in base.html on .js-datepicker.
            "start_date": forms.DateInput(
                attrs={"class": "form-control js-datepicker", "placeholder": "YYYY-MM-DD"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control js-datepicker", "placeholder": "YYYY-MM-DD"}
            ),
            "note": forms.TextInput(attrs={"class": "form-control"}),
        }


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Gửi tin nhắn", css_class="btn btn-primary"))

    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Nhập tin nhắn..."}
            )
        }
