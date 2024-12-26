import openai



def get_response(prompt, n):
  response = openai.chat.completions.create(    
      messages=[{"role": "user", "content": prompt}],
      model="gpt-4o",
      n=n,
      temperature=0.7)
  responses = []
  for choice in response.choices:
      if choice.message:
          responses.append(choice.message.content)
  return responses
