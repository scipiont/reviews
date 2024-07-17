from django.contrib import admin
from .models import Review, Profile, Company, TransactionModel
from django.http import HttpResponse
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.templatetags.static import static
import os
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import simpleSplit
# Получение пути к шрифту в папке static
# Получение абсолютного пути к шрифту в папке static
# font_path = finders.find('fonts/DejaVuSans.ttf')

# if font_path:
#     pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
# else:
#     raise FileNotFoundError("Font file 'DejaVuSans.ttf' not found in static files.")
# Получение абсолютного пути к шрифту в папке static
font_path = finders.find('fonts/FreeSerif.ttf')

if font_path:
    pdfmetrics.registerFont(TTFont('FreeSerif', font_path))
else:
    raise FileNotFoundError("Font file 'FreeSerif.ttf' not found in static files.")

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('service', 'topic', 'author', 'timestamp', 'rating')
    actions = ['export_as_csv', 'export_as_pdf']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected as CSV"

    def export_as_pdf(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reviews.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setFont("FreeSerif", 12)  # Использование шрифта
        width, height = letter

        y = height - 30
        for review in queryset:
            p.drawString(30, y, f"Service: {review.service}")
            p.drawString(30, y - 15, f"Topic: {review.topic}")
            p.drawString(30, y - 30, f"Author: {review.author.username}")
            p.drawString(30, y - 45, f"Timestamp: {review.timestamp}")
            p.drawString(30, y - 60, f"Rating: {review.rating}")
            y -= 90
            if y < 30:
                p.showPage()
                p.setFont("FreeSerif", 12) 
                y = height - 30

        p.save()
        return response

    export_as_pdf.short_description = "Export Selected as PDF"


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'timestamp')

    def total_mined(self, request):
        total_mined = sum(transaction.amount for transaction in TransactionModel.objects.filter(sender="Система"))
        total_bonus = sum(transaction.amount for transaction in TransactionModel.objects.filter(sender="Система", recipient="admin"))
        total_given = sum(transaction.amount for transaction in TransactionModel.objects.exclude(sender="Система"))
        return total_mined, total_given, total_bonus

    def changelist_view(self, request, extra_context=None):
        total_mined, total_given, total_bonus = self.total_mined(request)
        extra_context = extra_context or {}
        extra_context['total_mined'] = total_mined
        extra_context['total_given'] = total_given
        extra_context['total_bonus'] = total_bonus
        return super().changelist_view(request, extra_context=extra_context)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'rating', 'bonus_balance')
    search_fields = ('user__username', 'user__email')  # Позволяет искать по имени пользователя и email
    list_filter = ('rating',)  # Добавляет фильтр по рейтингу справа

# Функция для экспорта в CSV
def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response
export_as_csv.short_description = "Export Selected as CSV"

# Функция для экспорта в PDF
def export_as_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(modeladmin.model._meta.model_name)

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("FreeSerif", 12)  # Использование шрифта
    width, height = letter
    y = height - 30

    for obj in queryset:
        for field_name in modeladmin.list_display:
            value = getattr(obj, field_name, "")
            if isinstance(value, str):
                value = value.encode('utf-8').decode('utf-8')  # Убедитесь, что строка в формате UTF-8
            p.drawString(30, y, f"{field_name}: {value}")
            y -= 15
            if y < 40:
                p.showPage()
                p.setFont("FreeSerif", 12)  # Установите шрифт для новой страницы
                y = height - 30

    p.save()
    return response

export_as_pdf.short_description = "Export Selected as PDF"

# Админ-класс для Company
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating')
    actions = [export_as_csv, export_as_pdf]

# Админ-класс для TransactionModel
class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'timestamp')
    actions = [export_as_csv, export_as_pdf]

# Админ-класс для Profile
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'rating', 'bonus_balance')
    actions = [export_as_csv, export_as_pdf]

admin.site.register(TransactionModel, TransactionAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Company, CompanyAdmin)