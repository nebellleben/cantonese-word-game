Technical requirement:
- Use relevant javascript library such as react and angular to implement the front end
- Include an option to switch between English/Traditional Chinese interface on every page

Classes of users:
- There are three classes of users - student, teacher and admin
- All users can register an account under student or teacher class in a registration page
- There is only one admin account, default password is "cantonese"

Student users:
- Upon log in by a student user, the user can choose to start a game or review the statistics of his games
- Each user can choose the deck he wants to practice, the decks are defined by the admin
- Each game is a timed exercise, a list of words randomly appear (without duplication) one at a time, and the user is required to pronounce the word in Cantonese
- The game interface is swipe card style that can operate on both desktop and mobile, the user can swipe card to skip a word
- The game engine records the response and decides whether the pronunciation is correct
- The response time and whether the correctness of pronunciation are recorded
- At the end of each game, the score is shown based on the response time and number of words correctly pronounced
- An n-day streak is award to the user for n consecutive days of completing exercises 
- In the statistics page, the student user can review all the past scores; the scores are plotted in bar chart; there is a dropdown menu where the student can choose the specific deck he/she practiced or show all scores
- The top 20 wrongly pronounced words are also shown, where the student user can see number of times the words got wrongly pronounced 

Teacher users:
- The teacher's account, once logged in, shows the list of students under the teacher's management, and the teacher can review the statistics of scores of each individual student under the teacher's management
- There is another view in the teacher's account where the ratio of times of each word wrongly pronounced is shown, sorted in descending order

Admin user:
- The admin's account has four functions:
- Administer the words database which the students can play the games, the admin can create new word list, add or remove 
- Associate students with teachers, so that teachers can view statistics of each student associated with the teacher
- View the statistics of each student, and the statistic of all students collectively (as a class)
- Administer or reset account passwords of all student and teacher users