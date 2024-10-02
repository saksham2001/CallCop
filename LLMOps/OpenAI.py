from openai import OpenAI
from datetime import datetime
import logging
import json

class OpenAILLMHandler:
    '''
    This class handles the interaction with the OpenAI Large Language Model API.
    '''
    openai_models = {'gpt-3.5-turbo-0125' : [0.50, 1.50],
          'gpt-4-0613' : [30.00, 60.00],
          'gpt-4-0125-preview' : [30.00, 60.00],
          'gpt-4-1106-vision-preview' : [10.00, 30.00],
          'gpt-4-turbo-2024-04-09': [10.00, 30.00],
          'gpt-4o-2024-05-13': [5.00, 15.00]
          }
    
    usd_to_inr = 85.00
    
    def __init__(self, api_key, preprompt=None, optimize=False, tools=None, functions=None):
        '''
        Parameters:
        - api_key: The OpenAI API key
        - available_tools: The tools available to the models for function calling
            default: None
        - preprompt: The preprompt to add to the last message
            default: None
        - optimize: Optimize the messages by removing older image data
            default: False
        - tools: The tools available to the model
            default: None
        - functions: The functions available to the model
            default: None
        '''
        self.api_key = api_key
        self.openai_client = OpenAI()
        self.preprompt = preprompt
        self.optimize = optimize
        self.tools = tools
        self.functions = functions

    def estimate_api_cost(self, model, input_tokens, output_tokens):
        '''
        This function estimates the cost of the API call based on the model, input tokens and output tokens.

        Parameters:
        - model (str): Model used for the API call
        - input_tokens (int): Number of input tokens
        - output_tokens (int): Number of output tokens
        
        Returns:
        - float: Cost of the API call (in INR)
        '''
        
        # Estimate the cost
        cost = ((input_tokens/1e6)*self.openai_models[model][0] + (output_tokens/1e6)*self.openai_models[model][1])*self.usd_to_inr
        
        return cost
    
    def send_text(self, messages, model='gpt-3.5-turbo-0125', user_id=None, max_tokens=1000):
        '''
        This method sends a text to the OpenAI model and returns the response.

        Parameters:
        - model: The model to use
        - messages: The messages to send
        - user_id: The user id
            default: None
        - max_tokens: The maximum number of tokens to generate
            default: 1000

        Returns:
        - response_message: The response message
        - total_cost: The total cost of the API call (In INR)
        - role: The role of the message
        - model: The model used
        - completion_tokens: The number of tokens generated
        - prompt_tokens: The number of tokens in the prompt
        '''
        # add preprompt to the last message
        if self.preprompt:
            messages[-1]['content'] = self.preprompt + messages[-1]['content']
        
        if self.optimize:
            # iterate through the messages and check if the message has image and remove
            for i in range(len(messages)):
                try:
                    if 'image_url' == messages[i]['content'][1]['type']:
                        del messages[i]
                except:
                    pass

        # Send the text to OpenAI LLM
        response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto" if self.tools else None,
                    user=user_id,
                    max_tokens=max_tokens,
                )
        
        if response.choices[0].message.content:
            response_message = response.choices[0].message.content
            role = response.choices[0].message.role
            model = response.model
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            logging.info(f'Response: {response_message}')
            logging.info(f'Total Cost: {total_cost} INR')
        elif response.choices[0].message.tool_calls and self.tools and self.functions:
            response_message = response.choices[0].message
            tool_calls = response.choices[0].message.tool_calls
            role = response.choices[0].message.role
            model = response.model
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            messages.append(response_message)

            response_message, new_cost, new_completion_tokens, new_prompt_tokens = self.call_function(tool_calls, model, messages)

            total_cost += new_cost
            completion_tokens += new_completion_tokens
            prompt_tokens += new_prompt_tokens

            logging.info(f'Response: {response_message}')
            logging.info(f'Total Cost: {total_cost} INR')

        else:
            return None, None, None, None, None, None
        
        return response_message, total_cost, role, model, completion_tokens, prompt_tokens
            
    
    def send_text_and_image(self, messages, model='gpt-4o-2024-05-13', user_id=None, max_tokens=1000):
        '''
        This method sends a text and an image to the OpenAI model and returns the response.

        Parameters:
        - messages: message array containing the image and the text query
        - model: The model to use
            default: gpt-4-turbo-2024-04-09
        - user_id: The user id
            default: None
        - max_tokens: The maximum number of tokens to generate
            default: 1000

        Returns:
        - response_message: The response message
        - total_cost: The total cost of the API call (In INR)
        - role: The role of the message
        - model: The model used
        - completion_tokens: The number of tokens generated
        - prompt_tokens: The number of tokens in the prompt
        '''
        # add preprompt to the last message
        if self.preprompt:
            messages[-1]['content'][0]['text'] = self.preprompt + messages[-1]['content'][0]['text']

        if self.optimize:
            # iterate through the messages and check if the message has image and remove
            for i in range(len(messages)-1):
                try:
                    if 'image_url' == messages[i]['content'][1]['type']:
                        del messages[i]
                except:
                    pass

        # Send the text to OpenAI LLM
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto" if self.tools else None,
            user=user_id,
            max_tokens=max_tokens,
            )

        if response.choices[0].message.content:
            response_message = response.choices[0].message.content
            role = response.choices[0].message.role
            model = response.model
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            logging.info(f'Response: {response_message}')
            logging.info(f'Total Cost: {total_cost} INR')
        
        elif response.choices[0].message.tool_calls and self.tools and self.functions:
            response_message = response.choices[0].message
            tool_calls = response.choices[0].message.tool_calls
            role = response.choices[0].message.role
            model = response.model
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            messages.append(response_message)

            response_message, new_cost, new_completion_tokens, new_prompt_tokens = self.call_function(tool_calls, model, messages)

            total_cost += new_cost
            completion_tokens += new_completion_tokens
            prompt_tokens += new_prompt_tokens

            logging.info(f'Response: {response_message}')
            logging.info(f'Total Cost: {total_cost} INR')

        else:
            return None, None, None, None, None, None
        
        return response_message, total_cost, role, model, completion_tokens, prompt_tokens

        
    def call_function(self, tool_calls, model, messages):
        '''
        This function calls the function specified in the tool_call object and returns the response to the model.

        Args:
            tool_call (list): List of tool_call objects

        Returns:
            str: Response from the model
        '''
        # Call all the functions and get the response
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = self.functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            logging.info(f'Calling function: {function_name} with arguments: {function_args}')

            function_response = function_to_call(**function_args)

            # Append the response to the backend messages
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

            # Call the model again with the updated backend messages
            second_response = self.openai_client.chat.completions.create(
                model=model,   
                messages=messages,
            )

            # Update the cost for the recent model call
            model_reply = second_response.model
            new_prompt_tokens = second_response.usage.completion_tokens
            new_completion_tokens = second_response.usage.prompt_tokens

            new_cost = self.estimate_api_cost(model_reply, new_prompt_tokens, new_completion_tokens)
            
            return second_response.choices[0].message.content, new_cost, new_completion_tokens, new_prompt_tokens


