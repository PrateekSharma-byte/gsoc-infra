import os
import sqlite3

DEFAULT_DB_PATH = 'parametric_results/simulations.db'


def init_db(db_name=DEFAULT_DB_PATH):
    """Database aur Table banata hai agar nahi hai, aur performance index add karta hai."""
    db_dir = os.path.dirname(db_name)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                permittivity REAL,
                peak_amplitude REAL,
                arrival_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Indexing for faster analytical lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_permittivity 
            ON results (permittivity)
        ''')
        conn.commit()


def save_result(
    eps, peak, arrival, db_name=DEFAULT_DB_PATH
):
    """Ek single simulation ka data SQL mein save karta hai."""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO results (permittivity, peak_amplitude, arrival_time)
            VALUES (?, ?, ?)
        ''',
            (eps, peak, arrival),
        )
        conn.commit()
    print(f'💾 Data for Eps {eps} saved to SQLite database.')


def save_results_batch(data_list, db_name=DEFAULT_DB_PATH):
    """Batch insert lists of tuples (eps, peak, arrival) for optimized write speed."""
    if not data_list:
        return

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            '''
            INSERT INTO results (permittivity, peak_amplitude, arrival_time)
            VALUES (?, ?, ?)
        ''',
            data_list,
        )
        conn.commit()
    print(
        f'💾 Batch insert completed: {len(data_list)} simulation records saved.'
    )


def fetch_results(limit=100, db_name=DEFAULT_DB_PATH):
    """Retrieve recent simulation results."""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT id, permittivity, peak_amplitude, arrival_time, timestamp 
            FROM results 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''',
            (limit,),
        )
        return cursor.fetchall()
