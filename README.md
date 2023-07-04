# neos-gpt
Server to facilitate consumption of the OpenAI API from NeosVR, without exposing API keys in Logix.

Features:
* Rate limiting
* Max token limit
* Responses returned as plain text for easy consumption in Logix

To use:
1. Install Python 3
2. Install the requirements with `pip install -r requirements.txt`
3. Make a copy of `config_example.ini` and rename it to `config.ini`
4. Open `config.ini` in a text editor and enter your OpenAI API key to the api_key section. 
Change any other options as you see fit.
5. Run `python main.py` to start the server. The server will be hosted on the host and port you specified in `config.ini`

With the default configuration, you can test the server with Postman by making a POST HTTP request to your server at:
http://localhost:5000/prompt
And enter your prompt as raw text in the request body.