# Hack The North - Backend Challenge
To start the service run: ```docker compose up``` from /HTN-BE (runs on ```localhost:3000```)
## Endpoints
- ```GET http://localhost:3000/users/```: Return list of all user data 
- ```GET http://localhost:3000/users/<user_id>```: Returns specified user's information
- ```PUT http://localhost:3000/users/<user_id>```: Updates and returns specified user's information <br/>
Sample body: 
```
{
  "name": "Mc Lovin",
  "company": "Mclovin Inc",
  "email": "mclovin@gmail.com",
  "skills": [
    {
      "skill": "lovin",
      "rating": 100
    },
    {
      "skill": "Python",
      "rating": 1
    }
  ]
}
```
- ```GET http://localhost:3000/skills/```: Lists frequency of all skills
- ```GET http://localhost:3000/skills/?min_frequency=10&max_frequency=20```: Lists frequency of all skills based on filter
- ```GET http://localhost:3000/events/```: Lists all events
- ```GET http://localhost:3000/events/<event_id>```: Returns specified event's information
- ```GET http://localhost:3000/register/<user_id>```: Changes users 'registered' status to true
- ```POST http://localhost:3000/scan/```: handles QR code scanning and returns updated event information<br/>
Sample body:
```
{
"event_id": 1,
"hacker_id": 500
}
```
