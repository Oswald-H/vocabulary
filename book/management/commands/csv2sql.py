import pandas as pd
from django.core.management.base import BaseCommand
from book.models import Book, Word, WordTranslation, RelationBookWord
import logging
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import or delete data from CSV files into the database'

    def add_arguments(self, parser):
        # Add parameters --add and --delete
        parser.add_argument(
            '--add', 
            action='store_true', 
            help='Add data from CSV files to the database'
        )
        parser.add_argument(
            '--delete', 
            action='store_true', 
            help='Delete all data from the database'
        )
        parser.add_argument(
            '--path',
            type=str,
            default='./DictionaryData/',
            help='Path to directory containing CSV files'
        )

    def handle(self, *args, **kwargs):
        # Get CLI arguments
        add_data = kwargs['add']
        delete_data = kwargs['delete']
        path_dict = kwargs['path']

        # Check if path exists
        if add_data and not os.path.exists(path_dict):
            self.stderr.write(self.style.ERROR(f'Path does not exist: {path_dict}'))
            return

        # If the --delete parameter is passed, delete all data
        if delete_data:
            self.clear_data()

        # If the --add parameter is passed, import data
        if add_data:
            self.import_data(path_dict)

        # Success messages
        if add_data:
            self.stdout.write(self.style.SUCCESS('[+] Successfully imported CSV data'))
        if delete_data:
            self.stdout.write(self.style.SUCCESS('[+] Successfully cleared all data'))

    def import_data(self, path_dict):
        try:
            # Define target books
            target_books = [
                "TOEFL托福词汇正序版",
                "TOEFL托福词汇乱序版",
                "四级词汇正序版", 
                "四级词汇乱序版",
                "六级词汇正序版",
                "六级词汇乱序版"
            ]

            # Import Book information
            self.stdout.write("[-] Importing Book data...")
            df_book = pd.read_csv(os.path.join(path_dict, 'book.csv'), delimiter=">", encoding="utf-8")
            df_book = df_book[df_book['bk_name'].isin(target_books)]
            books = [
                Book(
                    bk_id=row['bk_id'],
                    bk_name=row['bk_name'],
                    bk_item_num=row['bk_item_num']
                ) for _, row in df_book.iterrows()
            ][1:]
            Book.objects.bulk_create(books, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(self.style.WARNING('[+] Successfully imported Book data'))

            # Get word IDs from target books
            df_relation = pd.read_csv(os.path.join(path_dict, 'relation_book_word', 'relation_book_word.csv'), delimiter=">", encoding="utf-8")
            target_book_ids = df_book['bk_id'].tolist()
            df_relation = df_relation[df_relation['bv_book_id'].isin(target_book_ids)]
            target_word_ids = df_relation['bv_voc_id'].unique().tolist()

            # Import Word information
            self.stdout.write("[-] Importing Word data...")
            df_word = pd.read_csv(os.path.join(path_dict, 'word.csv'), delimiter=">", encoding="utf-8")
            df_word = df_word[df_word['vc_id'].isin(target_word_ids)]
            words = [
                Word(
                    vc_id=row['vc_id'],
                    vc_vocabulary=row['vc_vocabulary'],
                    vc_phonetic_uk=row['vc_phonetic_uk'] or ''
                    # vc_phonetic_us=row['vc_phonetic_us'] or ''
                ) for _, row in df_word.iterrows()
            ]
            Word.objects.bulk_create(words, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(self.style.WARNING('[+] Successfully imported Word data'))

            # Import WordTranslation information
            self.stdout.write("[-] Importing WordTranslation data...")
            df_translation = pd.read_csv(os.path.join(path_dict, 'word_translation.csv'), encoding="utf-8")
            target_vocabularies = df_word['vc_vocabulary'].tolist()
            df_translation = df_translation[df_translation['word'].isin(target_vocabularies)]
            word_dict = {word.vc_vocabulary: word for word in Word.objects.all()}
            translations = [
                WordTranslation(
                    word=word_dict[row['word']], 
                    translation=row['translation']
                ) for _, row in df_translation.iterrows() if row['word'] in word_dict
            ]
            WordTranslation.objects.bulk_create(translations, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(self.style.WARNING('[+] Successfully imported WordTranslation data'))

            # Import RelationBookWord information
            self.stdout.write("[-] Importing RelationBookWord data...")
            book_dict = {book.bk_id: book for book in Book.objects.all()}
            word_dict = {word.vc_id: word for word in Word.objects.all()}
            relations = [
                RelationBookWord(
                    bv_id=row['bv_id'],
                    bv_book_id=book_dict[row['bv_book_id']],
                    bv_voc_id=word_dict[row['bv_voc_id']]
                ) for _, row in df_relation.iterrows() if row['bv_book_id'] in book_dict and row['bv_voc_id'] in word_dict
            ]
            RelationBookWord.objects.bulk_create(relations, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(self.style.WARNING('[+] Successfully imported RelationBookWord data'))

        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"File not found: {e}"))
        except pd.errors.ParserError as e:
            self.stderr.write(self.style.ERROR(f"CSV parsing error: {e}"))
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

    def clear_data(self):
        # Clear all data
        self.stdout.write("[-] Clearing data...")
        try:
            RelationBookWord.objects.all().delete()
            WordTranslation.objects.all().delete()
            Word.objects.all().delete()
            Book.objects.all().delete()
        except Exception as e:
            logger.error(f"An error occurred while clearing data: {e}")
            self.stderr.write(self.style.ERROR(f"An error occurred while clearing data: {e}"))