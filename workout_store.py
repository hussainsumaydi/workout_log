import sqlite3


class Workout:
    def __init__(self, name, muscle, weight, workout_id=None):
        self.id = workout_id
        self.name = name
        self.muscle = muscle
        self.weight = weight

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'muscle': self.muscle,
            'weight': self.weight
        }


class WorkoutStore:
    def __init__(self, path='workouts.db'):
        self.conn = sqlite3.connect(path)
        sql = ('CREATE TABLE IF NOT EXISTS workout '
               '(id INTEGER PRIMARY KEY, '
               'name TEXT NOT NULL, '
               'muscle TEXT NOT NULL, '
               'weight INTEGER NOT NULL)')
        self.conn.execute(sql)

    def add(self, workout):
        sql = 'INSERT INTO workout (name, muscle, weight) VALUES (?, ?, ?)'
        values = (workout.name, workout.muscle, workout.weight)
        with self.conn:
            cur = self.conn.execute(sql, values)
        return cur.lastrowid

    def all(self):
        sql = 'SELECT id, name, muscle, weight FROM workout ORDER BY id'
        workouts = []
        for row_id, name, muscle, weight in self.conn.execute(sql).fetchall():
            workouts.append(Workout(name, muscle, weight, row_id))
        return workouts

    def filter_by_muscle(self, muscle):
        sql = 'SELECT id, name, muscle, weight FROM workout WHERE muscle = ? ORDER BY id'
        workouts = []
        for row_id, name, muscle_name, weight in self.conn.execute(sql, (muscle,)).fetchall():
            workouts.append(Workout(name, muscle_name, weight, row_id))
        return workouts

    def find(self, workout_id):
        sql = 'SELECT id, name, muscle, weight FROM workout WHERE id = ?'
        row = self.conn.execute(sql, (workout_id,)).fetchone()
        if row is None:
            return None
        return Workout(row[1], row[2], row[3], row[0])

    def update(self, workout):
        sql = 'UPDATE workout SET name = ?, muscle = ?, weight = ? WHERE id = ?'
        values = (workout.name, workout.muscle, workout.weight, workout.id)
        with self.conn:
            cur = self.conn.execute(sql, values)
        return cur.rowcount > 0

    def delete(self, workout_id):
        sql = 'DELETE FROM workout WHERE id = ?'
        with self.conn:
            cur = self.conn.execute(sql, (workout_id,))
        return cur.rowcount > 0

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    store = WorkoutStore('workouts.db')
    if not store.all():
        store.add(Workout('Bench Press', 'Chest', 60))
        store.add(Workout('Squat', 'Legs', 80))
        store.add(Workout('Lat Pulldown', 'Back', 50))

    for w in store.all():
        print(w.id, w.name, w.muscle, w.weight)
    store.close()