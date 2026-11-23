import json
import socket
import threading
from urllib.error import URLError
from urllib.request import urlopen

URL = 'http://127.0.0.1:5050/workouts'
REPORT_FILE = 'workout_report.txt'
saved = False


def write_report(workouts):
    global saved
    try:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write('WORKOUT LOG REPORT\n')
            f.write('=' * 35 + '\n')
            if not workouts:
                f.write('No workouts found.\n')
            else:
                for w in workouts:
                    line = (f"ID: {w['id']} | Exercise: {w['name']} | "
                            f"Muscle: {w['muscle']} | Weight: {w['weight']} kg\n")
                    f.write(line)
                f.write('=' * 35 + '\n')
                f.write(f'Total workouts: {len(workouts)}\n')
        saved = True
    except OSError as error:
        print('File error:', error)
        saved = False


def main():
    try:
        with urlopen(URL, timeout=5) as reply:
            data = json.loads(reply.read().decode('utf-8'))
    except (URLError, socket.timeout) as error:
        print('Could not connect to Flask server:', error)
        return

    workouts = data.get('workouts', [])

    worker = threading.Thread(target=write_report, args=(workouts,))
    worker.start()
    worker.join()

    if saved:
        print('Report saved successfully to', REPORT_FILE)
    else:
        print('Failed to save report.')


if __name__ == '__main__':
    main()