import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

class AICodeAnalyzer:
    def __init__(self):
        model_path = "checkpoint-846"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def analyze(self, code):
        try:
            inputs = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = outputs.logits.softmax(dim=-1)
            
            # Get the predicted issues and their confidence scores
            issues = []
            for idx, score in enumerate(predictions[0]):
                if score > 0.5:  # Confidence threshold
                    issues.append({
                        'type': 'ai_analysis',
                        'confidence': float(score),
                        'issue': self.get_issue_description(idx),
                        'suggestion': self.get_suggestion(idx)
                    })
            
            return issues
        except Exception as e:
            print(f"AI Analysis error: {str(e)}")
            return []

    def get_issue_description(self, idx):
        # Map model output indices to issue descriptions
        issues = {
            0: "Potential code optimization opportunity",
            1: "Possible security vulnerability",
            2: "Code readability could be improved",
            3: "Performance bottleneck detected",
            # Add more based on your model's output classes
        }
        return issues.get(idx, "Unknown issue detected")

    def get_suggestion(self, idx):
        # Map model output indices to suggestions
        suggestions = {
            0: "Consider using more efficient data structures or algorithms",
            1: "Review security best practices and input validation",
            2: "Add comments and break down complex logic",
            3: "Use profiling tools to identify slow operations",
            # Add more based on your model's output classes
        }
        return suggestions.get(idx, "Review code for potential improvements") 