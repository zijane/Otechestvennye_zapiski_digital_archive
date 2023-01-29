import sys
import pymongo
import xmltodict
from bson import ObjectId
import json
import re
#from model.spellchecker import spellCorrect, read_corpus, Vocabulary, CharLM, check, probMaker
#import torch
from flask_cors import CORS
from transliterator.translit import translit_text
from flask import Flask, request, render_template, url_for, get_template_attribute, render_template_string, jsonify, send_file
#from sklearn.metrics import confusion_matrix

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

username = 'zijane'
password = 'newjayzp-assword231197'
client = pymongo.MongoClient('mongodb://%s:%s@172.20.0.6' % (username, password))
db = client['otechestvennie_zapiski']
text_collection = db.text_collection
pages = db.pages
dblemmas = db.lemmas
db_editpages = db.edit_pages
to_edit_pages = db.to_edit_pages



def translit(text):
    tokens = translit_text(text)
    new_text = ''
    for token in tokens:
        new_text = new_text + token.punct_prev + token.word + token.punct_next + ' '
    return new_text



#def load_model():
#    data = read_corpus('/home/zhenya/projects/newflasktest/model/vocabulary.txt')
#    V = Vocabulary(data)
#    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
#    model = CharLM(V.vocab_size, word_len=V.pad_len, emb_dim=128, hidden_size=64)
#    model_filename = "/home/zhenya/projects/newflasktest/model/old_rus_lm.pth"
#    model.load_state_dict(torch.load(model_filename, map_location={'cuda:0': 'cpu'}))
#    correct = spellCorrect(V=V, model=model)
#    return correct

#correct= load_model()

@app.route('/get_volume_titles',methods=['GET', 'POST', 'DELETE', 'PATCH'])
def get_volume_titles():    # СПИСОК ВЫДАЧИ ПОПРАВЛЕН! ФРОНТ РАБОТАЕТ# проверить, чтобы печаталось без повторений
    titles = [[title["volume_title"], title["number_of_volume"]] for title in pages.find({"volume_title": {"$exists": True}}, projection={'_id': False})]
    titles = [list(i) for i in set(tuple(i) for i in titles)]
    titles = sorted(titles, key=lambda k: k[1])
    vol_to_edit = [[title["volume_title"], title["number_of_volume"]] for title in to_edit_pages.find({"volume_title": {"$exists": True}}, projection={'_id': False})]
    #titles = set(titles)
    return jsonify(titles=titles, titles_to_edit=vol_to_edit)
    


def get_page(number_of_volume, id): #СПИСОК ВЫДАЧИ ПОПРАВЛЕН!!!! correct,
    print(number_of_volume, id)
    page = [page for page in to_edit_pages.find({ 'number_of_volume': int(number_of_volume), "pb": int(id)}, projection={'_id': False})]
    #page = []
    #for part_page in unedit_page:
    #    p = part_page['p'].split('\n')
    #    p = '\n'.join(text for text in p) #check(correct, text) 
    #    part_page['p'] = p
    #    page.append(part_page)
    return page
    
    

@app.route('/get_years', methods=['GET', 'POST'])
def get_years():
    list_of_years = [int(year) for year in pages.distinct('year')]
    list_of_years.sort()
    return jsonify(result=list_of_years)



@app.route('/years_aggr/<int:n>', methods=['GET', 'POST'])
def years_aggr(n):
    l = []
    for item in pages.find({'year': n, 'number_of_volume': {'$exists': True},  'volume_title': {'$exists': True}}, # поменять скачать tei на скачать xml,  узнать, можно ли добавить больше полей
                           projection={'_id': False, 'p': False, 'head': False, 'pb': False}):
        if item not in l:
            l.append(item)
        else:
            continue
    newlist = sorted(l, key=lambda k: k['number_of_volume'])
    return jsonify(result=newlist)
    
    
 
@app.route('/download/<int:n>', methods=['GET', 'POST'])
def download(n):
    return send_file(f"static/data/volume_{n}.xml", as_attachment=True)



#def search_engine(data): #СПИСОК ВЫДАЧИ ПОПРАВЛЕН!!!!
#    search_word = data
#    print(search_word)
 #   if len(data.split(' ')) <= 1:
#        results = list(pages.find({"$text": {"$search": data}}, projection={'_id': False}))
       # count = len(results)
        #if len(results) == 0:
         #   results = ['В нашем копусе не нашлось результатов.', '', '']
       # else:
        #    res = []
         #   for r in results:
         #       l = {"head":'Разделъ и номеръ страницы: {}'.format(str(r['head'])), "numberOfVolume": 'Томъ {}'.format(r['number_of_volume']),"year": 'Годъ {}'.format(r['year']), "pText": r['p'].replace(str(r['head']), '')}
         #       res.append(l)
        #        text = r['p'].replace(str(r['head']), '')
        #        new_text = translit(u"{}".format(text))
        #        disclaimer = {"head": 'Версия отрывка в современной орфографии', "numberOfVolume": '',"year": '', "pText": ''}
        #        edit_p = {"head":'Раздел и номер страницы: u{}'.format(translit_text(str(r['head']))), "numberOfVolume": 'Том {}'.format(r['number_of_volume']),"year": 'Год {}'.format(r['year']), "pText": new_text}
         #       res.append(disclaimer)
       #         res.append(edit_p)
   # elif len(data.split(' ')) > 1:
    #    results = list(pages.find({"$text": {"$search": "\"{}\"".format(data)}}, projection={'_id': False}))
    #    count = len(results)
    #    if count == 0:
    #        results = ['В нашем копусе не нашлось результатов.', '', '']
    #    else:
     #       res = []
     #       for r in results:
    #            l = {"head":'Раздел и номер страницы: {}'.format(str(r['head'])), "numberOfVolume": 'Том {}'.format(r['number_of_volume']), "year": 'Год {}'.format(r['year']), "pText": r['p'].replace(str(r['head']), '')}
    #            res.append(l)
     #           text = r['p'].replace(str(r['head']), '')
    #            new_text = translit(u"{}".format(text))
    #            disclaimer = {"head": 'Версия отрывка в современной орфографии', "numberOfVolume": '',"year": '', "pText": ''}
    #            edit_p = {"head":'Раздел и номер страницы: u{}'.format(translit_text(str(r['head']))), "numberOfVolume": 'Том {}'.format(r['number_of_volume']),"year": 'Год {}'.format(r['year']), "pText": new_text}
    #            res.append(disclaimer)
    #            res.append(edit_p)
   # results = res
   # print(res)
   # return results, count
 
 
