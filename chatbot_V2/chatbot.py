from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import os

load_dotenv()

client = MongoClient()
db = client["Practice"]
model = ChatGoogleGenerativeAI(model='gemini-1.5-flash')
parser = StrOutputParser()

def get_chatbot_response(user_id: str, customer_query: str) -> str:
    """
    Get the chatbot response for a given user_id and query.
    """
    cust_col = db["customer_details"]
    c = cust_col.find_one({"customerDetails.member_code": user_id})
    
    if not c:
        return f"No customer found with member code: {user_id}"

    ticket_col = db["Ticket_details"].find({"ticket_id": c['systemGenerated']['ticket_id']})

    # Format the ticket history
    formatted_ticket_history = ""
    for item in ticket_col:
        formatted_ticket_history += f"- Status: {item.get('status')}, Request Type: {item.get('request_type')}, Remarks: {item.get('remarks')}\n"

    prompt1 = """
    You are a highly intelligent and empathetic customer service chatbot. Your primary goal is to provide accurate, clear, and helpful responses to customer queries based on the information provided below.

    **Customer Information:**
    - Name: {customer_name}
    - Member Code: {member_code}
    - Contact: {phone_no}, {email_id}
    - Address: {address}

    **Account Details:**
    - Loan: {loan_details}
    - Fixed Deposit: {fixed_deposit}
    - Recurring Deposit: {recurring_deposit}
    - Savings Account: {savings_account}
    - Current Account: {current_account}

    **Ticket History for Ticket ID {ticket_id}:**
    {ticket_history}

    **Customer Query:**
    \"{customer_query}\"\n\n    Based on the information above, please provide a comprehensive and helpful response to the customer's query. If the query is about a past issue, use the ticket history to understand the context and resolution.

    **Your Response:**
    """

    prompt_template = PromptTemplate(
        input_variables=[
            "customer_name",
            "member_code",
            "phone_no",
            "email_id",
            "address",
            "loan_details",
            "fixed_deposit",
            "recurring_deposit",
            "savings_account",
            "current_account",
            "ticket_id",
            "ticket_history",
            "customer_query",
        ],
        template=prompt1,
    )

    chain = prompt_template | model | parser
    
    response = chain.invoke({
        "customer_name": c['customerDetails']['customer_name'],
        "member_code": c['customerDetails']['member_code'],
        "phone_no": c['customerDetails']['phone_no'],
        "email_id": c['customerDetails']['email_id'],
        "address": c['customerDetails']['address'],
        "loan_details": c['accountDetails']['loan_details'],
        "fixed_deposit": c['accountDetails']['fixed_deposit'],
        "recurring_deposit": c['accountDetails']['recurring_deposit'],
        "savings_account": c['accountDetails']['savings_account'],
        "current_account": c['accountDetails']['current_account'],
        "ticket_id": c['systemGenerated']['ticket_id'],
        "ticket_history": formatted_ticket_history,
        "customer_query": customer_query
    })

    return response
