from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page

from .models import Book, RelationBookWord, Word, WordTranslation


@csrf_protect
def book_list(request):
    # Get book list
    book_list = Book.objects.filter(
        bk_name__in=[
            "四级词汇乱序版",
            "四级词汇正序版",
            "六级词汇正序版",
            "六级词汇乱序版",
            "TOEFL托福词汇正序版",
            "TOEFL托福词汇乱序版",
        ]
    )

    index_book_id = request.GET.get("index_id")

    if index_book_id is not None:
        try:
            index_book_id = int(index_book_id) - 1
        except ValueError:
            return redirect("book_list")

        if 0 <= index_book_id < len(book_list):
            book_id = book_list[index_book_id].bk_id
            response = render(request, "book/book_list.html", {"book_list": book_list})
            response.set_cookie("book_id", book_id, max_age=60 * 60 * 24)
            return response

    return render(request, "book/book_list.html", {"book_list": book_list})


@cache_page(60 * 60)
def word_list(request, index):
    # Get book list
    book_list = Book.objects.filter(
        bk_name__in=[
            "四级词汇乱序版",
            "四级词汇正序版",
            "六级词汇正序版",
            "六级词汇乱序版",
            "TOEFL托福词汇正序版",
            "TOEFL托福词汇乱序版",
        ]
    )

    # Get book index
    try:
        index = int(index) - 1  # transfer to 0 index
        if not (0 <= index < len(book_list)):
            return redirect("book_list")
    except ValueError:
        return redirect("book_list")
    
    # Get book object
    book = book_list[index]

    # Get words
    relation_book_word_list = RelationBookWord.objects.filter(bv_book_id=book)
    words = [relation.bv_voc_id for relation in relation_book_word_list]

    # more detail
    word_details = []
    for word in words:
        translations = WordTranslation.objects.filter(word=word)
        translation_list = [t.translation for t in translations]
        word_details.append({
            'word': word,
            'phonetic_uk': word.vc_phonetic_uk,
            'phonetic_us': word.vc_phonetic_us,
            'translations': translation_list
        })

    # Pagination
    page = request.GET.get("page", 1)  # default page 1
    paginator = Paginator(word_details, 20)
    page_obj = paginator.get_page(page)

    return render(request, "book/word_list.html", {"book": book, "page_obj": page_obj, "index": index + 1})

