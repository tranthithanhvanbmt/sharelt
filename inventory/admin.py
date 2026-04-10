from django.contrib import admin

from .models import BorrowRequest, Conversation, Item, Message


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "category")
    search_fields = ("name", "owner__username", "category")


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ("item", "borrower", "start_date", "end_date", "status")
    list_filter = ("status",)
    search_fields = ("item__name", "borrower__username")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("borrow_request", "created_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "created_at")
    search_fields = ("sender__username", "content")
