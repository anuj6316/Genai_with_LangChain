from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import os
import json
from datetime import datetime
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Banking Customer Service API",
    description="API for banking customer service chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
client = MongoClient()
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
parser = StrOutputParser()
db = client["Practice"]

# Pydantic models for request/response
class CustomerQueryRequest(BaseModel):
    member_code: str
    question: str

class CustomerInfoRequest(BaseModel):
    member_code: str

class CustomerInfo(BaseModel):
    customer_name: str
    member_code: str
    phone_no: str
    email_id: str
    address: str
    ticket_id: str
    department: str
    status: str

class TicketInfo(BaseModel):
    request_date: str
    status: str
    request_type: str
    requested_by: str
    remarks: str

class CustomerResponse(BaseModel):
    customer_info: CustomerInfo
    tickets: List[TicketInfo]
    context: str

class QueryResponse(BaseModel):
    query: str
    response: str
    customer_name: str
    member_code: str

class ErrorResponse(BaseModel):
    error: str
    detail: str

# Helper functions (from original code)
def get_customer_data(member_code: str):
    """Retrieve customer and ticket data"""
    try:
        # Get customer details
        cust_col = db["customer_details"]
        customer = cust_col.find_one({"customerDetails.member_code": member_code})
        
        if not customer:
            return None, f"No customer found with member code: {member_code}"
        
        # Get ticket details
        ticket_col = db["Ticket_details"]
        tickets = list(ticket_col.find({"ticket_id": customer['systemGenerated']['ticket_id']}))
        
        return customer, tickets
        
    except Exception as e:
        return None, f"Error retrieving data: {str(e)}"

def format_customer_context(customer, tickets):
    """Format customer and ticket data for the prompt"""
    
    # Format customer information
    customer_info = f"""
Customer Details:
- Name: {customer['customerDetails']['customer_name']}
- Member Code: {customer['customerDetails']['member_code']}
- Phone: {customer['customerDetails']['phone_no']}
- Email: {customer['customerDetails']['email_id']}
- Address: {customer['customerDetails']['address']}

Account Details:
- Loan: {customer['accountDetails']['loan_details']}
- Fixed Deposit: {customer['accountDetails']['fixed_deposit']}
- Recurring Deposit: {customer['accountDetails']['recurring_deposit']}
- Savings Account: {customer['accountDetails']['savings_account']}
- Current Account: {customer['accountDetails']['current_account']}

Current Issue:
- Department: {customer['agentInput']['department']}
- Contact Mode: {customer['agentInput']['mode_of_contact']}
- Call Type: {customer['agentInput']['call_type']}
- Category: {customer['agentInput']['category_name']}
- Account No: {customer['ticketInfo']['account_no']}
- Remarks: {customer['ticketInfo']['remarks']}
- Attachments: {customer['ticketInfo']['attachments']}
- Ticket ID: {customer['systemGenerated']['ticket_id']}
"""
    
    # Format ticket history
    ticket_history = "\nTicket History:\n"
    for i, ticket in enumerate(tickets, 1):
        ticket_history += f"""
{i}. Date: {ticket['request_date']} | Status: {ticket['status']} | Type: {ticket['request_type']}
   Requested by: {ticket['requested_by']}
   Remarks: {ticket['remarks']}
"""
    
    return customer_info + ticket_history

# API Routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Banking Customer Service API",
        "version": "1.0.0",
        "endpoints": [
            "/customer/{member_code} - Get customer information",
            "/query - Ask questions about customer data"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.list_collection_names()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/customer/{member_code}", response_model=CustomerResponse)
async def get_customer_info(member_code: str):
    """Get customer information and ticket history"""
    try:
        customer, tickets = get_customer_data(member_code)
        
        if customer is None:
            raise HTTPException(status_code=404, detail=tickets)
        
        # Format response
        customer_info = CustomerInfo(
            customer_name=customer['customerDetails']['customer_name'],
            member_code=customer['customerDetails']['member_code'],
            phone_no=customer['customerDetails']['phone_no'],
            email_id=customer['customerDetails']['email_id'],
            address=customer['customerDetails']['address'],
            ticket_id=customer['systemGenerated']['ticket_id'],
            department=customer['agentInput']['department'],
            status=customer['systemGenerated'].get('status', 'Active')
        )
        
        ticket_list = []
        for ticket in tickets:
            ticket_info = TicketInfo(
                request_date=ticket['request_date'],
                status=ticket['status'],
                request_type=ticket['request_type'],
                requested_by=ticket['requested_by'],
                remarks=ticket['remarks']
            )
            ticket_list.append(ticket_info)
        
        context = format_customer_context(customer, tickets)
        
        return CustomerResponse(
            customer_info=customer_info,
            tickets=ticket_list,
            context=context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_customer(request: CustomerQueryRequest):
    """Ask a question about customer data"""
    try:
        # Get customer data
        customer, tickets = get_customer_data(request.member_code)
        
        if customer is None:
            raise HTTPException(status_code=404, detail=tickets)
        
        # Format context
        context = format_customer_context(customer, tickets)
        
        # Create prompt template
        prompt = PromptTemplate(
            template="""Based on the customer information below, please answer this specific question:
            
Question: {question}

Customer Information:
{context}

Please provide a helpful and accurate response in normal text no need to make it in markdown format.""",
            input_variables=['question', 'context']
        )
        
        # Create chain and get response
        chain = prompt | model | parser
        response = chain.invoke({
            "question": request.question,
            "context": context
        })
        
        return QueryResponse(
            query=request.question,
            response=response,
            customer_name=customer['customerDetails']['customer_name'],
            member_code=request.member_code
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not Found", "detail": str(exc.detail)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal Server Error", "detail": "Something went wrong"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Replace "main" with your filename if different
        host="0.0.0.0",
        port=8000,
        reload=True
    )