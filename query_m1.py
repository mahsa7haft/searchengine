import ujson as json
import indexer
import numpy as np
from nltk.stem import WordNetLemmatizer
import time
import pickle
from scoring import calc_tf
from scoring import calc_idf
from scipy.spatial import distance

lemmatizer = WordNetLemmatizer()
stops = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}


def getDocs(corpes, docs):
    docids = dict()
    for token,posting_list in corpes.items():
        for docid in posting_list.keys():
            if docid != "idf":
                docids[docid] = 0
    return len(docids), docids

#postings list:  {"idf": idf score }, {docid1: (tf, pos_score1)}, {docid2: (tf, pos_score2)},...
#returns {docid1:total score1, docid2:totalscore2,...}
def getScores(posting_list):
    doc_dict = dict()
    docids = []
    tfscores = []
    pos_scores = []
    for k,v in posting_list.items():
        if k == "idf":
            idf_score = v
        else:
            id = k
            score = v
            docids.append(id)
            tfscores.append(score[0])
            pos_score = score[1]
            pos_scores.append(pos_score)
    tfidfscores = np.dot(idf_score ,tfscores)
    tfidfscores = np.add(tfidfscores , pos_scores)
    for i in range(len(docids)):
        doc_dict[docids[i]] = tfidfscores[i]
    return doc_dict

        
def query(queries):
    global doc_dict
    queries = [lemmatizer.lemmatize(t.lower()) for t in queries]
    ranked = dict()
    start_time = time.time()
    print(f'starting')
    print("loading corpes...")
    
    with open('scores.pickle','rb') as file:
        corpes = pickle.load(file)
    
    current_time = time.time()
    elapsed_time = (current_time - start_time)
    print(f'loaded at: {elapsed_time/60:.2f} minutes.')
    print("retrieving result...")
    
    N, ranked = getDocs(corpes, ranked)
    # scores: token : {"idf": idf score }, {docid1: (tf, pos_score1)}, {docid2: (tf, pos_score2)},...
    
    token_dict = {}
    #calculating token tfs
    for token in queries:
        if token in token_dict:
            token_dict[token] +=1
        else:
            token_dict[token] = 1
    
    #calculating tfidfs for the queries
    q_vector = []
    for token in queries:
        if token not in stops:
            q_vector.append(corpes[token]["idf"] * calc_tf(token_dict[token]))
    
    #postings = []
    #docid_list = []
    docid_set = set()
    for token in queries:
        if token not in stops:
            if token in corpes:
                postings_lists = getScores(corpes[token])
                for id, s in postings_lists.items():
                    ranked[id] += s
                
    '''
    #calculate the cosine similarity for every id
    for id in docid_set:
        for token in queries:
            if token in corpes:
                d_vector = []
                if token not in stops:
                    postings_list = corpes[token]
                    if id in postings_list:
                        d_vector.append(postings_list[id])
                    else:
                        d_vector.append(0)
            ranked[id] += distance.cosine(q_vector, d_vector)
    '''
    current_time = time.time()
    elapsed_time = (current_time - start_time)
    print(f'retrieved at: {elapsed_time/60:.2f} minutes.')
    ranking_dict = sorted(ranked.items(), key = lambda x : (-x[1] , x[0]))
    
    print('Number of unique document ids: ')
    print(len(ranked), '\n')
    
    print('Number of unique words: ')
    print(len(corpes), '\n')
    
    with open('WEBPAGES_RAW/bookkeeping.json') as j:
        books = json.load(j)
    results = []
    i = 0
    for docid in ranking_dict:
        if docid[1] != 0 :
            url = books[docid[0]]
            results.append(url)
            i = i+1
    print(f'found {i} results:\n')
    for i in range(len(results)):
        if i > 30:
            break
        print(results[i])
        print()
    current_time = time.time()
    elapsed_time = (current_time - start_time) /60
            
if __name__ == "__main__":
    #queries = ['Informatics', 'Mondego','Irvine']
    #input_string = input('Input your query: ')
    #queries = input_string.split()
    print('results for informatics: \n')
    query(['Informatics'])
    print('\n************************\n')
    print('results for Mandego: \n')
    query(['Mondego'])
    print('\n************************\n')
    print('results for Irvine: \n')
    query(['Irvine'])
    print('\n************************\n')
