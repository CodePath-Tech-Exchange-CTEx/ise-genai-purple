import streamlit as st
from google.cloud import bigquery
import uuid
import binascii
import os
import hashlib

def hash_password(password: str):
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return binascii.hexlify(salt).decode(), binascii.hexlify(derived_key).decode()


def verify_password(password: str, salt_hex: str, stored_hash_hex: str):
    salt = binascii.unhexlify(salt_hex.encode())
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return binascii.hexlify(derived_key).decode() == stored_hash_hex


def username_exists(username: str):
    query = """
    SELECT username
    FROM `joshua-stevenson-hu.team_purple_dataset.users_table`
    WHERE username = @username
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )

    rows = list(get_client().query(query, job_config=job_config).result())
    return len(rows) > 0


def create_user(name: str, username: str, password: str):
    name = name.strip()
    username = username.strip().lower()
    password = password.strip()

    if not name or not username or not password:
        return False, "All fields are required.", None

    try:
        if username_exists(username):
            return False, "Username already exists.", None

        salt, password_hash = hash_password(password)
        user_id = str(uuid.uuid4())

        query = """
        INSERT INTO `joshua-stevenson-hu.team_purple_dataset.users_table`
        (id, name, username, password_salt, password_hash)
        VALUES (@id, @name, @username, @password_salt, @password_hash)
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "STRING", user_id),
                bigquery.ScalarQueryParameter("name", "STRING", name),
                bigquery.ScalarQueryParameter("username", "STRING", username),
                bigquery.ScalarQueryParameter("password_salt", "STRING", salt),
                bigquery.ScalarQueryParameter("password_hash", "STRING", password_hash),
            ]
        )

        get_client().query(query, job_config=job_config).result()

        user = {
            "id": user_id,
            "name": name,
            "username": username,
        }
        return True, "Account created successfully.", user

    except Exception as e:
        print("Error", e)
        return False, "Something went wrong while creating the account.", None


def login_user(username: str, password: str):
    username = username.strip().lower()
    password = password.strip()

    if not username or not password:
        return False, "Please enter both username and password.", None

    query = """
    SELECT id, name, username, password_salt, password_hash
    FROM `joshua-stevenson-hu.team_purple_dataset.users_table`
    WHERE username = @username
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )

    try:
        rows = list(get_client().query(query, job_config=job_config).result())

        if not rows:
            return False, "Invalid username.", None

        user = rows[0]

        if not verify_password(password, user.password_salt, user.password_hash):
            return False, "Invalid password.", None

        return True, "Login successful.", {
            "id": user.id,
            "name": user.name,
            "username": user.username,
        }
    except Exception as e:
        print("Error", e)
        return False, "Something went wrong during login.", None

def set_user(user):
    st.session_state.authenticated = True
    st.session_state.current_user = user