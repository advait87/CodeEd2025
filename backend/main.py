from google import genai
from google.genai import types

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyCS7wULK5N2pMAK9Iu6a9kBDt0y_b1TEzw")


with open('./workshop_image.png', 'rb') as f:
  image_bytes = f.read()

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
      types.Part.from_bytes(
        data=image_bytes,
        mime_type='image/jpeg',
      ),
      'Explain this image'
    ]
)

print(response.text)
