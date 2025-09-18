from fastapi.middleware.cors import CORSMiddleware

def add_cors(app): # type: ignore
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development, allow all. Restrict in production.
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
