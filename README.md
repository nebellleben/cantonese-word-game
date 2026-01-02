# cantonese-word-game
Cantonese Word Game Created for the AI Development Tools Zoomcamp Capstone Project


Points for brainstorming:

- Frontend
>create the snake game with two models: pass-through and walls. prepare to make it multiplayers - we will have this functionality: leaderboard and watching (me following other players that currently play). add mockups for that and also for log in. everything should be interactive - I can log in, sign up, see my username when I'm logged in, see leaderboard, see other people play (in this case just implement some playing logic yourself as if somebody is playing) make sure that all the logic is covered with tests
>don't implement backend, so everything is mocked. But centralize all the calls to the backend in one place
- Backend
>analyse the content of the client and create an OpenAPI specs based on what it needs. later we want to implement backend based on these specs
>based on the OpenAPI specs, create fastapi backend for now use a mock database, which we will later replace with a real one create tests to make sure the implementation works
>follow the guidelines in AGENTS.md
- Can implement *agent* for generating the word lists for different school grades
- Think about how *MCP* shall be applied
- Integrating Frontend and Backend
>Make frontend use backend. use OpenAPI specs for guidance follow the guidelines in AGENTS.md
>How can I run both frontend and backend at the same time? Let's use concurrently instead of our own script
- Database
>Database is for storing individual student progress, score, weak areas etc
>now for backend let's use postgres and sqlite database (via sqlalchemy) follow the guidelines in AGENTS.md
>let's also add some integration tests (using sqlite) to make sure things work put the integration test in a separate folder tests_integration
- Containerization
>right now we have frontend, backend, and database (sqlite)
>let's put everything into docker compose and use postgres there. we can serve frontend with nginx or whatever you recommend
- CD/CI: prompt 
>I want to create a CI/CD pipeline with github actions with two parts
> - first we run tests (frontend + backend)
> - if tests pass, I want to deploy the update to render