import os, dotenv
from groq import Groq
try:
    dotenv.load_dotenv('.env')
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    print("Sending ping to Groq...")
    res = client.chat.completions.create(
        model=os.getenv('GROQ_MODEL') or 'llama3-8b-8192',
        messages=[{"role": "user", "content": "ping"}],
        timeout=10
    )
    print("SUCCESS:", res.choices[0].message.content)
except Exception as e:
    print("GROQ ERROR:", str(e))
