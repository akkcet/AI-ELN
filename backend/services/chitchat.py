# -----------------------------------------------------
# ✅ Chit-chat detection (Safe, text-only)
# -----------------------------------------------------

CHITCHAT_KEYWORDS = [
    "hi", "hello", "hey", "good morning", "good evening",
    "how are you", "what's up", "whats up", "good afternoon",
    "who are you", "your name", "nice to meet you",
    "how is it going", "how are things",
    "thank you", "thanks", "bye", "goodbye", "good night"
]

def is_chitchat(message: str) -> bool:
    msg = message.lower().strip()
    return any(k in msg for k in CHITCHAT_KEYWORDS)