from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Item(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_items",
        verbose_name="Chủ sở hữu",
    )
    name = models.CharField(max_length=150, verbose_name="Tên món đồ")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    category = models.CharField(max_length=120, blank=True, verbose_name="Danh mục")
    is_available = models.BooleanField(default=True, verbose_name="Sẵn sàng cho mượn")
    image = models.ImageField(upload_to="items/", null=True, blank=True, verbose_name="Hình ảnh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Món đồ"
        verbose_name_plural = "Món đồ"

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def get_absolute_url(self):
        return reverse("item_detail", kwargs={"item_id": self.id})

    @property
    def active_request(self):
        today = timezone.localdate()
        return (
            self.borrow_requests.filter(
                status=BorrowRequest.Status.APPROVED,
                returned_at__isnull=True,
                start_date__lte=today,
                end_date__gte=today,
            )
            .select_related("borrower")
            .first()
        )

    @property
    def status_label(self):
        return "Sẵn sàng" if self.is_available else "Đang cho mượn"


class BorrowRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"
        RETURNED = "returned", "Đã trả"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="borrow_requests")
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowed_requests",
        verbose_name="Người mượn",
    )
    start_date = models.DateField(verbose_name="Ngày mượn")
    end_date = models.DateField(verbose_name="Ngày trả")
    note = models.CharField(max_length=250, blank=True, verbose_name="Ghi chú")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Trạng thái",
    )
    returned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lượt mượn"
        verbose_name_plural = "Lượt mượn"

    def __str__(self):
        return f"{self.item.name} - {self.borrower.username}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Ngày mượn phải nhỏ hơn hoặc bằng ngày trả.")

        if not self.item_id or not self.start_date or not self.end_date:
            return

        overlap_qs = BorrowRequest.objects.filter(
            item=self.item,
            status=BorrowRequest.Status.APPROVED,
            returned_at__isnull=True,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        ).exclude(pk=self.pk)

        if overlap_qs.exists():
            raise ValidationError("Món đồ đã có lịch mượn trong khoảng thời gian này.")

    def mark_returned(self):
        self.status = BorrowRequest.Status.RETURNED
        self.returned_at = timezone.now()
        self.item.is_available = True
        self.item.save(update_fields=["is_available"])
        self.save(update_fields=["status", "returned_at"])

    def approve(self):
        self.status = BorrowRequest.Status.APPROVED
        self.full_clean()
        self.item.is_available = False
        self.item.save(update_fields=["is_available"])
        self.save(update_fields=["status"])

    @classmethod
    def close_expired_requests(cls):
        today = timezone.localdate()
        expired = cls.objects.filter(
            status=cls.Status.APPROVED,
            returned_at__isnull=True,
            end_date__lt=today,
        ).select_related("item")
        count = 0
        for req in expired:
            req.status = cls.Status.RETURNED
            req.returned_at = timezone.now()
            req.item.is_available = True
            req.item.save(update_fields=["is_available"])
            req.save(update_fields=["status", "returned_at"])
            count += 1
        return count


class Conversation(models.Model):
    borrow_request = models.OneToOneField(
        BorrowRequest,
        on_delete=models.CASCADE,
        related_name="conversation",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hội thoại"
        verbose_name_plural = "Hội thoại"

    def __str__(self):
        return f"Chat #{self.borrow_request_id or 'n/a'}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Nội dung")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Tin nhắn"
        verbose_name_plural = "Tin nhắn"

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
