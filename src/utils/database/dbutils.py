import psycopg2
import dbcreds


def connect():
    """
    Creates a connection to the Postgres database specified in the credentials
    file dbcreds.py

    Returns:
        Psycopg.connection: The database connection
    """

    config = {
        'database': dbcreds.database,
        'user': dbcreds.user,
        'password': dbcreds.password,
        'host': dbcreds.host,
        'port': dbcreds.port
    }

    return psycopg2.connect(**config)
