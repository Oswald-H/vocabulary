from django.urls import path
from . import views

urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("<int:index>/", views.word_list, name="word_list"),
    path('word/write/<int:index>/', views.word_write, name='word_write'),
    # 其他URL配置
    path('update_current_word_index/', views.update_current_word_index, name='update_current_word_index'),
    path('save_counts/', views.save_counts, name='save_counts'),
]
