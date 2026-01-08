import openai
import json

class RequestHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def send_request(self, prompt):
        try:
            response = openai.Completion.create(
                engine='davinci',
                prompt=prompt,
                max_tokens=150
            )
            return response
        except Exception as e:
            print(f'Error sending request: {e}')
            return None

    def process_response(self, response):
        if response:
            try:
                return json.loads(response.choices[0].text.strip())
            except json.JSONDecodeError as e:
                print(f'Error decoding response: {e}')
                return None
        return None
