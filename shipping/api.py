from fastapi import FastAPI


def build_app():
    app = FastAPI()

    @app.get("/hello")
    async def hello():
        return {"message": "Hello!"}

    return app
