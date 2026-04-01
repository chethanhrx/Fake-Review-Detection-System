import re
import math

def detect_review(text):
    """
    Analyzes review text and returns (label, confidence_percent)
    label: 'CG' or 'OR'
    confidence: float 0-100
    """
    score = 0
    reasons = []

    words = text.strip().split()
    word_count = len(words)
    text_lower = text.lower()

    # --- Rule 1: Length check ---
    if word_count < 8:
        score += 30
        reasons.append("Very short review")
    elif word_count > 250:
        score += 10
        reasons.append("Unusually long review")

    # --- Rule 2: Generic CG phrases ---
    cg_phrases = [
        "highly recommend", "great product", "five stars", "excellent quality",
        "must buy", "best purchase", "love this product", "amazing product",
        "works perfectly", "totally worth", "exceeded expectations",
        "10/10 would recommend", "would recommend", "very satisfied",
        "great value for money", "good quality", "fast delivery",
        "as described", "exactly as expected", "no complaints"
    ]
    phrase_hits = sum(1 for p in cg_phrases if p in text_lower)
    if phrase_hits >= 3:
        score += 35
        reasons.append(f"{phrase_hits} generic CG phrases found")
    elif phrase_hits >= 1:
        score += 15
        reasons.append(f"{phrase_hits} generic phrase(s) found")

    # --- Rule 3: Personal pronouns (humans use them) ---
    personal_pronouns = ['i ', "i'", 'my ', 'we ', 'our ', "i've", "i'm", "i'll", 'me ']
    pronoun_count = sum(1 for p in personal_pronouns if p in text_lower)
    if pronoun_count == 0:
        score += 25
        reasons.append("No personal pronouns found")
    elif pronoun_count >= 3:
        score -= 15  # Strongly human-like

    # --- Rule 4: Punctuation & caps abuse ---
    exclamation_count = text.count('!')
    if exclamation_count > 4:
        score += 20
        reasons.append("Excessive exclamation marks")
    if text.isupper():
        score += 20
        reasons.append("All caps text")

    # --- Rule 5: Repetitive sentence structure ---
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if len(sentences) >= 3:
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        if variance < 3:
            score += 20
            reasons.append("Very uniform sentence lengths (CG pattern)")

    # --- Rule 6: Spelling mistakes / informal tone (OR indicator) ---
    informal_words = ["lol", "omg", "tbh", "ngl", "imo", "btw", "haha",
                      "kinda", "gonna", "wanna", "gotta", "sorta"]
    informal_hits = sum(1 for w in informal_words if w in text_lower)
    if informal_hits >= 1:
        score -= 20  # Informal = more human

    # --- Rule 7: Specific details (OR indicator) ---
    specificity_patterns = [
        r'\d+ (days|weeks|months|hours)',  # time references
        r'(delivery|shipping|arrived|package)',
        r'(color|colour|size|fit|material)',
        r'(compared to|better than|worse than)',
        r'(my (husband|wife|son|daughter|friend|mom|dad))',
    ]
    specificity_hits = sum(1 for p in specificity_patterns if re.search(p, text_lower))
    if specificity_hits >= 2:
        score -= 20
        reasons.append("Contains specific personal details")

    # --- Clamp score ---
    score = max(0, min(100, score))

    if score >= 45:
        label = 'CG'
        confidence = round(50 + (score - 45) * 1.0, 1)
        confidence = min(confidence, 98.0)
    else:
        label = 'OR'
        confidence = round(50 + (45 - score) * 1.1, 1)
        confidence = min(confidence, 98.0)

    return label, confidence, reasons
