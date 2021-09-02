# IS IT POSSIBLE TO IDENTIFY THE AUTHOR THROUGH ITS STYLOMETRIC FEATURES? 
# AUTHORSHIP DETECTION APPROACHES APPLIED TO ECB SPEECHES
"""

from google.colab import drive
drive.mount('/content/drive')

"""### Download packages"""

!pip install "tensorflow==2.3.1"

!pip install tensorflow==2.0  #prima 2,5 poi 2,0 va

!pip install delayed

!pip3 install auto-sklearn

!pip install scikit-learn

!pip install dask

!python -m pip install "dask[array]" --upgrade

!python -m pip install "dask[dataframe]" --upgrade

!python -m pip install dask distributed --upgrade

!pip install pytorch

!pip install sentencepiece

!pip install torchtext

!pip install transformers

!pip install textstat

!pip install pillow

!pip install sklearn

!python -m pip install "dask[array]" --upgrade

!pip install PipelineProfiler

"""### Import libraries"""

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import requests
from tensorflow.keras.layers import SimpleRNN, Dropout, Activation, Dense, Embedding

from tensorflow.keras.optimizers import Adam, SGD

from tensorflow.keras.callbacks import LearningRateScheduler
from tensorflow.keras.callbacks import History
from tensorflow.keras.optimizers.schedules import ExponentialDecay
import numpy
from sklearn.model_selection import GridSearchCV
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from bs4 import BeautifulSoup
import seaborn as sns
import os
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import math
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import confusion_matrix

# import fastai, torch, pytorch_transformers
from fastai.text import *
from fastai.metrics import *
import torch
import torch.nn as nn

from transformers import PreTrainedModel, PreTrainedTokenizer, PretrainedConfig
#from torchtext.data import Field, TabularDataset
from transformers import XLNetLMHeadModel, XLNetTokenizer, XLNetForSequenceClassification, XLNetConfig
#from balancer import ClassBalancer
import sentencepiece 
from transformers import  DistilBertForSequenceClassification, DistilBertTokenizer, DistilBertConfig
# Garbage Collector
import gc
import PipelineProfiler

import sklearn
print(sklearn.__version__)

#import autosklearn.classification
import sklearn.model_selection
import sklearn.datasets
import sklearn.metrics
from sklearn.pipeline import Pipeline

# Commented out IPython magic to ensure Python compatibility.
import nltk

nltk.download('cmudict')
nltk.download('stopwords')
nltk.download('punkt')

import string 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import cmudict
import collections as coll
import ast
import collections
import spacy

import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud

import matplotlib.pyplot as plt
# %matplotlib inline

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn import preprocessing

from gensim.models.doc2vec import Doc2Vec, TaggedDocument

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import ExtraTreesClassifier
from matplotlib import pyplot

import tensorflow as tf

from tensorflow import feature_column
from tensorflow.keras import layers

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pandas as pd

#try:
  # %tensorflow_version only exists in Colab.
  #!pip install tf-nightly-gpu-2.0-preview
#except Exception:
  #pass



!pip install sklearn
import tensorflow as tf

from tensorflow import feature_column
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
print("GPU Available: ", tf.test.is_gpu_available())

"""# IMPORT OF THE DATASET AND EXTRACTION OF THE SPEECHES

In order to start the analysis, the dataset has to imported. More specifically, a dataset from kaggle based on second dataset on the European Central Bank website is used.

Kaggle dataset source: https://www.kaggle.com/robertolofaro/ecb-speeches-1997-to-20191122-frequencies-dm

ECB website dataset source: https://www.ecb.europa.eu/press/key/html/downloads.en.html
"""

dataset = pd.read_csv('/content/drive/MyDrive/ECB_SPEECHES.csv')
dataset.set_index('speech_id')

"""Firstly, we check for missing values:"""

dataset.isnull().values.any()

"""Since there are some missing values, we check the presence of the missing value in each column specifically:"""

dataset.isnull().sum()

"""Then, we remove the missing values:"""

dataset.dropna(inplace=True)

dataset.isnull().values.any()

"""At this point, we remove the speeches made in a language different than English:"""

dataset = dataset[dataset['what_language'] == 'EN']

dataset.reset_index(drop=True, inplace=True)

"""Inside the dataset, there were some speeches classified as 'English' and in reality they were in different language. Do to that, I removed them.

Moreover, inside the dataset some speeches in reality were slides of power points with only graphs, due to that, I also removed those observations since they are not useful for the analysis.
"""

dataset.drop([226,521,544,585,943,947,999,1423,1442,1579,2394, 2464, 2481, 2490,2563,
2630, 2652, 2668, 2697, 2706, 2780, 2784, 2792, 2835, 2845, 2852, 2861, 2876], axis=0,inplace=True)

dataset = dataset[dataset['what_type'] != 'E' ]

dataset.reset_index(drop=True, inplace=True)

dataset

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

"""The column 'what_weblink' of the dataset is composed by URL of the speeches, with this function we clean the webpage and we extract the content of the text.

Moreover, we insert the speeches into a list which is then joined inside the dataset.
"""

link_dataset = dataset.iloc[:,6]
speeches = []
for i in link_dataset:
  req = requests.get(i, headers)
  speeches_extraction = BeautifulSoup(req.content, 'html.parser', from_encoding="iso-8859-1")
  for link in speeches_extraction.find_all(['p'], recursive=True):
    resulted_speech = str(link.text)
    speeches.append(resulted_speech)
  speeches.append('Speech end')

speeches = [x for x in ','.join('' if not e else e for e in speeches).split('Speech end') if x]

"""Before joining the speeches, I want to clean each speech properly.
Every speech extract from the webpage presentes a final disclaimer regrading the cookies.
This disclaimer must be removed since it is not useful for the analysis.

The disclaimer about cookies is the following one:

*We are always working to improve this website for our users. To do this, we use the anonymous data provided by cookies.\nLearn more about how we use cookies,We are always working to improve this website for our users. To do this, we use the anonymous data provided by cookies.\nSee what has changed in our privacy policy,We are always working to improve this website for our users. To do this, we use the anonymous data provided by cookies.\nLearn more about how we use cookies,*
"""

clean_speeches = [x for x in ','.join('' if not e else e for e in speeches).split('We are always working to improve this website for our users. To do this, we use the anonymous data provided by cookies.\nLearn more about how we use cookies,We are always working to improve this website for our users. To do this, we use the anonymous data provided by cookies.\nSee what has changed in our privacy policy,We are always working to improve this website for our users. To do this, we use the anonymous data provided by cookies.\nLearn more about how we use cookies,,,') if x]

clean_speeches

speeches_df= pd.DataFrame(clean_speeches, columns = ['Speeches'])

speeches_df

"""Now that we have the speeches in a text format, we join them to the original dataset:"""

dataset = dataset.join(speeches_df)

"""Now, we save the dataset:"""

dataset.to_csv('clean_dataset')

"""# AUTHORSHIP DETECTION - DISTILBERT TRANSFOMER MODEL"""

dataset = pd.read_csv('/content/drive/MyDrive/clean_dataset.csv')

"""Check the distribution of the target variabel 'Who':"""

dataset['who'].value_counts()

fig, ax = plt.subplots()
fig.set_size_inches(20, 8)
sns.countplot(x = 'who', data = dataset, order = dataset['who'].value_counts().index, 
              palette = sns.color_palette('rocket',2))
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.set_xlabel('Authors of the Speech', fontsize=15)
ax.set_ylabel('Frequency', fontsize=15)
ax.set_title('Distribution of Authors', fontsize=15)
ax.tick_params(labelsize=15)
sns.despine()

"""As we can see, we have many authors in the dataset, some speeches are also written by multiple authors, so I decided to incorporate those speeches to the first author in order of apperence."""

dataset.loc[dataset['who'] == 'Andrea Enria, Pien van Erp Taalman Kip and Linette Field', 'who'] = 'Andrea Enria'
dataset.loc[dataset['who'] == 'Fabio Panetta and Isabel Schnabel', 'who'] = 'Fabio Panetta'
dataset.loc[dataset['who'] == 'Vitor Constancio, Daniele Nouy', 'who'] = 'Vitor Constancio'
dataset.loc[dataset['who'] == 'Mario Draghi and Ilmars Rimsevics', 'who'] = 'Mario Draghi'
dataset.loc[dataset['who'] == 'Willem F. Duisenberg, Otmar Issing, Lucas Papademos', 'who'] = 'Willem F. Duisenberg'
dataset.loc[dataset['who'] == 'Willem F. Duisenberg,Eugenio Domingo Solans', 'who'] = 'Willem F. Duisenberg'
dataset.loc[dataset['who'] == 'Benoit Coure and Joachim Nagel', 'who'] = 'Benoit Coure'
dataset.loc[dataset['who'] == 'Willem F. Duisenberg, Rodrigo Rato, Pedro Solbes', 'who'] = 'Willem F. Duisenberg'
dataset.loc[dataset['who'] == 'Gertrude Tumpel-Gugerell, Lucas Papademos, Jean-Claude Trichet', 'who'] = 'Gertrude Tumpel-Gugerell'
dataset.loc[dataset['who'] == 'Vitor Constancio, Mario Draghi, Ewald Nowotny', 'who'] = 'Vitor Constancio, Mario Draghi'
dataset.loc[dataset['who'] == 'Mario Draghi, Vitor Constancio, Benoit Coure', 'who'] = 'Vitor Constancio, Mario Draghi'
dataset.loc[dataset['who'] == 'Christine Lagarde, Luis de Guindos', 'who'] = 'Christine Lagarde'
dataset.loc[dataset['who'] == 'Mario Draghi, Luis de Guindos', 'who'] = 'Mario Draghi'
dataset.loc[dataset['who'] == 'Willem F. Duisenberg, Lucas Papademos', 'who'] = 'Willem F. Duisenberg'
dataset.loc[dataset['who'] == 'Jean-Claude Trichet, Vitor Constancio', 'who'] = 'Jean-Claude Trichet'
dataset.loc[dataset['who'] == 'Willem F. Duisenberg, Christian Noyer', 'who'] = 'Willem F. Duisenberg'

dataset['who'].value_counts()

fig, ax = plt.subplots()
fig.set_size_inches(20, 8)
sns.countplot(x = 'who', data = dataset, order = dataset['who'].value_counts().index, 
              palette = sns.color_palette('rocket',2), )
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.set_xlabel('Authors of the Speech', fontsize=15)
ax.set_ylabel('Frequency', fontsize=15)
ax.set_title('Distribution of Authors', fontsize=15)
ax.tick_params(labelsize=15)
sns.despine()

"""We select the columns of the dataframe that we are interested in: Speeches and the target variable 'Who'


"""

dataset_class = dataset.iloc[:,[3,9]]
dataset_class

"""For the aim of our analysis, only the four ECB Presidents will be considered. More specifically, Jean-Claude Trichet, Willem F. Duisenberg, Christine Lagarde and Mario Draghi."""

dataset_class = dataset_class[(dataset_class['who'] == 'Jean-Claude Trichet') | (dataset_class['who'] == 'Willem F. Duisenberg' ) | (dataset_class ['who'] == 'Mario Draghi')| (dataset_class ['who'] == 'Christine Lagarde')]

dataset_class.to_csv('dataset_speech_extracted')

# Parameters
seed = 42
use_fp16 = False
bs = 16
max_seq_len=112653

model_type = 'distilbert'
pretrained_model_name = 'distilbert-base-uncased'

MODEL_CLASSES = {
    'distilbert': (DistilBertForSequenceClassification, DistilBertTokenizer, DistilBertConfig)}
model_class, tokenizer_class, config_class = MODEL_CLASSES['distilbert']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(dataset_class['Speeches'], dataset_class['who'], test_size=0.30, random_state=42)

