from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import io
import re
import base64
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

app = FastAPI(title="Future Sight API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChartRequest(BaseModel):
    prompt: str
    datasetInfo: dict

class ChartResponse(BaseModel):
    success: bool
    chart_image: str
    message: str

class ChatRequest(BaseModel):
    message: str
    datasetInfo: dict
class ChatResponse(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Future Sight API is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
        
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        df_dict = df.to_dict(orient='records')

        return {
            "message": "File uploaded successfully",
            "columns": df.columns.tolist(),
            "sample_data": df.head(5).to_dict('records'),
            "row_count": len(df),
            "data": df_dict
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    datasetInfo = request.datasetInfo
    if datasetInfo is None:
        raise HTTPException(status_code=400, detail="No data uploaded. Please upload a file first.")

    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("Gemini API key not configured")
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        columns = datasetInfo['columns']
        # Include up to 10 rows of sample data for context
        sample_data = datasetInfo.get('sample_data', [])
        if not sample_data:
            # fallback: use first 10 rows from 'data'
            sample_data = datasetInfo.get('data', [])[:10]
        sample_data_json = json.dumps(sample_data, indent=2)

        prompt = (
            "You are a data insights expert. "
            "A user has uploaded a dataset. Your task is to provide clear, concise, and actionable insights, summaries, or analysis about the data based on the user's question or request. "
            "Do not generate Python code or charts. "
            f"Dataset columns are: {', '.join(columns)}.\n"
            f"Here are some sample rows from the dataset:\n{sample_data_json}\n"
            f"User request: '{request.message}'"
        )

        response = model.generate_content(prompt)
        ai_response = getattr(response, "text", "")
        if not ai_response or not isinstance(ai_response, str):
            print("AI did not return a valid response.")
            raise HTTPException(status_code=500, detail="AI did not return a valid response.")

        ai_response = ai_response.strip()
        print(f"AI Chat Response: {ai_response}")

        return {"message": ai_response}

    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        return {"message": f"Sorry, I encountered an error processing your request: {str(e)}"}

@app.post("/generate-chart", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    if request.datasetInfo is None:
        raise HTTPException(status_code=400, detail="No data uploaded. Please upload a file first.")

    ai_response = ""
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')  # Use 2.0-flash everywhere

        df = pd.DataFrame.from_records(request.datasetInfo['data'])
        columns = request.datasetInfo['columns']
        user_visual_request = request.prompt
        # Step 1: Initial Code Generation with explicit aggregation instructions
        generation_prompt = (
            "You are a data visualization assistant. "
            "A user has uploaded a dataset, which is already loaded as the pandas DataFrame df. "
            "Your task is to generate Python code using matplotlib and pandas to create the requested chart. "
            "**Crucially, if the user's request implies aggregating data (e.g., 'total sales per category', 'units sold of every region'), you MUST use appropriate pandas functions like `groupby()` and aggregation methods (`sum()`, `mean()`, etc.) before plotting.** "
            "Do not use pd.read_csv. Use descriptive labels and titles. "
            "Ensure the code ends with plt.show(). Return ONLY Python code, no text or markdown. "

            f"Dataset columns: {', '.join(columns)}. "
            f"User request: '{user_visual_request}'."
        )

        response = model.generate_content(generation_prompt)
        raw_response = getattr(response, "text", "").strip()
        initial_code = re.sub(r'```python\n|```', '', raw_response)
        print(f"Initial AI Code: {initial_code}")

        # Step 2: Code Review and Correction with explicit aggregation check
        review_prompt = (
            "You are a Python code reviewer. Your task is to check if the provided Python code correctly implements the user's visualization request given the dataset's columns. "
            "The code operates on a pandas DataFrame named 'df'. "
            f"Dataset columns: {', '.join(columns)}. "
            f"User request: '{user_visual_request}'.\n\n"
            f"Python code to review:\n{initial_code}\n\n"
            "Does this code correctly generate the chart the user asked for? Pay close attention to column names, chart types, and **whether any necessary data aggregation (like `groupby().sum()`) was performed correctly according to the user's request.** "
            "If the code is correct, return it as is. If it is incorrect, fix it and return only the corrected Python code. "
            "Do not add any explanations, comments, or markdown."
        )

        review_response = model.generate_content(review_prompt)
        raw_reviewed_response = getattr(review_response, "text", "").strip()
        final_code = re.sub(r'```python\n|```', '', raw_reviewed_response)
        ai_response = final_code
        print(f"Final (Reviewed) AI Code: {final_code}")

        # Step 3: Execution of the final, reviewed code
        if not final_code or len(final_code) < 10:
            raise Exception("AI did not return valid Python code for chart generation.")

        exec_globals = {'df': df, 'pd': pd, 'plt': plt}
        try:
            exec(final_code, exec_globals)
        except Exception as exec_err:
            print(f"Error executing AI code: {exec_err}")
            raise Exception(f"Error executing AI code: {exec_err}")

        fig = plt.gcf()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return {
            "success": True,
            "chart_image": chart_base64,
            "message": "Chart generated successfully"
        }

    except Exception as e:
        print(f"Error during chart generation: {str(e)}")
        # Fallback chart generation
        df = pd.DataFrame.from_records(request.datasetInfo['data'])
        fig, ax = plt.subplots(figsize=(10, 6))

        if len(df.columns) >= 2:
            x_col, y_col = df.columns[0], df.columns[1]
            ax.bar(df[x_col], df[y_col].fillna(0))
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"Fallback Chart for: {request.prompt}")
        else:
            ax.hist(df.iloc[:, 0].dropna(), bins=20)
            ax.set_xlabel(df.columns[0])
            ax.set_ylabel('Count')
            ax.set_title(f"Fallback Chart for: {request.prompt}")

        if len(df) > 10:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return {
            "success": True,
            "chart_image": chart_base64,
            "message": f"Chart generated (fallback mode): {str(e)} - AI Code: {ai_response}"
        }
