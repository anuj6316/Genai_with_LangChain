from locale import strcoll
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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
import uuid
from datetime import date
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Banking Customer Service API",
    description="API for banking customer service chatbot",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:8000', 'http://localhost:8000'],
    # allow_origins=["*"],
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
    # context: str

class QueryResponse(BaseModel):
    query: str
    response: str
    customer_name: str
    member_code: str

class ErrorResponse(BaseModel):
    error: str
    detail: str

def formatted_today_date():
    today = date.today()
    return today.strftime("%Y-%M-%D")

class TicketRaiseResponse(BaseModel):
    ticket_id: str = Field(default=str(uuid.uuid4()), description="Unique id for ticket generated automatically.")
    status: str = Field(default=True, description="Status of ticket closed, open, escalated, pending and so on so forth, by default it's open")
    account_number: str = Field(description="account number of user")
    complaint_date: str = Field(default=formatted_today_date(), description="Date when ticket was created")
    member_id: str = Field(description="Unique member id of a customer")
    customer_name: str = Field(description="Customer Name")
    category: str = Field(default = None, description="customer's Query category like: FD related issue, Payment Related")
    call_type: str = Field(default = None, description="What problem customer is facing")
    complaint_details: str = Field(description="Complete deatil of customery complaint")
    request_type: str = Field(default = "Open", description="Type of the request, like if the user wants to open new query or trying to reopen a query and so on so forth")
    requested_by: str = Field(default = None, description="")
    request_date: str = Field(default = formatted_today_date(),description="request date")
    remarks: str = Field(description="Overview/remarks of the customer query")

class TicketRaiseRequest(BaseModel):
    status: str = Field(default="Open", description="Status of ticket closed, open, escalated, pending and so on so forth, by default it's open")
    account_number: str = Field(description="account number of user")
    # complaint_date: str = Field(default=formatted_today_date(), description="Date when ticket was created")
    member_id: str = Field(description="Unique member id of a customer")
    customer_name: str = Field(description="Customer Name")
    category: str = Field(default = None, description="customer's Query category like: FD related issue, Payment Related")
    call_type: str = Field(default = None, description="What problem customer is facing")
    complaint_details: str = Field(description="Complete deatil of customery complaint")
    request_type: str = Field(default = "Open", description="Type of the request, like if the user wants to open new query or trying to reopen a query and so on so forth")
    requested_by: str = Field(default = None, description="")
    request_date: str = Field(default = formatted_today_date(),description="request date")
    remarks: str = Field(description="Overview/remarks of the customer query")

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
# @app.post("/query")
@app.websocket('/ws/{member_code}')
async def websocket_endpoint(websocket: WebSocket, member_code: str):
    await websocket.accept()
    print(f"WebSocket connection accepted for member_code: {member_code}")
    try:
        customer, tickets = get_customer_data(member_code)
        if customer is None:
            await websocket.send_text(f"Error: No customer found with member code: {member_code}")
            await websocket.close()
            return
        
        context = format_customer_context(customer, tickets)
        await websocket.send_text("Connection successful. How can i help you today?")
    except Exception as e:
        await websocket.send_text(f"Error initializing connection: str{e}")
        await websocket.close()
        return 
    try:
        while True:
            # wait for a message from the client
            question = await websocket.receive_text()
            print(f"Received message: {question}")

            # create prompt template and chain
            prompt = PromptTemplate(
                template="""Based on the customer information below, please answer this specific question:
    question: {question}
    Customer Information:
    {context}

    Please provide a helpful and accurate response in normal text no need to make it in markdown format.""",
    input_variables = ['question', 'context']
            )
            chain = prompt | model | parser

            # get response from AI
            ai_response = chain.invoke({
                'question': question,
                'context': context
            })

            # send response back to client 
            await websocket.send_text(ai_response)
            print(f"Sent AI response: {ai_response}")
    except WebSocketDisconnect:
        print(f"Client for member_code {member_code} disconnected.")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        print(f"Closing connection for member_code {member_code}")
        await websocket.close()
        print("WebSocket connection closed")

# @app.get("/")
# async def root():
#     """Root endpoint with API information"""
#     return {
#         "message": "Banking Customer Service API",
#         "version": "1.0.0",
#         "endpoints": [
#             "/customer/{member_code} - Get customer information",
#             "/query - Ask questions about customer data"
#         ]
#     }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     try:
#         # Test database connection
#         db.list_collection_names()
#         return {"status": "healthy", "database": "connected"}
#     except Exception as e:
#         raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

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
            # context=context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/raise_query", response_model=TicketRaiseResponse)
def raise_ticket(request: TicketRaiseRequest):
    """Create a new ticket in the database"""
    try:
        ticket_col = db["Ticket_details"]
        
        # Create a new ticket document
        ticket_id = str(uuid.uuid4())
        complaint_date = formatted_today_date()
        
        ticket_data = {
            "ticket_id": ticket_id,
            "status": request.status,
            "account_number": request.account_number,
            "complaint_date": complaint_date,
            "member_id": request.member_id,
            "customer_name": request.customer_name,
            "category": request.category,
            "call_type": request.call_type,
            "complaint_details": request.complaint_details,
            "request_type": request.request_type,
            "requested_by": request.requested_by,
            "request_date": request.request_date,
            "remarks": request.remarks
        }
        
        # Insert the new ticket into the database
        ticket_col.insert_one(ticket_data)
        
        # Return the response by creating a TicketRaiseResponse instance
        return TicketRaiseResponse(
            ticket_id=ticket_id,
            status=request.status,
            account_number=request.account_number,
            complaint_date=complaint_date,
            member_id=request.member_id,
            customer_name=request.customer_name,
            category=request.category,
            call_type=request.call_type,
            complaint_details=request.complaint_details,
            request_type=request.request_type,
            requested_by=request.requested_by,
            request_date=request.request_date,
            remarks=request.remarks
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

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