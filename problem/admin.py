from django.contrib import admin
from django.utils.html import format_html

from .models import ProblemFile, Problem, Question, QuestionTag, QuestionSet

admin.site.site_header = 'Problem Admin'
# admin.site.register(ProblemFile)
# admin.site.register(Problem)
# admin.site.register(Question)
admin.site.register(QuestionTag)
admin.site.register(QuestionSet)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('_id',
                    'title',
                    'description',
                    'created_by',
                    'difficulty',
                    'date')

    list_display_links = ('_id', 'title', 'description')

    list_per_page = 10

    search_fields = ('title', 'description')

    list_filter = ('created_by', 'difficulty')

    def date(self, obj):
        return format_html(
            '<span style="color: green;">{}</span>',
            obj.create_time.strftime('%Y-%m-%d %H:%M:%S')
        )

    filter_horizontal = ('tags',)


admin.site.register(Question, QuestionAdmin)

