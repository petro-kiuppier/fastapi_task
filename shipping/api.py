from fastapi import FastAPI, status, Response
from .schemas import Transaction, ProcessedTransaction, CarriersList, Carrier
from .transactions import transaction_processor


def build_app():
    app = FastAPI()

    @app.get("/hello")
    async def hello():
        return {"message": "Hello!"}

    @app.post("/transactions", response_model=ProcessedTransaction)
    async def post_transactions(transaction: Transaction):
        return transaction_processor.process_transaction(dict(transaction))

    @app.get("/carriers", response_model=CarriersList)
    async def get_carriers():
        carriers = transaction_processor.get_carriers()
        res = {"carriers": []}
        for carrier in carriers:
            res['carriers'].append(carrier.to_json())

        return res

    @app.post("/carriers", status_code=status.HTTP_204_NO_CONTENT)
    async def post_carriers(carrier: Carrier):
        stored_carrier = transaction_processor.get_carrier(carrier.code)
        stored_carrier.enabled = carrier.enabled

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app
