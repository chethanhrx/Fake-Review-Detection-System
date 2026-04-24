import re
import math
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# ===========================================================================
# DistilBERT ML Model Setup (Hybrid Integration)
# ===========================================================================
try:
    from transformers import pipeline
    # Load DistilBERT model. For production, replace the generic model with a 
    # fine-tuned fake-review detector (e.g. 'mrm8488/distilbert-base-uncased-finetuned-sms-spam-detection')
    distilbert_model = pipeline("text-classification", model="distilbert-base-uncased", truncation=True, max_length=512)
    HAS_DISTILBERT = True
    logger.info("DistilBERT model loaded successfully.")
except ImportError:
    HAS_DISTILBERT = False
    logger.info("Transformers not installed. Running in standalone Rules-based mode.")
except Exception as e:
    HAS_DISTILBERT = False
    logger.warning(f"Failed to load DistilBERT model: {e}")

# ---------------------------------------------------------------------------
# Handcrafted feature-based fake review detector
# ---------------------------------------------------------------------------
# Architecture:
#   1. Extract 20+ linguistic, structural, and semantic features
#   2. Compute weighted CG score and OR score independently
#   3. Apply a confidence dampening curve for ambiguous / short reviews
#   4. Return (label, confidence%, reasons[])
# ---------------------------------------------------------------------------


# ─── Feature weights (tuned empirically) ────────────────────────────────────
W = {
    # CG weights
    "very_short":          28,   # < 8 words
    "short":               14,   # 8–15 words
    "too_long":             6,   # > 300 words
    "cg_phrases_heavy":    42,   # ≥ 4 marketing phrases
    "cg_phrases_medium":   26,   # 2–3 marketing phrases
    "cg_phrases_light":    10,   # 1 marketing phrase
    "superlatives_heavy":  24,   # ≥ 4 superlatives
    "superlatives_medium": 12,   # 2–3 superlatives
    "no_pronouns":         24,   # zero first-person pronouns
    "exclaim_heavy":       18,   # > 5 !
    "exclaim_medium":       8,   # 3–5 !
    "all_caps_words":      14,   # many fully-uppercase words
    "all_caps_text":       18,   # entire text is uppercase
    "uniform_sentences":   22,   # variance < 2
    "somewhat_uniform":    10,   # variance < 5
    "word_repeat_heavy":   20,   # meaningful word repeated ≥ 5×
    "word_repeat_light":    8,   # meaningful word repeated 3–4× in short text
    "low_vocab_ratio":     12,   # unique_ratio < 0.35
    "repetitive_starters": 16,   # non-trivial starter repeated ≥ 3×
    "adj_density":         14,   # adjective ratio > 0.15
    "template_heavy":      22,   # ≥ 3 template patterns
    "template_medium":     13,   # 2 template patterns
    "template_light":       6,   # 1 template pattern
    "purely_positive":     10,   # no negatives in long text
    "low_ttr":              8,   # low type-token ratio

    # OR weights
    "pronouns_heavy":      22,   # ≥ 5 pronoun occurrences
    "pronouns_medium":     14,   # 3–4 pronoun occurrences
    "pronouns_light":       6,   # 1–2 pronoun occurrences
    "informal_heavy":      14,   # ≥ 2 informal words
    "informal_light":       7,   # 1 informal word
    "specificity_very":    26,   # ≥ 4 specific-detail patterns
    "specificity_high":    18,   # 2–3 specific-detail patterns
    "specificity_low":      8,   # 1 specific-detail pattern
    "has_negatives":       10,   # balanced review
    "has_negatives_multi": 14,   # clearly balanced
    "high_ttr":            10,   # high vocabulary richness
    "narrative_strong":    22,   # ≥ 3 narrative signals
    "narrative_medium":    14,   # 2 narrative signals
    "narrative_light":      7,   # 1 narrative signal
    "usage_context_heavy": 18,   # ≥ 4 real-world context signals
    "usage_context_medium":12,   # 2–3 real-world context signals
    "usage_context_light":  5,   # 1 real-world context signal
    "has_emoji":            5,   # emojis suggest real humans
    "typos_or_quirks":      8,   # minor typos / spacing errors = human
    "sentence_variation":   6,   # varied sentence lengths = human
}

