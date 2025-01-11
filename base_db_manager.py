from sqlalchemy import create_engine, Column, Integer, String, Text, Table, MetaData, inspect
from sqlalchemy.orm import sessionmaker, scoped_session

class BaseDBManager:
    def __init__(self, db_url):
        """
        Initialize the database manager with SQLAlchemy.
        """
        self.engine = create_engine(db_url)
        self.metadata = MetaData(bind=self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        print("Database connection established.")
    
    def table_exists(self, table_name):
        # Create an inspector
        inspector = inspect(self.engine)

        # Check if the table exists
        return table_name in inspector.get_table_names()

    def create_table(self, table_name, columns):
        """
        Dynamically create a table with the given name and columns.
        """
        columns_list = [Column(name, dtype) for name, dtype in columns.items()]
        table = Table(table_name, self.metadata, *columns_list)
        table.create(checkfirst=True)  # Creates the table if it does not exist
        print(f"Table '{table_name}' created or already exists.")

    def insert_data(self, table_name, data):
        """
        Insert data into the specified table.
        """
        with self.Session() as session:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            insert_stmt = table.insert().values(**data)
            session.execute(insert_stmt)
            session.commit()
            print(f"Data inserted into table '{table_name}'.")

    def query_data(self, table_name, conditions=None):
        """
        Query data from the specified table with optional conditions.
        """
        with self.Session() as session:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            query = table.select()
            if conditions:
                query = query.where(conditions)
            results = session.execute(query).fetchall()
            return results

    def update_data(self, table_name, updates, conditions):
        """
        Update data in the specified table.
        """
        with self.Session() as session:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            update_stmt = table.update().values(**updates).where(conditions)
            session.execute(update_stmt)
            session.commit()
            print(f"Data updated in table '{table_name}'.")

    def delete_data(self, table_name, conditions):
        """
        Delete data from the specified table.
        """
        with self.Session() as session:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            delete_stmt = table.delete().where(conditions)
            session.execute(delete_stmt)
            session.commit()
            print(f"Data deleted from table '{table_name}'.")

    def close(self):
        """
        Dispose of the database connection and engine.
        """
        self.engine.dispose()
        print("Database connection closed.")