class OpenAISpeechHandler:
    '''
    This class handles the interaction with the OpenAI Speech API.
    '''

    whisper_price = 0.006 #$0.006 per minute
    tts_price = 15.00 # per milion tokens
    
    usd_to_inr = 85.00

    def __init__(self, api_key):
        '''
        Parameters:
        - api_key: The OpenAI API key
        '''
        self.api_key = api_key
        self.openai_client = OpenAI()

    def estimate_api_cost(self, model, amount):
        '''
        This function estimates the cost of the API call based on the model, input tokens and output tokens.

        Parameters:
        - model (str): Model used for the API call
        
        Returns:
        - float: Cost of the API call (in INR)
        '''
        
        if model == "whisper-1":
            cost = (amount/60)*self.whisper_price
        elif model == "tts-1":
            # Estimate the cost
            cost = ((amount/1e6)*self.tts_price)*self.usd_to_inr
        
        return cost

    def transcribe(self, audio_file, model="whisper-1"):
        '''
        This method transcribes an audio file using the OpenAI API.

        Parameters:
        - audio_file: The name of the audio file
        - model: The model to use
            default: whisper-1

        Returns:
        - transcription: The transcription of the audio file
        - cost: The cost of the API call (In INR)
        - language: The language of the audio file
        '''
        audio_file = open(audio_file, "rb")

        if model=='whisper-1':
            transcription = self.openai_client.audio.transcriptions.create(
                model=model, 
                file=audio_file,
                response_format='verbose_json'
                )
            
            length = transcription.duration
            cost = self.estimate_api_cost(model, length)
            text = transcription.text
            language = transcription.language

        logging.info(f'Transcription: {text}')

        return text, cost, language
    
    def transcribe_buffer(self, audio_buffer, model="whisper-1"):
        '''
        This method transcribes an audio buffer using the OpenAI API.

        Parameters:
        - audio_buffer: The audio buffer
        - model: The model to use
            default: whisper-1
        '''
        if model=='whisper-1':
            transcription = self.openai_client.audio.transcriptions.create(
                model=model, 
                file=audio_buffer,
                response_format='verbose_json'
                )
            
            length = transcription.duration
            cost = self.estimate_api_cost(model, length)
            text = transcription.text
            language = transcription.language

        logging.info(f'Transcription: {text}')

        return text, cost, language
    
    def translate(self, audio_file, model="whisper-1"):
        '''
        This method translates an audio file using the OpenAI API.

        Parameters:
        - audio_file: The name of the audio file
        - model: The model to use
            default: whisper-1

        Returns:
        - translation: The translation of the audio file.
        '''
        audio_file= open(audio_file+'.mp3', "rb")

        translation = self.openai_client.audio.translations.create(
            model=model, 
            file=audio_file
            )
        
        logging.info(f'Translation: {translation.text}')

        return translation.text
    
    def speak(self, text, file_name=None, model="tts-1", voice="nova"):
        '''
        This method generates an audio file using the OpenAI API.

        Parameters:
        - text: The text to convert to speech
        - file_name: The name of the audio file
        - model: The model to use
            default: tts-1

        Returns:
        - file_name: The name of the audio file
        '''
        # if file_name is none, create a unique file name
        if file_name is None:
            file_name = f"data/t2s/audio_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        response = self.openai_client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format='wav'
            )

        response.stream_to_file(file_name+'.wav')

        logging.info(f'Audio File Generated: {file_name}.wav')

        return file_name+'.wav'