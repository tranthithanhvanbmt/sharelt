from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView

from .forms import ItemForm, LoanRequestForm, MessageForm
from .models import BorrowRequest, Conversation, Item


def refresh_expired_requests():
    BorrowRequest.close_expired_requests()


class ItemListView(ListView):
    model = Item
    template_name = "inventory/item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        refresh_expired_requests()
        queryset = Item.objects.select_related("owner").filter(is_available=True)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(category__icontains=query)
                | Q(description__icontains=query)
                | Q(owner__username__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = "inventory/item_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Đăng món đồ thành công.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ItemDetailView(DetailView):
    model = Item
    template_name = "inventory/item_detail.html"
    context_object_name = "item"
    pk_url_kwarg = "item_id"

    def get_queryset(self):
        refresh_expired_requests()
        return Item.objects.select_related("owner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = context["item"]
        context["pending_requests"] = item.borrow_requests.filter(
            status=BorrowRequest.Status.PENDING
        ).select_related("borrower")
        context["approved_requests"] = item.borrow_requests.filter(
            status=BorrowRequest.Status.APPROVED
        ).select_related("borrower")
        return context

@login_required
def request_loan(request, item_id):
    refresh_expired_requests()
    item = get_object_or_404(Item, pk=item_id)

    if item.owner_id == request.user.id:
        return HttpResponseForbidden("Bạn không thể tự mượn món đồ của mình.")

    if not item.is_available:
        messages.error(request, "Món đồ này hiện không sẵn sàng để mượn.")
        return redirect("item_detail", item_id=item.id)

    if request.method == "POST":
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            borrow_request = form.save(commit=False)
            borrow_request.item = item
            borrow_request.borrower = request.user
            borrow_request.status = BorrowRequest.Status.PENDING
            borrow_request.full_clean()
            borrow_request.save()
            Conversation.objects.create(borrow_request=borrow_request)
            messages.success(request, "Đã gửi yêu cầu mượn. Hãy nhắn tin để hẹn thời gian nhận đồ.")
            return redirect("conversation_detail", request_id=borrow_request.id)
    else:
        form = LoanRequestForm()

    return render(request, "inventory/loan_request_form.html", {"item": item, "form": form})


@login_required
def approve_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest.objects.select_related("item"), pk=request_id)
    if borrow_request.item.owner_id != request.user.id:
        return HttpResponseForbidden("Bạn không có quyền duyệt yêu cầu này.")

    borrow_request.approve()
    messages.success(request, "Đã duyệt yêu cầu mượn.")
    return redirect("item_detail", item_id=borrow_request.item_id)


@login_required
def reject_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest.objects.select_related("item"), pk=request_id)
    if borrow_request.item.owner_id != request.user.id:
        return HttpResponseForbidden("Bạn không có quyền từ chối yêu cầu này.")

    borrow_request.status = BorrowRequest.Status.REJECTED
    borrow_request.save(update_fields=["status"])
    messages.info(request, "Đã từ chối yêu cầu mượn.")
    return redirect("item_detail", item_id=borrow_request.item_id)


@login_required
def mark_returned(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest.objects.select_related("item"), pk=request_id)
    if borrow_request.item.owner_id != request.user.id and borrow_request.borrower_id != request.user.id:
        return HttpResponseForbidden("Bạn không có quyền cập nhật lượt mượn này.")

    borrow_request.mark_returned()
    messages.success(request, "Đã đánh dấu món đồ đã được trả.")
    return redirect("item_detail", item_id=borrow_request.item_id)


@login_required
def my_loans(request):
    refresh_expired_requests()
    today = timezone.localdate()
    borrowed = BorrowRequest.objects.filter(borrower=request.user).select_related("item", "item__owner")
    active = borrowed.filter(
        status=BorrowRequest.Status.APPROVED, end_date__gte=today, returned_at__isnull=True
    )
    return render(
        request,
        "inventory/my_loans.html",
        {"borrowed": borrowed, "active": active},
    )


@login_required
def my_items(request):
    refresh_expired_requests()
    items = Item.objects.filter(owner=request.user).prefetch_related("borrow_requests__borrower")
    pending_requests = BorrowRequest.objects.filter(
        item__owner=request.user,
        status=BorrowRequest.Status.PENDING,
    ).select_related("item", "borrower")
    return render(request, "inventory/my_items.html", {"items": items, "pending_requests": pending_requests})


@login_required
def conversation_detail(request, request_id):
    borrow_request = get_object_or_404(
        BorrowRequest.objects.select_related("item", "borrower", "item__owner"), pk=request_id
    )
    if request.user.id not in {borrow_request.borrower_id, borrow_request.item.owner_id}:
        return HttpResponseForbidden("Bạn không thể truy cập hội thoại này.")

    conversation, _ = Conversation.objects.get_or_create(borrow_request=borrow_request)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = conversation
            msg.sender = request.user
            msg.save()
            return redirect("conversation_detail", request_id=borrow_request.id)
    else:
        form = MessageForm()

    return render(
        request,
        "inventory/conversation.html",
        {
            "borrow_request": borrow_request,
            "conversation": conversation,
            "messages_list": conversation.messages.select_related("sender").all(),
            "form": form,
        },
    )
