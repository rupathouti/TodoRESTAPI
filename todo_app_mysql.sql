DROP DATABASE IF EXISTS todo;
CREATE DATABASE IF NOT EXISTS todo;
USE todo;

-- drop old versions of users and tasks tables
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tasks;

-- create users and tasks table
CREATE TABLE users(
    id INT NOT NULL AUTO_INCREMENT, -- sql will automatically choose ids for me
    email_id VARCHAR(500),
    password  VARCHAR(1000),
    PRIMARY KEY(id)
);

CREATE TABLE tasks(
    id INT NOT NULL AUTO_INCREMENT, -- sql will automatically choose ids for me
    task VARCHAR(1000) NOT NULL,
	status boolean DEFAULT false,
	user_id INT NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (user_id) REFERENCES users(id) -- sql now knows that user_ids must match ids in the users table
);

-- add users
INSERT INTO users (email_id, password) 
  VALUES ("bhaskar343@gmail.com", "bhaskar");
  
INSERT INTO users (email_id, password) 
  VALUES ("rupadussa@gmail.com", "rupa");
  
  
-- add tasks
INSERT INTO tasks (task, user_id) 
  VALUES ("create UI for todo app", (SELECT id FROM users WHERE email_id = "bhaskar343@gmail.com"));
  
INSERT INTO tasks (task, user_id) 
  VALUES ("Setup TODO Rest API ", (SELECT id FROM users WHERE email_id = "bhaskar343@gmail.com"));

INSERT INTO tasks (task, user_id) 
  VALUES ("Create a mySQL DB Script for Todo app", (SELECT id FROM users WHERE email_id = "bhaskar343@gmail.com"));

INSERT INTO tasks (task, user_id) 
  VALUES ("Drink honey water at 7am/7pm daily", (SELECT id FROM users WHERE email_id = "rupadussa@gmail.com"));

 