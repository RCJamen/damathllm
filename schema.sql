USE `damathllm`;

DROP TABLE IF EXISTS `game_history`;
CREATE TABLE IF NOT EXISTS `game_history` (
    id INT NOT NULL AUTO_INCREMENT,
    move_history JSON DEFAULT NULL,
    scores JSON DEFAULT NULL,
    winner VARCHAR(10) DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS `move_history` (
    id INT NOT NULL AUTO_INCREMENT,
    color VARCHAR(10) DEFAULT NULL,
    valid_moves JSON DEFAULT NULL,
    choice JSON DEFAULT NULL,
    reasoning VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (id)
);