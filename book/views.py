from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Case, When

from .models import Book, RelationBookWord, Word, WordTranslation




@csrf_protect
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


def word_list(request, index):
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

    try:
        index = int(index) - 1
        if not (0 <= index < len(book_list)):
            return redirect("book_list")
    except ValueError:
        return redirect("book_list")
    
    book = book_list[index]

    # 获取该书籍下所有单词的关联记录，只查询一次获取所需的word信息
    relation_book_word_list = RelationBookWord.objects.select_related('bv_voc_id').filter(
        bv_book_id=book
    )

    # 获取所有单词ID
    word_ids = [relation.bv_voc_id.id for relation in relation_book_word_list]

    # 批量获取单词翻译，使用values_list减少数据传输
    translations = WordTranslation.objects.filter(
        word_id__in=word_ids
    ).values_list('word_id', 'translation')
    
    # 构建翻译字典
    word_translations = {}
    for word_id, translation in translations:
        if word_id not in word_translations:
            word_translations[word_id] = []
        word_translations[word_id].append(translation)

    # 组装单词详情，使用已经通过select_related获取的word信息
    word_details = []
    for relation in relation_book_word_list:
        word = relation.bv_voc_id  # 直接使用已经获取的word对象
        word_details.append({
            'word': word,
            'phonetic_uk': word.vc_phonetic_uk,
            'translations': word_translations.get(word.id, [])
        })

    # 分页
    page = request.GET.get("page", 1)
    paginator = Paginator(word_details, 20)
    page_obj = paginator.get_page(page)

    return render(request, "book/word_list.html", {
        "book": book,
        "page_obj": page_obj,
        "index": index + 1
    })