# Words that are naturally repeated when describing a product
NATURAL_REPEATS = {
    'soft', 'hard', 'good', 'nice', 'bad', 'just', 'very', 'really',
    'quite', 'well', 'like', 'also', 'even', 'back', 'size', 'colour',
    'color', 'feel', 'look', 'work', 'used', 'time', 'came', 'come',
    'this', 'that', 'with', 'have', 'been', 'from', 'they', 'some',
    'more', 'than', 'when', 'here', 'there', 'were', 'your', 'their',
    'best', 'great', 'love', 'wear', 'fits', 'look', 'feels', 'looks',
}

# Common sentence-starting words — not meaningful for bot detection
TRIVIAL_STARTERS = {
    'the', 'a', 'an', 'it', 'i', 'this', 'that', 'he', 'she', 'they',
    'we', 'my', 'its', 'and', 'but', 'so', 'also', 'there', 'if', 'in',
    'on', 'at', 'for', 'to', 'with', 'has', 'have', 'is', 'was', 'are',
    'were', 'you', 'your', 'what', 'when', 'where', 'then', 'these',
    'very', 'quite', 'really', 'just', 'only', 'not',
}

EMOJI_RE = re.compile(
    "["
    u"\U0001F600-\U0001F64F"
    u"\U0001F300-\U0001F5FF"
    u"\U0001F680-\U0001F9FF"
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE
)


def _has_typos_or_quirks(text):
    """Detect spacing errors or minor typos common in human-typed reviews."""
    # e.g. ".very" (missing space after period), "allday", double spaces, etc.
    if re.search(r'[.!?,][a-zA-Z]', text):     # no space after punctuation
        return True
    if re.search(r'[a-zA-Z]{2,}\s{2,}[a-zA-Z]', text):  # double spaces
        return True
    if re.search(r'\b[a-z][A-Z]', text):        # mid-word capitalisation
        return True
    return False


