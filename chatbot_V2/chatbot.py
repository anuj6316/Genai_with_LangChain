from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import os
import json
from datetime import datetime
from langchain_redis import RedisChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
load_dotenv()

client = MongoClient()
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
parser = StrOutputParser()
db = client["Practice"]

def get_customer_data(member_code):
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
prompt_template = PromptTemplate(
    template="""You are a helpful customer service assistant for a banking institution. 
Based on the customer information and ticket history provided below, please:

Customer and Ticket Information:
{context}

Please provide a comprehensive response addressing the customer's situation and query but make you don't imagine anythings which is not provided if you don't know somethings just say so.""",
    input_variables=['context']
)

def main():
    print("=== Banking Customer Service Chatbot ===")
    
    # Get user input
    member_code = input("Enter Member Code (or 'quit' to exit): ").strip()
    
    if member_code.lower() == 'quit':
        return
    
    chat_history = RedisChatMessageHistory(redis_url = "redis://default:sO1mAtzEBPbuItKnw3CXUvtj4fpIl4FO@redis-17824.c279.us-central1-1.gce.redns.redis-cloud.com:17824", session_id=member_code)
        # Retrieve customer data
    print("\nRetrieving customer information...")
    customer, tickets = get_customer_data(member_code)
    
    if customer is None:
        print(f"Error: {tickets}")
        return
    
    # Format context for the AI
    context = format_customer_context(customer, tickets)
    print(f"\nCustomer: {customer['customerDetails']}")
    
    # Create chain and get response
    chain = prompt_template | model | parser
    
    # Option for follow-up questions
    while True:
        user_input = input("\nQuery: ").strip().lower()
        if user_input in ['quit', 'q', 'exit']:
            break
            
        prompt = PromptTemplate(
                template="""Based on the customer information below, please answer this specific question:
                
Question: {question}

Customer Information:
{context}

previous chat history: 
{chat_history}

Please provide a helpful and accurate response in normal text no need to make it in markdown format.""",
                input_variables=['question', 'context', 'chat_history']
            )
            
        follow_up_chain = prompt | model | parser
        try:
            response = follow_up_chain.invoke({
                "question": user_input,
                "context": context,
                'chat_history': chat_history.messages})
            print(f"\nResponse: {response}")
            chat_history.add_user_message(user_input)
            chat_history.add_ai_message(response)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()