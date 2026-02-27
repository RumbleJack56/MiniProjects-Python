# /// script
# requires-python = ">=3.12"
# dependencies = [
#  "fastapi",
#  "uvicorn",
# ]
# ///
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def health():
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test:app", host="0.0.0.0", port=8000)