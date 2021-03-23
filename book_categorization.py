#-*- coding:utf-8 -*-
import json
from konlpy.tag import Okt
from keras.preprocessing.text import tokenizer_from_json
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import text_to_word_sequence
from tensorflow.compat.v2.keras.models import model_from_json
import math

class BookCategorization:

    def __init__(self):
        category_list = ['경제/경영', '사회/정치', '시/소설', '어린이', '역사', '인문', '과학']
        categorys = {}
        for i, category in enumerate(category_list):
            categorys[i] = category
        self.categorys = categorys
    
    def get_okt(self):
        text = """맨손에서 만들어낸 종잣돈으로 돈 버는 방법을 알려준다. 부모에게 받은 유산은 커녕, 30대 후반까지 낡은 자동차에 그날 판매할 과일을 싣고 다니던 어느 가난한 이민 가장이 이룬 진짜 부에 대한 모든 방법이 담겼다. 종잣돈 천만 원을 만들고 그 돈을 1억 원, 10억 원, 100억 원, 수천억 원이 될 때까지 돈을 관리하며 터득한 ‘돈’이 가진 속성을 정리한 안내서다. ‘진짜 부자’가 된 실제 인물이 말해주는 ‘진짜 돈’만들기에 대한 책이다.
        저자는 돈의 특성을 매우 특이하게 정의했는데 바로, 인격체라고 지칭한 것이다. 돈을 너무 사랑해서 집 안에만 가둬 놓으면 기회만 있으면 나가버리려고 할 것이고 다른 돈에게 주인이 구두쇠니 오지 마라 할 것이다. 자신을 존중해주지 않는 사람을 부자가 되게 하는 데 협조도 하지 않는다. 가치 있는 곳과 좋은 일에 쓰인 돈은 그 대우에 감동해 다시 다른 돈을 데리고 주인을 찾을 것이고 술집이나 도박에 자신을 사용하면 비참한 마음에 등을 돌리는 게 돈이다.
        옛말에 ‘고기를 주기보다 고기를 낚는 법을 주라’ 했다. 우리는 모두 각기 다른 환경에 놓여 있다. 지적 수준이 다르며 경제적 상황 역시 다르다. 그러니 누군가에게 이득이 된 방법이라고 나에게 이득이 될 수는 없다. 우리는 이 책 『돈의 속성』을 통해 돈을 만들고 지키고 기르는 한 명의 농부가 되는 방법을 배워야 할 것이다."""
        okt = Okt()
        okt.pos(text, norm=True ,stem=True)
        
        return okt
        
    def get_tokenizer_from_json(self, token_file_dir):
        # tokenizer 가져오기
        with open(token_file_dir, 'r') as f:
            json_data = json.load(f)

        # t에 tokenizer 할당.
        tokenizer = tokenizer_from_json(json_data)
        return tokenizer

    def preprocess_text(self, text, okt):
        #텍스트 전처리하기
        word_s = okt.pos(text, norm=True, stem=True)

         # 전처리된 텍스트가 refined_text에 담김
        refined_text= []
        for n, h in word_s:
            if h in ['Noun', 'Verb ', 'Adjective'] and len(n) != 1: 
                refined_text.append(n)

        refined_text = ' '.join(refined_text)
        
        return refined_text

    def get_sequences(self, refined_text, tokenizer):
        #전처리된 텍스트 정수 변환하기.
        corpus= text_to_word_sequence(refined_text)
        sequences = tokenizer.texts_to_sequences([corpus])

        return sequences

    @staticmethod
    def get_padded_sequences(sequences):
        # 300개로 패딩
        padded_sequences = pad_sequences(sequences, maxlen=300, padding='post')

        return padded_sequences

    def get_pretrained_model_from_json(self, model_file_dir, weights_file_dir):
        #모델 로드하기
        with open(model_file_dir, 'r') as f:
            pretrained_model_json = f.read() 
        pretrained_model = model_from_json(pretrained_model_json)
        pretrained_model.load_weights(weights_file_dir)
        pretrained_model.compile(optimizer = 'adam',
                    loss = 'sparse_categorical_crossentropy',
                    metrics = ['accuracy'])
        
        return pretrained_model
    
    def predict(self, text, model, tokenizer, okt):
        refined_text = self.preprocess_text(text, okt)
        sequences = self.get_sequences(refined_text, tokenizer)
        padded_sequences = self.get_padded_sequences(sequences)

        # 로드된 모델로 텍스트 분류하기
        predict = model.predict(padded_sequences)

        accuracy = round(max(predict[0])*1000)/10
        category = self.categorys[predict.argmax()]
        return [category, accuracy]

if __name__ == '__main__':
    # test
    text = """코로나19와 황우석 사태 등을 취재하며 한국 사회에 과학기술이 미치는 영향력에 대해 성찰해온 과학 전문 기자 강양구가 이번에는 과학 고전을 읽는다. 
    문학과지성사에서 출간된 『강양구의 강한 과학-과학 고전 읽기』가 그것이다. 이 책의 제목 ‘강한 과학’이 나타내듯 과학기술은 우리 삶을 좌지우지할 정도로 강하다. 
    최근 전 세계적으로 유행 중인 코로나19바이러스의 정체를 밝히고 막아내는 데도 과학기술의 힘이 중요하다. 
    사회적 거리 두기를 하는 시민들을 비대면 경제로 연결하는 것도, 기본소득처럼 사회안전망을 둘러싼 논의를 이끄는 것도 과학기술이다. 
    이렇게 과학기술이 사회 변화에 대응하거나 심지어는 변화를 주도하며 둘 사이가 긴밀해질수록, “과학기술이 할 수 있는 것과 할 수 없는 것을 섬세하게 구분하는 지혜가 필요하다”고 저자 강양구는 말한다. 
    흔히 과학기술은 객관적이고, 과학자는 이성적인 판단력으로 “모든 세상사를 놓고서 올바른 입장을 가진 사람”이라 여겨진다. 
    하지만 실제로 과학기술은 사회적 조건에서 자유롭지 못하다. 
    구글에 일자리를 검색할 때, 사회적 편견을 학습한 검색 엔진이 여성에게 남성보다 더 낮은 급여를 주는 일자리 광고를 보여주는 것은 그 단적인 사례다. 
    이 책은 이렇게 갈수록 힘을 더해가는 과학기술을 바로 이해하고, “과학을 맹신하지 않으면서 적절히 관심을 두고 감시”해야 모든 사람을 위한 과학기술을 만들어나갈 수 있다고 이야기한다. 
    그러기 위해 저자가 이 책에서 제안하는 것은 오래 읽혀온 과학 고전을 새로 읽으며, 과학기술과 사회가 어떤 관계를 맺어왔는지를 되짚어보는 것이다. 
    23권의 과학 고전을 선별해 읽은 이 책은 『코스모스』 『이기적 유전자』 등의 과학책 베스트셀러가 과학기술과 사회를 어떻게 연결하고 있는지를 검토하는 한편, 과학기술 시대의 사회적ㆍ윤리적 쟁점들을 다룬 과학책을 조명함으로써 현재적 관점에서 읽어나간다."""
    token_file_dir = './model/token'
    model_file_dir = './model/CNN_model.json'
    weights_file_dir = './model/CNN_model.h5'

    BC = BookCategorization()
    tokenizer = BC.get_tokenizer_from_json(token_file_dir)
    pretrained_model = BC.get_pretrained_model_from_json(model_file_dir, weights_file_dir)
    okt = BC.get_okt()
    category = BC.predict(text, model=pretrained_model, tokenizer=tokenizer, okt=okt)

    print(category)
