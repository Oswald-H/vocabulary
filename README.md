# vocabulary

## 环境配置
建议在目录下用 venv
```python
pip install -r requirements.txt
```
使用 [DictionaryData](https://github.com/LinXueyuanStdio/DictionaryData.git) 作为数据库  
下载到根目录下解压 `relation_book_word.zip`
## 导入数据库
```
python manage.py makemigrations
python manage.py migrate
```
从csv导入单词书进数据库
```
python manage.py csv2sql --add
```
这一步骤大概要花1分钟
## 启动
```
python manage.py runserver
```
进入 `http://127.0.0.1:8000/` 就能看到单词表了
