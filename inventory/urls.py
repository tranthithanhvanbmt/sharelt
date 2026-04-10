from django.urls import path

from . import views


urlpatterns = [
    path("", views.ItemListView.as_view(), name="item_list"),
    path("accounts/signup/", views.signup, name="signup"),
    path("items/new/", views.ItemCreateView.as_view(), name="item_create"),
    path("items/<int:item_id>/", views.ItemDetailView.as_view(), name="item_detail"),
    path("items/<int:item_id>/request-loan/", views.request_loan, name="request_loan"),
    path("requests/<int:request_id>/approve/", views.approve_request, name="approve_request"),
    path("requests/<int:request_id>/reject/", views.reject_request, name="reject_request"),
    path("requests/<int:request_id>/returned/", views.mark_returned, name="mark_returned"),
    path("loans/me/", views.my_loans, name="my_loans"),
    path("items/me/", views.my_items, name="my_items"),
    path("requests/<int:request_id>/conversation/", views.conversation_detail, name="conversation_detail"),
]
