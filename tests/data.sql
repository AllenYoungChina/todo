INSERT INTO user (username, password)
VALUES
    ('test', 'scrypt:32768:8:1$ok9Ftvu73pllNoYA$35ff222926e3574bded0c593196d94fd815ffcf71f21065985e26a78eda3653195d6dc28630f577f6640ef46153e50676e14710aaeec1f59f5a9e94c5fd3b190'),
    ('other', 'scrypt:32768:8:1$ok9Ftvu73pllNoYA$35ff222926e3574bded0c593196d94fd815ffcf71f21065985e26a78eda3653195d6dc28630f577f6640ef46153e50676e14710aaeec1f59f5a9e94c5fd3b190');

INSERT INTO todo (user_id, content, finished, schedule)
VALUES
    (1, 'today', 1, CURRENT_TIMESTAMP),
    (1, 'yesterday', 0, DATETIME('now', '-1 day')),
    (1, 'before yesterday', 0, DATETIME('now', '-2 day')),
    (1, 'tomorrow', 0, DATETIME('now', '+1 day'));