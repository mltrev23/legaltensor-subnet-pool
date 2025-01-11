from .base_db_manager import BaseDBManager
from sqlalchemy import String, Integer, and_, Boolean, Table

class SubnetPoolDBManager(BaseDBManager):
    def __init__(self, db_url = "postgresql://user:password@localhost:5432/db_name"):
        super(self).__init__(db_url)

        # Define table schema
        self.task_approval_table = "validator_task_approval_apis"
        if not self.table_exists(self.task_approval_table):
            columns = {
                "uid": Integer, 
                "hotkey": String,
                "api_url": String, 
                "status": Boolean
            }

            # Create the table
            self.create_table(self.task_approval_table, columns)
    
    def update_endpoint(self, uid, hotkey, api_url):
        table = Table(self.task_approval_table, self.metadata, autoload_with=self.engine)
        condition = table.hotkey == hotkey
        result = self.query_data(self.task_approval_table, condition)

        if result is None:
            self.insert_data(self.task_approval_table, {
                'uid': uid,
                'hotkey': hotkey,
                'api_url': api_url,
                'status': True
            })
        else:
            self.update_data(self.task_approval_table, {
                'uid': uid,
                'hotkey': hotkey,
                'api_url': api_url,
                'status': True
            }, condition)
            
    def mark_down_endpoint(self, uid, hotkey, api_url):
        table = Table(self.task_approval_table, self.metadata, autoload_with=self.engine)
        condition = table.hotkey == hotkey
        result = self.query_data(self.task_approval_table, condition)

        if result is not None:
            self.update_data(self.task_approval_table, {'status': False}, condition)
            return True
            
        return False
    
    def get_endpoint_data(self, uid):
        table = Table(self.task_approval_table, self.metadata, autoload_with = self.engine)
        condition = table.uid = uid
        result = self.query_data(self.task_approval_table, condition)

        if result:
            return result
        
        return None

    def __close__(self):
        delete_conditions = and_(self.task_approval_table.c.id == 1)
        self.delete_data(self.task_approval_table, delete_conditions)

        # Close the connection
        self.close()

    