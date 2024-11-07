from text_to_sql import get_gemini_response
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn


load_dotenv()

    
app = FastAPI(title='EmpowerHub', version='0.0.1')


@app.post('/get-prompt')
async def get_text_to_sql_response(query: str):
    # query = {
    #     "question" : "Get all the users"
    # }
    return get_gemini_response(query)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8080)