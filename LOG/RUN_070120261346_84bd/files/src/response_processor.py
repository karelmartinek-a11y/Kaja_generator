import json

class ResponseProcessor:
    def __init__(self, log_path):
        self.log_path = log_path

    def process_response(self, response):
        try:
            data = json.loads(response)
            self.log_response(data)
            return data
        except json.JSONDecodeError as e:
            self.log_error(f'Error decoding JSON: {e}')
            return None

    def log_response(self, data):
        with open(self.log_path, 'a') as log_file:
            log_file.write(json.dumps(data, indent=2) + '\n')

    def log_error(self, message):
        with open(self.log_path, 'a') as log_file:
            log_file.write(f'ERROR: {message}\n')