class TransformersBaseTokenizer(BaseTokenizer):
    def __init__(self, pretrained_tokenizer: PreTrainedTokenizer, model_type = 'distilbert', **kwargs):
        self._pretrained_tokenizer = pretrained_tokenizer
        self.max_seq_len = pretrained_tokenizer.model_max_length
        self.model_type = model_type

    def __call__(self, *args, **kwargs): 
        return self

    def tokenizer(self, t:str) -> List[str]:
        """Limits the maximum sequence length and add the special tokens"""
        CLS = self._pretrained_tokenizer.cls_token
        SEP = self._pretrained_tokenizer.sep_token
        tokens = self._pretrained_tokenizer.tokenize(t)[:self.max_seq_len - 2]
        return tokens

transformer_tokenizer = tokenizer_class.from_pretrained(pretrained_model_name)
transformer_base_tokenizer = TransformersBaseTokenizer(pretrained_tokenizer = transformer_tokenizer, model_type = model_type)
fastai_tokenizer = Tokenizer(tok_func = transformer_base_tokenizer, pre_rules=[], post_rules=[])

"""Now, we need a Numericalizer. 
We firsly convert the tokens into their numerical ids.

The functions gestate and setstate allow the functions export and load_learner to work correctly with TransformersVocab
"""

class TransformersVocab(Vocab):
    def __init__(self, tokenizer: PreTrainedTokenizer):
        super(TransformersVocab, self).__init__(itos = [])
        self.tokenizer = tokenizer
    
    def numericalize(self, t:Collection[str]) -> List[int]:
        "Convert a list of tokens `t` to their ids."
        return self.tokenizer.convert_tokens_to_ids(t)
        #return self.tokenizer.encode(t)

    def textify(self, nums:Collection[int], sep=' ') -> List[str]:
        "Convert a list of `nums` to their tokens."
        nums = np.array(nums, dtype='object', copy=False).tolist()
        return sep.join(self.tokenizer.convert_ids_to_tokens(nums)) if sep is not None else self.tokenizer.convert_ids_to_tokens(nums)
    
    def __getstate__(self):
        return {'itos':self.itos, 'tokenizer':self.tokenizer}

    def __setstate__(self, state:dict):
        self.itos = state['itos']
        self.tokenizer = state['tokenizer']
        self.stoi = collections.defaultdict(int,{v:k for k,v in enumerate(self.itos)})

transformer_vocab =  TransformersVocab(tokenizer = transformer_tokenizer)
numericalize_processor = NumericalizeProcessor(vocab=transformer_vocab)

tokenize_processor = TokenizeProcessor(tokenizer=fastai_tokenizer, include_bos=False, include_eos=False)

transformer_processor = [tokenize_processor, numericalize_processor]

pad_idx = transformer_tokenizer.pad_token_id

train = X_train.to_frame().join(y_train.to_frame())
test = X_test.to_frame().join(y_test.to_frame())

databunch = (TextList.from_df(train, cols='Speeches', processor=transformer_processor)
             .split_by_rand_pct(0.1,seed=seed)
             .label_from_df(cols= 'who', label_cls = CategoryList)
             .add_test(test)
             .databunch(bs=bs, pad_first=False, pad_idx=pad_idx))

"""Considering the DistilBERT model, the following tags will be deployed:[CLS] + tokens + [SEP] + padding."""

print('[CLS] token :', transformer_tokenizer.cls_token)
print('[SEP] token :', transformer_tokenizer.sep_token)
print('[PAD] token :', transformer_tokenizer.pad_token)
databunch.show_batch()

print('[CLS] id :', transformer_tokenizer.cls_token_id)
print('[SEP] id :', transformer_tokenizer.sep_token_id)
print('[PAD] id :', pad_idx)
test_one_batch = databunch.one_batch()[0]
print('Batch shape : ',test_one_batch.shape)
print(test_one_batch)

class CustomTransformerModel(nn.Module):
    def __init__(self, transformer_model: PreTrainedModel):
        super(CustomTransformerModel,self).__init__()
        self.transformer = transformer_model
        
    def forward(self, input_ids, attention_mask=None):
        attention_mask = (input_ids!=pad_idx).type(input_ids.type()) 
        
        logits = self.transformer(input_ids,
                                  attention_mask = attention_mask)[0]   
        return logits

config = config_class.from_pretrained(pretrained_model_name)
config.num_labels = 4
config.use_bfloat16 = use_fp16
print(config)

transformer_model = model_class.from_pretrained(pretrained_model_name, config = config)

custom_transformer_model = CustomTransformerModel(transformer_model = transformer_model)

from fastai.callbacks import *
from transformers import AdamW
from functools import partial

CustomAdamW = partial(AdamW, correct_bias=False)

learner = Learner(databunch, 
                  custom_transformer_model, 
                  opt_func = CustomAdamW, 
                  metrics=[accuracy, error_rate])

# Show graph of learner stats and metrics after each epoch.
learner.callbacks.append(ShowGraph(learner))

"""The process of training is divided into layers that will be progressively freezed and unfreezed."""

list_layers = [learner.model.transformer.distilbert.embeddings,
               learner.model.transformer.distilbert.transformer.layer[0],
               learner.model.transformer.distilbert.transformer.layer[1],
               learner.model.transformer.distilbert.transformer.layer[2],
               learner.model.transformer.distilbert.transformer.layer[3],
               learner.model.transformer.distilbert.transformer.layer[4],
               learner.model.transformer.distilbert.transformer.layer[5],
               learner.model.transformer.pre_classifier]

learner.split(list_layers)
num_groups = len(learner.layer_groups)
print('Learner split in',num_groups,'groups')
print(learner.layer_groups)

learner.freeze_to(-1)

learner.lr_find()

"""First cycle:"""

learner.recorder.plot(skip_end=10,suggestion=True)

learner.fit_one_cycle(1,max_lr=2e-03,moms=(0.8,0.7))

learner.save('first_cycle_distilbert')
learner.load('first_cycle_distilbert');

"""Second cycle:"""

learner.freeze_to(-2)
lr = 1e-5

learner.fit_one_cycle(1, max_lr=slice(lr*0.95**num_groups, lr), moms=(0.8, 0.9))

learner.save('second_cycle_distilbert')
learner.load('second_cycle_distilbert');

"""Third cycle:"""

learner.freeze_to(-3)

learner.fit_one_cycle(1, max_lr=slice(lr*0.95**num_groups, lr), moms=(0.8, 0.9))

learner.save('third_cycle_distilbert')
learner.load('third_cycle_distilbert');

"""All layers together:"""

learner.unfreeze()

learner.fit_one_cycle(2, max_lr=slice(lr*0.95**num_groups, lr), moms=(0.8, 0.9))

"""Lastly, export the transformer model:"""

learner.export(file = 'transformer_speeches_distilbert.pkl');

path = '/content/drive/MyDrive'
export_learner = load_learner(path, file = 'transformer_speeches_distilbert.pkl')

"""#AUTHORSHIP DETECTION - STYLOMETRY ML MODEL

So far, we computed a transformer approach for classifying the author of a certain speech. 
As we saw before, we obtained descrete results with that approach (70% accuracy). The trasnformer approach is an end-to-end one, this means that it not possible to tune the parameters to achieve a better result.

Taking this consideration in mind, we decided to pursue to a second approach: a Machine Learning one.
In this way, we are able to fine tune each parameter and to focus on the stylometric features for each speech.

In fact, we this approach, some stylometric features are computed and addeded to the datatset as training parameters with the aim of supporting the classification of the author by the algorithm.
The stylometric features considered follow three categories:

- Lexical parameters
- Richness of the vocabulary parameters
- Readability scores

First of all, we start by selecting the 5 ECB presidents and we create a distinct dataset to which we are going to add the stylometric features:
"""

dataset_stylo = dataset.iloc[:,[3,5,9]]
dataset_stylo = dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet') | (dataset_stylo['who'] == 'Willem F. Duisenberg' ) | (dataset_stylo['who'] == 'Mario Draghi')| (dataset_stylo['who'] == 'Christine Lagarde')]
dataset_stylo.reset_index(drop=True, inplace=True)
dataset_stylo

"""## LEXICAL PARAMETERS

The lexical definition of a term, also known as the dictionary definition, is the definition closely matching the meaning of the term in common usage. As its other name implies, this is the sort of definition one is likely to find in the dictionary. A lexical definition is usually the type expected from a request for definition, and it is generally expected that such a definition will be stated as simply as possible in order to convey information to the widest audience. 

So far, we displayed the definition of lexicality for a specific term, if we instead we consider the lexicality in the context of a sentence or a speech, we may define it as: 
group relating to words, or the vocabulary of a language as distinguished from its grammar and construction

### Average word length

We start by considering as first parameter the average length of a word inside the ECB Presidents speech. 
In detail, we delete all characters considered as 'special' in the english language and then count the average length for each word.
"""

def Avg_wordLength(string):
    tokens = word_tokenize(string, language='english')
    st = [",", ".", "'", "!", '"', "#", "$", "%", "&", "(", ")", "*", "+", "-", ".", "/", ":", ";", "<", "=", '>', "?",
          "@", "[", "\\", "]", "^", "_", '`', "{", "|", "}", '~', '\t', '\n']
    stop = stopwords.words('english') + st
    words = [word for word in tokens if word not in stop]
    return np.average([len(word) for word in words])

avg_word_len=[]
for el in dataset_stylo['Speeches']:
  avg_word_len.append(Avg_wordLength(el))

avg_word_len= pd.DataFrame(avg_word_len)
avg_word_len.columns=['avg_word_len']

dataset_stylo = dataset_stylo.join(avg_word_len)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['avg_word_len']:
  start = start + el

