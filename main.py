from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return "pong"


# def main():
#     print("Hello from devops-engineer-from-scratch-project-313!")


# if __name__ == "__main__":
#     main()
