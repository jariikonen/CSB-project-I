from django.contrib import admin

from .models import Choice, Question, Voter, Message, SecurityQuestion, SecurityAnswer


class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['question_text']}),
        ('Date information',    {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInLine]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Voter)
admin.site.register(Message)
admin.site.register(SecurityQuestion)
admin.site.register(SecurityAnswer)
