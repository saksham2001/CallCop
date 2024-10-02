# Define the tools available to the models
openai_tools = [
{
    "type": "function",
    "function": {
        "name": "record_video",
        "description": "Record a 15 seconds video using the camera",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the video file (default: auto generated)",
                },
                "video_length": {
                    "type": "number",
                    "description": "The length of the video in seconds (default: 15 seconds)",
                },
            },
            "required": [],
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "capture_image",
        "description": "Capture an image using the camera",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the image file (default: auto generated)",
                },
            },
            "required": [],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city",
                },
                "unit": {
                    "type": "string",
                    "description": "The unit for the temperature",
                    "enum": ["celsius", "fahrenheit"],
                },
            },
            "required": ["location"],
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "get_news",
        "description": "Get the latest news with title, snippet and source from Google News",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for",
                },
            },
            "required": ["query"],
        },
    }   
},
{
    "type": "function",
    "function": {
        "name": "internet_search",
        "description": "Search the internet for a given query and return the top results with snippets",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for",
                },
            },
            "required": ["query"],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "set_alarm",
        "description": "Set an alarm for a given time",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "The time to set the alarm. Format: HH:MM AM/PM",
                },
            },
            "required": ["time"],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "set_timer",
        "description": "Set a timer for a given duration",
        "parameters": {
            "type": "object",
            "properties": {
                "duration": {
                    "type": "number",
                    "description": "The duration of the timer in minutes",
                },
            },
            "required": ["duration"],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "create_calendar_event",
        "description": "Create a calendar event for a given date, time and event",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The date of the event. Format: YYYY-MM-DD",
                },
                "time": {
                    "type": "string",
                    "description": "The time of the event. Format: HH:MM AM/PM",
                },
                "event": {
                    "type": "string",
                    "description": "The event description",
                },
                "location": {
                    "type": "string",
                    "description": "The location of the event",
                },
            },
            "required": ["date", "time", "event"],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "create_reminder",
        "description": "Create a reminder for a given time and message",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "The time of the reminder. Format: HH:MM AM/PM",
                },
                "message": {
                    "type": "string",
                    "description": "The reminder message",
                },
            },
            "required": ["time", "message"],
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "create_note",
        "description": "Create a note",
        "parameters": {
            "type": "object",
            "properties": {
                "note": {
                    "type": "string",
                    "description": "The note content",
                },
            },
            "required": ["note"],
        },
    }
},
]

claude_tools = [
{
        "name": "record_video",
        "description": "Record a 15 seconds video using the camera",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the video file (default: auto generated)",
                },
                "video_length": {
                    "type": "number",
                    "description": "The length of the video in seconds (default: 15 seconds)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "capture_image",
        "description": "Capture an image using the camera",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the image file (default: auto generated)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city",
                    },
                "unit": {
                    "type": "string", 
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit for the temperature",
                    "default": "celsius"
                    },
                },
            "required": ["city_name"],
        },
    },

    {
        "name": "get_news",
        "description": "Get the latest news with title, snippet and source from Google News",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "internet_search",
        "description": "Search the internet for a given query and return the top results with snippets",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "set_alarm",
        "description": "Set an alarm for a given time",
        "input_schema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "The time to set the alarm. Format: HH:MM AM/PM",
                },
            },
            "required": ["time"],
        },
    },
    {
        "name": "set_timer",
        "description": "Set a timer for a given duration",
        "input_schema": {
            "type": "object",
            "properties": {
                "duration": {
                    "type": "number",
                    "description": "The duration of the timer in minutes",
                },
            },
            "required": ["duration"],
        },
    },
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event for a given date, time and event",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The date of the event. Format: YYYY-MM-DD",
                },
                "time": {
                    "type": "string",
                    "description": "The time of the event. Format: HH:MM AM/PM",
                },
                "event": {
                    "type": "string",
                    "description": "The event description",
                },
                "location": {
                    "type": "string",
                    "description": "The location of the event",
                },
            },
            "required": ["date", "time", "event"],
        },
    },
    {
        "name": "create_reminder",
        "description": "Create a reminder for a given time and message",
        "input_schema": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "The time of the reminder. Format: HH:MM AM/PM",
                },
                "message": {
                    "type": "string",
                    "description": "The reminder message",
                },
            },
            "required": ["time", "message"],
        },
    },
    {
        "name": "create_note",
        "description": "Create a note",
        "input_schema": {
            "type": "object",
            "properties": {
                "note": {
                    "type": "string",
                    "description": "The note content",
                },
            },
            "required": ["note"],
        },
    },
    
]