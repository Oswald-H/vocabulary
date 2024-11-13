from django.shortcuts import render
from .models import Book, Word, WordTranslation, RelationBookWord


def book_list(request):
    book_list = Book.objects.filter(bk_name__in=[
        "四级词汇乱序版",
        "四级词汇正序版",
        "大学英语四级词汇",
        "四级英语新大纲词汇表",
        "六级词汇正序版",
        "六级词汇乱序版",
        "六级英语新大纲词汇表",
        "大学英语六级词汇",
        "大学英语四六级词组必备",
        "托福词组必备",
        "托福词汇",
        "TOEFL托福词汇正序版",
        "TOEFL托福词汇乱序版",
        "雅思词汇",
        "雅思词组必备"
    ])
    return render(request, 'book/book_list.html', {'book_list': book_list})

