import pandas as pd
from django.core.management.base import BaseCommand
from book.models import Book, Word, WordTranslation, RelationBookWord
import logging

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

    def handle(self, *args, **kwargs):
        # Get CLI arguments
        add_data = kwargs['add']
        delete_data = kwargs['delete']

        # If the --delete parameter is passed, delete all data
        if delete_data:
            self.clear_data()

        # If the --add parameter is passed, import data
        if add_data:
            self.import_data()

        # Success messages.
        if add_data:
            self.stdout.write(self.style.SUCCESS('[+] Successfully imported CSV data'))
        if delete_data:
            self.stdout.write(self.style.SUCCESS('[+] Successfully cleared all data'))

    def import_data(self):
        path_dict = "./dict/"
        
        try:
            # Import Book information
            self.stdout.write("[-] Importing Book data...")
            df_book = pd.read_csv(path_dict + 'book.csv', delimiter=">", encoding="utf-8")
            books = [
                Book(
                    bk_id=row['bk_id'],
                    bk_parent_id=row['bk_parent_id'],
                    bk_level=row['bk_level'],
                    bk_order=row['bk_order'],
                    bk_name=row['bk_name'],
                    bk_item_num=row['bk_item_num'],
                    bk_author=row['bk_author'],
                    bk_book=row['bk_book'],
                    bk_comment=row['bk_comment'],
                    bk_orgnization=row['bk_orgnization'],
                    bk_publisher=row['bk_publisher'],
                    bk_version=row['bk_version'],
                    bk_flag=row['bk_flag']
                ) for _, row in df_book.iterrows()
            ]
            Book.objects.bulk_create(books)
            self.stdout.write(self.style.SUCCESS('[+] Successfully imported Book data'))

            # Import Word information
            self.stdout.write("[-] Importing Word data...")
            df_word = pd.read_csv(path_dict + 'word.csv', delimiter=">", encoding="utf-8")
            words = [
                Word(
                    vc_id=row['vc_id'],
                    vc_vocabulary=row['vc_vocabulary'],
                    vc_phonetic_uk=row['vc_phonetic_uk'],
                    vc_phonetic_us=row['vc_phonetic_us'],
                    vc_frequency=row['vc_frequency'],
                    vc_difficulty=row['vc_difficulty'],
                    vc_acknowledge_rate=row['vc_acknowledge_rate']
                ) for _, row in df_word.iterrows()
            ]
            Word.objects.bulk_create(words)
            self.stdout.write(self.style.SUCCESS('[+] Successfully imported Word data'))

            # Import WordTranslation information
            self.stdout.write("[-] Importing WordTranslation data...")
            df_translation = pd.read_csv(path_dict + 'word_translation.csv', encoding="utf-8")
            word_dict = {word.vc_vocabulary: word for word in Word.objects.all()}
            translations = [
                WordTranslation(word=word_dict[row['word']], translation=row['translation'])
                for _, row in df_translation.iterrows() if row['word'] in word_dict
            ]
            WordTranslation.objects.bulk_create(translations)
            self.stdout.write(self.style.SUCCESS('[+] Successfully imported WordTranslation data'))

            # Import RelationBookWord information
            self.stdout.write("[-] Importing RelationBookWord data...")
            df_relation = pd.read_csv(path_dict + 'relation_book_word/relation_book_word.csv', delimiter=">", encoding="utf-8")
            book_dict = {book.bk_id: book for book in Book.objects.all()}
            word_dict = {word.vc_id: word for word in Word.objects.all()}
            relations = [
                RelationBookWord(
                    bv_id=row['bv_id'],
                    bv_book_id=book_dict[row['bv_book_id']],
                    bv_voc_id=word_dict[row['bv_voc_id']],
                    bv_flag=row['bv_flag'],
                    bv_tag=row['bv_tag'],
                    bv_order=row['bv_order']
                ) for _, row in df_relation.iterrows() if row['bv_book_id'] in book_dict and row['bv_voc_id'] in word_dict
            ]
            RelationBookWord.objects.bulk_create(relations)
            self.stdout.write(self.style.SUCCESS('[+] Successfully imported RelationBookWord data'))

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
            Book.objects.all().delete()
            Word.objects.all().delete()
            WordTranslation.objects.all().delete()
            RelationBookWord.objects.all().delete()
        except Exception as e:
            logger.error(f"An error occurred while clearing data: {e}")
            self.stderr.write(self.style.ERROR(f"An error occurred while clearing data: {e}"))