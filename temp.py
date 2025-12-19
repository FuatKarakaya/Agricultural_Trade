from database import execute_query

if __name__ == "__main__":
    # Reset the production_id sequence to the max value + 1
    result1 = execute_query(
        r"""
            SELECT setval('production_production_id_seq', 
                          (SELECT COALESCE(MAX(production_id), 0) + 1 FROM Production), 
                          false);
        """
    )
    print(f"Production sequence reset: {result1}")

    # Reset the production_value_id sequence to the max value + 1
    result2 = execute_query(
        r"""
            SELECT setval('production_value_production_value_id_seq', 
                          (SELECT COALESCE(MAX(production_value_id), 0) + 1 FROM Production_Value), 
                          false);
        """
    )
    print(f"Production_Value sequence reset: {result2}")

    print("Done! Sequences have been reset.")
