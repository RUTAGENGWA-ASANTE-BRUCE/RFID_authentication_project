#!/usr/bin/env python3
import serial
import os
import sqlite3


def create_database():
    db_file = os.path.join(os.path.dirname(__file__), 'RFID.db')
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authorised_cards (
            entry INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id TEXT
        )
    ''')

    connection.commit()
    connection.close()


def search_database(card_id):
    db_file = os.path.join(os.path.dirname(__file__), 'RFID.db')
    with sqlite3.connect(db_file) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM authorised_cards WHERE card_id=?", (card_id,))
        result = cursor.fetchone()
    return result is not None


def count_cards():
    db_file = os.path.join(os.path.dirname(__file__), 'RFID.db')
    with sqlite3.connect(db_file) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM authorised_cards")
        result = cursor.fetchone()
        return result[0]



def insert_card(card_id):
    db_file = os.path.join(os.path.dirname(__file__), 'RFID.db')
    with sqlite3.connect(db_file) as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO authorised_cards (card_id) VALUES (?)", (str(card_id),))
        connection.commit()


def truncate_db():
    db_file = os.path.join(os.path.dirname(__file__), 'RFID.db')
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM authorised_cards")
    connection.commit()
    connection.close()

def initialize_database_with_cards(cards):
    # Create the database
    create_database()

    # Insert some initial cards
    for card in cards:
        insert_card(card)


def initialize_database_if_not_exist():
     # Check if the database file already exists
    db_file = os.path.join(os.path.dirname(__file__), 'RFID.db')
    if os.path.exists(db_file):
        return
    else:
        cards = ['card1', 'card2', 'card3']  # Add the initial cards for your organization
        initialize_database_with_cards(cards)

ser = serial.Serial(
        port='COM7', #plz change this according to your port number
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

ser.flush()
if __name__ == '__main__':
    initialize_database_if_not_exist();
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            if(search_database(line)):
                print('UID with id: '+line+" is registered")
                ser.write(b'A')
                
            else:
                ser.write(b'D')
                print('UID with id: '+line+" is not registered")
