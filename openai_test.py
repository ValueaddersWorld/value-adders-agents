import os

import openai

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY not found in environment variables.")
else:
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello, OpenAI!"}]
        )
        print("API key works! Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("Error communicating with OpenAI API:", e)
