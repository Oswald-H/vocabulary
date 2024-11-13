from django.db import models


class Book(models.Model):
    bk_id = models.CharField(max_length=255)
    bk_parent_id = models.CharField(max_length=255)
    bk_level = models.IntegerField()
    bk_order = models.FloatField()
    bk_name = models.CharField(max_length=255)
    bk_item_num = models.IntegerField()
    bk_author = models.CharField(max_length=255)
    bk_book = models.CharField(max_length=255)
    bk_comment = models.TextField()
    bk_orgnization = models.CharField(max_length=255)
    bk_publisher = models.CharField(max_length=255)
    bk_version = models.CharField(max_length=255)
    bk_flag = models.CharField(max_length=255)

    def __str__(self):
        return self.bk_name


class Word(models.Model):
    vc_id = models.CharField(max_length=255, unique=True)
    vc_vocabulary = models.CharField(max_length=255)
    vc_phonetic_uk = models.CharField(max_length=255)
    vc_phonetic_us = models.CharField(max_length=255)
    vc_frequency = models.FloatField()
    vc_difficulty = models.IntegerField()
    vc_acknowledge_rate = models.FloatField()

    def __str__(self):
        return self.vc_vocabulary


class WordTranslation(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    translation = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.word.vc_vocabulary} - {self.translation}"


class RelationBookWord(models.Model):
    bv_id = models.CharField(max_length=255, unique=True)
    bv_book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    bv_voc_id = models.ForeignKey(Word, on_delete=models.CASCADE)
    bv_flag = models.CharField(max_length=255)
    bv_tag = models.CharField(max_length=255)
    bv_order = models.IntegerField()

    def __str__(self):
        return f"{self.bv_book_id.bk_name} - {self.bv_voc_id.vc_vocabulary}"
