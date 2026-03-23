"""
Delay Cause Classifier — Naive Bayes text classifier.
Classifies delay root cause from task context + blocker description.
Training data: seed task outcomes. Updates with real outcomes.
"""
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import joblib

DELAY_CLASSES = [
    "overload",
    "skill_mismatch",
    "process_failure",
    "external_dependency",
    "unclear_requirements",
]

# Seed training examples — (text, label)
TRAINING_DATA = [
    ("Alice had 3 tasks simultaneously too many tasks concurrent overloaded", "overload"),
    ("too many concurrent tasks workload exceeded capacity overload", "overload"),
    ("member has 3 active tasks pushed over capacity load too high", "overload"),
    ("backend python async database wrong skill frontend engineer mismatch", "skill_mismatch"),
    ("skill mismatch wrong category engineer frontend assigned backend", "skill_mismatch"),
    ("developer struggled unfamiliar technology outside expertise domain", "skill_mismatch"),
    ("requirements changed mid sprint scope added product manager", "process_failure"),
    ("process failure sprint planning poor requirements not locked", "process_failure"),
    ("unclear requirements scope changed definition done shifted", "unclear_requirements"),
    ("waiting for external team third party API dependency blocked", "external_dependency"),
    ("blocked dependency another team upstream service unavailable", "external_dependency"),
    ("requirements unclear vague specification incomplete brief", "unclear_requirements"),
    ("ambiguous requirements specification missing incomplete", "unclear_requirements"),
]


class DelayClassifier:
    def __init__(self):
        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2), min_df=1, max_features=500
        )
        self._model = MultinomialNB(alpha=1.0)
        self._encoder = LabelEncoder()
        self._encoder.fit(DELAY_CLASSES)
        self._n_real_samples = 0
        self._fitted = False
        self._train_seed()

    def _train_seed(self):
        try:
            texts = [t for t, _ in TRAINING_DATA]
            labels = [l for _, l in TRAINING_DATA]
            X = self._vectorizer.fit_transform(texts)
            y = self._encoder.transform(labels)
            self._model.fit(X, y)
            self._fitted = True
        except Exception as e:
            print(f"[DelayClassifier] Seed train warning: {e}")

    def classify(self, task_title: str, category: str,
                 blocker_type: str = "", reason: str = "") -> dict:
        """
        Classify delay cause from task context.
        Returns top predicted class + probability distribution.
        """
        try:
            if not self._fitted:
                return {
                    "cause": "unknown", "confidence": 0.0,
                    "probabilities": {c: 0.2 for c in DELAY_CLASSES}
                }
            text = f"{task_title} {category} {blocker_type} {reason}"
            X = self._vectorizer.transform([text])
            probs = self._model.predict_proba(X)[0]
            classes = self._encoder.inverse_transform(range(len(probs)))
            prob_dict = dict(zip(classes, [round(float(p), 3) for p in probs]))
            best_class = classes[np.argmax(probs)]
            best_prob = float(np.max(probs))
            return {
                "cause": best_class,
                "confidence": round(best_prob, 3),
                "probabilities": prob_dict,
                "model": "NaiveBayes",
                "real_samples_trained": self._n_real_samples,
            }
        except Exception as e:
            print(f"[DelayClassifier] Classify warning: {e}")
            return {"cause": "unknown", "confidence": 0.0, "probabilities": {}}

    def update(self, task_title: str, category: str,
               blocker_type: str, reason: str, true_cause: str) -> None:
        """
        Update model with a confirmed delay cause (from task.complete()).
        Only called when delay_days > 0 and blocker_type is provided.
        """
        try:
            if true_cause not in DELAY_CLASSES:
                return
            text = f"{task_title} {category} {blocker_type} {reason}"
            X = self._vectorizer.transform([text])
            y = self._encoder.transform([true_cause])
            self._model.partial_fit(X, y, classes=self._encoder.transform(DELAY_CLASSES))
            self._n_real_samples += 1
        except Exception as e:
            print(f"[DelayClassifier] Update warning: {e}")


delay_classifier = DelayClassifier()
