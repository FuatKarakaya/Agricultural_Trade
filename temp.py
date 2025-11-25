from database import execute_query

if __name__ == "__main__":

    r = execute_query('''COPY staging_landuse FROM '/filtered_landuse_area_final.csv' DELIMITER ',' CSV HEADER;''')
    print(r)