trichet_avg_word_len = start/len(trichet_mean['avg_word_len'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['avg_word_len']:
  start = start + el

duisen_avg_word_len = start/len(duisen_mean['avg_word_len'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['avg_word_len']:
  start = start + el

draghi_avg_word_len = start/len(draghi_mean['avg_word_len'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['avg_word_len']:
  start = start + el

lagarde_avg_word_len =start/len(lagarde_mean['avg_word_len'])

"""### Average sentence length by word

As second parameter, we can consider the average sentence length by counting by word for each ECB President Speech.
"""

def Avg_SentLenghtByWord(text):
    tokens = sent_tokenize(text)
    return np.average([len(token.split()) for token in tokens])

avg_speech_len=[]
for el in dataset_stylo['Speeches']:
  avg_speech_len.append(Avg_SentLenghtByWord(el))

avg_speech_len= pd.DataFrame(avg_speech_len)
avg_speech_len.columns=['avg_speech_len']

dataset_stylo = dataset_stylo.join(avg_speech_len)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['avg_speech_len']:
  start = start + el

trichet_avg_speech_len = start/len(trichet_mean['avg_speech_len'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['avg_speech_len']:
  start = start + el

duisen_avg_speech_len = start/len(duisen_mean['avg_speech_len'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['avg_speech_len']:
  start = start + el

draghi_avg_speech_len= start/len(draghi_mean['avg_speech_len'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['avg_speech_len']:
  start = start + el

lagarde_avg_speech_len =start/len(lagarde_mean['avg_speech_len'])

"""### Presence of special characters

Thirdly, the presence of special characters is counted. Such characters can define a speech which might be more technical, social related (thanks to the hashtag) and more modern.
"""

def CountSpecialCharacter(text):
    st = ["#", "$", "%", "&", "(", ")", "*", "+", "-", "/", "<", "=", '>',
          "@", "[", "\\", "]", "^", "_", '`', "{", "|", "}", '~', '\t', '\n']
    count = 0
    for i in text:
        if (i in st):
            count = count + 1
    return count / len(text)

special_char=[]
for el in dataset_stylo['Speeches']:
  special_char.append(CountSpecialCharacter(el))

special_char= pd.DataFrame(special_char)
special_char.columns=['special_char']

dataset_stylo = dataset_stylo.join(special_char)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['special_char']:
  start = start + el

trichet_special_char= start/len(trichet_mean['special_char'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['special_char']:
  start = start + el

duisen_special_char = start/len(duisen_mean['special_char'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['special_char']:
  start = start + el

draghi_special_char= start/len(draghi_mean['special_char'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['special_char']:
  start = start + el

lagarde_special_char =start/len(lagarde_mean['special_char'])

"""### Count of punctuation

Fourthly, the lexicality of speech is also composed by the punctuation used. For this reason, the presence of the punctuation could be considered as a distinctive stylometric parameter between two speakers.
"""

def CountPuncuation(text):
    st = [",", ".", "'", "!", '"', ";", "?", ":", ";"]
    count = 0
    for i in text:
        if (i in st):
            count = count + 1
    return float(count) / float(len(text))

count_punct=[]
for el in dataset_stylo['Speeches']:
  count_punct.append(CountPuncuation(el))

count_punct= pd.DataFrame(count_punct)
count_punct.columns=['count_punct']

dataset_stylo = dataset_stylo.join(count_punct)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['count_punct']:
  start = start + el

trichet_count_punct= start/len(trichet_mean['count_punct'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['count_punct']:
  start = start + el

duisen_count_punct = start/len(duisen_mean['count_punct'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['count_punct']:
  start = start + el

draghi_count_punct = start/len(draghi_mean['count_punct'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['count_punct']:
  start = start + el

lagarde_count_punct =start/len(lagarde_mean['count_punct'])

"""### Count of function words

Function words can be defined as words that exist to explain or create grammatical or structural relationships into which the content words may fit.

Due to that, it is possible to consider it as a suitable parameter for our analysis.
"""

def RemoveSpecialCHs(text):
    text = word_tokenize(text)
    st = [",", ".", "'", "!", '"', "#", "$", "%", "&", "(", ")", "*", "+", "-", ".", "/", ":", ";", "<", "=", '>', "?",
          "@", "[", "\\", "]", "^", "_", '`', "{", "|", "}", '~', '\t', '\n']

    words = [word for word in text if word not in st]
    return words

def CountFunctionalWords(text):
    functional_words = """a between in nor some upon
    about both including nothing somebody us
    above but inside of someone used
    after by into off something via
    all can is on such we
    although cos it once than what
    am do its one that whatever
    among down latter onto the when
    an each less opposite their where
    and either like or them whether
    another enough little our these which
    any every lots outside they while
    anybody everybody many over this who
    anyone everyone me own those whoever
    anything everything more past though whom
    are few most per through whose
    around following much plenty till will
    as for must plus to with
    at from my regarding toward within
    be have near same towards without
    because he need several under worth
    before her neither she unless would
    behind him no should unlike yes
    below i nobody since until you
    beside if none so up your
    """

    functional_words = functional_words.split()
    words = RemoveSpecialCHs(text)
    count = 0

    for i in text:
        if i in functional_words:
            count += 1

    return count / len(words)

count_fun_words=[]
for el in dataset_stylo['Speeches']:
  count_fun_words.append(CountFunctionalWords(el))

count_fun_words= pd.DataFrame(count_fun_words)
count_fun_words.columns=['count_fun_words']

dataset_stylo = dataset_stylo.join(count_fun_words)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['count_fun_words']:
  start = start + el

trichet_count_fun_words= start/len(trichet_mean['count_fun_words'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['count_fun_words']:
  start = start + el

duisen_count_fun_words = start/len(duisen_mean['count_fun_words'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['count_fun_words']:
  start = start + el

draghi_count_fun_words= start/len(draghi_mean['count_fun_words'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['count_fun_words']:
  start = start + el

lagarde_count_fun_words =start/len(lagarde_mean['count_fun_words'])

"""After computing all the lexical features, it is possible to create a summary class to distinguish each President's styling feature:"""

# Libraries
import matplotlib.pyplot as plt
import pandas as pd
from math import pi
 
# Set data
df = pd.DataFrame({
'who': ['Jean-Claude Trichet','Willem F. Duisenberg ','Mario Draghi','Christine Lagarde'],
'avg_word_len': [trichet_avg_word_len, duisen_avg_word_len, draghi_avg_word_len, lagarde_avg_word_len],
'avg_speech_len': [trichet_avg_speech_len, duisen_avg_speech_len, draghi_avg_speech_len, lagarde_avg_speech_len],
'special_char': [trichet_special_char, duisen_special_char, draghi_special_char, lagarde_special_char],
'count_punct': [trichet_count_punct, duisen_count_punct, draghi_count_punct, lagarde_count_punct],
'count_function': [trichet_count_fun_words, duisen_count_fun_words, draghi_count_fun_words, lagarde_count_fun_words]
})

scaler = MinMaxScaler()

df[['avg_word_len', 'avg_speech_len', 'special_char', 'count_punct', 'count_function']]= scaler.fit_transform(df[['avg_word_len', 'avg_speech_len', 'special_char', 'count_punct', 'count_function']])
 
# ------- PART 1: Create background
 
# number of variable
categories=list(df)[1:]
N = len(categories)
 
# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]
 
# Initialise the spider plot
ax = plt.subplot(111, polar=True)
 
# If you want the first axis to be on top:
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
 
# Draw one axe per variable + add labels
plt.xticks(angles[:-1], categories)
 
# Draw ylabels
ax.set_rlabel_position(0)
#plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
#plt.ylim(0,40)
 

# ------- PART 2: Add plots
 
# Plot each individual = each line of the data
# I don't make a loop, because plotting more than 3 groups makes the chart unreadable
 
# Ind1
values=df.loc[0].drop('who').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="Jean-Claude Trichet")
ax.fill(angles, values, 'b', alpha=0.1)
 
# Ind2
values=df.loc[1].drop('who').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="Willem F. Duisenberg")
ax.fill(angles, values, 'r', alpha=0.1)

# Ind3
values=df.loc[2].drop('who').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="Mario Draghi")
ax.fill(angles, values, 'r', alpha=0.1)
 

# Ind4
values=df.loc[3].drop('who').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="Christine Lagarde")
ax.fill(angles, values, 'r', alpha=0.1)
 
 
# Add legend
plt.legend(loc= 'best', bbox_to_anchor=(0.1, 0.1))
plt.title("Lexical parameters for ECB Presidents")


# Show the graph
plt.show()

"""As we can see from the plot, on average, Trichet is the president that uses longer words with respect to other presidents, more specifically, the average word lenght for Trichet is 6.77.

On the other side, we can see that Madame Lagarde instead deploys much shorter words, respectively for 6.47.

It must be highlighted that there is not a significant difference among all presidents, hence it is not possible to identify the average word length as a stylometric distinctive parameter.

Considering the sentences' length, the Presidents that deploys a longer amount of sentences in his speeches is Jean-Claude Trichet.

So far, we saw that Trichet accounts for the longest words and also the longest sentences on average.

On the other hand, we can see that Mario Draghi instead formulates shorter sentences with respect to other Presidents.

As with the other parameter, it is not possible to define the average sentence length as a distinctive parameter, however, some distinctive features related to the stylomentric way of speaking start to rise up.

As we can see from the plot, we can notice that Christine Lagarde deploys the highest amount of punctuation in her speeches despite the fact that the avarage length of the sentences and words is the shortes among all Presidents.

The opposite can be visualize for Trichet.

Lastly, we can notice that the two Presidents that deploy the most functional words are Trichet and Draghi.

## VOCABULARY RICHNESS PARAMETERS

As second set of parameters, we considered the richeness of the vocabulary used by the ECB Presidents. 

More specifically, we aimed at defining the variety of words deployed during their speeches and to identify a distinctive vocabulary to place the speech in a specific historic timeframe and to identify unique expressions used by the Presidents.

### Yules Characteristic K

From statistical linguistics, Yule's Characteristic (K) is a word frequency measurement for large blocks of text. It measures the likelyhood of two nouns, chosen at random from the text, being the same. Thus, it is a measure of the complexity of the text, as well as its repetitiveness. Yule's Characteristic measurements are given in the form of an positive integer which represents the ratio of misses to hits of the block of text. That is, a K value of 300 means that for any pair of nouns chosen at random from the given text, there's a 1 in 300 chance that they will be the same.

Yule's Characteristic was invented in 1938 by George Udny Yule, a Cambridge statistician. It was most famously used as yet more fuel for the "Bacon was Shakespeare" debate in a 1957 paper. The paper showed that K measurements of Shakespeare's works were a useful metric for judging style, and varied predictably based on which act of each play was analyzed. However, in the author's own words, he "should not care to suggest that the characteristic is going to provide an infallible test of authorship."
"""

def YulesCharacteristicK(text):
    words = RemoveSpecialCHs(text)
    N = len(words)
    freqs = coll.Counter()
    freqs.update(words)
    vi = coll.Counter()
    vi.update(freqs.values())
    M = sum([(value * value) * vi[value] for key, value in freqs.items()])
    K = 10000 * (M - N) / math.pow(N, 2)
    return K

yules_char_k=[]
for el in dataset_stylo['Speeches']:
  yules_char_k.append(YulesCharacteristicK(el))

yules_char_k= pd.DataFrame(yules_char_k)
yules_char_k.columns=['yules_char_k']

dataset_stylo = dataset_stylo.join(yules_char_k)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['yules_char_k']:
  start = start + el

trichet_yules_char_k= start/len(trichet_mean['yules_char_k'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['yules_char_k']:
  start = start + el

duisen_yules_char_k = start/len(duisen_mean['yules_char_k'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['yules_char_k']:
  start = start + el

draghi_yules_char_k= start/len(draghi_mean['yules_char_k'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['yules_char_k']:
  start = start + el

lagarde_yules_char_k =start/len(lagarde_mean['yules_char_k'])

"""### Shannon Entropy

In information theory, the entropy of a random variable is the average level of "information", "surprise", or "uncertainty" inherent in the variable's possible outcomes. The concept of information entropy was introduced by Claude Shannon in his 1948 paper "A Mathematical Theory of Communication",[1][2] and is sometimes called Shannon entropy in his honour.
"""

def ShannonEntropy(text):
    words = RemoveSpecialCHs(text)
    lenght = len(words)
    freqs = coll.Counter()
    freqs.update(words)
    arr = np.array(list(freqs.values()))
    distribution = 1. * arr
    distribution /= max(1, lenght)
    import scipy as sc
    H = sc.stats.entropy(distribution, base=2)
    # H = sum([(i/lenght)*math.log(i/lenght,math.e) for i in freqs.values()])
    return H

shannon_entropy=[]
for el in dataset_stylo['Speeches']:
  shannon_entropy.append(ShannonEntropy(el))

shannon_entropy= pd.DataFrame(shannon_entropy)
shannon_entropy.columns=['shannon_entropy']

dataset_stylo = dataset_stylo.join(shannon_entropy)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['shannon_entropy']:
  start = start + el

trichet_shannon_entropy= start/len(trichet_mean['shannon_entropy'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['shannon_entropy']:
  start = start + el

duisen_shannon_entropy = start/len(duisen_mean['shannon_entropy'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['shannon_entropy']:
  start = start + el

draghi_shannon_entropy= start/len(draghi_mean['shannon_entropy'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['shannon_entropy']:
  start = start + el

lagarde_shannon_entropy =start/len(lagarde_mean['shannon_entropy'])

"""### Simpson's Index

A diversity index (also called phylogenetic index) is a quantitative measure that reflects how many different types (such as species) there are in a dataset (a community), and that can simultaneously take into account the phylogenetic relations among the individuals distributed among those types, such as richness, divergence or evenness.[1] These indices are statistical representations of biodiversity in different aspects (richness, evenness, and dominance).
"""

def SimpsonsIndex(text):
    words = RemoveSpecialCHs(text)
    freqs = coll.Counter()
    freqs.update(words)
    N = len(words)
    n = sum([1.0 * i * (i - 1) for i in freqs.values()])
    D = 1 - (n / (N * (N - 1)))
    return D

simpson_index=[]
for el in dataset_stylo['Speeches']:
  simpson_index.append(SimpsonsIndex(el))

simpson_index= pd.DataFrame(simpson_index)
simpson_index.columns=['simpson_index']

dataset_stylo = dataset_stylo.join(simpson_index)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['simpson_index']:
  start = start + el

trichet_simpson_index= start/len(trichet_mean['simpson_index'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['simpson_index']:
  start = start + el

duisen_simpson_index = start/len(duisen_mean['simpson_index'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['simpson_index']:
  start = start + el

draghi_simpson_index= start/len(draghi_mean['simpson_index'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['simpson_index']:
  start = start + el

lagarde_simpson_index =start/len(lagarde_mean['simpson_index'])

"""### Hapax Legomenon and Honor Measure

Hapax legomenon refers to the appearance of a word or an expression in a body of text, not to either its origin or its prevalence in speech. It thus differs from a nonce word, which may never be recorded, may find currency and may be widely recorded, or may appear several times in the work which coins it, and so on.
"""

def hapaxLegemena(text):
    words = RemoveSpecialCHs(text)
    V1 = 0
    # dictionary comprehension . har word kay against value 0 kardi
    freqs = {key: 0 for key in words}
    for word in words:
        freqs[word] += 1
    for word in freqs:
        if freqs[word] == 1:
            V1 += 1
    N = len(words)
    V = float(len(set(words)))
    R = 100 * math.log(N) / max(1, (1 - (V1 / V)))
    h = V1 / N
    return R, h

hapax_legemena=[]
for el in dataset_stylo['Speeches']:
  hapax_legemena.append(hapaxLegemena(el))

hapax_legemena= pd.DataFrame(hapax_legemena)
hapax_legemena.columns=['hapax_legemena', 'honor_measure']

dataset_stylo = dataset_stylo.join(hapax_legemena)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['hapax_legemena']:
  start = start + el

trichet_hapax_legemena= start/len(trichet_mean['hapax_legemena'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['hapax_legemena']:
  start = start + el

duisen_hapax_legemena = start/len(duisen_mean['hapax_legemena'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['hapax_legemena']:
  start = start + el

draghi_hapax_legemena= start/len(draghi_mean['hapax_legemena'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['hapax_legemena']:
  start = start + el

lagarde_hapax_legemena =start/len(lagarde_mean['hapax_legemena'])

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['honor_measure']:
  start = start + el

trichet_honor_measure= start/len(trichet_mean['honor_measure'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['honor_measure']:
  start = start + el

duisen_honor_measure = start/len(duisen_mean['honor_measure'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['honor_measure']:
  start = start + el

draghi_honor_measure= start/len(draghi_mean['honor_measure'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['honor_measure']:
  start = start + el

lagarde_honor_measure =start/len(lagarde_mean['honor_measure'])

"""### Brunets Measure W

Brunet’s index is a measure of lexical diversity, known as W, that has been used instylometric analyses of text and is often claimed to be independent of text length.
"""

def BrunetsMeasureW(text):
    words = RemoveSpecialCHs(text)
    a = 0.17
    V = float(len(set(words)))
    N = len(words)
    B = (V - a) / (math.log(N))
    return B

brunets_w=[]
for el in dataset_stylo['Speeches']:
  brunets_w.append(BrunetsMeasureW(el))

brunets_w= pd.DataFrame(brunets_w)
brunets_w.columns=['brunets_w']

dataset_stylo = dataset_stylo.join(brunets_w)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['brunets_w']:
  start = start + el

trichet_brunets_w= start/len(trichet_mean['brunets_w'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['brunets_w']:
  start = start + el

duisen_brunets_w = start/len(duisen_mean['brunets_w'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['brunets_w']:
  start = start + el

draghi_brunets_w= start/len(draghi_mean['brunets_w'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['brunets_w']:
  start = start + el

lagarde_brunets_w =start/len(lagarde_mean['brunets_w'])

"""Also considering vocabulary richness features, it is possible to create a distinctive plot for each ECB President to identify his stylometric features:"""

# Libraries
import matplotlib.pyplot as plt
import pandas as pd
from math import pi
 
# Set data
df_3 = pd.DataFrame({
'who': ['Jean-Claude Trichet','Willem F. Duisenberg ','Mario Draghi','Christine Lagarde'],
'yules_char_k' : [trichet_yules_char_k, duisen_yules_char_k, draghi_yules_char_k, lagarde_yules_char_k],
'shannon_entropy': [trichet_shannon_entropy, duisen_shannon_entropy, draghi_shannon_entropy, lagarde_shannon_entropy],
'simpson_index': [trichet_simpson_index, duisen_simpson_index, draghi_simpson_index, lagarde_simpson_index],
'hapax_legemena' : [trichet_hapax_legemena, duisen_hapax_legemena, draghi_hapax_legemena, lagarde_hapax_legemena],
'honor_measure': [trichet_honor_measure, duisen_honor_measure, draghi_honor_measure, lagarde_honor_measure],
'brunets_w': [trichet_brunets_w, duisen_brunets_w, draghi_brunets_w, lagarde_brunets_w]
})

#df_3[['yules_char_k','shannon_entropy','simpson_index','hapax_legemena', 'honor_measure','brunets_w']]= scaler.fit_transform(df_3[['yules_char_k','shannon_entropy','simpson_index','hapax_legemena', 'honor_measure','brunets_w']])
 
 
# ------- PART 1: Define a function that do a plot for one line of the dataset!
 
def make_spider( row, title, color):

    # number of variable
    categories=list(df_3)[1:]
    N = len(categories)

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    

    # Initialise the spider plot
    ax = plt.subplot(2,2,row+1, polar=True, )

    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, color='grey', size=8)

    # Draw ylabels
    ax.set_rlabel_position(0)
    #plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
    #plt.ylim(0,40)

    # Ind1
    values=df.loc[row].drop('who').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)


     # Ind2
    angles += angles[:1]
    values=df.loc[row].drop('who').values.flatten().tolist()
    values += values[:2]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)

    # Ind3
    angles += angles[:1]
    values=df.loc[row].drop('who').values.flatten().tolist()
    values += values[:3]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)

     # Ind4
    angles += angles[:1]
    values=df.loc[row].drop('who').values.flatten().tolist()
    values += values[:4]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)

    # Add a title
    plt.title(title, size=11, color=color, y=1)

    
# ------- PART 2: Apply the function to all individuals
# initialize the figure
my_dpi=96
plt.figure(figsize=(1000/my_dpi, 1000/my_dpi), dpi=my_dpi)


 
# Create a color palette:
my_palette = plt.cm.get_cmap("Set2", len(df.index))

 
# Loop to plot
for row in range(0, len(df.index)):
    make_spider( row=row, title=''+df['who'][row], color=my_palette(row))

"""### Vocabulary frequency of ECB presidents words

In the dataset, some word frquency was already included. With this parameter, the aim is not identifying the vocabulary richness as we did with other parameters before.

On the contrary, the purpose of this parameter is to identify a distinctive vocabulary used by each ECB President.

In fact, we collected all the keys of the word frequencies of the database and we deleted the keys that were shared at least by two presidents. 
In this way, we were able to identify a vocabulary representing a specific presidents among the others, this parameters can also help us to collocate the speech  in a specific time frame during history, or to identify some main topics deployed in that specific moment in time.
"""

#TRICHET
trichet_dictionary = (dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]).iloc[:,1]

dict_tr_2 = []
for i in trichet_dictionary:
  dict_tr_1 = ast.literal_eval(i)
  for key, value in dict_tr_1.items():
    dict_tr_2.append({key:value})


counter_tr = collections.Counter()
for el in dict_tr_2:
  counter_tr.update(el)
freq_ecword_tr=dict(counter_tr)
freq_ecword_tr = dict( sorted(freq_ecword_tr.items(), key=lambda item: item[1], reverse=True))

#DUISENBERG
duisenberg_dictionary = (dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]).iloc[:,1]

dict_du_2 = []
for i in duisenberg_dictionary:
  dict_du_1 = ast.literal_eval(i)
  for key, value in dict_du_1.items():
    dict_du_2.append({key:value})


counter_du = collections.Counter()
for el in dict_du_2:
  counter_du.update(el)
freq_ecword_du=dict(counter_du)
freq_ecword_du = dict( sorted(freq_ecword_du.items(), key=lambda item: item[1], reverse=True))

#DRAGHI
draghi_dictionary = (dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]).iloc[:,1]

dict_dra_2 = []
for i in draghi_dictionary:
  dict_dra_1 = ast.literal_eval(i)
  for key, value in dict_dra_1.items():
    dict_dra_2.append({key:value})


counter_dra = collections.Counter()
for el in dict_dra_2:
  counter_dra.update(el)
freq_ecword_dra=dict(counter_dra)
freq_ecword_dra = dict( sorted(freq_ecword_dra.items(), key=lambda item: item[1], reverse=True))

#LAGARDE
lagarde_dictionary = (dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]).iloc[:,1]

dict_la_2 = []
for i in lagarde_dictionary:
  dict_la_1 = ast.literal_eval(i)
  for key, value in dict_la_1.items():
    dict_la_2.append({key:value})


counter_la = collections.Counter()
for el in dict_la_2:
  counter_la.update(el)
freq_ecword_la=dict(counter_la)
freq_ecword_la = dict( sorted(freq_ecword_la.items(), key=lambda item: item[1], reverse=True))

def convert(set):
    return list(set)

def Find_common_keys(dict_a, dict_b, dict_c, dict_d):
  ecb_common_terms =  []
  a_b = dict_a.keys() & dict_b.keys() 
  ecb_common_terms.append(convert(a_b))

  a_c = dict_a.keys() & dict_c.keys() 
  ecb_common_terms.append(convert(a_c))

  a_d = dict_a.keys() & dict_d.keys() 
  ecb_common_terms.append(convert(a_d))

  b_c = dict_b.keys() & dict_c.keys() 
  ecb_common_terms.append(convert(b_c))

  b_d = dict_b.keys() & dict_d.keys() 
  ecb_common_terms.append(convert(b_d))

  c_d = dict_c.keys() & dict_d.keys() 
  ecb_common_terms.append(convert(c_d))

  ecb_common_terms= [ item for elem in ecb_common_terms for item in elem]
  ecb_common_terms = list(dict.fromkeys(ecb_common_terms))
  return ecb_common_terms

ecb_common_pres_speech = Find_common_keys(freq_ecword_tr, freq_ecword_du, freq_ecword_dra, freq_ecword_la)

"""Now, we delete the common keys to find words that are unique to each president:"""

def entries_to_remove(entries, the_dict):
    for key in entries:
        if key in the_dict:
            del the_dict[key]

#Trichet
entries_to_remove(ecb_common_pres_speech, freq_ecword_tr)
#freq_ecword_tr = sorted(freq_ecword_tr.items(), key=lambda x:x[1], reverse=True)
freq_ecword_tr_df = pd.DataFrame([[freq_ecword_tr]], columns=['ecb_pres_dict'])
freq_ecword_tr_df['who'] = 'Jean-Claude Trichet'
stylo_tr = pd.DataFrame.merge(dataset_stylo,freq_ecword_tr_df,on='who')


#Duisenberg
entries_to_remove(ecb_common_pres_speech, freq_ecword_du)
#freq_ecword_du = sorted(freq_ecword_du.items(), key=lambda x:x[1], reverse = True)
freq_ecword_du_df = pd.DataFrame([[freq_ecword_du]], columns=['ecb_pres_dict'])
freq_ecword_du_df['who'] = 'Willem F. Duisenberg'
stylo_du = pd.DataFrame.merge(dataset_stylo,freq_ecword_du_df,on='who')


#Draghi
entries_to_remove(ecb_common_pres_speech, freq_ecword_dra)
#freq_ecword_dra = sorted(freq_ecword_dra.items(), key=lambda x:x[1], reverse = True)
freq_ecword_dra_df = pd.DataFrame([[freq_ecword_dra]], columns=['ecb_pres_dict'])
freq_ecword_dra_df['who'] = 'Mario Draghi'
stylo_dra = pd.DataFrame.merge(dataset_stylo,freq_ecword_dra_df,on='who')


#Lagarde
entries_to_remove(ecb_common_pres_speech, freq_ecword_la)
#freq_ecword_la = sorted(freq_ecword_la.items(), key=lambda x:x[1], reverse = True)
freq_ecword_la_df = pd.DataFrame([[freq_ecword_la]], columns=['ecb_pres_dict'])
freq_ecword_la_df['who'] = 'Christine Lagarde'
stylo_la = pd.DataFrame.merge(dataset_stylo,freq_ecword_la_df,on='who')

dataset_stylo = stylo_tr.append([stylo_du, stylo_dra, stylo_la], ignore_index=True)

del dataset_stylo['what_frequencies']

#Duisenberg

wc_duisenberg = WordCloud(background_color='white', width= 5000, height= 5000, max_words=100,
               relative_scaling = 0.5, normalize_plurals= False).generate_from_frequencies(freq_ecword_du)
plt.title('Willem F. Duisenberg distinctive vocabulary')
plt.imshow(wc_duisenberg)
plt.show()
wc_duisenberg.to_file('wordcloud_duisenberg.png')

"""Willem F. Duisenberg was the president of the ECB from 1998 to 2003. 
From his vocabulary, we can identify the following distinctive words:
- 'Randzioplath' a Member of the European Parliament from 1989 to 2004, representing the Social Democratic Party of Germany.

- 'PES' which stands for the European Socialist Party in the European Parliament for which Ranzioplath was a member.

- 'EMI' which is the acronym for European Monetary Institute. 
After the Maastricht Treaty, a road map to a common currency and a central bank for the European Union was began.
The European Monetary Institute (EMI) was established in January 1994 and was an intermediate, but crucial step towards establishing the ECB. The EMI had two presidents: Alexandre Lamfalussy and Duisenberg itself. 

- 'Translation' which describes perfectly the historic period of transition to the Euro and the institution of the Central Banks.

- 'Noyer' which is the surname for Christian Noyer, the vice president and Duisenberg.


"""

#Trichet

wc_trichet = WordCloud(background_color='white', width= 5000, height= 5000, max_words=100,
               relative_scaling = 0.5, normalize_plurals= False).generate_from_frequencies(freq_ecword_tr)
plt.imshow(wc_trichet)
plt.show()
wc_trichet.to_file('wordcloud_trichet.png')

"""Jean Claude Trichet has been an ECB President from 2003 to 2011.
As we can see the most deployed words in his speeches are here displayed. More specifically, we can identify some of these words:

- *'Estonia'* and *'Slovakia'* which joined the European Union in 2004
- *'Bubble'* from the 2007 economic crisis 
- *'Basel'* since Trichet was part of the Board of Directors of the Bank of International Settlements (BIS) which is located in Basel

- *'Imports'* that could possibly be related to the increasing role of New EU Member States as trade partners, as well as rapidly increasing imports from Asia, especially China.

- *'Turmoil'* and *'Turbolence'* which could be easily linked to the feelings arose from the economic crisis in 2007.
Moreover, they could also be considered as two distinctive vocabulary features used many times by Trichet in his speeches to relate to the feelings of fear and unknown from the US stock-market crisis. 

"""

#Draghi

wc_draghi = WordCloud(background_color='white', width= 5000, height= 5000, max_words=100,
               relative_scaling = 0.5, normalize_plurals= False).generate_from_frequencies(freq_ecword_dra)
plt.imshow(wc_draghi)
plt.show()
wc_draghi.to_file('wordcloud_draghi.png')

"""Draghi has been the President of the European Central Bank from 2011 to 2019.
Also with him, it is possible to highlight the most deployed words in his speeches: 

- *'QE'* which stands for Quantitative Easing. It is a monetary policy startegy  in which a central bank purchases longer-term securities from the open market in order to increase the money supply and encourage lending and investment. 
Buying these securities adds new money to the economy, and also serves to lower interest rates. 

This policy was used to fight back the previous economic crisis and it started in 2015.

- 'Risk - sharing', the QE policy is a risk-sharing policy due to the fact that National Central Banks asks loans to the ECB to acquire the Govies (State Obbligations). With this mechanism, the ECB didn't expose itself to the sovereign risk of the obbligations acquired and allowed the consecutive spread of the risk in the Eurosystem.

- *'SSM'* which is the acronynim for Single Supervisory Mechanism (SSM) refers to the system of banking supervision in Europe. It comprises the ECB and the national supervisory authorities of the participating countries.
It has the aim of supervising the European banking system after the 2007 financial crisi and it came into force in 2014.

- *'ABS'* which stands for Asset-Backed Securities that were the topic of a repurchase programe started by Draghi to inject liquidity in the system and by forcing the banks that sold these ABS to deploy the profit for giving loans to their customers and increase the amount of liquidity in the economy.
"""

#Lagarde

wc_lagarde = WordCloud(background_color='white', width= 5000, height= 5000, max_words=100,
               relative_scaling = 0.5, normalize_plurals= False).generate_from_frequencies(freq_ecword_la)
plt.imshow(wc_lagarde)
plt.show()
wc_lagarde.to_file('wordcloud_lagarde.png')

"""Madame Lagarde is the current President of the European Central Bank from 2019. 
As we can see, the majority of the words deployed in her speeches are covid-related: 

- *'Pandemic'*, *'Covid'*, *'Coronavirus'*, *'Lockdown'* are words that unfortunately can be tighted linked to the present situation.
With this vocabulary, we can see that it is possible to select a specific historic timeframe that will help the algorithm to better classify it author. 

- *'PEPP'* which stands for Pandemic emergency purchase programme that aims to counter the serious risks to the monetary policy transmission mechanism and the outlook for the euro area posed by the coronavirus (COVID-19) outbreak.
The PEPP is a temporary asset purchase programme of private and public sector securities which started in March 2020.

## READABILITY SCORES

As last set parameters, we decided to consider the ease of readability of a text.
"""

def syllable_count(word):
    global cmudict
    d = cmudict
    try:
        syl = [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
    except:
        syl = syllable_count_Manual(word)
    return syl


def syllable_count_Manual(word):
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
            if word.endswith("e"):
                count -= 1
    if count == 0:
        count += 1
    return count

"""### Flesch Reading Ease

The Flesch Reading Ease gives a text a score between 1 and 100, with 100 being the highest readability score. Scoring between 70 to 80 is equivalent to school grade level 8. This means text should be fairly easy for the average adult to read.

The formula was developed in the 1940s by Rudolf Flesch. He was a consultant with the Associated Press, developing methods for improving the readability of newspapers.

Now, over 70 years later, the Flesch Reading Ease is used by marketers, research communicators and policy writers, amongst many others. All use it to help them assess the ease by which a piece of text will be understood and engaged with.
"""

def FleschReadingEase(text):
    number_of_sentences = sent_tokenize(text)
    NoOfsentences= len(number_of_sentences)
    words = RemoveSpecialCHs(text)
    l = float(len(words))
    scount = 0
    for word in words:
        scount += syllable_count(word)

    I = 206.835 - 1.015 * (l / float(NoOfsentences)) - 84.6 * (scount / float(l))
    return I

flesch_read_ease=[]
for el in dataset_stylo['Speeches']:
  flesch_read_ease.append(FleschReadingEase(el))

flesch_read_ease= pd.DataFrame(flesch_read_ease)
flesch_read_ease.columns=['flesch_read_ease']

dataset_stylo = dataset_stylo.join(flesch_read_ease)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['flesch_read_ease']:
  start = start + el

trichet_flesch_read_ease = start/len(trichet_mean['flesch_read_ease'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['flesch_read_ease']:
  start = start + el

duisen_flesch_read_ease = start/len(duisen_mean['flesch_read_ease'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['flesch_read_ease']:
  start = start + el

draghi_flesch_read_ease = start/len(draghi_mean['flesch_read_ease'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['flesch_read_ease']:
  start = start + el

lagarde_flesch_read_ease =start/len(lagarde_mean['flesch_read_ease'])

"""### Flesch-Kincaid Grade Level

The Flesch–Kincaid readability tests are readability tests designed to indicate how difficult a passage in English is to understand. There are two tests, the Flesch Reading-Ease, and the Flesch–Kincaid Grade Level. Although they use the same core measures (word length and sentence length), they have different weighting factors.

The results of the two tests correlate approximately inversely: a text with a comparatively high score on the Reading Ease test should have a lower score on the Grade-Level test. Rudolf Flesch devised the Reading Ease evaluation; somewhat later, he and J. Peter Kincaid developed the Grade Level evaluation for the United States Navy.
"""

def FleschCincadeGradeLevel(text):
    number_of_sentences = sent_tokenize(text)
    NoOfsentences= len(number_of_sentences)
    words = RemoveSpecialCHs(text)
    scount = 0
    for word in words:
        scount += syllable_count(word)

    l = len(words)
    F = 0.39 * (l / NoOfsentences) + 11.8 * (scount / float(l)) - 15.59
    return F

flesch_kincaid_read=[]
for el in dataset_stylo['Speeches']:
  flesch_kincaid_read.append(FleschCincadeGradeLevel(el))

flesch_kincaid_read= pd.DataFrame(flesch_kincaid_read)
flesch_kincaid_read.columns=['flesch_kincaid_read']

dataset_stylo = dataset_stylo.join(flesch_kincaid_read)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['flesch_kincaid_read']:
  start = start + el

trichet_flesch_kincaid_read = start/len(trichet_mean['flesch_kincaid_read'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['flesch_kincaid_read']:
  start = start + el

duisen_flesch_kincaid_read = start/len(duisen_mean['flesch_kincaid_read'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['flesch_kincaid_read']:
  start = start + el

draghi_flesch_kincaid_read = start/len(draghi_mean['flesch_kincaid_read'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['flesch_kincaid_read']:
  start = start + el

lagarde_flesch_kincaid_read =start/len(lagarde_mean['flesch_kincaid_read'])

"""### Gunning-Fog Index

In linguistics, the Gunning fog index is a readability test for English writing. The index estimates the years of formal education a person needs to understand the text on the first reading. For instance, a fog index of 12 requires the reading level of a United States high school senior (around 18 years old). The test was developed in 1952 by Robert Gunning, an American businessman who had been involved in newspaper and textbook publishing.

The fog index is commonly used to confirm that text can be read easily by the intended audience. Texts for a wide audience generally need a fog index less than 12. Texts requiring near-universal understanding generally need an index less than 8.
"""

def GunningFoxIndex(text):
    number_of_sentences = sent_tokenize(text)
    NoOfsentences= len(number_of_sentences)
    words = RemoveSpecialCHs(text)
    NoOFWords = float(len(words))
    complexWords = 0
    for word in words:
        if (syllable_count(word) > 2):
            complexWords += 1

    G = 0.4 * ((NoOFWords / NoOfsentences) + 100 * (complexWords / NoOFWords))
    return G

gunning_fox_read=[]
for el in dataset_stylo['Speeches']:
  gunning_fox_read.append(GunningFoxIndex(el))

gunning_fox_read= pd.DataFrame(gunning_fox_read)
gunning_fox_read.columns=['gunning_fox_read']

dataset_stylo = dataset_stylo.join(gunning_fox_read)

# Trichet
trichet_mean= dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
start = 0
for el in trichet_mean['gunning_fox_read']:
  start = start + el

trichet_gunning_fox_read = start/len(trichet_mean['gunning_fox_read'])

#Duisenberg
duisen_mean= dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
start = 0
for el in duisen_mean['gunning_fox_read']:
  start = start + el

duisen_gunning_fox_read = start/len(duisen_mean['gunning_fox_read'])

#Draghi
draghi_mean= dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
start = 0
for el in draghi_mean['gunning_fox_read']:
  start = start + el

draghi_gunning_fox_read= start/len(draghi_mean['gunning_fox_read'])

#Lagarde
lagarde_mean= dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]
start = 0

for el in lagarde_mean['gunning_fox_read']:
  start = start + el

lagarde_gunning_fox_read =start/len(lagarde_mean['gunning_fox_read'])

"""Lastly, a plot considering each readability score for each ECB President is computed:"""

fig, (plt1, plt2, plt3) = plt.subplots(1, 3)
plt.tight_layout()
fig.suptitle('Readability scores for ECB President')
plt.subplots_adjust(top=0.85)

presidents = ['Jean-Claude Trichet','Willem F. Duisenberg ','Mario Draghi','Christine Lagarde']
quantity_1 = [trichet_flesch_read_ease,duisen_flesch_read_ease,draghi_flesch_read_ease,lagarde_flesch_read_ease]

plt1.barh(presidents,quantity_1)
plt1.set(xlabel="Flesch readability ")
plt1.set_xlim([30, 45])

quantity_2 = [trichet_flesch_kincaid_read,duisen_flesch_kincaid_read,draghi_flesch_kincaid_read,lagarde_flesch_kincaid_read]

plt2.barh(presidents,quantity_2)
plt2.set(xlabel="Flesch Kincaid readability ")
plt2.yaxis.set_visible(False)
plt2.set_xlim([10, 15.5])

quantity_3 = [trichet_gunning_fox_read,duisen_gunning_fox_read,draghi_gunning_fox_read,lagarde_gunning_fox_read]

plt3.barh(presidents,quantity_3)
plt3.set(xlabel="Gunning Fog readability")
plt3.yaxis.set_visible(False)
plt3.set_xlim([15, 19.5])


fig.show()

"""## API FEATURES"""

!pip install -U expertai-nlapi

import os
os.environ["EAI_USERNAME"] = 'riva.arianna.97@gmail.com'
os.environ["EAI_PASSWORD"] = 'Liliana1958#'

from expertai.nlapi.cloud.client import ExpertAiClient
client = ExpertAiClient()

language= 'en'

"""### Behavioural traits"""

client = ExpertAiClient()
language= 'en'

plt.style.use('ggplot')

def behavioural_traits(client, text, language):
    try:
      text = str(text)[0:10000]  # limit the input size
      geo_classification = client.classification(body={"document": {"text": text}}, params={'language': language, 'taxonomy': 'behavioral-traits'})
      geo_categories = []
      geo_scores = []
      for category in geo_classification.categories:
        geo_categories.append(category.label)
        geo_scores.append(category.frequency)
        
      df_test = (pd.DataFrame([geo_categories,geo_scores])).transpose()
      df_test.columns=['cat_label','cat_score']
      df_test = df_test[df_test.cat_score == df_test.cat_score.max()]
      df_test.drop(columns= 'cat_score', inplace=True)
      df_test = df_test.to_string(header=False, index=False)
      return df_test
      
    except Exception as e: 
        print(str(e) +": " + str(text))

dataset_stylo['behavioural_traits'] = dataset_stylo['Speeches'].apply(lambda Speeches: behavioural_traits(client, Speeches, language))

dataset_stylo.to_csv('dataset_behavioural')

"""### Emotional traits"""

dataset_stylo = dataset = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/dataset_behavioural.csv')

client = ExpertAiClient()
language= 'en'

plt.style.use('ggplot')

def emotional_traits(client, text, language):
    try:
      text = str(text)[0:10000]  # limit the input size
      geo_classification = client.classification(body={"document": {"text": text}}, params={'taxonomy': 'emotional-traits','language': language})
      geo_categories = []
      geo_scores = []
      for category in geo_classification.categories:
        geo_categories.append(category.label)
        geo_scores.append(category.frequency)
        
      df_test = (pd.DataFrame([geo_categories,geo_scores])).transpose()
      df_test.columns=['cat_label','cat_score']
      df_test = df_test[df_test.cat_score == df_test.cat_score.max()]
      df_test.drop(columns= 'cat_score', inplace=True)
      df_test = df_test.to_string(header=False, index=False)
      return df_test
      
    except Exception as e: 
        print(str(e) +": " + str(text))

dataset_stylo['emotional_traits'] = dataset_stylo['Speeches'].apply(lambda Speeches: emotional_traits(client, Speeches, language))

dataset_stylo.to_csv('dataset_emotional')

"""### Topic analysis"""

dataset_stylo = dataset = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/dataset_emotional.csv')

client = ExpertAiClient()
language= 'en'

plt.style.use('ggplot')

def topic_analysis (client, text, language):
    try:
      text = str(text)[0:10000]  # limit the input size
      geo_classification = client.classification(body={"document": {"text": text}}, params={'taxonomy': 'iptc','language': language})
      geo_categories = []
      geo_scores = []
      for category in geo_classification.categories:
        geo_categories.append(category.label)
        geo_scores.append(category.frequency)
        
      df_test = (pd.DataFrame([geo_categories,geo_scores])).transpose()
      df_test.columns=['cat_label','cat_score']
      df_test = df_test[df_test.cat_score == df_test.cat_score.max()]
      df_test.drop(columns= 'cat_score', inplace=True)
      df_test = df_test.to_string(header=False, index=False)
      return df_test
      
    except Exception as e: 
        print(str(e) +": " + str(text))

dataset_stylo['topyc_analysis'] = dataset_stylo['Speeches'].apply(lambda Speeches: topic_analysis(client, Speeches, language))

dataset_stylo.to_csv('dataset_topic')

"""As last step, it is possible to compute a representative plot for each ECB President regarding the emotional, behavioural traits, and the topics deployed in their speeches."""

dataset_stylo = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/dataset_topic.csv')

dataset_stylo.drop(dataset_stylo.columns[0], axis=1, inplace=True)
dataset_stylo.drop(dataset_stylo.columns[0], axis=1, inplace=True)
dataset_stylo.drop(dataset_stylo.columns[0], axis=1, inplace=True)

df_behavioural = dataset_stylo.loc[:,['who', 'behavioural_traits']]

df_trichet_behave = df_behavioural[(dataset_stylo['who'] == 'Jean-Claude Trichet')]

df_duisen_behave = df_behavioural[(dataset_stylo['who'] == 'Willem F. Duisenberg')]

df_draghi_behave = df_behavioural[(dataset_stylo['who'] == 'Mario Draghi')]

df_lagarde_behave = df_behavioural[(dataset_stylo['who'] == 'Christine Lagarde')]

df_trichet_behave = pd.DataFrame(df_trichet_behave['behavioural_traits'].value_counts())
df_trichet_behave.rename(columns={'behavioural_traits' : 'behave_trichet'},inplace=True)

df_duisen_behave = pd.DataFrame(df_duisen_behave['behavioural_traits'].value_counts())
df_duisen_behave.rename(columns={'behavioural_traits' : 'behave_duisen'}, inplace=True)

df_draghi_behave = pd.DataFrame(df_draghi_behave['behavioural_traits'].value_counts())
df_draghi_behave.rename(columns={'behavioural_traits' : 'behave_draghi'}, inplace=True)

df_lagarde_behave = pd.DataFrame(df_lagarde_behave['behavioural_traits'].value_counts())
df_lagarde_behave.rename(columns={'behavioural_traits' : 'behave_lagarde'}, inplace=True)

result_behavioural = ((df_trichet_behave.join(df_duisen_behave)).join(df_draghi_behave)).join(df_lagarde_behave)
result_behavioural.fillna(0, inplace=True)
result_behavioural = result_behavioural.iloc[0:10]

sns.heatmap(result_behavioural)
plt.title('Behavioural traits for ECB Presidents')
plt.show()

df_emotional = dataset_stylo.loc[:,['who', 'emotional_traits']]

df_trichet_emotional = df_emotional[(dataset_stylo['who'] == 'Jean-Claude Trichet')]

df_duisen_emotional = df_emotional[(dataset_stylo['who'] == 'Willem F. Duisenberg')]

df_draghi_emotional = df_emotional[(dataset_stylo['who'] == 'Mario Draghi')]

df_lagarde_emotional = df_emotional[(dataset_stylo['who'] == 'Christine Lagarde')]

df_trichet_emotional = pd.DataFrame(df_trichet_emotional['emotional_traits'].value_counts())
df_trichet_emotional.rename(columns={'emotional_traits' : 'emotional_trichet'},inplace=True)

df_duisen_emotional = pd.DataFrame(df_duisen_emotional['emotional_traits'].value_counts())
df_duisen_emotional.rename(columns={'emotional_traits' : 'emotional_duisen'}, inplace=True)

df_draghi_emotional = pd.DataFrame(df_draghi_emotional['emotional_traits'].value_counts())
df_draghi_emotional.rename(columns={'emotional_traits' : 'emotional_draghi'}, inplace=True)

df_lagarde_emotional = pd.DataFrame(df_lagarde_emotional['emotional_traits'].value_counts())
df_lagarde_emotional.rename(columns={'emotional_traits' : 'emotional_lagarde'}, inplace=True)

result_emotional = ((df_trichet_emotional.join(df_duisen_emotional)).join(df_draghi_emotional)).join(df_lagarde_emotional)
result_emotional.fillna(0, inplace=True)
result_emotional.drop(['Empty DataFrame\nColumns: [cat_label]\nIndex: []'],inplace=True)
result_emotional = result_emotional.iloc[0:10]

sns.heatmap(result_emotional)
plt.title('Emotional traits for ECB Presidents')
plt.show()

df_topic = dataset_stylo.loc[:,['who', 'topyc_analysis']]

df_trichet_topic = df_topic[(dataset_stylo['who'] == 'Jean-Claude Trichet')]

df_duisen_topic = df_topic[(dataset_stylo['who'] == 'Willem F. Duisenberg')]

df_draghi_topic = df_topic[(dataset_stylo['who'] == 'Mario Draghi')]

df_lagarde_topic = df_topic[(dataset_stylo['who'] == 'Christine Lagarde')]

df_trichet_topic = pd.DataFrame(df_trichet_topic['topyc_analysis'].value_counts())
df_trichet_topic.rename(columns={'topyc_analysis' : 'topic_trichet'},inplace=True)

df_duisen_topic = pd.DataFrame(df_duisen_topic['topyc_analysis'].value_counts())
df_duisen_topic.rename(columns={'topyc_analysis' : 'topic_duisen'}, inplace=True)

df_draghi_topic = pd.DataFrame(df_draghi_topic['topyc_analysis'].value_counts())
df_draghi_topic.rename(columns={'topyc_analysis' : 'topic_draghi'}, inplace=True)

df_lagarde_topic = pd.DataFrame(df_lagarde_topic['topyc_analysis'].value_counts())
df_lagarde_topic.rename(columns={'topyc_analysis' : 'topic_lagarde'}, inplace=True)

result_topic = ((df_trichet_topic.join(df_duisen_topic)).join(df_draghi_topic)).join(df_lagarde_topic)
result_topic.fillna(0, inplace=True)

result_topic = result_topic.iloc[0:10]

sns.heatmap(result_topic)
plt.title('Topics for ECB Presidents')
plt.show()

"""## FEATURE ENGINEERING

## 1) Handling missing values
"""

dataset_stylo.isnull().sum()

dataset_stylo.dropna(inplace=True)

dataset_stylo.isna().any().any()

"""As we can see, there are missing values in the dataset. 

To avoid further problems during the training, our first step of feature engineering will be deleting them.

## 2) Outliers

Outliers can be unusually and extremely different from most of the data points existing in our sample. It could be a very large observation or a very small observation. Outliers can create biased results while calculating the stats of the data due to its extreme nature, thereby affecting further statistical/ML models.

AVERAGE WORD LENGTH
"""

import seaborn as sns

fig, ax = plt.subplots()
fig.set_size_inches(10, 8)
sns.boxplot( x=dataset_stylo["who"], y=dataset_stylo["avg_word_len"],  palette="Reds")
sns.set(style="darkgrid")
plt.title('Outliers for avg_word_len')
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
plt.tight_layout()


plt.show()

dataset_stylo = dataset_stylo[(dataset_stylo['avg_word_len'] < 7.4) & (dataset_stylo['avg_word_len'] > 6)]

"""AVERAGE SENTENCE LENGTH"""

import seaborn as sns

fig, ax = plt.subplots()
fig.set_size_inches(10, 8)
sns.boxplot( x=dataset_stylo["who"], y=dataset_stylo["avg_speech_len"],  palette="Reds")
sns.set(style="darkgrid")
plt.title('Outliers for avg_speech_len')
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
plt.tight_layout()


plt.show()

dataset_stylo = dataset_stylo[(dataset_stylo['avg_speech_len'] < 40)]

"""YULES CHARACTERISTIC K"""

import seaborn as sns

fig, ax = plt.subplots()
fig.set_size_inches(10, 8)
sns.boxplot( x=dataset_stylo["who"], y=dataset_stylo["yules_char_k"],  palette="Reds")
sns.set(style="darkgrid")
plt.title('Outliers for yules_char_k')
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
plt.tight_layout()


plt.show()

dataset_stylo = dataset_stylo[(dataset_stylo['yules_char_k'] < 2500)]

"""SIMPSON INDEX"""

import seaborn as sns

fig, ax = plt.subplots()
fig.set_size_inches(10, 8)
sns.boxplot( x=dataset_stylo["who"], y=dataset_stylo["simpson_index"],  palette="Reds")
sns.set(style="darkgrid")
plt.title('Outliers for simpson_index')
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
plt.tight_layout()


plt.show()

dataset_stylo = dataset_stylo[(dataset_stylo['simpson_index'] > 0.9800)]

"""## 3) Binning

Binning is a tecnique that can be applied to both numerical and categorical data. 
It has the aim of grouping observation together in one category. 

In addition, binning is a tecnique that allows you to have a more robust model and it prevents overfitting.

First of all, binning could be suitable option for the readability scores whose indeces are already classified in grading class.

Due to the reason above stated, it is possible to take the numerical score and to bin it in terms of the index considered.

### Flesch Reading Ease

The Flesch Reading Ease gives a text a score between 1 and 100, with 100 being the highest readability score. Scoring between 70 to 80 is equivalent to school grade level 8. This means text should be fairly easy for the average adult to read.

We can divide the redability score in the following categories:

- Between 0 and 30: Very Difficult
- Between 30 and 50: Difficult
- Between 50 and 60: Fairly difficult
- Between 60 and 70: Standard difficulty
- Between 70 and 80: Fairly Easy
- Between 80 and 90: Easy
- Above 90: Very Easy
"""

dataset_stylo['flesch_read_ease_bin'] = pd.cut(dataset_stylo['flesch_read_ease'], bins=[0,30,50,60,70,80,90,100], labels=["Very difficult",
                                              "Difficult", "Fairly difficult", "Standard","Fairly Easy", "Easy", "Very Easy"])

"""### Flesch-Kincaid Grade Level

Flesch-Kincaid grade level tells you the American school grade you would need to be in to comprehend the material on the page.

As a measure, most of your writing should be able to be understood by students in seventh grade.

This readability score describes its grade levels in the following table:
- Between 0 and 30: College Graduate
- Between 30 and 50: College student 
- Between 50 and 60: 10th/12th Grade
- Between 60 and 70: 8th/9th Grade
- Between 70 and 80: 7th Grade
- Between 80 and 90: 6th Grade
- Above 90: 5th Grade
"""

dataset_stylo['flesch_kincaid_read_bin'] = pd.cut(dataset_stylo['flesch_kincaid_read'], bins=[0,30,50,60,70,80,90,100], labels=["College Graduate",
                                              "College Student", "10th/12th Grade", "8th/9th Grade","7th Grade", "6th Grade", "5th Grade"])

"""### Gunning Fog index

The index estimates the years of formal education a person needs to understand the text on the first reading. For instance, a fog index of 12 requires the reading level of a United States high school senior (around 18 years old). The test was developed in 1952 by Robert Gunning, an American businessman who had been involved in newspaper and textbook publishing.

The fog index is commonly used to confirm that text can be read easily by the intended audience. Texts for a wide audience generally need a fog index less than 12. Texts requiring near-universal understanding generally need an index less than 8.

This index could be considered in the following categories:
- Below 6: 6th Grade
- Around 7: 7th Grade
- Around 8: 8th Grade
- Around 9: High school freshman
- Around 10: High school sophomore
- Between 11-12: High school senior
- Between 13 and 15: College junior
- Around 16: College senior
- Between 17 and 20: Post-graduate
- Above 20: Post-graduate plus
"""

dataset_stylo['gunning_fox_read_bin'] = pd.cut(dataset_stylo['gunning_fox_read'], bins=[0,6,7,8,9,10,12,15,16,17,20,27], labels=["6th Grade",
                                              "7th Grade", "8th Grade", "High school freshman","High school sophomore","High school senior", "College junior", "College senior", "Post-graduate", "Higher than post-graduate plus","Post-graduate plus"])

"""## 4) Count column frequency

For categorical variables such as emtional and behavioural traits, topic, and readability indexes.

For Flesch Reading Ease aatribute:
"""

counts_flesch_ease = dataset_stylo['flesch_read_ease_bin'].value_counts()
counts_flesch_ease = counts_flesch_ease.to_dict()
dataset_stylo['flesch_read_ease_bin'+'_counts'] = dataset_stylo['flesch_read_ease_bin'].map(counts_flesch_ease)

counts_flesch_ease

"""For Flesch Kincaid Ease attribute:"""

counts_flesch_kincaid_ease = dataset_stylo['flesch_kincaid_read_bin'].value_counts()
counts_flesch_kincaid_ease = counts_flesch_kincaid_ease.to_dict()
dataset_stylo['flesch_kincaid_read_bin'+'_counts'] = dataset_stylo['flesch_kincaid_read_bin'].map(counts_flesch_kincaid_ease)

counts_flesch_kincaid_ease

"""For Gunning Fox Index:"""

counts_gunning_fox = dataset_stylo['gunning_fox_read'].value_counts()
counts_gunning_fox  = counts_gunning_fox.to_dict()
dataset_stylo['gunning_fox_read'+'_counts'] = dataset_stylo['gunning_fox_read'].map(counts_gunning_fox )

"""For emotional traits:"""

counts_emotional_traits = dataset_stylo['emotional_traits'].value_counts()
counts_emotional_traits  = counts_emotional_traits.to_dict()
dataset_stylo['emotional_traits'+'_counts'] = dataset_stylo['emotional_traits'].map(counts_emotional_traits )

"""For behavioural traits:"""

counts_behavioural_traits = dataset_stylo['behavioural_traits'].value_counts()
counts_behavioural_traits  = counts_behavioural_traits.to_dict()
dataset_stylo['behavioural_traits'+'_counts'] = dataset_stylo['behavioural_traits'].map(counts_behavioural_traits )

"""For topic attribute:"""

counts_topic = dataset_stylo['topyc_analysis'].value_counts()
counts_topic  = counts_topic.to_dict()
dataset_stylo['topyc_analysis'+'_counts'] = dataset_stylo['topyc_analysis'].map(counts_topic )

"""## 5) Group Statistics"""

def group_stats(input_str):
  temp = dataset_stylo.groupby('who')[input_str].agg(['mean']).rename({'mean': input_str},axis=1)

  conditions = [
    (dataset_stylo['who'] == 'Jean-Claude Trichet'),
    (dataset_stylo['who'] == 'Willem F. Duisenberg'),
    (dataset_stylo['who'] == 'Mario Draghi'),
    (dataset_stylo['who'] == 'Christine Lagarde')
    ]
  values = [temp.iloc[1,0], temp.iloc[3,0], temp.iloc[2,0], temp.iloc[0,0]]
  dataset_stylo[input_str +'_mean'] = np.select(conditions, values)

"""For avg_word_len:"""

group_stats('avg_word_len')

"""For avg_speech_len:"""

group_stats('avg_speech_len')

"""For count_punct:"""

group_stats('count_punct')

"""For yules_char_k:"""

group_stats('yules_char_k')

"""For shannon_entropy:"""

group_stats('shannon_entropy')

"""For simpson_index:"""

group_stats('simpson_index')

"""For hapax_legemena:"""

group_stats('hapax_legemena')

"""For honor_measure:"""

group_stats('honor_measure')

"""For brunets_w:"""

group_stats('brunets_w')

"""## 6) Normalization

Normalization is a technique often applied as part of data preparation for machine learning. The goal of normalization is to change the values of numeric columns in the dataset to use a common scale, without distorting differences in the ranges of values or losing information. Normalization is also required for some algorithms to model the data correctly.
"""

scaler = MinMaxScaler()

dataset_stylo[['avg_word_len','avg_speech_len', 'count_punct', 'count_fun_words', 'yules_char_k', 'shannon_entropy', 
               'simpson_index', 'hapax_legemena', 'honor_measure', 'brunets_w', 'avg_word_len_mean', 'avg_speech_len_mean',
               'count_punct_mean', 'yules_char_k_mean', 'shannon_entropy_mean', 'simpson_index_mean', 'hapax_legemena_mean',
               'honor_measure_mean', 'brunets_w_mean']] = scaler.fit_transform(dataset_stylo[['avg_word_len','avg_speech_len', 
                                                                                              'count_punct', 'count_fun_words', 
                                                                                              'yules_char_k', 'shannon_entropy', 'simpson_index', 'hapax_legemena', 'honor_measure', 'brunets_w', 'avg_word_len_mean', 'avg_speech_len_mean', 'count_punct_mean', 'yules_char_k_mean', 'shannon_entropy_mean', 'simpson_index_mean', 'hapax_legemena_mean', 'honor_measure_mean', 'brunets_w_mean']])

"""## 7) Permutation of the Database"""

dataset_stylo = dataset_stylo.sample(frac = 1)
dataset_stylo.reset_index(drop= True, inplace=True)

"""## FEATURE SELECTION - MANUAL

### With sklearn selectkbest

The scikit-learn library provides the SelectKBest class that can be used with a suite the chi-squared (chi²) statistical test for non-negative features to select 10 of the best features from the Dataset.
"""

dataset_stylo.drop(dataset_stylo.columns[0], axis=1, inplace=True)

dataset_stylo.drop(dataset_stylo.columns[0], axis=1, inplace=True)

dataset_stylo.drop(dataset_stylo.columns[0], axis=1, inplace=True)

y = dataset_stylo['who']
X = dataset_stylo.loc[:, dataset_stylo.columns != 'who']

def prepare_inputs(X):
	oe = OrdinalEncoder()
	oe.fit(X)
	X = oe.transform(X)
	return X

X = prepare_inputs(X)

def select_features(X, y):
	fs = SelectKBest(score_func=chi2, k='all')
	fs.fit(X, y)
	X = fs.transform(X)
	return X,fs

X, fs = select_features(X,y)

np.random.seed(6)
for i in range(len(fs.scores_)):
	print('Feature %d: %f' % (i, fs.scores_[i]))

x_labels = ['Speeches','avg_word_len','avg_speech_len','special_char,','count_punct','count_fun_words','yules_char_k','shannon_entropy','simpson_index','hapax_legemena','honor_measure','brunets_w','ecb_pres_dict','flesch_read_ease','flesch_kincaid_read','gunning_fox_read','behavioural_traits','emotional_traits','topyc_analysis','flesch_read_ease_bin','flesch_kincaid_read_bin','gunning_fox_read_bin','flesch_read_ease_bin_counts','flesch_kincaid_read_bin_counts','gunning_fox_read_counts','emotional_traits_counts','behavioural_traits_counts','topyc_analysis_counts','avg_word_len_mean','avg_speech_len_mean','count_punct_mean','yules_char_k_mean','shannon_entropy_mean','simpson_index_mean','hapax_legemena_mean','honor_measure_mean','brunets_w_mean']

# plot the scores
pyplot.bar([i for i in range(len(fs.scores_))], fs.scores_)
pyplot.title('Chi-squared test applied on dataset features')
#pyplot.addlabels(x_labels)
pyplot.show()

"""From the plot, it is possible to see that the most important feature is the shannon entropy.

Moreover, we can see that the features with less importance are gunning_fox_read_counts, emotional_traits_counts, topyc_analysis_counts.

### With ExtraTreesClassifier

Feature importance gives you a score for each feature of your data, the higher the score more important or relevant is the feature towards your output variable.

Feature importance is an inbuilt class that comes with Tree Based Classifiers, we will be using Extra Tree Classifier for extracting the top 10 features for the dataset.
"""

np.random.seed(6)
model = ExtraTreesClassifier()
model.fit(X,y)
feat_importances = pd.Series(model.feature_importances_)
y_labels= ['ecb_pres_dict', 'count_punct_mean', 'avg_speech_len_mean', 'shannon_entropy_mean', 'avg_word_len_mean', 'honor_measure_mean',
           'hapax_legemena_mean','yules_char_k_mean','simpson_index_mean','brunets_w_mean']
y_lab =  np.arange(len(y_labels))

fig, ax = plt.subplots()
feat_importances.nlargest(10).plot(kind='barh')
ax.set_yticks(y_lab)
ax.set_yticklabels(y_labels)
ax.set_title('Feature importances ExtraTreesClassifier')
plt.show()

"""From this model, it is possible to see that the least important features are gunning_fox_read_counts, emotional_traits_counts,flesch_kincaid_read_bin_counts and flesch_kincaid_read_bin.

As we can see, the two models have agreed the same features so far.

### With the correlation heatmap
"""

correlations = dataset_stylo.corr()
plt.figure(figsize=(9, 7))
sns.heatmap(correlations)
plt.title('Correlation among attributes')
plt.show()

"""Also in this case, we see that emotional_traits_counts, behavioural_traits_counts, gunning_fox_counts and flesch_read_ease_bin counts have a very neutral correlation, meaning that they have a low impact on the target variable.

## FEATURE SELECTION - AUTO SK-LEARN
"""

automl = autosklearn.classification.AutoSklearnClassifier()
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, random_state=1)
automl.fit(X_train, y_train)
y_hat = automl.predict(X_test)
print("Accuracy score", sklearn.metrics.accuracy_score(y_test, y_hat))

print(automl.sprint_statistics())

# automl is an object Which has already been created.
profiler_data= PipelineProfiler.import_autosklearn(automl)
PipelineProfiler.plot_pipeline_matrix(profiler_data)

PipelineProfiler.get_exported_pipelines()

"""## MACHINE LEARNING

### Pre-processing
"""

dataset_stylo.drop(['emotional_traits_counts', 'behavioural_traits_counts', 'gunning_fox_read_counts'], inplace=True, axis=1)

dataset_stylo.to_csv('premodel_dataset')

dataset_stylo = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/premodel_dataset.csv')

dataset_stylo.drop(dataset_stylo.columns[0], axis=1, inplace=True)

fig, ax = plt.subplots()
fig.set_size_inches(20, 8)
sns.countplot(x = 'who', data = dataset_stylo, order = dataset_stylo['who'].value_counts().index, 
              palette = sns.color_palette('rocket',2))
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.set_xlabel('Authors of the Speech', fontsize=15)
ax.set_ylabel('Frequency', fontsize=15)
ax.set_title('Distribution of Authors', fontsize=15)
ax.tick_params(labelsize=15)
sns.despine()

"""At this point, we can balance the dataset:"""

np.random.seed(6)
df_trichet = dataset_stylo[(dataset_stylo['who'] == 'Jean-Claude Trichet')]
df_trichet = df_trichet.iloc[0:30,:]

df_duisen = dataset_stylo[(dataset_stylo['who'] == 'Willem F. Duisenberg')]
df_duisen = df_duisen.iloc[0:30,:]

df_draghi = dataset_stylo[(dataset_stylo['who'] == 'Mario Draghi')]
df_draghi = df_draghi.iloc[0:30,:]

df_lagarde = dataset_stylo[(dataset_stylo['who'] == 'Christine Lagarde')]

dataset_stylo = df_trichet.append([df_duisen, df_lagarde, df_draghi], ignore_index=True)

dataset_stylo = dataset_stylo.sample(frac = 1)
dataset_stylo.reset_index(drop= True, inplace=True)

"""Now, we encode the target variable:"""

np.random.seed(6)
LabelEnc = preprocessing.LabelEncoder()
dataset_stylo['who'] = LabelEnc.fit_transform(dataset_stylo.who.values)

"""Now, we can split the dataset into train, test and validation:"""

np.random.seed(6)
train, test = train_test_split(dataset_stylo, test_size=0.33, random_state=42)

y_test = test['who']

x_test = test.loc[:, test.columns != 'who']

np.random.seed(6)
train, val = train_test_split(train, test_size=0.20)

print ("Training  set size", train.shape)
print ("Test set size", test.shape)
print ("Val set size",val.shape)

"""### Feature creation for training

Check for missing values:
"""

train.isnull().sum()

def df_to_dataset(dataframe, shuffle=True, batch_size=32):
  dataframe = dataframe.copy()
  labels = dataframe.pop('who')
  ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
  if shuffle:
    ds = ds.shuffle(buffer_size=len(dataframe))
  ds = ds.batch(batch_size)
  return ds

batch_size = 32
np.random.seed(6)
train_ds = df_to_dataset(train, batch_size=batch_size)
test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)

for feature_batch, label_batch in train_ds.take(1):
  print('Every feature:', list(feature_batch.keys()))
  print('A batch of average word length:', feature_batch['avg_word_len'])
  print('A batch of targets:', label_batch )

dataset_stylo.columns

#Numerical features
num_features = ['avg_word_len', 'avg_speech_len' ,'special_char','count_punct', 'count_fun_words', 'yules_char_k','shannon_entropy',
         'simpson_index', 'hapax_legemena', 'honor_measure', 'brunets_w', 'flesch_read_ease', 'flesch_kincaid_read',
       'gunning_fox_read', 'flesch_read_ease_bin_counts', 'flesch_kincaid_read_bin_counts', 'avg_word_len_mean', 'avg_speech_len_mean', 'count_punct_mean' ,'yules_char_k_mean', 'shannon_entropy_mean', 'simpson_index_mean', 'hapax_legemena_mean', 'honor_measure_mean',
         'brunets_w_mean', 'topyc_analysis_counts']

#Crossed-features columns

#flesch_read_ease and flesch_read_ease_bin_counts
#flesch_kincaid_read and flesch_kincaid_read_bin_counts
#topyc_analysis and topyc_analysis_counts

#Categorical embedded features
cat_features = ['ecb_pres_dict','flesch_read_ease_bin', 'flesch_kincaid_read_bin', 'gunning_fox_read_bin', 'behavioural_traits', 'emotional_traits', 'topyc_analysis']

feature_columns = []

#Numerical Features
np.random.seed(6)
for header in num_features:
  feature_columns.append(feature_column.numeric_column(header))

#Categorical Crossed-Features

def cat_cross_feat(input1, input2):
  vocabulary = dataset_stylo[input2].unique()
  input_2 = tf.feature_column.categorical_column_with_vocabulary_list(input2, vocabulary)
  crossed_feature = feature_column.crossed_column([input1, input_2], hash_bucket_size=1000)
  crossed_feature = feature_column.indicator_column(crossed_feature)
  feature_columns.append(crossed_feature)

np.random.seed(6)
cat_cross_feat('flesch_read_ease', 'flesch_read_ease_bin_counts')
cat_cross_feat('flesch_kincaid_read', 'flesch_kincaid_read_bin_counts')
cat_cross_feat('topyc_analysis', 'topyc_analysis_counts')

#Categorical Embedded Features
np.random.seed(6)
for feature_name in cat_features:
  vocabulary = dataset_stylo[feature_name].unique()
  cat_c = tf.feature_column.categorical_column_with_vocabulary_list(feature_name, vocabulary)
  embedding = feature_column.embedding_column(cat_c, dimension=50)
  feature_columns.append(embedding)

"""### Training of the model

At this point, we start to create the model:
"""

np.random.seed(6)
feature_columns = tf.keras.layers.DenseFeatures(feature_columns)

#lr_schedule = ExponentialDecay()

adam = Adam(lr=1e-2)

emb_dim = 64
n_most_common_words = 80000

np.random.seed(6)
categories_output= len(np.unique(dataset_stylo['who']))
model = tf.keras.Sequential([feature_columns,
                             #layers.Embedding(n_most_common_words,emb_dim),
                             #layers.LSTM(64, dropout=0.1, recurrent_dropout=0.1),
                             layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l1(0.0004)),
                             layers.Dropout(0.02),
                             layers.Dense(64, activation='relu'),
                             layers.Dense(categories_output, activation='softmax')])

model.compile(optimizer= adam,
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

np.random.seed(6)
history = model.fit(train_ds, epochs=30,
                    validation_data=val_ds)

epochs= range(30)
plt.title('Accuracy')
plt.plot(epochs,history.history['accuracy'], color='blue', label='Train')
plt.plot(epochs, history.history['val_accuracy'], color='orange', label='Val')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

_ = plt.figure()
plt.title('Loss')
plt.plot(epochs, history.history['loss'], color='blue', label='Train')
plt.plot(epochs, history.history['val_loss'], color='orange', label='Val')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

test_loss, test_acc = model.evaluate(test_ds)

print('Test Loss:', test_loss)
print('Test Accuracy:', test_acc)

# serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk")

def test_input_fn(features, batch_size=32):
    """An input function for prediction."""
    # Convert the inputs to a Dataset without labels.
    return tf.data.Dataset.from_tensor_slices(dict(features)).batch(batch_size)

test_predict = test_input_fn(dict(x_test))

predict_probs = model.predict(test_predict)
predict_probs

prova = []
results_class = []
for i in predict_probs:
  prova.append(i[0])
  prova.append(i[1])
  prova.append(i[2])
  prova.append(i[3])
  if max([i[0], i[1], i[2], i[3]]) == i[0]:
    results_class.append(0)
  elif max([i[0], i[1], i[2], i[3]]) == i[1]:
    results_class.append(1)
  elif max([i[0], i[1], i[2], i[3]]) == i[2]:
    results_class.append(2)
  else:
    results_class.append(3)

cnf_matrix = confusion_matrix(y_test, results_class)

cnf_matrix

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    plt.figure(figsize = (6,6))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    cm = np.round(cm,2)
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()

cm = plot_confusion_matrix(cnf_matrix, classes = [0,1,2,3],normalize=False)
