# -*- coding: utf-8 -*-
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional

class ColumnMatcher:
    def __init__(self, threshold=0.6):
        self.threshold = threshold
    
    def find_similar_columns(self, col1_list, col2_list):
        matches = {}
        for col1 in col1_list:
            best_match = None
            best_score = 0
            for col2 in col2_list:
                score = SequenceMatcher(None, col1.lower(), col2.lower()).ratio()
                if score > best_score and score >= self.threshold:
                    best_score = score
                    best_match = col2
            if best_match:
                matches[col1] = (best_match, best_score)
        return matches
    
    def suggest_standard_name(self, column_names):
        return column_names[0] if column_names else None
