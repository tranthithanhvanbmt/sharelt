from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import BorrowRequest, Comment, Item, Message


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"

    class Meta:
        model = Item
        fields = ["name", "category", "description", "is_available", "image", "is_published"]
        labels = {
            "is_published": "Tôi đồng ý đăng món đồ này lên trang chủ"
        }
        help_texts = {
            "is_published": "Bạn phải xác nhận trước khi đăng bài lên diễn đàn."
        }


class LoanRequestForm(forms.ModelForm):
    agree_to_rent = forms.BooleanField(
        required=True,
        label="Tôi đồng ý thuê món đồ này",
        help_text="Bạn phải đồng ý để gửi yêu cầu thuê."
    )

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


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Bình luận", css_class="btn btn-primary btn-sm"))

    class Meta:
        model = Comment
        fields = ["content"]
        labels = {
            "content": "Viết bình luận"
        }
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Chia sẻ ý kiến của bạn về món đồ này..."
            })
        }
        widgets = {
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Nhập tin nhắn..."}
            )
        }
