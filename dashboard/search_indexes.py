from haystack.indexes import *
from haystack import site
from dashboard.models import *

class UserDocumentsIndex(SearchIndex):
    text 		=CharField(document =True ,use_template=True)
    file_name	=CharField(model_attr='file_name')
    
    
site.register(upload_documents,UserDocumentsIndex)

