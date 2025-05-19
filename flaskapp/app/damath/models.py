from app import mysql
import json

class GameHistory(object):

    def __init__(self, move_history = None, scores = None, winner = None):
        self.move_history = move_history
        self.scores = scores
        self.winner = winner

    def add(self):
        cursor = mysql.connection.cursor()
        sql = 'INSERT INTO game_history (move_history, scores, winner) VALUES (%s, %s, %s)'
        cursor.execute(sql, (self.move_history, json.dumps(self.scores), self.winner))
        mysql.connection.commit()

    @classmethod
    def all(cls):
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM game_history"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    @classmethod
    def get(cls, id):
        cursor = mysql.connection.cursor()
        sql = f"SELECT * FROM game_history WHERE id = '{id}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    
    @classmethod
    def get_winrate(cls, player):
        cursor = mysql.connection.cursor()
        sql = f"SELECT ROUND(100 * SUM(CASE WHEN winner = 'r' THEN 1 ELSE 0 END) / COUNT(*), 2) AS {player+'_winrate'} FROM game_history;"
        result = cursor.fetchone()
        return result    

class MoveHistory(object):
    def __init__(self, color = None, valid_moves = None, choice = None, reasoning = None):
        self.color = color
        self.valid_moves = valid_moves
        self.choice = choice
        self.reasoning= reasoning

    def add(self):
        cursor = mysql.connection.cursor()
        sql = 'INSERT INTO move_history (color, valid_moves, choice, reasoning) VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, (self.color, json.dumps(self.valid_moves), json.dumps(self.choice), self.reasoning))
        mysql.connection.commit()

    @classmethod
    def all(cls):
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM move_history"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    @classmethod
    def get(cls, id):
        cursor = mysql.connection.cursor()
        sql = f"SELECT * FROM move_history WHERE id = '{id}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
