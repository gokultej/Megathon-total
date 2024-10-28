from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

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

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True, port=5000)
