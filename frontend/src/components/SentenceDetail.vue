<template>
  <div class="sentence-detail">
    <h1>句子详情</h1>
    <p>{{ sentenceContent }}</p>
    <div v-for="wordId in annotatedWordIds" :key="wordId" class="word">
      <span>{{ getWordContent(wordId) }}</span>
      <button :class="getSentimentClass(wordId)" @click="annotateWord(wordId, 'positive')">积极</button>
      <button :class="getSentimentClass(wordId)" @click="annotateWord(wordId, 'neutral')">中性</button>
      <button :class="getSentimentClass(wordId)" @click="annotateWord(wordId, 'negative')">消极</button>
     </div>
  </div>
</template>

<script>
export default {
  props: {
    sentenceId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      sentenceContent: '',
      annotatedWordIds: [],
      words: {} // 存储单词信息
    };
  },
  mounted() {
    this.fetchSentenceDetail();
  },
  methods: {

    fetchSentenceDetail() {
      const sentenceId = this.$route.params.id;
      console.log(sentenceId);
      const apiUrl = `/api/annotated_sentences/${sentenceId}/`;
      fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
          this.sentenceContent = data.content;
          this.annotatedWordIds = data.annotated_words;
          this.annotatedWordIds.forEach(wordId => this.fetchWordDetail(wordId));
        })
        .catch(error => {
          console.error('获取句子详情失败:', error);
        });
    },
    fetchWordDetail(wordId) {
        const apiUrl = `/api/annotated_words/${wordId}/`;
        fetch(apiUrl)
            .then(response => response.json())
            .then(wordData => {
            this.words[wordId] = wordData; // 直接更新对象属性
            })
            .catch(error => {
            console.error('获取单词详情失败:', error);
            });
        },
    getWordContent(wordId) {
      return this.words[wordId]?.word_content || '';
    },
    getSentimentClass(wordId) {
      const sentiment = this.words[wordId]?.sentiment;
      if (sentiment === 'positive') {
        return 'positive-button';
      } else if (sentiment === 'neutral') {
        return 'neutral-button';
      } else if (sentiment === 'negative') {
        return 'negative-button';
      }
      return '';
    },
    annotateWord(wordId, sentiment) {
      const apiUrl = `/api/annotated_words/${wordId}/`;
      const data = {
        id: wordId,
        word_content: this.getWordContent(wordId),
        sentiment: sentiment
      };
      fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(updatedWordData => {
        this.words[wordId] = updatedWordData;
      })
      .catch(error => {
        console.error('标注单词失败:', error);
      });
    },
  }
};
</script>

<style>
.word {
  margin: 5px;
}

button {
  margin-left: 5px;
}
</style>


<style>
.positive-button {
  background-color: blue;
  color: white;
}

.neutral-button {
  background-color: grey;
  color: white;
}

.negative-button {
  background-color: red;
  color: white;
}
</style>