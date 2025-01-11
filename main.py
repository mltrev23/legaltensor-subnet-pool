import os
import bittensor as bt
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from bittensor_wallet import Keypair
from .subnet_pool_db_manager import SubnetPoolDBManager

def get_subnet_pool_db_url():
    load_dotenv()

    pg_addr = os.environ.get('POSTGRES_ADDRESS')
    pg_port = os.environ.get('POSTGRES_PORT')

    pg_dbname = os.environ.get('SUBNET_POOL_PG_DB')
    pg_username = os.environ.get('SUBNET_POOL_PG_USERNAME')
    pg_password = os.environ.get('SUBNET_POOL_PG_PASSWORD')

    return f'postgresql://{pg_username}:{pg_password}@{pg_addr}:{pg_port}/{pg_dbname}'

class EndpointRequest(BaseModel):
    uid: int
    hotkey: str
    api_url: str
    signature: str

class HealthyEndpointsRequest(BaseModel):
    uids: List[int]

# Contribution API Server
class SubnetPool:
    def __init__(self, netuid = 205, network = 'test'):
        self.app = FastAPI()
        self.setup_routes()

        self.netuid = netuid
        self.network = network
        self.metagraph = bt.metagraph(netuid, network = network)

        self.subnet_pool_db = SubnetPoolDBManager(db_url = get_subnet_pool_db_url())

    def setup_routes(self):
        def validate_request(data: EndpointRequest):
            # Check if UID is within the valid range
            if data.uid < 0 or data.uid >= len(self.metagraph.uids):
                raise ValueError(f"UID {data.uid} is out of range for the metagraph with netuid {self.netuid}.")

            # Check if the provided hotkey matches the hotkey in the metagraph for the given UID
            if data.hotkey != self.metagraph.hotkeys[data.uid]:
                raise ValueError(f"Hotkey {data.hotkey} does not match the hotkey for UID {data.uid}.")

            # Verify the digital signature
            message = f"{data.uid}-{data.hotkey}-{data.api_url}"
            keypair = Keypair(ss58_address=data.hotkey)
            if not keypair.verify(message, data.signature, data.hotkey):
                raise ValueError("Invalid signature.")
            
            return True

        @self.app.post("/register-endpoint")
        async def register_endpoint(data: EndpointRequest):
            if validate_request(data):
                self.subnet_pool_db.update_endpoint(data.uid, data.hotkey, data.api_url)
                return {"message": "Endpoint registered successfully."}

        @self.app.post("/down-endpoint")
        async def down_endpoint(data: EndpointRequest):
            if validate_request(data):
                self.subnet_pool_db.mark_down_endpoint(data.uid, data.hotkey, data.api_url)
                return {"message": "Endpoint marked as down."}

        @self.app.post("/healthy-endpoints")
        async def get_healthy_endpoints(data: HealthyEndpointsRequest):
            healthy_endpoints = []

            for uid in data.uids:
                endpoint_data = self.subnet_pool_db.get_endpoint_data(uid)
                if endpoint_data and endpoint_data.status:
                    healthy_endpoints.append(endpoint_data.api_url)

            return healthy_endpoints

if __name__ == "__main__":
    import uvicorn

    # Initialize the SubnetPool app
    subnet_pool = SubnetPool()

    # Run the FastAPI application
    uvicorn.run(subnet_pool.app, host="0.0.0.0", port=20501)
