"""
    1.ASCII
    2.nltk, strip(), splitline()
    3.Bigram
    4.Good-turing Count
    5.Custom sentence break
    6.Results on dev set:
        austen: 89 / 100
        dickens: 77 / 100
        tolstoy: 78 / 100
        wilde: 62 / 100
"""
import nltk
import sys
import itertools
import operator
import re
import random
import math
from collections import Counter

class Ngram:
    test_flag = False
    test_file = None
    file_names = []
    file_tokenized = []
    file_src = []
    file_training = []
    file_trainingSet = []

    file_sum = []
    file_unigram = []
    file_bigram = []
    file_trigram = []
    file_zeroGram = []
    
    def __init__(self, srcFile, flag):
        if flag == "-test":
            self.test_flag = True
            self.test_file = sys.argv[3]

        lines = re.split(r'[\n\s]',open(srcFile,"r").read())
        for line in lines:
            if len(line) > 4:
                self.file_names.append(re.split(r"\.",line)[0])
                self.file_trainingSet = self.buildTrainDevSet(open(line,"r").read())
                self.file_src.append(self.file_trainingSet[0])
                self.file_training.append(self.file_trainingSet[1])
                self.file_unigram.append(self.count_Ngram(self.buildNgram(self.file_src[-1],1)))
                self.file_bigram.append(self.count_Ngram(self.buildNgram(self.file_src[-1],2)))
                self.file_trigram.append(self.count_Ngram(self.buildNgram(self.file_src[-1],3)))
                self.file_sum.append(sum(self.file_unigram[-1].values()))
        if self.test_flag:
            self.file_training = []
            self.file_training.append(self.file_trainingSet[1])
        self.v0calculator()

    def buildTrainDevSet(self,file_content):
        if self.test_flag:
            return [self.sent_tokenize(file_content),open(self.test_file,"r").read().splitlines()]
        else:
            file_sent = self.sent_tokenize(file_content)
            length = len(file_sent)
            return [file_sent[0:-100], file_sent[-100:]]

    def v0calculator(self):
        for index in range(len(self.file_names)):
            all_vocab = len(self.file_unigram[index])
            all_vocab = all_vocab * all_vocab
            sum_Nx = 0
            for i in range(10):
                sum_Nx += operator.countOf(self.file_unigram[index].values(), i)
            self.file_zeroGram.append(all_vocab - sum_Nx)


    def bigramProbability(self, sequence, text):
        first_word = re.split(r'\s', sequence)[0]
        text_index = self.file_names.index(text)
        
        sequence_count = self.file_bigram[text_index][sequence]+1
        divider = self.file_zeroGram[text_index] if sequence_count - 1 == 0 else operator.countOf(self.file_bigram[text_index].values(),sequence_count-1)
        # print("sequence count: " + str(sequence_count-1))
        if sequence_count < 6:
            smoothed_Count = (sequence_count) * operator.countOf(self.file_bigram[text_index].values(),sequence_count) / divider
            
            # print("count of " + str(operator.countOf(file_bigram[text_index].values(),sequence_count)))
            # print("smoothed_count: " + str(smoothed_Count))
            # print("smoothed_count log: " + str(math.log(smoothed_Count,10)))
            return math.log(smoothed_Count,10)
        else:
            if self.file_unigram[text_index][first_word] == 0:
                return 0
            return self.file_bigram[text_index][sequence]/self.file_unigram[text_index][first_word]

    def trigramProbability(self,sequence,text):
        first_2word = "".join(re.split(r'\s', sequence)[0:2])
        text_index = self.file_names.index(text)
        
        sequence_count = self.file_trigram[text_index][sequence]+1
        divider = int(math.sqrt(self.file_zeroGram[text_index]))^3 if sequence_count - 1 == 0 else operator.countOf(self.file_trigram[text_index].values(),sequence_count-1)
        if sequence_count < 6:
            smoothed_Count = (sequence_count) * operator.countOf(self.file_bigram[text_index].values(),sequence_count) / divider
            return math.log(smoothed_Count,10)
        else:
            if self.file_bigram[text_index][first_2word] == 0:
                return 0
            return self.file_trigram[text_index][sequence]/self.file_bigram[text_index][first_2word]

    def probabilityCheck(self,result_array):
        return result_array.index(max(result_array))    

    def sent_tokenize(self,str):
        # negative lookbehind position names: mr. jr. etc
        # negative loogbehind float numbers
        # positive lookbehind ?.! before whitespace
        punc_sentence = re.split(r'(?<![A-Z][a-z]\.)(?<!\w\.\w.)(?<=[\.\?\!])\s',str)
        newline_removed = []
        for i in punc_sentence:
            newline_removed.append(" ".join(i.splitlines()))

        stripped_sentences = [i.strip() for i in newline_removed]
        return list(filter(None,stripped_sentences))

    def buildNgram(self,tokenized_sentence, n=2):
        ngram = []
        tokenized_sentence.append("")
        for i in range(len(tokenized_sentence)-1):
            word_tokenized = nltk.word_tokenize(tokenized_sentence[i])
            if len(word_tokenized) == 1:
                str_temp = word_tokenized[0] + " "
                tokenized_sentence[i+1] = str_temp + tokenized_sentence[i+1]
            elif len(word_tokenized) == 2:
                ngram.append(' '.join(word_tokenized[0:2]))
            else:
                for j in range(len(word_tokenized)-n):
                    ngram.append(' '.join(word_tokenized[j:j+n]))
        
        return ngram

    def count_Ngram(self,ngram):
        return Counter(ngram)

    def sentence_probability(self, sentence,text_name, n=2):
        # print(sentence)
        index = self.file_names.index(text_name)
        if re.search(r'\s',sentence[0]) == None:
            return self.file_unigram[index][sentence[0]]/self.file_sum[index]
        else:
            ngram = self.buildNgram(sentence,n)
            # print("bigram: " + str(bigram))
            total_prob = 0
            for items in ngram:
                if n == 2:
                    total_prob += self.bigramProbability(items,text_name)
                else:
                    total_prob += self.trigramProbability(items,text_name)

            return total_prob

    def test(self):

        correctness = []
        for i in range(len(self.file_names)):
            correctness.append(0)
        
        for i,test_set in enumerate(self.file_training):
            for test in test_set:
                prob = []
                for name in self.file_names:
                    prob.append(self.sentence_probability(self.sent_tokenize(test),name,2))

                if self.probabilityCheck(prob) == i:
                    correctness[i] += 1
                
                if self.test_flag:
                    print(self.file_names[self.probabilityCheck(prob)])

        if not self.test_flag:
            print("Results on dev set:")
            for i in range(len(correctness)):
                print(self.file_names[i] + ": " + str(correctness[i]) + " / 100")
def main():
    myNgram = Ngram(sys.argv[1],sys.argv[2])
    myNgram.test()

if __name__ == '__main__':
    main()
