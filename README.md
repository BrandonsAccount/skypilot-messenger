<h3 align="center"><img src="docs/messenger.png" height="64"><br>SkyPilot Messenger</h3>
<!-- https://raw.githubusercontent.com/brandonsaccount/skypilot-gui/poc/ -->

## A flexible MCP host that can be run on your local machine or remote.
SkyPilot Messenger takes user prompts, enriches them with context, and delivers them to the SkyPilot Thinker service (LLM provider). 
It’s not just message passing, it’s intelligent orchestration. This is the service that ensures your LLMs respond 
consistently, securely, and with the right abstractions for downstream systems.

# How to configure Messenger
`conf/instructions.md` contains the buildtime policies/instructions that Messenger will use to interact with the LLM API. 
These get translated into a JSON format and stored in `app/message/instructions.json` during the build process by using `build-tools/instructions_translator.py`.

`app/message/` contains the runtime configuration files that Messenger will use to interact with the LLM API and MCP servers.

# How to build and run Messenger
```bash
./build-tools/instructions_translator.py --input_file "conf/instructions.md" --output_file "app/message/instructions.json"
docker build -t skypilot-messenger .
docker run --rm -p 8000:8000 --env-file conf/.env.local --network skypilot --name skypilot-messenger skypilot-messenger
```