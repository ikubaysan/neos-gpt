# neos-gpt
Server to facilitate consumption of the OpenAI API from NeosVR, without exposing API keys in Logix.

## Features:
* Handling contexts of multiple conversations
* Rate limiting
* Max token limit
* Responses returned as plain text for easy consumption in Logix
* IP whitelist

## Local Server Setup:
1. Install Python 3
2. Open a command prompt and navigate to the root of this project (`cd path/to/neos-gpt`)
3. Install the requirements with `pip install -r requirements.txt`
4. Make a copy of `config_example.ini` and rename it to `config.ini`
5. Open `config.ini` in a text editor and enter your OpenAI API key to the `api_key` section. 
Change any other options as you see fit. Set `host` to `localhost` if you intend to run the server on the same 
machine you are running Neos. Otherwise, set `host` to `0.0.0.0`
6. Run `python main.py` to start the server. You will see a message like this, take note of the URL:
```
 * Running on http://localhost:5000
```

With the default configuration, you can test the server with an API client like Postman.
Make a POST HTTP request to your server at:
http://localhost:5000/prompt
and enter your prompt as raw text in the request body.

## (Optional) Daemonized VPS Setup:
Hosting the server on a remote system is not required, but is possible.
If you want to run on a headless linux EC2 for instance, you can create a service for the server.
Look at neos_gpt_server.service as an example, changing the ExecStart and WorkingDirectory values as needed.
Then copy the service file to `/etc/systemd/system/` and run:

* `sudo systemctl daemon-reload` to reload service files
* `sudo systemctl start neos_gpt_server.service` to start the service
* `sudo systemctl enable neos_gpt_server.service` to enable the service to start on boot (optional)

## Client Setup in NeosVR:
1. This public folder contains the client:
`neosrec:///U-DingoYabuki/R-9793cb26-f9ac-4eea-b52d-1bafdff8e502`
Copy this URI and paste it into Neos, and the public folder will spawn. 
The client item is in the folder, named `NeosGPTClient`. 
2. Spawn the item and navigate to the root of it with your Inspector tool.
3. You will see 2 `DynamicValueVariable<string>` components with VariableNames `Settings/URL` and `and Settings/ClientUserID`. Modify those components' values to match your server's URL (suffixed with `/prompt`, eg `http://localhost:5000/prompt`) and your Neos UserID.
   * Your Neos UserID is `U-`, followed by your regular Neos username. Eg `U-MyUsername`.

Now your client has been configured. 
It will only work when you are in a session. The client will connect to your server, and send queries to OpenAI using your API key. 

When other users send prompts, the requests will be sent to your server on your behalf. There is no need for other users to connect to your server.

You can duplicate the client to start a new conversation, and have multiple conversations going at once.

<img src="resources/readme/images/inspector.jpg"/>
<img src="resources/readme/images/client.jpg"/>