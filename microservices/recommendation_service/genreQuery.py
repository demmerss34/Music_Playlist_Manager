import sqlite3
import io
import os


def createConnection():
    """
    Create a database if not already created, restore from backup
    if needed
    """
    db_file = 'songsData.db'
    backup_file = 'songsData_dump.sql'
    
    # Check if database file exists
    if not os.path.exists(db_file) and os.path.exists(backup_file):
        print(f"Database '{db_file}' not found. Restoring from backup...")
        
        # Create a new database
        connection = sqlite3.connect(db_file)
        
        # Read SQL statements from backup file
        with open(backup_file, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script to restore the database
        connection.executescript(sql_script)
        connection.commit()
        print("Database restored successfully from backup!")
    else:
        # Just connect to the existing database
        connection = sqlite3.connect(db_file)
        print("Connection established successfully")
    
    return connection


def closeConnection(connection):
    connection.close()


def createCursor(connection):
    cursor = connection.cursor()
    return cursor


def backupDB(connection):
    with io.open('songData_dump.sql', 'w') as p:

        for line in connection.iterdump():
            p.write('%s\n' % line)
    print("Backup performed succesfully!") 

def returnByGenre(connection, genre, table="songs"):
    cur = connection.cursor()
    cur.execute(f"""
    SELECT *
    FROM(
        SELECT *
        FROM {table}
        WHERE genre = ?
        ORDER BY popularity DESC
        LIMIT 200
        )
    ORDER BY RANDOM()
    LIMIT 10;    
        """, (genre,))
    result = cur.fetchall()
    result_arr = list(result)
    return result_arr


def formartDict(connection, arr):
    result = []
    for row in arr:
        record = {
            "title": row[1],
            "artist": row[0],
            "genre": row[3],
            "popularity": row[2]}
        result.append(record)
    results = {"recommendations": result}

    return results


def returnAll(connection, table):
    cur = connection.cursor()
    cur.execute(f'SELECT * FROM {table};')
    result = cur.fetchall()
    return result


connection = createConnection()
#cursor = createCursor(connection)
#backupDB(connection)
