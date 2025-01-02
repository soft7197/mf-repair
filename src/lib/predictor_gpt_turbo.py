import openai
import json

openai.api_key =""

def get_response(prompt, n):
  response = openai.chat.completions.create(    
      messages=[{"role": "user", "content": prompt}],
      model="gpt-4o",
      n=n,
      temperature=1)
  responses = []
  for choice in response.choices:
      if choice.message:
          responses.append(choice.message.content)
  return responses
