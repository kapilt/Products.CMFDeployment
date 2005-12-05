#class ContentMap

from BTrees.OOBTree import OOBTree
import pprint
from URIResolver import normalize
from Namespace import *

class ContentMap(SimpleItem):

    meta_type = 'Content Map'

    def __init__(self, id=None, resolver=None):
        self.content_map= OOBTree()
        self.resolver=resolver
        self.id= id
        
    def addContentMap(self, url_key, physical_path):
        #add a new descriptor url as a key
        #and his referencer as a value
        result = self.content_map.get(url_key)
        if(result):
            #look if it is already in the list
            if not (physical_path in self.content_map[url_key]):
                self.content_map[url_key].append(physical_path)
        else:
            self.content_map[url_key]= [physical_path]
        
        
    def getKeyURL(self, descriptor):
        relative_url = descriptor.getSourcePath() or descriptor.content_url
        content_path = descriptor.getContentPath()
        
        if content_path is None:
            content_path=''
            mlen = len(self.resolver.mount_path)                
            url_context  = relative_url[:relative_url.rfind('/')]
            cut2= url_context.rfind('/')
            if (cut2 != -1):
                content_path = url_context[url_context.rfind('/'):]

        nu = normalize('/'.join( (self.resolver.target_path,
                                            content_path,
                                            descriptor.getFileName() ) ),
                                 '/'
                                 )
        return nu
        
        
    def getReverseDependencies(self, descriptor): #url):  
        #get the referencers of a descriptor       
        nu= self.getKeyURL(descriptor)
        result= self.content_map.get(nu)
        if (not result):
            result= []
        return result
        
        
    def pprint(self):
        pprint.pprint(dict(self.content_map.items()))
        
        
    def clean(self, descriptor):
        #clean the content map when an object has been deleted
        #remove all the urls in the contentmap 
        key_url = self.getKeyURL(descriptor)
        if key_url in self.content_map.items():
            del self.content_map[key_url]
        
        value_url= "/"+descriptor.getContentURL()
        for k,v in self.content_map.items():
            if value_url in v:
                self.content_map[k].remove(value_url)       
        
        