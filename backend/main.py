from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import io

# Load environment variables
load_dotenv()

app = FastAPI(title="Future Sight API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChartRequest(BaseModel):
    prompt: str

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
        print(f"Filename: {file.filename}")
        print(f"Content type: {file.content_type}")
        # Check if file is CSV or Excel
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
        print("File type check passed")

        # Read file content
        content = await file.read()
        print(f"File content length: {len(content)}")

        # Parse based on file extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(content))
        print(f"Dataframe shape: {df.shape}")

        # Convert DataFrame to dictionary
        df_dict = df.to_dict(orient='records')

        # Prepare response data
        response_data = {
            "message": "File uploaded successfully",
            "columns": df.columns.tolist(),
            "sample_data": df.head(5).to_dict('records'),
            "row_count": len(df),
            "data": df_dict  # Include the data
        }
        return response_data

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    datasetInfo = request.datasetInfo
    if datasetInfo is None:
        raise HTTPException(status_code=400, detail="No data uploaded. Please upload a file first.")

    try:
        # Get Gemini API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Extract dataset information
        columns = datasetInfo['columns']
        data_types = {}
        for col in columns:
            data_types[col] = 'unknown'  # Since we don't have specific datatypes, mark as unknown
        sample_data = datasetInfo['sample_data']

        # Construct the prompt for the AI model
        prompt = f"""You are a data analysis assistant. The user has uploaded a dataset and is asking questions about it. Use the following information to answer the user's question as accurately as possible.\n\n        Dataset columns: {columns}\n        Data types: {data_types}\n        Sample data: {sample_data}\n\n        User question: {request.message}"""

        # Call Gemini API
        response = model.generate_content(prompt)

        # Extract and return the AI-generated response
        ai_response = response.text.strip()
        return {
            "message": ai_response
        }

    except Exception as e:
        print(f"Error generating chat response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating chat response: {str(e)}")

@app.post("/generate-chart", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    # global uploaded_data - no longer needed
    # uploaded_data = request.datasetInfo #Not the right type
    #global uploaded_data

    #if uploaded_data is None:
    #    raise HTTPException(status_code=400, detail="No data uploaded. Please upload a file first.")

    try:
        # Get Gemini API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Prepare data summary for AI
        #columns = uploaded_data.columns.tolist()
        #data_types = uploaded_data.dtypes.to_dict()
        #sample_data = uploaded_data.head(3).to_dict('records')

        #prompt = f"""You are a data visualization expert. Given a dataset and a user's request, \n        #generate Python code using matplotlib and pandas to create a chart or give future predictions based on the data and user request if the user request is related to future predictions\n        #generate the predictions in text or requested fromat.\n        #\n        #Dataset columns: {columns}\n        #Data types: {data_types}\n        #Sample data: {sample_data}\n        #\n        #User request: {request.prompt}\n        #\n        #Requirements:\n        #1. Use matplotlib for plotting
        #2. The dataframe is already loaded as 'df'
        #3. Return ONLY the Python code, no explanations or markdown
        #4. Include proper imports (matplotlib.pyplot as plt, pandas as pd)
        #5. Use plt.show() at the end
        #6. Make the chart visually appealing with proper labels, titles, and colors
        #7. Handle missing data appropriately
        #8. Choose the most appropriate chart type for the data and request"""

        # Call Gemini API
        #response = model.generate_content(prompt)
        # the model isn't used in this version of code so ignoring for now

        return {
                "success": False,
                "chart_image": "",
                "message": "This feature is not yet implemented due to refactoring for chat interface!"
            }

        # Get AI-generated Python code
        #ai_response = response.text.strip()

        # Execute the Python code
        #try:
        #    # Create a safe execution environment
        #    exec_globals = {
        #        'df': uploaded_data,
        #        'pd': pd,
        #        'plt': __import__('matplotlib.pyplot'),
        #        'np': __import__('numpy')
        #    }

        #    # Execute the generated code
        #    exec(ai_response, exec_globals)

        #    # Get the current figure
        #    import matplotlib.pyplot as plt
        #    fig = plt.gcf()

        #    # Save the chart as base64
        #    import io
        #    import base64

        #    buffer = io.BytesIO()
        #    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        #    buffer.seek(0)

        #    # Convert to base64
        #    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        #    plt.close(fig)  # Clean up

        #    return {
        #        "success": True,
        #        "chart_image": chart_base64,
        #        "message": "Chart generated successfully"
        #    }

        #except Exception as e:
        #    # Fallback: create a simple chart
        #    import matplotlib.pyplot as plt
        #    import io
        #    import base64

        #    fig, ax = plt.subplots(figsize=(10, 6))

        #    if len(uploaded_data.columns) >= 2:
        #        x_col = uploaded_data.columns[0]
        #        y_col = uploaded_data.columns[1]

        #        # Create a simple bar chart
        #        ax.bar(range(len(uploaded_data)), uploaded_data[y_col].fillna(0))
        #        ax.set_xlabel(x_col)
        #        ax.set_ylabel(y_col)
        #        ax.set_title(f"Chart for: {request.prompt}")

        #    # Rotate x-axis labels if too many
        #    if len(uploaded_data) > 10:
        #        ax.tick_params(axis='x', rotation=45)
        #    else:
        #        # Simple count chart
        #        ax.hist(uploaded_data.iloc[:, 0].dropna(), bins=20)
        #        ax.set_xlabel(uploaded_data.columns[0])
        #        ax.set_ylabel('Count')
        #        ax.set_title(f"Chart for: {request.prompt}")

        #    plt.tight_layout()

        #    # Save as base64
        #    buffer = io.BytesIO()
        #    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        #    buffer.seek(0)

        #    # Convert to base64
        #    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        #    plt.close(fig)  # Clean up

        #    return {
        #        "success": True,
        #        "chart_image": chart_base64,
        #        "message": f"Chart generated (fallback mode): {str(e)}"
        #    }

    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
