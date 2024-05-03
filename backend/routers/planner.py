from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from langchain import OpenAI, PromptTemplate
from langchain.chains import LLMChain
from sqlalchemy.orm import Session
from database import SessionLocal, Itinerary
from schemas import ItineraryRequest, ItineraryResponse

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key for LangChain
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Initialize LangChain with OpenAI
langchain_llm = OpenAI(api_key=api_key)

# Define the prompt template
itinerary_template_string = """
        Give me itinerary for:
        {days} days in {city}. Donot include more than 3 things to do in a single day. Make your response for each days no more than 30 words. 
"""
itinerary_prompt = PromptTemplate(
    template=itinerary_template_string,
    input_variables=['days', 'city'],
)
itinerary_chain = LLMChain(
    llm=langchain_llm,
    prompt=itinerary_prompt,
)

router = APIRouter(prefix="/planner")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/provide-itinerary', response_model=ItineraryResponse)
async def plan_travel(itinerary_request: ItineraryRequest, db: Session = Depends(get_db)):
    try:
        
        input_data = {"days": itinerary_request.days, "city": itinerary_request.city}
        plan = itinerary_chain.run(input_data)
        new_itinerary = Itinerary(days=itinerary_request.days, city=itinerary_request.city)
        db.add(new_itinerary)
        db.commit()
        db.refresh(new_itinerary)

        return ItineraryResponse(itinerary=plan)
    except HTTPException as http_exc:
        # Forward FastAPI HTTP exceptions
        raise http_exc
    except Exception as exc:
        # Catch other unexpected issues and wrap them in HTTPException
        raise HTTPException(status_code=500, detail=str(exc))

