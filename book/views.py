from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.db.models import Case, When

from .models import Book, RelationBookWord, WordTranslation


@csrf_protect
@cache_page(60 * 60 * 24)
def book_list(request):
    book_names = [
        "TOEFL托福词汇正序版",
        "TOEFL托福词汇乱序版",
        "四级词汇正序版",
        "四级词汇乱序版",
        "六级词汇正序版",
        "六级词汇乱序版",
    ]

    book_list = Book.objects.filter(bk_name__in=book_names).distinct().annotate(
        order=Case(
            *[When(bk_name=name, then=order) for order, name in enumerate(book_names)]
        )
    ).order_by('order')

    unique_books = list(dict.fromkeys(book_list))[:6]

    index_book_id = request.GET.get("index_id")

    if index_book_id is not None:
        try:
            index_book_id = int(index_book_id) - 1
        except ValueError:
            return redirect("book_list")

        if 0 <= index_book_id < len(unique_books):
            book_id = unique_books[index_book_id].bk_id
            response = render(request, "book/book_list.html", {"book_list": unique_books})
            response.set_cookie("book_id", book_id, max_age=60 * 60 * 24)
            return response

    return render(request, "book/book_list.html", {"book_list": unique_books})


@cache_page(60 * 60 * 24)
def word_list(request, index):
    book_list = Book.objects.filter(
        bk_name__in=[
            "TOEFL托福词汇正序版",
            "TOEFL托福词汇乱序版",
            "四级词汇正序版",
            "四级词汇乱序版",
            "六级词汇正序版",
            "六级词汇乱序版",
        ]
    ).distinct().annotate(
        order=Case(
            *[When(bk_name=name, then=order) for order, name in enumerate([
                "TOEFL托福词汇正序版",
                "TOEFL托福词汇乱序版",
                "四级词汇正序版",
                "四级词汇乱序版",
                "六级词汇正序版",
                "六级词汇乱序版",
            ])]
        )
    ).order_by('order')

    try:
        index = int(index) - 1
        if not (0 <= index < len(book_list)):
            return redirect("book_list")
    except ValueError:
        return redirect("book_list")
    
    book = book_list[index]

    relation_book_word_list = RelationBookWord.objects.filter(bv_book_id=book).only('bv_voc_id')
    words = [relation.bv_voc_id for relation in relation_book_word_list]

    word_details = []
    for word in words:
        translations = WordTranslation.objects.filter(word=word).only('translation')
        translation_list = [t.translation for t in translations]
        word_details.append({
            'word': word,
            'phonetic_uk': word.vc_phonetic_uk,
            'translations': translation_list
        })

    page = request.GET.get("page", 1)
    paginator = Paginator(word_details, 20)
    page_obj = paginator.get_page(page)


    return render(request, "book/word_list.html", {"book": book, "page_obj": page_obj, "index": index + 1})
