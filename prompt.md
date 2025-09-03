Populate the skyassist directory based on the information in this file.

# Description
Skypilot is an MCP Host that is responsible for orchestrating tasks that benefit from AI.

# Responsibilities

1. Handling user prompts from a front-end interface
   1. It should do this via HTTP API, preferably RESTful and using FastAPI
1. Reaching out to an LLM API using an MCP client, in order to provide it with context and instructions
   1. The data provided must follow the format in messages/message.json
1. If the LLM API returns an action, it should execute that action using the MCP clients
   1. The action must be executed in a way that is consistent with the MCP design principles
1. If the LLM API returns an answer, it should return that answer to the front-end interface
1. If the LLM API returns an error, it should return that error to the front-end interface
1. If the LLM API does not provide a response that is validated by messages/output-schema.json, the messenger must add feedback to the message.json and make another request to the LLM API.
   1. If the LLM API fails to adhere to the output-schema after 3 attempts, the messenger should stop attempting and return an error message to the front-end interface response


# Requirements
* This service must follow MCP design principles
* This codebase must adhere to 12 factor app principles
* This codebase's code must be commented to include "what" and "why"
* This codebase's README.md must include instructions on how to install, build, run, and test the service
* All documentation, whether README or comments, must be written for an audience that is not familiar with the service.
* Recommendations may be made to improve the files in the `message` directory, but not made. The recommendations should be written to the bottom of the README.md