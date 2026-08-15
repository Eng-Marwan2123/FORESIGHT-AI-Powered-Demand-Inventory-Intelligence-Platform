from sqlalchemy import create_engine, text
import pandas as pd
# ==========================================================
# LOAD DATA based on the provided paths
# after collect in the data from the cSV files, we will save the data in the PostgreSQL database (Neon)
# ==========================================================
engine = create_engine(
    "postgresql+psycopg://neondb_owner:npg_L78TmfsVoiWY@ep-damp-rice-zapgu6fx-pooler.c-2.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

def save_data_to_db(df, table_name):

    df = df.copy()

    print(f"Saving {len(df)} rows to {table_name}...")

    df.to_sql(
        table_name,
        engine,
        schema="public",
        if_exists="append",
        index=False
    )

    print(f"Data saved to {table_name} successfully!")