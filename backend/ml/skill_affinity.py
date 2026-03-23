"""
Skill Affinity Model — cosine similarity between member skills and task category.
Replaces the regex-based task_type_success feature in features.py.
Returns 0.0 (total mismatch) to 1.0 (perfect match).
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Skill vocabulary per category — maps task categories to skill keywords
CATEGORY_SKILLS = {
    "Backend":  "python fastapi postgresql sql sqlalchemy async api rest database backend",
    "Frontend": "react typescript javascript css html ui ux tailwind responsive frontend",
    "DevOps":   "docker kubernetes ci cd github actions deployment cloud infrastructure devops",
    "Testing":  "pytest selenium testing qa automation unit integration e2e test",
    "ML":       "machine learning xgboost sklearn numpy pandas model training inference",
    "Design":   "figma ui ux design prototype wireframe user interface visual",
    "General":  "general management documentation planning coordination",
}

# Known member skill profiles — updated when members are onboarded
MEMBER_PROFILES = {
    "Alice": "python fastapi postgresql sql sqlalchemy async api rest database backend ml xgboost",
    "Bob":   "react typescript javascript css html tailwind ui ux responsive frontend",
    "Priya": "python react devops docker ci cd github actions redis testing backend frontend",
    "Raj":   "testing pytest selenium qa automation documentation unit integration e2e",
}


class SkillAffinityModel:
    def __init__(self):
        self._vectorizer = None
        self._member_vectors = {}
        self._category_vectors = {}
        self._fitted = False
        self._fit()

    def _fit(self):
        try:
            all_docs = (
                list(CATEGORY_SKILLS.values()) +
                list(MEMBER_PROFILES.values())
            )
            self._vectorizer = TfidfVectorizer(
                ngram_range=(1, 1), min_df=1, max_features=200
            )
            self._vectorizer.fit(all_docs)

            for cat, text in CATEGORY_SKILLS.items():
                self._category_vectors[cat] = (
                    self._vectorizer.transform([text])
                )
            for member, skills in MEMBER_PROFILES.items():
                self._member_vectors[member] = (
                    self._vectorizer.transform([skills])
                )
            self._fitted = True
        except Exception as e:
            print(f"[SkillAffinity] Fit warning: {e}")

    def score(self, member: str, task_category: str) -> float:
        """
        Returns affinity score 0.0-1.0.
        1.0 = perfect match (Bob → Frontend)
        0.0 = no match     (Bob → Backend)
        """
        try:
            if not self._fitted:
                return 0.65

            cat = task_category if task_category in self._category_vectors \
                  else "General"
            mem = member if member in self._member_vectors else None

            if mem is None:
                # Unknown member — build vector from name as fallback
                member_vec = self._vectorizer.transform([member.lower()])
            else:
                member_vec = self._member_vectors[mem]

            cat_vec = self._category_vectors[cat]
            sim = float(cosine_similarity(member_vec, cat_vec)[0][0])
            return round(sim, 3)

        except Exception:
            return 0.65

    def update_member(self, member: str, skills: list) -> None:
        """Call when a new member is onboarded or skills are updated."""
        try:
            skills_text = " ".join(s.lower() for s in skills)
            MEMBER_PROFILES[member] = skills_text
            if self._fitted and self._vectorizer:
                self._member_vectors[member] = (
                    self._vectorizer.transform([skills_text])
                )
        except Exception as e:
            print(f"[SkillAffinity] Update warning: {e}")

    def get_all_affinities(self, member: str) -> dict:
        """Returns affinity score for all categories. Used on MemberCard."""
        return {
            cat: self.score(member, cat)
            for cat in CATEGORY_SKILLS
        }


skill_affinity = SkillAffinityModel()
