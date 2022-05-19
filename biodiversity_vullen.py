#!/usr/bin/python3
import psycopg2
import sys
 
def main():
    #connectie maken met de database en postgres
    conn_string = "host='localhost' dbname='s1101573_db' user='s1101573' password='s1101573'"
    print("Connecting to database\n	->%s" % (conn_string))
    conn = psycopg2.connect(conn_string)
    	
    # cursor aangemaakt om SQL commando's uit te voeren
    cursor = conn.cursor()
    print("Connected!\n")

    # drop de tabellen als ze al bestaan
    cursor.execute("""DROP TABLE IF EXISTS status CASCADE;""")
    cursor.execute("""DROP TABLE IF EXISTS taxonomy CASCADE;""")
    cursor.execute("""DROP TABLE IF EXISTS subtax CASCADE;""")
    cursor.execute("""DROP TABLE IF EXISTS biological_entity CASCADE;""")
    cursor.execute("""DROP TABLE IF EXISTS county CASCADE;""")
    cursor.execute("""DROP TABLE IF EXISTS sightings CASCADE;""")
    print("gedropd")

    # creeer de tabellen
    sql = """
    CREATE TABLE status (
        description VARCHAR PRIMARY KEY);"""
    cursor.execute(sql)
    conn.commit()

    sql = """
    CREATE TABLE taxonomy (
        tax_name VARCHAR PRIMARY KEY);"""
    cursor.execute(sql)
    conn.commit()

    sql = """
    CREATE TABLE subtax (
        subtax_name VARCHAR PRIMARY KEY,
        tax_name VARCHAR REFERENCES taxonomy(tax_name));"""
    cursor.execute(sql)
    conn.commit()

    sql = """
    CREATE TABLE biological_entity (
        scientific_name VARCHAR PRIMARY KEY,
        common_name VARCHAR,
        subtax_name VARCHAR REFERENCES subtax(subtax_name),
        description VARCHAR REFERENCES status(description));"""
    cursor.execute(sql)
    conn.commit()

    sql = """
    CREATE TABLE county (
        county_name VARCHAR PRIMARY KEY);"""
    cursor.execute(sql)
    conn.commit()

    sql = """
    CREATE TABLE sightings (
        county_name VARCHAR REFERENCES county(county_name),
        scientific_name VARCHAR REFERENCES biological_entity(scientific_name),
        year INT,
        PRIMARY KEY(county_name, scientific_name));"""
    cursor.execute(sql)
    conn.commit()
    print("aangemaakt")
    
    infile = open('biodiversity.tsv', 'r')
    content = infile.readlines()
    infile.close()
    
    status_list = []
    tax_group_list = []
    county_list = []
    sighting_list = []
    tax_subgroup_dict = {}
    scientific_name_dict = {}
    
    for line in content[1:]:
        splitlist = line.strip().split('\t')
        county = splitlist[0]
        scientific_name = splitlist[1]
        common_name = splitlist[2]
        if splitlist[3]!='NA':
            year = int(splitlist[3])
        else:
            year = None
        tax_subgroup = splitlist[4]
        tax_group = splitlist[5]
        status = splitlist[6]
        status_list.append(status)
        tax_group_list.append(tax_group)
        county_list.append(county)
        sighting_list.append([county, scientific_name, year])
        if tax_subgroup not in tax_subgroup_dict:
            tax_subgroup_dict[tax_subgroup] = tax_group
        if scientific_name not in scientific_name_dict:
            scientific_name_dict[scientific_name] = [common_name, tax_subgroup, status]
        
    # vul de tabel 'status':        
    sql = """
    INSERT INTO status VALUES (%s)"""
    unique_status = list(set(status_list))
    for status in unique_status:
        cursor.execute(sql, [status])

    # vul de tabel 'taxonomy':        
    sql = """
    INSERT INTO taxonomy VALUES (%s)"""
    unique_tax_group = list(set(tax_group_list))
    for tax_group in unique_tax_group:
        cursor.execute(sql, [tax_group])

    # vul de tabel 'county':        
    sql = """
    INSERT INTO county VALUES (%s)"""
    unique_county = list(set(county_list))
    for county in unique_county:
        cursor.execute(sql, [county])

    # vul de tabel 'subtax':
    sql = """
    INSERT INTO subtax VALUES (%s, %s)"""
    for subgroup in tax_subgroup_dict:
        cursor.execute(sql, [subgroup, tax_subgroup_dict[subgroup]])        

    # vul de tabel 'biological_entity':
    sql = """
    INSERT INTO biological_entity VALUES (%s, %s, %s, %s)"""
    for county_name in scientific_name_dict:
        cursor.execute(sql, [county_name] + scientific_name_dict[county_name])
        
    # vul de tabel 'sightings':
    sql = """
    INSERT INTO sightings VALUES (%s, %s, %s)"""
    for sighting in sighting_list:
        cursor.execute(sql, sighting)       
  
    conn.commit()    
    conn.close()

 
if __name__ == "__main__":
	main()

