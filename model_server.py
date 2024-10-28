from flask import Flask, request, jsonify
from transformers import pipeline
from keybert import KeyBERT
from emotion_detector import detect_emotion
from flask import Flask, jsonify

from pymongo import MongoClient
import matplotlib.pyplot as plt

# Initialize Flask app
app = Flask(__name__)

# Load sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Initialize the keyword extraction model
kw_model = KeyBERT()

def detect_emotion_with_keywords(text):
    # Use the imported detect_emotion function
    emotion_output = detect_emotion(text)
    
    # Extract keywords
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')
    keywords = [kw[0] for kw in keywords]  # Extract just the words
    
    # Update the emotion output with keywords
    emotion_output["keywords"] = keywords
    return emotion_output

@app.route('/analyze', methods=['POST'])
def analyze_text():
    # Get the input text
    data = request.json
    text = data.get("text", "")

    # Detect emotion with keywords
    emotion_output = detect_emotion_with_keywords(text)

    # Process with the sentiment analysis model
    sentiment_output = sentiment_pipeline(text)

    # Return combined output
    return jsonify({
        "emotion": emotion_output,
        "sentiment": sentiment_output[0]  # Assuming it returns a list of predictions
    })

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['analysisDB']
collection = db['analysisResults']

@app.route('/getGraphs', methods=['GET'])
def get_graphs():
    try:
        data = list(collection.find({}))
        if not data:
            return jsonify({"error": "No data found in the database."}), 404

        # Example analysis: Count sentiment occurrences
        sentiment_counts = {}
        for entry in data:
            sentiment = entry.get('sentls')
            if sentiment:
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Example graph generation
        plt.figure(figsize=(10, 6))
        plt.bar(sentiment_counts.keys(), sentiment_counts.values(), color='blue')
        plt.title('Sentiment Analysis')
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        graph_path = 'static/sentiment_analysis.png'
        plt.savefig(graph_path)
        plt.close()

        return jsonify({"message": "Graphs generated successfully.", "graphPath": graph_path})
    except Exception as e:
        print("Error generating graphs:", e)
        return jsonify({"error": "Error generating graphs."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