def detect_review(text: str):
    """
    Returns (label, confidence_percent, reasons).
      label      : 'CG' (computer-generated) or 'OR' (original/human)
      confidence : float 0–100
      reasons    : list of human-readable detection signal strings
    """
    cg_score = 0
    or_score = 0
    reasons = []

    # ── Preprocessing ────────────────────────────────────────────────────────
    text_clean = EMOJI_RE.sub(' ', text)           # strip emojis for NLP (keep for signal)
    words = text_clean.strip().split()
    word_count = len(words)
    text_lower = text_clean.lower()
    sentences = re.split(r'[.!?]+', text_clean)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    has_emoji = bool(EMOJI_RE.search(text))
    has_quirks = _has_typos_or_quirks(text)

    # ── DistilBERT Analysis (Hybrid Upgrade) ─────────────────────────────────
    if HAS_DISTILBERT:
        try:
            ml_result = distilbert_model(text[:512])[0]
            ml_label = ml_result['label'].upper()
            ml_conf = ml_result['score']
            
            # Map standard spam/fake labels to CG points
            if ml_label in ['FAKE', 'SPAM', 'CG', 'LABEL_1']:
                boost = int(30 * ml_conf)
                cg_score += boost
                reasons.append(f"DistilBERT ML model detected CG pattern (+{boost} score)")
            # Map authentic labels to OR points
            elif ml_label in ['REAL', 'HUMAN', 'OR', 'HAM', 'LABEL_0']:
                boost = int(30 * ml_conf)
                or_score += boost
                reasons.append(f"DistilBERT ML model detected Human pattern (+{boost} score)")
        except Exception:
            pass

    # ── Personal pronouns (by occurrence count, not distinct types) ──────────
    pronoun_patterns = [
        r'\bi\b', r"\bi'", r'\bmy\b', r'\bwe\b', r'\bour\b',
        r"\bi've\b", r"\bi'm\b", r"\bi'll\b", r'\bme\b',
        r'\bmine\b', r'\bmyself\b', r'\bus\b',
    ]
    pronoun_occurrences = sum(len(re.findall(p, text_lower)) for p in pronoun_patterns)

    # ── Negative / hedging words ─────────────────────────────────────────────
    negative_patterns = [
        r'\b(but|however|although|downside|drawback|con|negative|issue|problem|'
        r'flaw|disappoint|wish|could be|could have|lacking|missing|complaint)\b'
    ]
    negative_hits = len(re.findall(negative_patterns[0], text_lower))

    # =====================================================================
    # CG SIGNALS
    # =====================================================================

    # CG-1 Length
    if word_count < 8:
        cg_score += W["very_short"]
        reasons.append("Very short review (common fake pattern)")
    elif word_count < 15:
        cg_score += W["short"]
        reasons.append("Short review — low detail level")
    elif word_count > 300:
        cg_score += W["too_long"]
        reasons.append("Unusually long review")

    # CG-2 Generic marketing phrases
    cg_phrases = [
        "highly recommend", "great product", "five stars", "excellent quality",
        "must buy", "best purchase", "love this product", "amazing product",
        "works perfectly", "totally worth", "exceeded expectations",
        "10/10 would recommend", "would recommend", "very satisfied",
        "great value for money", "good quality", "fast delivery",
        "as described", "exactly as expected", "no complaints",
        "game changer", "life changing", "game-changer",
        "don't hesitate", "buy it now", "look no further",
        "top notch", "top-notch", "can't say enough",
        "hands down", "bar none", "second to none",
        "customer service", "well worth", "every penny",
    ]
    phrase_hits = sum(1 for p in cg_phrases if p in text_lower)
    if phrase_hits >= 4:
        cg_score += W["cg_phrases_heavy"]
        reasons.append(f"Heavy use of generic marketing phrases ({phrase_hits} found)")
    elif phrase_hits >= 2:
        cg_score += W["cg_phrases_medium"]
        reasons.append(f"Multiple generic marketing phrases ({phrase_hits} found)")
    elif phrase_hits >= 1:
        cg_score += W["cg_phrases_light"]
        reasons.append(f"Contains a generic marketing phrase")

    # CG-3 Superlatives / hype words
    superlative_re = re.compile(
        r'\b(best|worst|greatest|amazing|incredible|awesome|fantastic|perfect|'
        r'stunning|phenomenal|outstanding|exceptional|unbelievable|mind.blowing|'
        r'flawless|spectacular|revolutionary|ultimate|supreme)\b'
    )
    superlative_hits = len(superlative_re.findall(text_lower))
    if superlative_hits >= 4:
        cg_score += W["superlatives_heavy"]
        reasons.append(f"Excessive hype/superlative words ({superlative_hits} found)")
    elif superlative_hits >= 2:
        cg_score += W["superlatives_medium"]
        reasons.append(f"Multiple superlatives ({superlative_hits} found)")

    # CG-4 No pronouns
    if pronoun_occurrences == 0:
        cg_score += W["no_pronouns"]
        reasons.append("No first-person pronouns — impersonal tone (bot pattern)")

    # CG-5 Exclamation marks & all caps
    exclaim_count = text.count('!')
    if exclaim_count > 5:
        cg_score += W["exclaim_heavy"]
        reasons.append("Excessive exclamation marks (over-enthusiasm)")
    elif exclaim_count > 2:
        cg_score += W["exclaim_medium"]
        reasons.append("Multiple exclamation marks")

    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    if len(caps_words) > 3:
        cg_score += W["all_caps_words"]
        reasons.append("Excessive ALL-CAPS words")
    if text_clean.isupper():
        cg_score += W["all_caps_text"]
        reasons.append("Entire review in ALL CAPS")

    # CG-6 Uniform sentence lengths
    if len(sentences) >= 3:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        if variance < 2.0:
            cg_score += W["uniform_sentences"]
            reasons.append("Very uniform sentence lengths (AI/bot pattern)")
        elif variance < 5.0:
            cg_score += W["somewhat_uniform"]
            reasons.append("Somewhat uniform sentence structure")
        else:
            or_score += W["sentence_variation"]

    # CG-7 Repetitive word usage (excluding naturally repeated words)
    word_freq = Counter(
        w.lower().strip('.,!?;:"\'()') for w in words
        if len(w) > 3 and w.lower().strip('.,!?;:"\'()') not in NATURAL_REPEATS
    )
    if word_freq:
        max_repeat = max(word_freq.values())
        top_word = word_freq.most_common(1)[0][0]
        unique_ratio = len(word_freq) / max(len(words), 1)
        if max_repeat >= 5:
            cg_score += W["word_repeat_heavy"]
            reasons.append(f"Repetitive word usage ('{top_word}' repeated {max_repeat}×)")
        elif max_repeat >= 3 and word_count < 60:
            cg_score += W["word_repeat_light"]
            reasons.append(f"Repeated word in short review ('{top_word}' {max_repeat}×)")
        if unique_ratio < 0.35 and word_count > 15:
            cg_score += W["low_vocab_ratio"]
            reasons.append("Low vocabulary diversity")

    # CG-8 Repetitive sentence starters (non-trivial words only)
    if len(sentences) >= 3:
        starters = [s.split()[0].lower() for s in sentences if s.split()]
        meaningful = [s for s in starters if s not in TRIVIAL_STARTERS]
        freq = Counter(meaningful)
        if freq and max(freq.values()) >= 3 and len(meaningful) >= 4:
            top = freq.most_common(1)[0]
            cg_score += W["repetitive_starters"]
            reasons.append(f"Repetitive sentence starts ('{top[0]}' used {top[1]}×)")

    # CG-9 High adjective density
    adj_re = re.compile(
        r'\b(great|good|nice|fine|lovely|beautiful|wonderful|excellent|'
        r'brilliant|superb|remarkable|magnificent|delightful|pleasant)\b'
    )
    adj_hits = len(adj_re.findall(text_lower))
    if word_count > 10 and adj_hits / word_count > 0.15:
        cg_score += W["adj_density"]
        reasons.append("High adjective density (over-descriptive)")

    # CG-10 Template-like structure (tightened to avoid false positives)
    template_patterns = [
        r'i (recently|just) (bought|purchased|ordered)',
        r'i (am|was) (very |extremely |really )?(impressed|pleased|satisfied)',
        r'(overall|in summary|in conclusion),?\s+i (would|highly)',
        r'(pros|cons)[:\-\s]',
        r'(firstly|secondly|thirdly),?\s',
        r'i (received|got) this (product|item)',
    ]
    template_hits = sum(1 for p in template_patterns if re.search(p, text_lower))
    if template_hits >= 3:
        cg_score += W["template_heavy"]
        reasons.append(f"Template-like review structure ({template_hits} patterns)")
    elif template_hits >= 2:
        cg_score += W["template_medium"]
        reasons.append(f"Structured template language ({template_hits} patterns)")
    elif template_hits >= 1:
        cg_score += W["template_light"]

    # CG-11 Purely positive (no negatives in a long review)
    if word_count > 25 and negative_hits == 0:
        cg_score += W["purely_positive"]
        reasons.append("Entirely positive — no reservations mentioned")

    # CG-12 Low type-token ratio
    if word_count > 15:
        unique_words = len(set(
            w.lower().strip('.,!?;:"\'()') for w in words if len(w) > 2
        ))
        ttr = unique_words / max(len([w for w in words if len(w) > 2]), 1)
        if ttr < 0.4:
            cg_score += W["low_ttr"]
            reasons.append("Limited vocabulary range")
    else:
        ttr = 1.0  # too short to judge

    # =====================================================================
    # OR SIGNALS
    # =====================================================================

    # OR-1 Personal pronouns (actual occurrence count)
    if pronoun_occurrences >= 5:
        or_score += W["pronouns_heavy"]
        reasons.append("Strong first-person voice (frequent pronoun use)")
    elif pronoun_occurrences >= 3:
        or_score += W["pronouns_medium"]
        reasons.append("Personal voice (multiple pronoun uses)")
    elif pronoun_occurrences >= 1:
        or_score += W["pronouns_light"]

    # OR-2 Informal / conversational tone
    # Only TRUE typing shorthands — things bots virtually never generate
    # but real humans commonly type on mobile keyboards
    informal_words = [
        "lol", "omg", "tbh", "ngl", "imo", "btw", "haha",
        "kinda", "gonna", "wanna", "gotta", "sorta",
        "yknow", "dunno", "heck", "rip",
        # Mobile / typing shorthands (phone buyers)
        "thank u", "thx", "thanku", "thnx",
        "gr8", "luv", "gud", "plz", "pls",
        "u r", "cant wait", "omfg", "wtf", "lmao",
    ]
    informal_hits = sum(
        1 for w in informal_words
        if re.search(r'\b' + re.escape(w) + r'\b', text_lower)
    )
    if informal_hits >= 2:
        or_score += W["informal_heavy"]
        reasons.append("Conversational / informal tone")
    elif informal_hits >= 1:
        or_score += W["informal_light"]
        reasons.append("Informal language detected")

    # OR-3 Specific personal details
    # Note: patterns are context-aware to avoid matching adjectives
    # (e.g. "light weight" as an adjective vs "weight: 200g" as a spec)
    specificity_patterns = [
        r'\d+ (days|weeks|months|hours|years|minutes)',
        r'(delivery|shipping|arrived|package|tracking)',
        # "weight" only as a measurement context, not as an adjective
        r'(color|colour|size|fit|material|texture|thickness)',
        r'(weight (is|was|of)|weighs|net weight|product weight)',
        r'(compared to|better than|worse than|unlike)',
        r'(my |for my )(mother|father|husband|wife|son|daughter|friend|'
        r'mom|dad|kid|baby|dog|cat|sister|brother|spouse|partner)',
        r'(bought this (for|as|to)|gift for|ordered for|took it for)',
        r'(returned|refund|exchange|warranty)',
        r'(after \d+|for over \d+|in the (morning|afternoon|evening))',
        r'(plastic bag|came in a|packaging was|came inside)',
        r'(earlier using|previously using|used to use|switched from)',
        r'(size \d+|\d+ (cm|mm|inch|kg|lb))',
    ]
    specificity_hits = sum(1 for p in specificity_patterns if re.search(p, text_lower))
    if specificity_hits >= 4:
        or_score += W["specificity_very"]
        reasons.append("Highly specific personal experience details")
    elif specificity_hits >= 2:
        or_score += W["specificity_high"]
        reasons.append("Rich specific personal details")
    elif specificity_hits >= 1:
        or_score += W["specificity_low"]
        reasons.append("Contains specific personal details")

    # OR-4 Balanced / critical content
    if negative_hits >= 2:
        or_score += W["has_negatives_multi"]
        reasons.append("Balanced review with honest critique")
    elif negative_hits >= 1:
        or_score += W["has_negatives"]
        reasons.append("Includes some criticism (honest tone)")

    # OR-5 Vocabulary richness
    if word_count > 15:
        if ttr > 0.7:
            or_score += W["high_ttr"]
            reasons.append("Rich vocabulary diversity")

    # OR-6 Narrative / storytelling elements
    narrative_patterns = [
        r'(when i|after i|before i|while i|since i)',
        r'(i decided|i chose|i picked|i ended up)',
        r'(at first|initially|first impression)',
        r'(the (first|second|other|next) time)',
        r'(surprisingly|unexpectedly|to my surprise)',
        r'(she was|he was|they were) (earlier|previously|before)',
        r'(took it for|bought it for|gifted to|ordered for) (my|her|him)',
        r'(finally (i|we) (ordered|bought|purchased|got))',
        r'(when (i|we) opened|upon opening|when it arrived)',
        r'(since (i|we)|ever since (i|buying|getting))',
    ]
    narrative_hits = sum(1 for p in narrative_patterns if re.search(p, text_lower))
    if narrative_hits >= 3:
        or_score += W["narrative_strong"]
        reasons.append("Strong personal narrative / storytelling style")
    elif narrative_hits >= 2:
        or_score += W["narrative_medium"]
        reasons.append("Personal narrative style")
    elif narrative_hits >= 1:
        or_score += W["narrative_light"]
        reasons.append("Contains narrative elements")

    # OR-7 Real-world usage context
    context_patterns = [
        r'(during (winters?|summers?|rainy|monsoon|season))',
        r'(while (walking|working|cooking|doing|performing|using|wearing|running))',
        r'(throughout the day|all day|day long|daily use)',
        r'(dry floor|wet floor|slippery|non.?slip)',
        r'(sole|heel|insole|cushion|arch|strap|buckle)',
        r'(feet|foot|ankle|toe|knee|back|shoulder|leg)',
        r'(house ?hold|domestic|kitchen|outdoor|indoor)',
        r'(lower side|upper side|top layer|bottom layer)',
        r'(activities|chores|errands|tasks|routine)',
        r'(pain|ache|discomfort|relief|support)',
    ]
    context_hits = sum(1 for p in context_patterns if re.search(p, text_lower))
    if context_hits >= 4:
        or_score += W["usage_context_heavy"]
        reasons.append("Detailed real-world usage context (strong human signal)")
    elif context_hits >= 2:
        or_score += W["usage_context_medium"]
        reasons.append("Specific usage context described")
    elif context_hits >= 1:
        or_score += W["usage_context_light"]

    # OR-8 Emoji presence (humans type emojis, bots rarely do)
    if has_emoji:
        or_score += W["has_emoji"]
        reasons.append("Contains emoji (human writing signal)")

    # OR-9 Natural typing quirks (spacing/punctuation errors = human)
    if has_quirks:
        or_score += W["typos_or_quirks"]
        reasons.append("Natural typing quirks detected (human writing signal)")

    # =====================================================================
    # FINAL CLASSIFICATION
    # =====================================================================
    net = cg_score - or_score
    total_evidence = cg_score + or_score

    # Determine label
    label = 'CG' if net > 0 else 'OR'

    # ── Confidence curve ────────────────────────────────────────────────────
    raw_conf = 50.0 + (net if net > 0 else -net)

    # ── Short-review override ────────────────────────────────────────────────
    # Bots NEVER produce typing shorthands (gr8, thx, thank u, luv…).
    # Emoji alone is weaker (bots can add them), but combined with no CG
    # marketing phrases it strongly suggests a real human typed this.
    # Condition: short review + CG verdict + human shorthand or emoji + NO cg phrases
    if word_count < 15 and label == 'CG' and (has_emoji or informal_hits > 0) and phrase_hits == 0:
        label = 'OR'
        raw_conf = 50.0 + min(informal_hits * 8 + (5 if has_emoji else 0), 20)
        reasons.append("Emoji / shorthand typing overrides CG flag (human writing signal)")

    # ── Confidence dampening ─────────────────────────────────────────────────
    # Dampen confidence when:
    #  a) Total evidence is very low (not enough signals either way)
    #  b) Review is very short — inherently ambiguous
    if total_evidence < 15:
        raw_conf = min(raw_conf, 57.0)
        if "Insufficient signals" not in " ".join(reasons):
            reasons.append("Low signal count — confidence capped")
    elif total_evidence < 30:
        raw_conf = min(raw_conf, 72.0)

    if word_count < 15 and abs(net) < 20 and label == 'CG':
        raw_conf = min(raw_conf, 65.0)
        if not any("short" in r.lower() or "ambiguous" in r.lower() for r in reasons):
            reasons.append("Short review — inherently harder to classify")

    confidence = round(min(raw_conf, 98.0), 1)

    return label, confidence, reasons
