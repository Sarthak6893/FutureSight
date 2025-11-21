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
import chardet

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

def restore_dataframe_types(df, datasetInfo):
    """Helper function to restore DataFrame data types from datasetInfo"""
    if 'column_types' in datasetInfo:
        column_types = datasetInfo['column_types']
        for col, dtype_str in column_types.items():
            if col in df.columns:
                try:
                    # Convert string dtype to actual dtype
                    if 'int' in dtype_str:
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                    elif 'float' in dtype_str:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    elif 'bool' in dtype_str:
                        df[col] = df[col].astype('bool')
                    elif 'datetime' in dtype_str:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    # If conversion fails, keep original type
                    pass
    return df

@app.get("/")
async def root():
    return {"message": "Future Sight API is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
        
        content = await file.read()
        
        # Handle CSV files with encoding detection
        if file.filename.endswith('.csv'):
            # Try to detect encoding
            try:
                detected = chardet.detect(content)
                encoding = detected.get('encoding', 'utf-8')
                confidence = detected.get('confidence', 0)
                
                # If confidence is low or encoding is None, try common encodings
                if confidence < 0.7 or encoding is None:
                    encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
                else:
                    encodings_to_try = [encoding, 'utf-8', 'latin-1']
                
                df = None
                last_error = None
                for enc in encodings_to_try:
                    try:
                        decoded_content = content.decode(enc)
                        df = pd.read_csv(io.StringIO(decoded_content))
                        break
                    except (UnicodeDecodeError, pd.errors.ParserError) as e:
                        last_error = e
                        continue
                
                if df is None:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Could not decode CSV file. Tried encodings: {', '.join(encodings_to_try)}. Error: {str(last_error)}"
                    )
            except Exception as e:
                # Fallback to utf-8
                try:
                    df = pd.read_csv(io.StringIO(content.decode('utf-8')))
                except Exception as decode_error:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error reading CSV file: {str(decode_error)}. The file might have encoding issues or be corrupted."
                    )
        else:
            # Handle Excel files
            try:
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error reading Excel file: {str(e)}. Make sure the file is a valid Excel file."
                )
        
        # Validate that we have data
        if df.empty:
            raise HTTPException(status_code=400, detail="The uploaded file appears to be empty or has no data rows.")
        
        # Clean column names (remove leading/trailing spaces, replace spaces with underscores)
        df.columns = df.columns.str.strip().str.replace(' ', '_', regex=False)
        
        # Convert data types to ensure proper JSON serialization
        # Convert numeric columns to appropriate types
        for col in df.columns:
            # Try to convert to numeric if possible
            if df[col].dtype == 'object':
                # Try to convert string numbers to numeric
                try:
                    numeric_series = pd.to_numeric(df[col], errors='ignore')
                    if numeric_series.dtype != 'object':
                        df[col] = numeric_series
                except:
                    pass
        
        # Convert to dict with proper handling of NaN values
        df_dict = df.replace({pd.NA: None, pd.NaT: None}).to_dict(orient='records')
        
        # Convert sample data similarly
        sample_df = df.head(5).replace({pd.NA: None, pd.NaT: None})
        sample_data = sample_df.to_dict('records')
        
        # Get data types for reference
        column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

        return {
            "message": "File uploaded successfully",
            "columns": df.columns.tolist(),
            "column_types": column_types,
            "sample_data": sample_data,
            "row_count": len(df),
            "column_count": len(df.columns),
            "data": df_dict
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    datasetInfo = request.datasetInfo
    # Allow chatting even if no dataset uploaded
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("Gemini API key not configured")
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        if not datasetInfo or not datasetInfo.get('data'):
            # No dataset - generic prompt
            prompt = (
                "You are a data analysis expert. Provide clear, concise, and helpful answers about data analysis, "
                "statistics, and best practices. "
                f"Answer the following question: '{request.message}'"
            )
            response = model.generate_content(prompt)
            ai_response = getattr(response, "text", "")
            if not ai_response or not isinstance(ai_response, str):
                raise HTTPException(status_code=500, detail="AI did not return a valid response.")
            return {"message": ai_response.strip()}
        else:
            # Dataset available - analyze the FULL dataset
            # Reconstruct DataFrame with proper data types if available
            df = pd.DataFrame.from_records(datasetInfo['data'])
            df = restore_dataframe_types(df, datasetInfo)
            
            columns = datasetInfo['columns']
            total_rows = len(df)
            
            # Calculate comprehensive statistics for numeric columns (from ALL data)
            numeric_stats = {}
            for col in df.select_dtypes(include=['number']).columns:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    numeric_stats[col] = {
                        'total_rows': total_rows,
                        'non_null_count': int(col_data.count()),
                        'null_count': int(df[col].isna().sum()),
                        'mean': float(col_data.mean()),
                        'median': float(col_data.median()),
                        'std': float(col_data.std()) if len(col_data) > 1 else 0.0,
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'q25': float(col_data.quantile(0.25)),
                        'q75': float(col_data.quantile(0.75))
                    }
            
            # Get comprehensive info for categorical columns (from ALL data)
            categorical_info = {}
            for col in df.select_dtypes(include=['object', 'category']).columns:
                value_counts = df[col].value_counts()
                total_count = len(df[col].dropna())
                top_values = {}
                for val, count in value_counts.head(15).items():
                    percentage = (count / total_count * 100) if total_count > 0 else 0
                    top_values[str(val)] = {
                        'count': int(count),
                        'percentage': round(percentage, 2)
                    }
                categorical_info[col] = {
                    'total_rows': total_rows,
                    'non_null_count': int(total_count),
                    'null_count': int(df[col].isna().sum()),
                    'unique_values': int(df[col].nunique()),
                    'top_values': top_values
                }
            
            # Get a small sample for data structure reference only (not for analysis)
            sample_data = df.head(5).to_dict('records')
            sample_data_json = json.dumps(sample_data, indent=2)
            stats_json = json.dumps({
                'numeric_columns': numeric_stats,
                'categorical_columns': categorical_info
            }, indent=2)
            
            # First, determine if the question requires a calculation
            calculation_keywords = ['total', 'sum', 'count', 'average', 'mean', 'how many', 'calculate', 
                                   'what is the', 'find', 'get', 'show me', 'list', 'filter', 'where']
            requires_calculation = any(keyword in request.message.lower() for keyword in calculation_keywords)
            
            if requires_calculation:
                # Generate Python code to calculate the answer
                code_prompt = (
                    f"You are a Python data analysis expert. A user has a pandas DataFrame called 'df' with {total_rows} rows "
                    f"and columns: {', '.join(columns)}.\n\n"
                    f"Dataset Statistics:\n{stats_json}\n\n"
                    f"Sample Data (first 5 rows):\n{sample_data_json}\n\n"
                    f"User Question: '{request.message}'\n\n"
                    f"Generate Python code that calculates the answer to this question using the DataFrame 'df'. "
                    f"The code should:\n"
                    f"1. Use pandas operations (filtering, grouping, aggregation, etc.) as needed\n"
                    f"2. Store the final answer in a variable called 'answer'\n"
                    f"3. Handle any potential errors (missing columns, null values, etc.)\n"
                    f"4. Return ONLY the Python code, no explanations or markdown\n"
                    f"5. Do NOT use print() statements - just assign to 'answer'\n"
                    f"6. If the answer is a DataFrame or Series, convert it to a string or dict for display\n"
                    f"7. For numeric results, return the actual number\n"
                    f"8. For text/categorical results, return a clear string description\n\n"
                    f"Example: If asked 'total units sold in 2020', the code should be:\n"
                    f"answer = df[df['Year'] == 2020]['Units_Sold'].sum()\n\n"
                    f"Generate the code now:"
                )
                
                code_response = model.generate_content(code_prompt)
                code = getattr(code_response, "text", "").strip()
                
                # Clean up code (remove markdown if present)
                code = re.sub(r'```(?:python)?\n?|\n?```', '', code).strip()
                
                # Execute the code
                calculated_answer = None
                execution_error = None
                try:
                    exec_globals = {'df': df, 'pd': pd, 'np': __import__('numpy')}
                    exec(code, exec_globals)
                    calculated_answer = exec_globals.get('answer', None)
                    
                    if calculated_answer is None:
                        # Try to get the last expression result if answer wasn't assigned
                        # This handles cases where code just returns a value
                        if 'result' in exec_globals:
                            calculated_answer = exec_globals['result']
                        else:
                            raise ValueError("Code did not assign a value to 'answer' variable")
                    
                    # Format the answer
                    if isinstance(calculated_answer, (pd.DataFrame, pd.Series)):
                        if isinstance(calculated_answer, pd.Series):
                            if len(calculated_answer) == 1:
                                calculated_answer = calculated_answer.iloc[0]
                            else:
                                calculated_answer = calculated_answer.to_dict()
                        else:
                            calculated_answer = calculated_answer.to_dict('records')
                    elif isinstance(calculated_answer, (int, float, complex)):
                        if isinstance(calculated_answer, complex):
                            calculated_answer = str(calculated_answer)
                        elif isinstance(calculated_answer, float):
                            # Round to reasonable precision
                            calculated_answer = round(calculated_answer, 6) if calculated_answer != int(calculated_answer) else int(calculated_answer)
                        else:
                            calculated_answer = int(calculated_answer)
                    elif calculated_answer is not None:
                        calculated_answer = str(calculated_answer)
                        
                except Exception as e:
                    execution_error = str(e)
                    print(f"Code execution error: {execution_error}")
                    print(f"Generated code: {code}")
                
                # Generate explanation with the calculated result
                if calculated_answer is not None:
                    explanation_prompt = (
                        f"You are a data insights expert. A user asked: '{request.message}'\n\n"
                        f"The calculation has been performed on the complete dataset ({total_rows} rows).\n"
                        f"Result: {calculated_answer}\n\n"
                        f"Provide a clear, concise answer that:\n"
                        f"1. Directly answers the question\n"
                        f"2. States the calculated result prominently\n"
                        f"3. Provides brief context if helpful\n"
                        f"4. Does NOT say 'I would need to calculate' - the calculation is already done\n"
                        f"5. Be confident and direct with the answer\n\n"
                        f"Answer:"
                    )
                    
                    explanation_response = model.generate_content(explanation_prompt)
                    explanation = getattr(explanation_response, "text", "").strip()
                    
                    return {"message": explanation}
                else:
                    # If calculation failed, fall back to statistics-based answer
                    execution_error_msg = f" (Calculation error: {execution_error})" if execution_error else ""
                    fallback_prompt = (
                        f"You are a data insights expert analyzing a COMPLETE dataset. "
                        f"IMPORTANT: The dataset contains {total_rows} TOTAL ROWS. "
                        f"All statistics below are calculated from the ENTIRE dataset.\n\n"
                        f"Dataset Structure:\n"
                        f"- Total Rows: {total_rows}\n"
                        f"- Columns: {', '.join(columns)}\n\n"
                        f"COMPREHENSIVE STATISTICS (from ALL {total_rows} rows):\n{stats_json}\n\n"
                        f"User Question: '{request.message}'\n\n"
                        f"Note: An attempt to calculate the answer programmatically failed{execution_error_msg}. "
                        f"Please provide the best answer you can using the statistics provided. "
                        f"Be specific and use the actual values from the statistics."
                    )
                    
                    fallback_response = model.generate_content(fallback_prompt)
                    fallback_answer = getattr(fallback_response, "text", "").strip()
                    return {"message": fallback_answer}
            else:
                # For non-calculation questions, use statistics-based insights
                prompt = (
                    "You are a data insights expert analyzing a COMPLETE dataset. "
                    f"IMPORTANT: The dataset contains {total_rows} TOTAL ROWS. "
                    f"All statistics below are calculated from the ENTIRE dataset, not just sample rows.\n\n"
                    f"Dataset Structure:\n"
                    f"- Total Rows: {total_rows}\n"
                    f"- Columns: {', '.join(columns)}\n\n"
                    f"COMPREHENSIVE STATISTICS (from ALL {total_rows} rows):\n{stats_json}\n\n"
                    f"Sample Data Structure (first 5 rows - for reference only, NOT for analysis):\n{sample_data_json}\n\n"
                    f"User Question: '{request.message}'\n\n"
                    f"CRITICAL INSTRUCTIONS:\n"
                    f"1. All statistics provided above are calculated from the COMPLETE dataset ({total_rows} rows).\n"
                    f"2. Use the statistical summaries to answer questions - they represent ALL the data.\n"
                    f"3. Do NOT base your answer only on the 5 sample rows shown - those are just for data structure reference.\n"
                    f"4. Be precise and reference the actual statistical values from the full dataset.\n"
                    f"5. Provide actionable insights based on the complete data."
                )
                
                response = model.generate_content(prompt)
                ai_response = getattr(response, "text", "")
                if not ai_response or not isinstance(ai_response, str):
                    raise HTTPException(status_code=500, detail="AI did not return a valid response.")
                
                return {"message": ai_response.strip()}

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
        df = restore_dataframe_types(df, request.datasetInfo)
        columns = request.datasetInfo['columns']
        total_rows = len(df)
        user_visual_request = request.prompt
        
        # Get data type info for better code generation
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Analyze data structure - check if comparing categories would need aggregation
        # Also detect which category column might be used for comparison
        needs_aggregation_for_comparison = False
        comparison_analysis = ""
        category_structure_info = {}
        
        if categorical_cols and numeric_cols:
            # Analyze each categorical column to see row distribution
            for cat_col in categorical_cols:
                category_counts = df[cat_col].value_counts()
                max_rows_per_category = category_counts.max()
                min_rows_per_category = category_counts.min()
                category_structure_info[cat_col] = {
                    'max_rows': max_rows_per_category,
                    'min_rows': min_rows_per_category,
                    'unique_count': len(category_counts)
                }
            
            # Check if user request mentions specific categories (like "North", "South", "Region")
            user_request_lower = user_visual_request.lower()
            detected_category_col = None
            for cat_col in categorical_cols:
                # Check if category column name or values appear in request
                if cat_col.lower() in user_request_lower or 'region' in user_request_lower:
                    detected_category_col = cat_col
                    break
            
            # Use detected column or first categorical column
            analysis_col = detected_category_col if detected_category_col else categorical_cols[0]
            col_info = category_structure_info[analysis_col]
            
            if col_info['max_rows'] == 1 and col_info['min_rows'] == 1:
                needs_aggregation_for_comparison = False
                comparison_analysis = (
                    f"DATA STRUCTURE ANALYSIS: The dataset has EXACTLY ONE row per category in '{analysis_col}'. "
                    f"Total categories: {col_info['unique_count']}. "
                    f"CRITICAL: When comparing values by {analysis_col}, use .iloc[0] to get the value. "
                    f"DO NOT use .sum() or .mean() - that will be wrong! "
                    f"Example: df[df['{analysis_col}']=='South']['Units_Sold'].iloc[0]"
                )
            else:
                needs_aggregation_for_comparison = True
                comparison_analysis = (
                    f"DATA STRUCTURE ANALYSIS: The dataset has MULTIPLE rows per category in '{analysis_col}' "
                    f"(min {col_info['min_rows']}, max {col_info['max_rows']} rows per category). "
                    f"If comparing by {analysis_col}, you MUST aggregate (sum/mean) to get accurate values."
                )
        
        # Get actual sample data to show structure
        sample_data = df.head(10).to_dict('records')
        sample_data_json = json.dumps(sample_data, indent=2, default=str)
        
        # Get unique values for categorical columns to help with filtering
        category_examples = {}
        for col in categorical_cols[:3]:  # Limit to first 3 to avoid too much data
            unique_vals = df[col].unique()[:10].tolist()
            category_examples[col] = [str(v) for v in unique_vals]

        generation_prompt = (
            f"You are an expert Python data visualization assistant. "
            f"A user has uploaded a dataset with {total_rows} TOTAL ROWS, which is already loaded as the pandas DataFrame 'df'.\n\n"
            f"Dataset Information:\n"
            f"- Total Rows: {total_rows}\n"
            f"- Columns: {', '.join(columns)}\n"
            f"- Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}\n"
            f"- Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}\n"
            f"- Date columns: {', '.join(date_cols) if date_cols else 'None'}\n\n"
            f"{comparison_analysis}\n\n"
            f"ACTUAL SAMPLE DATA (first 10 rows) - Use this to understand the data structure:\n{sample_data_json}\n\n"
            f"Category Examples (unique values):\n"
        )
        
        # Add category examples
        for col, vals in category_examples.items():
            generation_prompt += f"- {col}: {', '.join(vals[:5])}{'...' if len(vals) > 5 else ''}\n"
        
        generation_prompt += (
            f"\nYour task: Generate Python code to create a chart for: '{user_visual_request}'\n\n"
            f"CRITICAL RULES - READ CAREFULLY:\n"
            f"1. **For COMPARISON requests** (compare, show, display values by category):\n"
        )
        
        if not needs_aggregation_for_comparison:
            generation_prompt += (
                f"   - ⚠️ CRITICAL: The data has EXACTLY ONE row per category. Use values DIRECTLY with .iloc[0].\n"
                f"   - Example: 'Compare units in South and North' → \n"
                f"     south_val = df[df['Region']=='South']['Units_Sold'].iloc[0]  # ONE row, get that value\n"
                f"     north_val = df[df['Region']=='North']['Units_Sold'].iloc[0]  # ONE row, get that value\n"
                f"     plt.bar(['South', 'North'], [south_val, north_val])\n"
                f"   - ❌ NEVER use .sum() or .mean() when there's one row - that would WRONGLY double/triple values!\n"
                f"   - ✅ ALWAYS use .iloc[0] or .values[0] to get the single value from filtered data\n"
            )
        else:
            generation_prompt += (
                f"   - The data has MULTIPLE rows per category. You MUST aggregate.\n"
                f"   - Example: 'Compare units in South and North' → \n"
                f"     south_val = df[df['Region']=='South']['Units_Sold'].sum()  # Sum multiple rows\n"
                f"     north_val = df[df['Region']=='North']['Units_Sold'].sum()  # Sum multiple rows\n"
                f"     plt.bar(['South', 'North'], [south_val, north_val])\n"
            )
        
        generation_prompt += (
            f"2. **For AGGREGATION requests** (total, sum, average, mean, count):\n"
            f"   - Always use groupby() or aggregation functions\n"
            f"   - Example: 'Total sales by month' → grouped = df.groupby('Month')['Sales'].sum(); plt.bar(grouped.index, grouped.values)\n"
            f"3. **Column names**: Use exact names: {', '.join(columns)}\n"
            f"4. **NO plt.show()**: Do NOT call plt.show() - chart displays automatically\n"
            f"5. **Plot actual values**: If South=410 and North=320, plot exactly 410 and 320, NOT 820 and 640\n\n"
            f"Return ONLY Python code, no explanations. User request: '{user_visual_request}'"
        )

        response = model.generate_content(generation_prompt)
        raw_response = getattr(response, "text", "").strip()
        initial_code = re.sub(r'```(?:python)?\n?|\n?```', '', raw_response).strip()
        print(f"Initial AI Code: {initial_code}")

        review_prompt = (
            f"You are a highly meticulous Senior Python Data Reviewer. Your task is to critique and correct the provided Python code, "
            f"which must generate a chart using the pandas DataFrame 'df' containing {total_rows} rows.\n\n"
            f"Dataset Information:\n"
            f"- Total Rows: {total_rows}\n"
            f"- Columns: {', '.join(columns)}\n"
            f"- Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}\n"
            f"- Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}\n"
            f"- User request: '{user_visual_request}'\n\n"
            f"{comparison_analysis}\n\n"
            f"Sample Data Structure (first 5 rows):\n{json.dumps(df.head(5).to_dict('records'), indent=2, default=str)}\n\n"
            f"Python code to review:\n{initial_code}\n\n"
            f"CRITICAL Review Checklist:\n"
            f"1. **Full Dataset Usage**: Does the code use the complete DataFrame 'df' with all {total_rows} rows? "
            f"   It should NOT use df.head(), df.sample(), or limit the data unless specifically requested.\n"
            f"2. **CRITICAL - Aggregation Logic** (MOST IMPORTANT):\n"
        )
        
        if not needs_aggregation_for_comparison:
            review_prompt += (
                f"   - DATA HAS ONE ROW PER CATEGORY. For comparison requests, use .iloc[0] or direct value access.\n"
                f"   - If code uses .sum() or .mean() for comparison, it's WRONG and will double values!\n"
                f"   - CORRECT: south = df[df['Region']=='South']['Units_Sold'].iloc[0]\n"
                f"   - WRONG: south = df[df['Region']=='South']['Units_Sold'].sum()  # This doubles the value!\n"
            )
        else:
            review_prompt += (
                f"   - DATA HAS MULTIPLE ROWS PER CATEGORY. For comparison, aggregation is REQUIRED.\n"
                f"   - CORRECT: south = df[df['Region']=='South']['Units_Sold'].sum()\n"
            )
        
        review_prompt += (
            f"3. **Value Accuracy Check**: Look at the sample data above. If comparing categories:\n"
            f"   - Count how many rows exist per category in the sample\n"
            f"   - If 1 row per category: use .iloc[0] (NO aggregation)\n"
            f"   - If multiple rows: use .sum() or .mean() (aggregation needed)\n"
            f"4. **Column Name Accuracy**: Are all column names exact matches to: {', '.join(columns)}?\n"
            f"5. **NO plt.show()**: Remove any plt.show() calls.\n"
            f"6. **Code Correctness**: Is the code syntactically correct?\n"
            f"7. **Chart Quality**: Does it create a proper chart with labels and title?\n\n"
            f"If the code is WRONG (especially aggregation logic), fix it completely. Return ONLY the corrected Python code, no explanations."
        )

        review_response = model.generate_content(review_prompt)
        raw_reviewed_response = getattr(review_response, "text", "").strip()
        final_code = re.sub(r'```(?:python)?\n?|\n?```', '', raw_reviewed_response).strip()
        
        # Remove any plt.show() calls that might have been included
        final_code = re.sub(r'plt\.show\(\)\s*', '', final_code, flags=re.IGNORECASE)
        final_code = re.sub(r'plt\.show\(\)\s*$', '', final_code, flags=re.IGNORECASE | re.MULTILINE)
        
        ai_response = final_code
        print(f"Final (Reviewed) AI Code: {final_code}")

        if not final_code or len(final_code) < 10:
            raise Exception("AI did not return valid Python code for chart generation.")

        # Execute final validated code with full dataset
        exec_globals = {'df': df, 'pd': pd, 'plt': plt, 'np': __import__('numpy')}
        try:
            # Verify we're using the full dataset before execution
            original_row_count = len(df)
            print(f"Executing chart code on dataset with {original_row_count} rows")
            
            exec(final_code, exec_globals)
            
            # Verify a figure was created
            if not plt.get_fignums():
                raise Exception("Code executed but no matplotlib figure was created. Make sure the code creates a plot.")
            
            fig = plt.gcf()
            
            # Additional validation: Check if the chart has data
            axes = fig.get_axes()
            if not axes:
                raise Exception("Figure created but no axes found in the chart.")
            
            # Verify the chart has meaningful data and validate values
            chart_values_found = []
            for ax in axes:
                has_data = False
                chart_values = []
                
                # Extract values from the chart
                for line in ax.get_lines():
                    ydata = line.get_ydata()
                    if len(ydata) > 0:
                        has_data = True
                        chart_values.extend(ydata)
                
                for collection in ax.collections:
                    offsets = collection.get_offsets()
                    if len(offsets) > 0:
                        has_data = True
                        chart_values.extend([point[1] for point in offsets])
                
                for patch in ax.patches:
                    height = patch.get_height()
                    width = patch.get_width()
                    if height > 0 or width > 0:
                        has_data = True
                        chart_values.append(height if height > 0 else width)
                
                if chart_values:
                    chart_values_found.extend(chart_values)
                
                if not has_data and len(ax.get_lines()) == 0 and len(ax.collections) == 0 and len(ax.patches) == 0:
                    print("Warning: Chart may not have data plotted")
            
            # Validate chart values for comparison requests
            if chart_values_found and ('compare' in user_visual_request.lower() or 'vs' in user_visual_request.lower() or 'and' in user_visual_request.lower()):
                print(f"Chart values being plotted: {chart_values_found}")
                
                # Check if values seem incorrect (too large compared to dataset)
                if numeric_cols and categorical_cols:
                    dataset_max = df[numeric_cols[0]].max()
                    max_chart_value = max(chart_values_found) if chart_values_found else 0
                    
                    # If chart values are significantly larger than individual row values, likely wrong aggregation
                    if max_chart_value > dataset_max * 1.2 and not needs_aggregation_for_comparison:  # 20% larger suggests issue
                        print(f"ERROR DETECTED: Chart shows {max_chart_value} but dataset max is {dataset_max}")
                        print("Values appear to be incorrectly aggregated. Fixing automatically...")
                        
                        # Try to automatically fix by detecting category and value columns from the request
                        detected_cat_col = None
                        detected_val_col = None
                        
                        user_lower = user_visual_request.lower()
                        for cat_col in categorical_cols:
                            if cat_col.lower() in user_lower or any(val.lower() in user_lower for val in df[cat_col].astype(str).unique()[:5]):
                                detected_cat_col = cat_col
                                break
                        
                        for num_col in numeric_cols:
                            if num_col.lower() in user_lower:
                                detected_val_col = num_col
                                break
                        
                        if not detected_cat_col:
                            detected_cat_col = categorical_cols[0] if categorical_cols else None
                        if not detected_val_col:
                            detected_val_col = numeric_cols[0] if numeric_cols else None
                        
                        if detected_cat_col and detected_val_col:
                            # Get unique categories
                            categories = df[detected_cat_col].unique()[:10]  # Limit to 10
                            
                            # Generate fixed code directly
                            fixed_code_parts = [
                                "import matplotlib.pyplot as plt",
                                "fig, ax = plt.subplots(figsize=(10, 6))",
                                f"categories = {categories.tolist()}",
                                "values = []",
                                f"for cat in categories:",
                                f"    val = df[df['{detected_cat_col}']==cat]['{detected_val_col}'].iloc[0]",
                                "    values.append(val)",
                                "ax.bar(categories, values)",
                                f"ax.set_xlabel('{detected_cat_col}')",
                                f"ax.set_ylabel('{detected_val_col}')",
                                f"ax.set_title('{user_visual_request}')",
                                "plt.tight_layout()"
                            ]
                            
                            fixed_code = "\n".join(fixed_code_parts)
                            print(f"Auto-generated fixed code: {fixed_code}")
                            
                            # Close current figure and regenerate
                            plt.close(fig)
                            
                            # Execute corrected code
                            exec_globals = {'df': df, 'pd': pd, 'plt': plt, 'np': __import__('numpy')}
                            exec(fixed_code, exec_globals)
                            
                            fig = plt.gcf()
                            axes = fig.get_axes()
                            
                            # Verify corrected values
                            corrected_values = []
                            for ax in axes:
                                for patch in ax.patches:
                                    height = patch.get_height()
                                    if height > 0:
                                        corrected_values.append(height)
                            
                            print(f"Corrected chart values: {corrected_values}")
            
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            print(f"Chart generated successfully from {original_row_count} rows of data")

            return {
                "success": True,
                "chart_image": chart_base64,
                "message": f"Chart generated successfully using all {original_row_count} rows of data"
            }
            
        except Exception as exec_err:
            print(f"Error executing AI code: {exec_err}")
            print(f"Generated code was: {final_code}")
            raise Exception(f"Error executing chart code: {exec_err}")

    except Exception as e:
        print(f"Error during chart generation: {str(e)}")
        # Improved fallback chart generation with proper aggregations
        df = pd.DataFrame.from_records(request.datasetInfo['data'])
        df = restore_dataframe_types(df, request.datasetInfo)
        fig, ax = plt.subplots(figsize=(10, 6))
        
        total_rows = len(df)
        user_request_lower = request.prompt.lower()
        
        # Try to create a meaningful chart based on the request
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Check if request implies aggregation
            needs_aggregation = any(keyword in user_request_lower for keyword in 
                                  ['total', 'sum', 'average', 'mean', 'count', 'by', 'group', 'distribution'])
            
            if needs_aggregation and categorical_cols and numeric_cols:
                # Try to create aggregated chart
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                
                if 'sum' in user_request_lower or 'total' in user_request_lower:
                    grouped = df.groupby(cat_col)[num_col].sum()
                elif 'average' in user_request_lower or 'mean' in user_request_lower:
                    grouped = df.groupby(cat_col)[num_col].mean()
                else:
                    grouped = df.groupby(cat_col)[num_col].sum()
                
                ax.bar(grouped.index.astype(str), grouped.values)
                ax.set_xlabel(cat_col)
                ax.set_ylabel(f"{'Total' if 'sum' in user_request_lower or 'total' in user_request_lower else 'Average'} {num_col}")
                ax.set_title(f"{request.prompt} (from {total_rows} rows)")
                
            elif categorical_cols and ('distribution' in user_request_lower or 'count' in user_request_lower):
                # Value counts chart
                cat_col = categorical_cols[0]
                counts = df[cat_col].value_counts()
                ax.bar(counts.index.astype(str), counts.values)
                ax.set_xlabel(cat_col)
                ax.set_ylabel('Count')
                ax.set_title(f"Distribution of {cat_col} (from {total_rows} rows)")
                
            elif len(numeric_cols) >= 2:
                # Scatter or line plot
                x_col, y_col = numeric_cols[0], numeric_cols[1]
                ax.scatter(df[x_col], df[y_col].fillna(0))
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{request.prompt} (from {total_rows} rows)")
                
            elif len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                # Bar chart with categories
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                ax.bar(df[x_col].astype(str), df[y_col].fillna(0))
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{request.prompt} (from {total_rows} rows)")
                
            elif len(numeric_cols) == 1:
                # Histogram
                ax.hist(df[numeric_cols[0]].dropna(), bins=min(20, total_rows))
                ax.set_xlabel(numeric_cols[0])
                ax.set_ylabel('Frequency')
                ax.set_title(f"Distribution of {numeric_cols[0]} (from {total_rows} rows)")
                
            else:
                # Default: value counts of first column
                first_col = df.columns[0]
                counts = df[first_col].value_counts()
                ax.bar(counts.index.astype(str), counts.values)
                ax.set_xlabel(first_col)
                ax.set_ylabel('Count')
                ax.set_title(f"{request.prompt} (from {total_rows} rows)")
            
            if len(df) > 10:
                ax.tick_params(axis='x', rotation=45)
            
        except Exception as fallback_err:
            # Ultimate fallback
            print(f"Fallback chart generation error: {fallback_err}")
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
                ax.bar(df[x_col].astype(str), df[y_col].fillna(0))
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
            else:
                ax.hist(df.iloc[:, 0].dropna(), bins=min(20, total_rows))
                ax.set_xlabel(df.columns[0])
                ax.set_ylabel('Count')
            ax.set_title(f"Chart for: {request.prompt} (from {total_rows} rows)")
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return {
            "success": True,
            "chart_image": chart_base64,
            "message": f"Chart generated (fallback mode using all {total_rows} rows): {str(e)}"
        }