@app.route('/search_engine/', methods=['GET', 'POST'])
def search_engine():
    post_data = request.get_json()
    data = post_data.get('text')
    results = list(pages.find({"$text": {"$search": data}}, projection = {'pb': False}))
    for r in results:
        r1 = r['_id']
        r['_id'] = str(r1).strip("ObjectId()\'")
    counted = len(results)
    return jsonify(result=results, count=counted)
    
    
    
    
    
    
@app.route('/translate/', methods=['GET', 'POST'])
def translate():
    post_data = request.get_json()
    to_translate = post_data.get('text')
    tokens = translit_text(u"{}".format(to_translate))
    new_text = ''
    for token in tokens:
        new_text = new_text + token.punct_prev + token.word + token.punct_next + ' '
    response_object = {}
    response_object['_id'] = post_data.get('_id')
    response_object['translation'] = new_text
    return jsonify(response_object)


def create_js(number_of_volume, id): 
    result = get_page(number_of_volume, int(id))[0] #correct,
    print(result)
    file = open('templates/js_template.txt')
    template = file.read()
    if 'p' in result:
        template = template.replace('HEader', str(result['head']))
        template = template.replace('PAragraph', str(result['p'].replace(str(result['head']), '')))
        template = template.replace('Key features', str(result['pb']))
    else:
        template = template.replace('HEader', str(result['second_title']))
        template = template.replace('PAragraph', str(result['epigraph'] + '\\t' + result['meta'] + ' ' + result['censorship_approval']))
        template = template.replace('Key features', str(result['pb']))
    return template
    #with open('static/js/main.js', 'w') as fj:
    #   print(template, file= fj)
    #results= json.loads(results)
    
  

@app.route('/')
def index():
    return render_template('index.html', page_name='главная')


@app.route('/corpus/')
def corpus():
    return render_template('corpus.html', page_name = "корпус") 


@app.route('/')
@app.route('/about/')
def about():
    return render_template('about.html', page_name='о проекте')
    

@app.route('/')    
@app.route('/search/')
def search():
    return render_template('search.html', page_name = "поиск") 
    
@app.route('/')
@app.route('/volume_<int:volume_id>/')
def nav(volume_id):
    return render_template ('navigation.html')
  

  
@app.route('/get_list_of_pages',methods=['GET', 'POST', 'DELETE', 'PATCH'])
def get_list_of_pages(): #СПИСОК ВЫДАЧИ ПОПРАВЛЕН!!!!  РАБОТАЕТ ФРОНТ 
    print(request.url_rule)
    #volume_id = int(re.findall("\d" ,str(request.url_rule))[0])
    volume_id= 2
    results = [int(page['pb']) for page in to_edit_pages.find({'number_of_volume': int(volume_id), "pb": {"$gt": 2}}, projection={'_id': False})]
    try:
        return jsonify(result= results)
    except Exception as e:
        return str(e)



#функция, которую запускает AJAX-запрос
@app.route('/background_process', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def background_process():
    try:
        word = request.args.get('search', 0, type=str)
        # это необязательно - просто привожу к нижнему регистру. Можно сюда вставить любую предобработку.
        results, count = search_engine(word)
        # раскомментировать нижнюю строку и закомментировать верхнюю, чтобы проверить поиск по базе
        # results = search_engine2(lang.lower())
        #return jsonify(result=results)
        #print(word)
        return jsonify(result=results, count= count, word = word)
    except Exception as e:
        return str(e)



@app.route('/')
@app.route('/volume_<int:volume_id>/<int:id>/', methods =['get', 'post'])
def volume(volume_id, id):
    if request.method == 'GET':
        number_of_volume = int(volume_id)
        results = create_js(number_of_volume, id)
        return render_template('page.html', results = results)
    elif request.method == 'POST':
        client = pymongo.MongoClient('mongodb://%s:%s@172.20.0.6' % (username, password))
        db = client['otechestvennie_zapiski']
        db_editpages = db.edit_pages
        edit_page = request.get_json(force=True)['blocks']
        #print(edit_page)
        #print({'number_of_volume' : volume_id, 'pb': edit_page[2]['data']['text'],'head':edit_page[0]['data']['text'], 'p': edit_page[1]['data']['text'], 'edit_time': edit_page[3]['data']['text']})
        db_editpages = db_editpages.insert_one({'number_of_volume' : int(volume_id), 'pb': int(edit_page[2]['data']['text']),'head':edit_page[0]['data']['text'], 'p': edit_page[1]['data']['text'], 'edit_time': edit_page[3]['data']['text']})
        return 'OK!'
   
if __name__ == '__main__':
    app.run(debug=True)
