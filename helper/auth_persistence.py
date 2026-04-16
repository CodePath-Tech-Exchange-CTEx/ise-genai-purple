import uuid
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery


def get_client():
    return bigquery.Client()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_remember_token(user_id: str, remember_me: bool):
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)

    expiry_days = 365 if remember_me else 2
    expires_at = datetime.now(timezone.utc) + timedelta(days=expiry_days)

    query = """
    INSERT INTO `joshua-stevenson-hu.team_purple_dataset.remember_tokens`
    (id, user_id, token_hash, expires_at)
    VALUES (@id, @user_id, @token_hash, @expires_at)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("token_hash", "STRING", token_hash),
            bigquery.ScalarQueryParameter("expires_at", "TIMESTAMP", expires_at),
        ]
    )

    get_client().query(query, job_config=job_config).result()

    return raw_token, expires_at


def get_user_from_remember_token(raw_token: str):
    token_hash = hash_token(raw_token)

    query = """
    SELECT u.id, u.name, u.username
    FROM `joshua-stevenson-hu.team_purple_dataset.remember_tokens` t
    JOIN `joshua-stevenson-hu.team_purple_dataset.users_table` u
      ON t.user_id = u.id
    WHERE t.token_hash = @token_hash
      AND t.expires_at > CURRENT_TIMESTAMP()
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("token_hash", "STRING", token_hash),
        ]
    )

    rows = list(get_client().query(query, job_config=job_config).result())

    if not rows:
        return None

    row = rows[0]
    return {
        "id": row.id,
        "name": row.name,
        "username": row.username,
    }


def delete_remember_token(raw_token: str):
    token_hash = hash_token(raw_token)

    query = """
    DELETE FROM `joshua-stevenson-hu.team_purple_dataset.remember_tokens`
    WHERE token_hash = @token_hash
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("token_hash", "STRING", token_hash),
        ]
    )

    get_client().query(query, job_config=job_config).result()