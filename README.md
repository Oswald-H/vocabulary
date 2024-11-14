# vocabulary

## 环境配置
建议在目录下用 venv
```python
pip install -r requirements.txt
```
## 导入数据库
```
python manage.py csv2sql --add
```
这一步骤大概要花1分钟
## 启动
```
python manage.py runserver
```
进入 `/book/` 目录下就能看到单词表了
