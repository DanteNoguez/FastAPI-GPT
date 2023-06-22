PROMPT =  """
Sources: 
{sources}

Question: 
{query}

Answer:
"""

SYSTEM_MESSAGE = """
To answer a question please only use the Sources given, nothing else. Do not make up an answer, simply say 'I don't know' if you are not sure."""