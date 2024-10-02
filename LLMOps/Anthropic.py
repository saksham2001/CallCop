from email import message
from pyexpat.errors import messages
import anthropic
from datetime import datetime
import logging
import json

class ClaudeLLMHandler:
    '''
    This class handles the interaction with the OpenAI Large Language Model API.
    '''
    openai_models = {'claude-3-5-sonnet-20240620' : [0.50, 1.50],
          'claude-3-opus-20240229' : [30.00, 60.00],
          'claude-3-haiku-20240307' : [30.00, 60.00],
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
        self.claude_client = anthropic.Anthropic()
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
    
    def send_text(self, messages, model='claude-3-5-sonnet-20240620', user_id=None, max_tokens=1000):
        '''
        This method sends a text to the OpenAI model and returns the response.

        Parameters:
        - model: The model to use
            default: claude-3-5-sonnet-20240620
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
        response = self.claude_client.messages.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    tools=self.tools,
                    tool_choice={"type": "auto"} if self.tools else None,
                )
        
        if response.stop_reason == "end_turn":
            response_message = response.content[0].text
            role = response.role
            model = response.model
            completion_tokens = response.usage.input_tokens
            prompt_tokens = response.usage.output_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            logging.info(f'Response: {response_message}')
            logging.info(f'Total Cost: {total_cost} INR')
        elif response.stop_reason == "tool_use" and self.tools and self.functions:
            tool_calls = [c for c in response.content if c.type == "tool_use"]
            role = response.role
            model = response.model
            completion_tokens = response.usage.input_tokens
            prompt_tokens = response.usage.output_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            messages.append({"role": response.role, "content": response.content})

            response_message, new_cost, new_completion_tokens, new_prompt_tokens = self.call_function(tool_calls, model, messages)

            total_cost += new_cost
            completion_tokens += new_completion_tokens
            prompt_tokens += new_prompt_tokens

            logging.info(f'Response: {response_message}')
            logging.info(f'Total Cost: {total_cost} INR')

        else:
            return None, None, None, None, None, None
        
        return response_message, total_cost, role, model, completion_tokens, prompt_tokens
            
    
    def send_text_and_image(self, messages, model='claude-3-5-sonnet-20240620', user_id=None, max_tokens=1000):
        '''
        This method sends a text and an image to the OpenAI model and returns the response.

        Parameters:
        - messages: message array containing the image and the text query
        - model: The model to use
            default: claude-3-5-sonnet-20240620
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
        response = self.claude_client.messages.create(
            model=model,
            messages=messages,
            tools=self.tools,
            tool_choice={"type": "auto"} if self.tools else None,
            max_tokens=max_tokens,
            )

        if response.stop_reason == "end_turn":
            response_message = response.content[0].text
            role = response.role
            model = response.model
            completion_tokens = response.usage.input_tokens
            prompt_tokens = response.usage.output_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            logging.info(f'Response: {response_message}')
            logging.info(f'Total Cost: {total_cost} INR')
        elif response.stop_reason == "tool_use" and self.tools and self.functions:
            tool_calls = [c for c in response.content if c.type == "tool_use"]
            role = response.role
            model = response.model
            completion_tokens = response.usage.input_tokens
            prompt_tokens = response.usage.output_tokens
            total_cost = self.estimate_api_cost(model, prompt_tokens, completion_tokens)

            messages.append({"role": response.role, "content": response.content})

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
            model (str): Model used for the API call
            messages (list): List of messages

        Returns:
            str: Response from the model
        '''
        # Call all the functions and get the response
        for tool_call in tool_calls:
            function_name = tool_call.name
            function_to_call = self.functions[function_name]
            function_args = tool_call.input

            logging.info(f'Calling function: {function_name} with arguments: {function_args}')

            function_response = function_to_call(**function_args)

            # Append the response to the backend messages
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_call.id,
                            "content": [{"type": "text", "text": str(function_response)}],
                        }
                    ],
                }
            )

            # Call the model again with the updated backend messages
            second_response = self.claude_client.messages.create(
                model=model,   
                messages=messages,
                max_tokens=1000,
                tools=self.tools
            )

            # Update the cost for the recent model call
            model_reply = second_response.model
            new_completion_tokens = second_response.usage.input_tokens
            new_prompt_tokens = second_response.usage.output_tokens

            new_cost = self.estimate_api_cost(model_reply, new_prompt_tokens, new_completion_tokens)
            
            return second_response.content[0].text, new_cost, new_completion_tokens, new_prompt_tokens
