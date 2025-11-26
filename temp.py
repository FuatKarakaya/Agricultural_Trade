from database import execute_query

if __name__ == "__main__":

    X = execute_query(
        r"""ALTER TABLE production_value
            ADD CONSTRAINT production_value_production_id_fkey 
            FOREIGN KEY (production_id) 
            REFERENCES production(production_id)
            ON DELETE CASCADE;
        """
    )

    print(X)
