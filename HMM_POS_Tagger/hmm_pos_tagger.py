import enum
from json.encoder import INFINITY
from unittest import result
import nltk
import sys
import re
import pickle
from collections import Counter

class hmm_pos:
    tags_unigram = {}
    tags_bigram = {}
    tags_to_word = {}
    test_sent = ""
    test_sent_tag_only = []
    test_sent_word_only = []
    test_sent_tags_unigram = {}
    test_sent_tags_bigram = {}
    test_sent_tags_word = []
    tags = set()
    tagged = False

    def __init__(self,argv):
        if len(argv) == 3:
            self.test_sent = open(argv[2],'r').read()
            fp = open(argv[1],'rb')
            (self.tags_unigram,self.tags_bigram,self.tags_to_word) = pickle.load(fp)
            fp.close()
            self.sentence_read()
        elif len(argv) == 1:
            tagged_sents = nltk.corpus.brown.tagged_sents()
            self.corpus_process(tagged_sents)
            self.write_to_dat()
        else:
            print('''
            Command Line arguments Error:
             - 0 argument   -> Load brown corpus, generate model.dat
             - 2 arguments  -> hmm_pos_tagger.py model.dat sentence(tagged/untagged):
                if tagged   -> HMM Sequence Probability Calculation
                if untagged -> HMM Viterbi MLS Calcucation
            ''')

    def buildNgram(self,tokenized_sentence, n=2):
        ngram = []
        for i in range(len(tokenized_sentence)):
            for j in range(len(tokenized_sentence[i])-(n-1)):
                ngram.append(' '.join(tokenized_sentence[i][j:j+n]))
        
        return ngram
    
    def corpus_process(self,corpus):
        punc_removed_corpus = []
        tags_only_corpus = []
        for sent in corpus:
            punc_removed_sent = []
            tags_only_sent = []
            punc_removed_sent.append("<S> <S>")
            tags_only_sent.append("<S>")
            for w,t in sent:
                punc_removed_sent.append(w.lower() + " " + t)
                self.tags.add(t)
                tags_only_sent.append(t)
            punc_removed_sent.append("</S> </S>")
            tags_only_sent.append("</S>")

            tags_only_corpus.append(tags_only_sent)
            punc_removed_corpus.append(punc_removed_sent)

        self.tags_bigram = Counter(self.buildNgram(tags_only_corpus))
        self.tags_unigram = Counter(self.buildNgram(tags_only_corpus,1))
        self.tags_to_word = Counter(self.buildNgram(punc_removed_corpus, 1))
        
        return
    
    def write_to_dat(self):
        fp = open('model.dat','wb')
        pickle.dump((self.tags_unigram,self.tags_bigram,self.tags_to_word), fp, -1)
        fp.close()

    def compute_tags_bigram_prob(self,bigram):
        two_words = re.split("\s",bigram)
        return self.tags_bigram[two_words[0] + " " + two_words[1]]/self.tags_unigram[two_words[1]]

    def compute_tags_to_word_bigram_prob(self,bigram):
        two_words = re.split("\s",bigram)
        return self.tags_to_word[bigram]/self.tags_unigram[two_words[1]]

    def sentence_read(self):
        for key in self.tags_unigram:
            self.tags.add(key)
        word_tag_pairs = re.split("\s",self.test_sent)
        word_tag_pairs = [i for i in word_tag_pairs if i != '']

        if re.search("\/",word_tag_pairs[0]) == None:
            self.test_sent = "<S> " + self.test_sent + " </S>"
            self.tagged = False
            self.test_sent_word_only.append("<S>")
            for pairs in word_tag_pairs:
                self.test_sent_word_only.append(pairs.lower())
            self.test_sent_word_only.append("</S>")
            self.find_tags_for_sent()
        else:
            self.test_sent = "<S>/<S> " + self.test_sent + " </S>/</S>"
            self.test_sent_tag_only.append("<S>")
            self.test_sent_word_only.append("<S>")
            self.test_sent_tags_word.append("<S> <S>")
            self.tagged = True

            for pairs in word_tag_pairs:
                splitted = re.split("\/",pairs)
                if len(splitted) > 1:
                    self.test_sent_word_only.append(splitted[0].lower())
                    self.test_sent_tag_only.append(splitted[1])
                    self.test_sent_tags_word.append(splitted[0].lower() + " " + splitted[1])
            self.test_sent_tag_only.append("</S>")
            self.test_sent_word_only.append("</S>")
            self.test_sent_tags_word.append("</S> </S>")
            self.test_sent_tags_unigram = Counter(self.buildNgram([self.test_sent_tag_only],1))
            self.test_sent_tags_bigram = Counter(self.buildNgram([self.test_sent_tag_only]))
            self.compute_sent_prob()
        return

    def compute_sent_prob(self):
        
        result = 1
        for bi in self.test_sent_tags_word:
            prob = self.compute_tags_to_word_bigram_prob(bi)
            result *= prob
        print("HMM Sequence Probability: " + str(result))

    def find_tags_for_sent(self):
        vit = [dict() for x in range(len(self.test_sent_word_only)+1)]
        back = [dict() for i in range(len(self.test_sent_word_only)+1)]
        for tag in self.tags:
            vit[1][tag] = self.compute_tags_bigram_prob("<S> " + tag) * self.compute_tags_to_word_bigram_prob(self.test_sent_word_only[1] + " " + tag) * 100
            back[1][tag] = "<S>"

        for index_w in range(2,len(self.test_sent_word_only)):
            for index_t,tag in enumerate(self.tags):
                vit[index_w][tag] = -INFINITY
                for index_tp, tag_prev in enumerate(self.tags):
                    temp = vit[index_w-1][tag_prev] * self.compute_tags_bigram_prob(tag_prev + " " + tag) * self.compute_tags_to_word_bigram_prob(self.test_sent_word_only[index_w] + " " + tag)
                    if temp > vit[index_w][tag]:
                        vit[index_w][tag] = temp
                        back[index_w][tag] = tag_prev

        tag_index = len(self.test_sent_word_only)-2
        tag_find_pre = max(vit[tag_index], key=vit[tag_index].get)
        result = tag_find_pre + ""

        while tag_index > 1:
            tag_find_pre = back[tag_index][tag_find_pre]
            tag_index -= 1
            result = tag_find_pre + " " + result
        
        print("HMM Viterbi MLS: " + result)
        f = open("result.txt", "w")
        f.write(result)
        f.close()
        return
def main():
    hmm  = hmm_pos(sys.argv)

if __name__ == '__main__':
    main()