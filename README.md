\# GHOSTLAB



\## Virtual System Simulation, Fault Injection \& Testing Platform



GHOSTLAB is a software-only system simulator that creates virtual systems, simulates failures, runs automated tests, tracks dependencies, and analyzes system health.



The project is designed to demonstrate concepts from:



\- Python

\- Object-Oriented Programming

\- Data Structures \& Algorithms

\- Computer Networks

\- Concurrency

\- DBMS \& SQL

\- REST APIs

\- Software Testing

\- Fault Injection

\- System Diagnostics



\---



\## Features



\### Virtual System Simulation

Create and manage virtual nodes representing components of different environments:



\- Automotive

\- PC

\- Aircraft



Each node has properties such as:



\- Status

\- Health

\- CPU usage

\- Memory usage

\- Priority

\- Environment

\- Dependencies



\### Fault Injection



GHOSTLAB can deliberately introduce simulated failures such as:



\- CRASH

\- TIMEOUT

\- NETWORK

\- HIGH\_CPU

\- HIGH\_MEMORY

\- SENSOR\_FAULT



This allows the system to observe how failures affect individual nodes and dependent systems.



\### Dependency Simulation



Nodes can depend on other nodes.



For example:



```text

Battery

&#x20;  ↓

Lighting System


If the Battery fails, dependent systems can also be affected.
Automated Testing
GHOSTLAB runs automated tests against the current state of the simulated system.
Tests check conditions such as:
- Node availability
- System health
- CPU usage
- Memory usage
The system produces PASS/FAIL results.
Database & History
SQLite is used to store:
- Nodes
- Tests
- Test runs
- Test results
- Failures
- Events
- Dependencies
This allows system activity and testing history to be preserved.
Logs & Diagnostics
The dashboard provides:
- System logs
- Test results
- Failure information
- Test history
- Node health
- Diagnosis
- Recommended recovery actions
Architecture
                    GHOSTLAB
                        │
             ┌──────────┴──────────┐
             │                     │
         Frontend               Backend
             │                     │
       HTML/CSS/JS              FastAPI
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
               Simulation       Testing       Database
                    │              │              │
                  Nodes       Fault Injection   SQLite
                    │              │
              Dependencies    Diagnostics

Technology Stack
Frontend
- HTML
- CSS
- JavaScript
Backend
- Python
- FastAPI
- Uvicorn
Database
- SQLite
Development
- VS Code
- Git
- GitHub
Project Structure
GHOSTLAB/
│
├── Backend/
│   ├── api/
│   │   └── api.py
│   │
│   ├── database/
│   │   └── database_manager.py
│   │
│   ├── simulator/
│   │   └── node.py
│   │
│   ├── testing/
│   ├── scheduler/
│   ├── network/
│   ├── chaos/
│   │
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── requirements.txt
├── .gitignore
└── README.md

How to Run
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ghostLAB

2. Create a virtual environment
python -m venv venv

3. Activate the virtual environment
Windows:
venv\Scripts\activate

4. Install dependencies
pip install -r requirements.txt

5. Start the Backend
From the project root:
uvicorn Backend.api.api:app --reload

Backend:
http://127.0.0.1:8000

6. Start the Frontend
Open another terminal:
python -m http.server 5500

Frontend:
http://127.0.0.1:5500

Example Workflow
Create Virtual Nodes
        ↓
Start System
        ↓
Inject Failure
        ↓
Failure Changes Node State
        ↓
Dependencies Are Affected
        ↓
Run Automated Tests
        ↓
PASS / FAIL Results
        ↓
Store Results & Events
        ↓
Analyze System Health
        ↓
Recover System

Example Failure Scenario
A HIGH_CPU failure can push a node's simulated CPU usage to a critical level.
Normal Node
CPU: 25%
Health: 100%
Status: ONLINE

        ↓

Inject HIGH_CPU

        ↓

CPU: 95%
Health: 60%
Status: WARNING

        ↓

Run Tests

        ↓

CPU Test: FAIL

The failure and test activity are recorded in the database and displayed through the dashboard.
Purpose
GHOSTLAB demonstrates how software systems can be tested against simulated failures without requiring physical hardware.
The project combines system simulation, automated testing, fault injection, dependency management, networking concepts, concurrency, and database persistence into one software platform.
Future Scope
- Advanced failure propagation
- More detailed diagnostics
- Additional simulated environments
- Distributed node simulation
- Advanced test scheduling
- More failure types
- Performance monitoring
- Network visualization
- AI-assisted failure analysis
Author
Ayan Topno
B.Tech Computer Science & Engineering
GHOSTLAB — Software-Based Virtual System Simulation & Fault Testing Platform

