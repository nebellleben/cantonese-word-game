# cantonese-word-game

Cantonese Word Game Created for the AI Development Tools Zoomcamp Capstone Project

## Description of the project:

This game is created for primary school students in Hong Kong, espcially those diagnosed with Dyslexia, whose first language is Cantonese. This game aims to improve recognition of words and create motivation for them to practise regonising Chinese words

## Requirements of the project:

Each point below is a stage of implementation. You are required to run each stage and show the output, refine it based on my further input, and ask for permission to the next stage

### General Requirements:
- This project is a captone project that needs to fulfill all requirements under project_requirements.md
- You may seek clarifications if needed

### Frontend
- create the Cantonese Pronunciation Game based on the requirements of FRONTEND.md
- don't implement backend yet, so everything is mocked. But centralize all the calls to the backend in one place

### Backend
- create the game engine based on the requirements of BACKEND.md
- analyse the content of the client and create an OpenAPI specs based on what it needs. later we want to implement backend based on these specs
- based on the OpenAPI specs, create fastapi backend for now use a mock database, which we will later replace with a real one create tests to make sure the implementation works
- follow the guidelines in BACKEND_AGENTS.md

### Integrating Frontend and Backend
- Make frontend use backend. use OpenAPI specs for guidance follow the guidelines in AGENTS.md
- How can I run both frontend and backend at the same time? Let's use concurrently instead of our own script

### Database
- Database is for storing individual student progress, history of games, list of words for practice etc
- now for backend let's use postgres and sqlite database (via sqlalchemy) follow the guidelines in AGENTS.md
- let's also add some integration tests (using sqlite) to make sure things work put the integration test in a separate folder tests_integration

### MCP and Agents
- Now add a new function for the admin: create an *agent* for the admin to generate new word list
- The agent shall be able to intelligently generate a list of words, based on the inputs provided: (1) grade (2) number of words (3) theme (such as family, school, society... ), which can be selected from a list or entered as a free text 
- Suggest how *MCP* shall be applied for this task

### Containerization
- Right now we have frontend, backend, and database (sqlite)
- Let's put everything into docker compose and use postgres there. we can serve frontend with nginx or whatever you recommend

### CD/CI
- I want to create a CI/CD pipeline with github actions with two parts
- first we run tests (frontend + backend)
- if tests pass, I want to deploy the update to render

### Deployment
 Deployment to AWS for web based applciation and frontend 