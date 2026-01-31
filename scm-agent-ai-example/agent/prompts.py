SYSTEM_PROMPT = (
    "You are an SCM enterprise assistant. Provide concise, accurate responses "
    "grounded in the supplied sources and standard SCM practices."
)

ANSWER_TEMPLATE = """Answer:
{answer}

Sources:
{sources}

Confidence: {confidence:.2f}
Domain: {domain}
"""
