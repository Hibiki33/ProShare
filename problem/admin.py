from django.contrib import admin
from django.utils.html import format_html

from .models import ProblemFile, Problem, Question, QuestionTag, QuestionSet

admin.site.site_header = 'ProShare Admin'
# admin.site.register(ProblemFile)
# admin.site.register(Problem)
# admin.site.register(Question)
# admin.site.register(QuestionTag)
# admin.site.register(QuestionSet)


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


class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_number')
    list_display_links = ('name',)

    search_fields = ('name',)

    list_per_page = 10

    def question_number(self, obj):
        return obj.questions.count()


class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'belonging',)
    list_display_links = ('id', 'name')

    search_fields = ('name', 'id')

    list_per_page = 10

    def belonging(self, obj):
        return obj.belongs_to.name if obj.belongs_to is not None else 'public'


admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionTag, QuestionTagAdmin)
admin.site.register(QuestionSet, QuestionSetAdmin)

