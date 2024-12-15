import random
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.db.models import Case, When
from django.http import JsonResponse

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

    # 清除相关会话变量
    request.session.pop(f'correct_count_{page}', None)
    request.session.pop(f'incorrect_count_{page}', None)
    request.session.pop(f'current_word_index_{page}', None)

    return render(request, "book/word_list.html", {
        "book": book,
        "page_obj": page_obj,
        "index": index + 1
    })


def word_write(request, index):
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

    # 获取当前页的单词列表
    words_on_page = list(page_obj.object_list)

    # 获取当前单词索引
    #current_word_index = request.session.get(f'current_word_index_{page}', 0)
    session_key = f'current_word_index_{page}'
    current_word_index = request.session.get(session_key, 0)

    # 如果当前单词索引超出范围，则重置为0
    if current_word_index >= len(words_on_page):
        current_word_index = 0
        #request.session[f'current_word_index_{page}'] = current_word_index
        request.session[session_key] = current_word_index
    # 获取当前单词
    random_word = words_on_page[current_word_index] if words_on_page else None


    # 初始化正确数和错误数
    correct_count_key = f'correct_count_{page}'
    incorrect_count_key = f'incorrect_count_{page}'

    # 检查是否有新的请求参数来重置计数
    if request.GET.get('reset_counts', 'false') == 'true':
        correct_count = 0
        incorrect_count = 0
        current_word_index = 0
        request.session[correct_count_key] = correct_count
        request.session[incorrect_count_key] = incorrect_count
        request.session[session_key] = current_word_index
    else:
        correct_count = request.session.get(correct_count_key, 0)
        incorrect_count = request.session.get(incorrect_count_key, 0)

    return render(request, 'book/word_write.html', {
        "book": book,
        "page_obj": page_obj,
        "index": index + 1,
        "random_word": random_word,
        "current_index": current_word_index,
        "total_count": len(words_on_page),
        "next_url": f"?page={page}",
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
    })

@csrf_exempt
def save_counts(request):
    if request.method == 'POST':
        page = request.POST.get('page')
        correct_count = request.POST.get('correct_count')
        incorrect_count = request.POST.get('incorrect_count')

        correct_count_key = f'correct_count_{page}'
        incorrect_count_key = f'incorrect_count_{page}'

        request.session[correct_count_key] = int(correct_count)
        request.session[incorrect_count_key] = int(incorrect_count)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def update_current_word_index(request):
    if request.method == 'POST':
        page = request.POST.get('page')
        current_word_index = request.POST.get('current_word_index')
        #request.session[f'current_word_index_{page}'] = int(current_word_index)
        session_key = f'current_word_index_{page}'
        request.session[session_key] = int(current_word_index)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})



