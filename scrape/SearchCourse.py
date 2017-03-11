from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()


#es.indices.delete(index='lcourses', ignore=[400, 404]) 

class SearchCourse():

    '''
    Parameter filter takes a string name of the index 
    Parameter query takes the string query 
    Sideeffects : Outputs the result of searching the query in the index by matching against courseInfo , classNum or instructor field 
                  of each entry the given index name. 

    '''

    def searchCourses(filter,query):
        queryLower = query.lower()
        es.indices.refresh(index="cs")
        res = es.search(index="cs", body=
                        {"query":{"bool":{"should": [ {"wildcard": {"courseInfo":"*"+queryLower+"*"}},{"wildcard": {"classNum":"*"+queryLower+"*"}},{"wildcard": {"instructor":"*"+queryLower+"*"}} ]  }}})
        print("Got %d search results:" % res['hits']['total'])
        for hit in res['hits']['hits']:
            print("%(classNum)s %(courseInfo)s: %(instructor)s" % hit["_source"])


    searchCourses('cs','cda')

